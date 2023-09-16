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


import os
from typing import Dict, List, Tuple, Union

import langchain

from arcus.api_client import APIClient, ArcusResponse
from arcus.prompt.text.config import Config
from arcus.prompt.text.default_prompts import DEFAULT_CONTEXT_PROMPT
from arcus.prompt.text.llms import LLM, LLMOutput
from arcus.prompt.text.messages import (
    OpenAIMessage,
    OpenAIMessageList,
    OpenAIRole,
)

OPENAI_COMPLETION_MODEL_IDS = [
    "ada",
    "text-ada-001",
    "babbage",
    "text-babbage-001",
    "curie",
    "text-curie-001",
    "davinci",
    "text-davinci-002",
    "text-davinci-003",
    "code-cushman-001",
]

OPENAI_CHAT_MODEL_IDS = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
]

OPENAI_MODEL_IDS = OPENAI_COMPLETION_MODEL_IDS + OPENAI_CHAT_MODEL_IDS
HELPFUL_ASSISTANT_SYSTEM_MESSAGE = OpenAIMessage(
    {
        "role": OpenAIRole.SYSTEM.value,
        "content": "You are a helpful assistant.",
    }
)

OPENAI_API_KEY = "OPENAI_API_KEY"


class OpenAI(LLM):
    def __init__(
        self,
        model_id: str,
        config: Config,
        **kwargs,
    ):
        super().__init__(model_id, config)

        assert model_id in OPENAI_MODEL_IDS, (
            "Invalid model_id for OpenAI: "
            + f"{model_id}. Valid model_ids are: {OPENAI_MODEL_IDS}."
        )

        self._is_chat = model_id in OPENAI_CHAT_MODEL_IDS

        if self.config.get_llm_api_key() is None:
            self.config.set_llm_api_key(os.environ.get(OPENAI_API_KEY, None))

        if self.is_chat():
            self.model = langchain.chat_models.ChatOpenAI(
                model_name=model_id,
                openai_api_key=self.config.get_llm_api_key(),
                **kwargs,
            )
        else:
            self.model = langchain.llms.OpenAI(
                model_name=model_id,
                openai_api_key=self.config.get_llm_api_key(),
                **kwargs,
            )

        self.api_client = APIClient(self.config)

    def _augment_prompt_context(
        self, prompt: str, context_prompt: str = DEFAULT_CONTEXT_PROMPT
    ) -> Tuple[str, str]:
        if not self.is_chat():
            max_tokens_remaining = self.model.max_tokens_for_prompt(prompt)
        else:
            max_tokens_remaining = None

        response: ArcusResponse = self.api_client.request(
            "POST",
            "/prompt/enrich",
            {
                "project_id": self.config.get_project_id(),
                "max_tokens_remaining": max_tokens_remaining,
            },
            json={
                "prompt": prompt,
                "context_prompt": context_prompt,
            },
        )

        if not response.status_ok:
            raise Warning(
                f"Failed to get additional context for prompt: {prompt}. "
                + f"Response: {response}"
            )
            return prompt, ""

        enriched_prompt = response.data["enriched_prompt"]
        context_summary = response.data["context_summary"]

        return enriched_prompt, context_summary

    def _construct_llm_call(self, prompt_messages: OpenAIMessageList) -> str:
        if self.is_chat():
            return self.model(
                [
                    message.get_langchain_message()
                    for message in prompt_messages.get_message_list()
                ]
            ).content

        return self.model(prompt_messages.get_final_prompt())

    def generate(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        context_prompt: str = DEFAULT_CONTEXT_PROMPT,
    ) -> LLMOutput:
        if not isinstance(prompt, str):
            prompt_messages = OpenAIMessageList(
                [OpenAIMessage(message_dict) for message_dict in prompt]
            )
        else:
            prompt_messages = OpenAIMessageList(
                [
                    HELPFUL_ASSISTANT_SYSTEM_MESSAGE,
                    OpenAIMessage(
                        {
                            "role": OpenAIRole.USER.value,
                            "content": prompt,
                        }
                    ),
                ]
            )

        enriched_prompt, context_summary = self._augment_prompt_context(
            prompt_messages.get_final_prompt(), context_prompt
        )

        prompt_messages.set_final_prompt(enriched_prompt)

        return LLMOutput(
            self._construct_llm_call(prompt_messages), context_summary
        )

    def is_chat(self) -> bool:
        return self._is_chat
