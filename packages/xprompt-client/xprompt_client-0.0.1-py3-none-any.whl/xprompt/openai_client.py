import time

import requests

import xprompt
from xprompt.client_prompt_parser import ClientPromptParser
from xprompt.constants import BACKEND_ENDPOINT
from xprompt.data_client import OutputConvertorClient
from xprompt_common.errors import TryAgain
from xprompt.schemas import XPromptOutput


class OpenAIGenerate:
    output_convertor: OutputConvertorClient = OutputConvertorClient()

    @staticmethod
    def client_prompt_parsing(messages):
        for message in messages:
            if message["role"] != "assistant":
                prompt = message["content"]
                prompt_parser = ClientPromptParser(prompt=prompt)
                message["content"] = prompt_parser.run_services()

    @classmethod
    def create(cls, **kwargs):
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        kwargs["client_type"] = "chat_completion"
        kwargs["openai_api_key"] = xprompt.openai_api_key
        output_type = kwargs.pop("output_format", None)

        # client side parsing
        cls.client_prompt_parsing(kwargs["messages"])

        while True:
            try:
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {xprompt.api_key}",
                }

                response = requests.post(
                    f"{BACKEND_ENDPOINT}/generate/", headers=headers, json=kwargs
                )
                if response.status_code == 409:
                    raise TryAgain("failed with conflict")

                if response.status_code >= 300:
                    raise RuntimeError(response.text)

                break
            except TryAgain:
                if timeout is not None and time.time() > start + timeout:
                    raise
                time.sleep(1)

        generation_response = response.json()
        if output_type and generation_response["choices"]:
            for message in generation_response["choices"]:
                content = message["message"].get("content")
                if not content:
                    continue

                byte_content = cls.output_convertor.convert(
                    text=message["message"]["content"], output_type=output_type
                )
                message["message"]["byte_content"] = byte_content

        return XPromptOutput(generation_response)


class OpenAIChatCompletion(OpenAIGenerate):
    """
    Replace of openai.ChatCompletion
    """

    @classmethod
    def create(cls, **kwargs):
        kwargs["client_type"] = "chat_completion"
        return super().create(**kwargs)


class OpenAICompletion(OpenAIGenerate):
    """
    Replace of openai.Completion
    """

    @classmethod
    def create(cls, **kwargs):
        kwargs["client_type"] = "completion"
        return super().create(**kwargs)


class OpenAIEmbedding(OpenAIGenerate):
    """
    Replace of openai.Embedding
    """

    @classmethod
    def create(cls, **kwargs):
        kwargs["client_type"] = "embedding"
        return super().create(**kwargs)
