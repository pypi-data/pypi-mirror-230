import re
import typing
import abc
import openai
from .api_types import (
    LLMEventSchema,
    LLMOutputModel,
    LLMOutputModelMetadata,
    LLMEventInput,
    LLMEventInputPrompt,
)
from .logging import logger
from .tracer import set_llm_metadata


def safe_format(s: str, kwargs: typing.Dict[str, str]) -> str:
    for key, value in kwargs.items():
        s = s.replace("{@" + key + "}", value)
    # Throw error if there are any remaining placeholders of the form {@key}
    if re.search("{@.*?}", s):
        raise ValueError(f"Invalid template: {s}")
    return s


class LLMClient:
    def __init__(self, provider: str, **kwargs: typing.Any) -> None:
        self.__provider = provider
        self.__kwargs = kwargs

    @property
    def provider(self) -> str:
        return self.__provider

    @property
    def kwargs(self) -> typing.Dict[str, typing.Any]:
        return self.__kwargs

    @abc.abstractmethod
    def get_model_name(self) -> str:
        raise NotImplementedError

    async def run(self, prompt_template: str, vars: typing.Dict[str, str]) -> str:
        event = LLMEventSchema(
            provider=self.provider,
            model_name=self.get_model_name(),
            input=LLMEventInput(
                prompt=LLMEventInputPrompt(
                    template=prompt_template, template_args=vars
                ),
                invocation_params=self.__kwargs,
            ),
            output=None,
        )
        set_llm_metadata(event)
        prompt = safe_format(prompt_template, vars)
        logger.info(f"Running {self.provider} with prompt:\n{prompt}")
        model_name, response = await self._run(prompt)
        logger.info(f"RESPONSE:\n{response.raw_text}")
        # Update event with output
        event.output = response
        event.mdl_name = model_name
        return response.raw_text

    @abc.abstractmethod
    async def _run(self, prompt: str) -> typing.Tuple[str, LLMOutputModel]:
        raise NotImplementedError("Client must implement _run method")


class OpenAILLMClient(LLMClient):
    def __init__(self, provider: str, **kwargs: typing.Any) -> None:
        super().__init__(provider=provider, **kwargs)

    def get_model_name(self) -> str:
        # Try some well known keys
        for key in ["model_name", "model", "engine"]:
            if key in self.kwargs:
                val = self.kwargs[key]
                if isinstance(val, str):
                    return val.lower()
        return "unknown"

    def is_chat(self) -> bool:
        name = self.get_model_name()
        for chat in ["gpt-35", "gpt-4", "gpt-3.5"]:
            if chat in name:
                return True
        return False

    async def _run(self, prompt: str) -> typing.Tuple[str, LLMOutputModel]:
        # Guess is its a chatcompletions
        if self.is_chat():
            response = await openai.ChatCompletion.acreate(messages=[{"role": "user", "content": prompt}], **self.kwargs)  # type: ignore
            text = response["choices"][0]["message"]["content"]
            usage = response["usage"]
            model = response["model"]
            return model, LLMOutputModel(
                raw_text=text,
                metadata=LLMOutputModelMetadata(
                    logprobs=None,
                    prompt_tokens=usage.get("prompt_tokens", None),
                    output_tokens=usage.get("completion_tokens", None),
                    total_tokens=usage.get("total_tokens", None),
                ),
            )
        else:
            response = await openai.Completion.acreate(prompt=prompt, **self.kwargs)  # type: ignore
            text = response["choices"][0]["text"]
            usage = response["usage"]
            model = response["model"]
            return model, LLMOutputModel(
                raw_text=text,
                metadata=LLMOutputModelMetadata(
                    logprobs=response["choices"][0]["logprobs"],
                    prompt_tokens=usage.get("prompt_tokens", None),
                    output_tokens=usage.get("completion_tokens", None),
                    total_tokens=usage.get("total_tokens", None),
                ),
            )
