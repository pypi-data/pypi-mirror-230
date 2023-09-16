from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchaincoexpert.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchaincoexpert.chat_models.anthropic import convert_messages_to_prompt_anthropic
from langchaincoexpert.chat_models.base import BaseChatModel
from langchaincoexpert.llms.bedrock import BedrockBase
from langchaincoexpert.pydantic_v1 import Extra
from langchaincoexpert.schema.messages import AIMessage, BaseMessage
from langchaincoexpert.schema.output import ChatGeneration, ChatGenerationChunk, ChatResult


class ChatPromptAdapter:
    """Adapter class to prepare the inputs from langchaincoexpert to prompt format
    that Chat model expects.
    """

    @classmethod
    def convert_messages_to_prompt(
        cls, provider: str, messages: List[BaseMessage]
    ) -> str:
        if provider == "anthropic":
            prompt = convert_messages_to_prompt_anthropic(messages=messages)
        else:
            raise NotImplementedError(
                f"Provider {provider} model does not support chat."
            )
        return prompt


class BedrockChat(BaseChatModel, BedrockBase):
    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "amazon_bedrock_chat"

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        raise NotImplementedError(
            """Bedrock doesn't support stream requests at the moment."""
        )

    def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        raise NotImplementedError(
            """Bedrock doesn't support async requests at the moment."""
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        provider = self._get_provider()
        prompt = ChatPromptAdapter.convert_messages_to_prompt(
            provider=provider, messages=messages
        )

        params: Dict[str, Any] = {**kwargs}
        if stop:
            params["stop_sequences"] = stop

        completion = self._prepare_input_and_invoke(
            prompt=prompt, stop=stop, run_manager=run_manager, **params
        )

        message = AIMessage(content=completion)
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        raise NotImplementedError(
            """Bedrock doesn't support async stream requests at the moment."""
        )
