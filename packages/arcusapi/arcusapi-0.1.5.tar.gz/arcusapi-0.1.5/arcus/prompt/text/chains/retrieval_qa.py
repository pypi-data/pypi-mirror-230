# Copyright [2023] [Arcus Inc.]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.question_answering.stuff_prompt import PROMPT_SELECTOR
from langchain.chains.retrieval_qa.base import (
    BaseRetrievalQA as LangchainBaseRetrievalQA,
)
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from pydantic import Field

from arcus.api_client import APIClient, ArcusResponse
from arcus.prompt.text.config import Config


class BaseRetrievalQA(LangchainBaseRetrievalQA):
    """
    Retrieval QA using external data from Arcus along with a
    Langchain `BaseCombineDocumentsChain` to combine first-party
    documents.
    """

    config: Config
    combine_documents_chain: BaseCombineDocumentsChain
    """Chain to use to combine the documents."""
    input_key: str = "query"
    output_key: str = "result"
    external_data_summary_key: str = "external_data_summary"
    return_source_documents: bool = False
    """Return the source documents."""
    return_external_data_summary: bool = False

    @property
    def api_client(self) -> APIClient:
        """Return the API client."""
        return APIClient(self.config)

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.

        :meta private:
        """
        _output_keys = [self.output_key]
        if self.return_source_documents:
            _output_keys = _output_keys + ["source_documents"]
        if self.return_external_data_summary:
            _output_keys = _output_keys + [self.external_data_summary_key]
        return _output_keys

    @classmethod
    def from_llm(
        cls,
        config: Config,
        llm: BaseLanguageModel,
        prompt: Optional[PromptTemplate] = None,
        **kwargs: Any,
    ) -> BaseRetrievalQA:
        """Initialize from LLM."""
        _prompt = prompt or PROMPT_SELECTOR.get_prompt(llm)
        llm_chain = LLMChain(llm=llm, prompt=_prompt)
        document_prompt = PromptTemplate(
            input_variables=["page_content"],
            template="Context:\n{page_content}",
        )
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_variable_name="context",
            document_prompt=document_prompt,
        )

        return cls(
            config=config,
            combine_documents_chain=combine_documents_chain,
            **kwargs,
        )

    @classmethod
    def from_chain_type(
        cls,
        config: Config,
        llm: BaseLanguageModel,
        chain_type: str = "stuff",
        chain_type_kwargs: Optional[dict] = None,
        **kwargs: Any,
    ) -> BaseRetrievalQA:
        """Load chain from chain type."""
        _chain_type_kwargs = chain_type_kwargs or {}
        combine_documents_chain = load_qa_chain(
            llm, chain_type=chain_type, **_chain_type_kwargs
        )
        return cls(
            config=config,
            combine_documents_chain=combine_documents_chain,
            **kwargs,
        )

    def _augment_question_with_arcus(
        self, question: str, max_tokens_remaining: Optional[int] = None
    ) -> Tuple[str, str]:
        """Augment the question with Arcus API.

        Returns a summary of the context as well as the augmented question.
        """
        response: ArcusResponse = self.api_client.request(
            "POST",
            "/prompt/enrich",
            {
                "project_id": self.config.get_project_id(),
                "max_tokens_remaining": max_tokens_remaining,
            },
            json={"prompt": question},
        )

        if not response.status_ok:
            raise Warning(
                f"Failed to get additional context from Arcus for prompt: "
                f"{question}. Response: {response}"
            )
            return question, ""

        enriched_question = response.data["enriched_prompt"]
        context_summary = response.data["context_summary"]

        return enriched_question, context_summary

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Run get_relevant_text and llm on input query.

        If chain has 'return_source_documents' as 'True', returns
        the retrieved documents as well under the key 'source_documents'.

        If the chain has 'return_external_data_summary' as 'True', returns
        the external data summary under the key 'external_data_summary'.

        Example:
        .. code-block:: python

        res = indexqa({'query': 'This is my query'})
        answer, docs, external_docs = (
            res['result'],
            res['source_documents'],
            res['external_data_summary'],
        )
        """
        _run_manager = (
            run_manager or CallbackManagerForChainRun.get_noop_manager()
        )
        question = inputs[self.input_key]

        docs = self._get_docs(question)

        prompt_length: Optional[
            int
        ] = self.combine_documents_chain.prompt_length(docs, question=question)

        # set a max tokens if it's available
        if prompt_length is None or not hasattr(
            self.combine_documents_chain.llm_chain.llm, "max_tokens_for_prompt"
        ):
            max_tokens_remaining = None
        else:
            # Maximum tokens remaining is the maximum tokens for the prompt
            llm = self.combine_documents_chain.llm_chain.llm
            max_tokens_remaining = (
                llm.max_tokens_for_prompt("") - prompt_length
            )

        # Augment the question with Arcus data
        enriched_question, context_summary = self._augment_question_with_arcus(
            question,
            max_tokens_remaining=max_tokens_remaining,
        )

        answer = self.combine_documents_chain.run(
            input_documents=docs,
            question=enriched_question,
            callbacks=_run_manager.get_child(),
        )

        output_dict: Dict[str, Any] = {}

        for key in self.output_keys:
            if key == self.output_key:
                output_dict[key] = answer
            elif key == "source_documents":
                output_dict[key] = docs
            elif key == self.external_data_summary_key:
                output_dict[key] = context_summary
            else:
                raise ValueError(f"Unknown output key: {key}")

        return output_dict

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Run get_relevant_text and llm on input query.

        If chain has 'return_source_documents' as 'True', returns
        the retrieved documents as well under the key 'source_documents'.

        If the chain has 'return_external_data_summary' as 'True', returns
        the external data summary under the key 'external_data_summary'.

        Example:
        .. code-block:: python

        res = indexqa({'query': 'This is my query'})
        answer, docs, external_docs = (
            res['result'],
            res['source_documents'],
            res['external_data_summary'],
        )
        """
        _run_manager = (
            run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        )
        question = inputs[self.input_key]

        docs = await self._aget_docs(question)

        prompt_length: Optional[
            int
        ] = self.combine_documents_chain.prompt_length(docs, question=question)

        # set a max tokens if it's available
        if prompt_length is None or not hasattr(
            self.combine_documents_chain.llm_chain.llm, "max_tokens_for_prompt"
        ):
            max_tokens_remaining = None
        else:
            # Maximum tokens remaining is the maximum tokens for the prompt
            llm = self.combine_documents_chain.llm_chain.llm
            max_tokens_remaining = (
                llm.max_tokens_for_prompt("") - prompt_length
            )

        # Augment the question with Arcus data
        enriched_question, context_summary = self._augment_question_with_arcus(
            question,
            max_tokens_remaining=max_tokens_remaining,
        )

        answer = await self.combine_documents_chain.arun(
            input_documents=docs,
            question=enriched_question,
            callbacks=_run_manager.get_child(),
        )

        output_dict: Dict[str, Any] = {}

        for key in self.output_keys:
            if key == self.output_key:
                output_dict[key] = answer
            elif key == "source_documents":
                output_dict[key] = docs
            elif key == self.external_data_summary_key:
                output_dict[key] = context_summary
            else:
                raise ValueError(f"Unknown output key: {key}")

        return output_dict


class RetrievalQA(BaseRetrievalQA):
    """Chain for question-answering against a first-party index along
    with external data from Arcus.

    Example:
        .. code-block:: python

            from arcus.prompt.text.chains import RetrievalQA
            from arcus.prompt.text.config import Config

            from langchain.llms import OpenAI
            from langchain.vectorstores import FAISS
            from langchain.vectorstores.base import VectorStoreRetriever

            retriever = VectorStoreRetriever(vectorstore=FAISS(...))
            retrievalQA = RetrievalQA.from_llm(
                config=Config(...),
                llm=OpenAI(),
                retriever=retriever
            )

    """

    retriever: BaseRetriever = Field(exclude=True)

    def _get_docs(self, question: str) -> List[Document]:
        return self.retriever.get_relevant_documents(question)

    async def _aget_docs(self, question: str) -> List[Document]:
        return await self.retriever.aget_relevant_documents(question)
