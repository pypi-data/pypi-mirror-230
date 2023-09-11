import asyncio
import inspect
import warnings
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import Extra, Field, root_validator
import dlm_matrix
from dlm_matrix.models import BaseLanguageModel
from dlm_matrix.callbacks.base import BaseCallbackManager
from dlm_matrix.callbacks.manager import (
    AsyncCallbackManager,
    AsyncCallbackManagerForLLMRun,
    CallbackManager,
    CallbackManagerForLLMRun,
    Callbacks,
)
from dlm_matrix.models import (
    Chain,
    ChatGeneration,
    ChatResult,
    LLMResult,
    PromptValue,
    get_buffer_string,
)
from dlm_matrix.chaintrees.base import UserChain, AssistantChain


def _get_verbosity() -> bool:
    return dlm_matrix.verbose


class BaseChatModel(BaseLanguageModel, ABC):
    """Whether to print out response text."""

    verbose: bool = Field(default_factory=_get_verbosity)

    callbacks: Callbacks = Field(default=None, exclude=True)
    callback_manager: Optional[BaseCallbackManager] = Field(default=None, exclude=True)

    @root_validator()
    def raise_deprecation(cls, values: Dict) -> Dict:
        """Raise deprecation warning if callback_manager is used."""
        if values.get("callback_manager") is not None:
            warnings.warn(
                "callback_manager is deprecated. Please use callbacks instead.",
                DeprecationWarning,
            )
            values["callbacks"] = values.pop("callback_manager", None)
        return values

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _combine_llm_outputs(self, llm_outputs: List[Optional[dict]]) -> dict:
        return {}

    def generate(
        self,
        messages: List[List[Chain]],
        stop: Optional[List[str]] = None,
        callbacks: Callbacks = None,
    ) -> LLMResult:
        """Top Level call"""

        callback_manager = CallbackManager.configure(
            callbacks, self.callbacks, self.verbose
        )
        message_strings = [get_buffer_string(m) for m in messages]
        run_manager = callback_manager.on_llm_start(
            {"name": self.__class__.__name__}, message_strings
        )

        new_arg_supported = inspect.signature(self._generate).parameters.get(
            "run_manager"
        )
        try:
            results = [
                self._generate(m, stop=stop, run_manager=run_manager)
                if new_arg_supported
                else self._generate(m, stop=stop)
                for m in messages
            ]
        except (KeyboardInterrupt, Exception) as e:
            run_manager.on_llm_error(e)
            raise e
        llm_output = self._combine_llm_outputs([res.llm_output for res in results])
        generations = [res.generations for res in results]
        output = LLMResult(generations=generations, llm_output=llm_output)
        run_manager.on_llm_end(output)
        return output

    async def agenerate(
        self,
        messages: List[List[Chain]],
        stop: Optional[List[str]] = None,
        callbacks: Callbacks = None,
    ) -> LLMResult:
        """Top Level call"""

        callback_manager = AsyncCallbackManager.configure(
            callbacks, self.callbacks, self.verbose
        )
        message_strings = [get_buffer_string(m) for m in messages]
        run_manager = await callback_manager.on_llm_start(
            {"name": self.__class__.__name__}, message_strings
        )

        new_arg_supported = inspect.signature(self._agenerate).parameters.get(
            "run_manager"
        )
        try:
            results = await asyncio.gather(
                *[
                    self._agenerate(m, stop=stop, run_manager=run_manager)
                    if new_arg_supported
                    else self._agenerate(m, stop=stop)
                    for m in messages
                ]
            )
        except (KeyboardInterrupt, Exception) as e:
            await run_manager.on_llm_error(e)
            raise e
        llm_output = self._combine_llm_outputs([res.llm_output for res in results])
        generations = [res.generations for res in results]
        output = LLMResult(generations=generations, llm_output=llm_output)
        await run_manager.on_llm_end(output)
        return output

    def generate_prompt(
        self,
        prompts: List[PromptValue],
        stop: Optional[List[str]] = None,
        callbacks: Callbacks = None,
    ) -> LLMResult:
        prompt_messages = [p.to_chain() for p in prompts]
        return self.generate(prompt_messages, stop=stop, callbacks=callbacks)

    async def agenerate_prompt(
        self,
        prompts: List[PromptValue],
        stop: Optional[List[str]] = None,
        callbacks: Callbacks = None,
    ) -> LLMResult:
        prompt_messages = [p.to_chain() for p in prompts]
        return await self.agenerate(prompt_messages, stop=stop, callbacks=callbacks)

    @abstractmethod
    def _generate(
        self,
        messages: List[Chain],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        """Top Level call"""

    @abstractmethod
    async def _agenerate(
        self,
        messages: List[Chain],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        """Top Level call"""

    def __call__(
        self,
        messages: List[Chain],
        stop: Optional[List[str]] = None,
        callbacks: Callbacks = None,
    ) -> Chain:
        generation = self.generate(
            [messages], stop=stop, callbacks=callbacks
        ).generations[0][0]
        if isinstance(generation, ChatGeneration):
            return generation.message
        else:
            raise ValueError("Unexpected generation type")

    def call_as_llm(self, message: str, stop: Optional[List[str]] = None) -> str:
        result = self([UserChain(content=message)], stop=stop)
        return result.content
