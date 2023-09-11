from __future__ import annotations
import logging
import sys
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Union
from dlm_matrix.utils import log_handler
from pydantic import Extra, Field, root_validator
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
import os
from dlm_matrix.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from dlm_matrix.embedding.utils import semantic_similarity_cosine
from dlm_matrix.infrence.base import BaseChatModel
from dlm_matrix.models.message.generation import (
    Chain,
    ChatGeneration,
    ChatResult,
)
from dlm_matrix.chaintrees.base import _convert_dict_to_message
from collections import deque

logger = logging.getLogger(__name__)


def _create_retry_decorator(llm: ChatOpenAI) -> Callable[[Any], Any]:
    import openai

    min_seconds = 1
    max_seconds = 60
    # Wait 2^x * 1 second between each retry starting with
    # 4 seconds, then up to 10 seconds, then 10 seconds afterwards
    return retry(
        reraise=True,
        stop=stop_after_attempt(llm.max_retries),
        wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
        retry=(
            retry_if_exception_type(openai.error.Timeout)
            | retry_if_exception_type(openai.error.APIError)
            | retry_if_exception_type(openai.error.APIConnectionError)
            | retry_if_exception_type(openai.error.RateLimitError)
            | retry_if_exception_type(openai.error.ServiceUnavailableError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )


def _convert_message_to_dict(message: Dict[str, Any]) -> dict:
    if "role" in message and "content" in message:
        message_dict = {"role": message["role"], "content": message["content"]}
    else:
        raise ValueError(f"Got unknown type {message}")

    if "name" in message:
        message_dict["name"] = message["name"]
    return message_dict


class ChatOpenAI(BaseChatModel):
    """Chat wrapper for OpenAI API.

    Args:
        model_name (str): Model name to use.
        temperature (float): What sampling temperature to use.
        model_kwargs (Dict[str, Any]): Holds any model parameters valid for `create` call not explicitly specified.
        openai_api_key (Optional[str]): OpenAI API key, if not available as an environment variable.
        openai_organization (Optional[str]): OpenAI organization, if not available as an environment variable.
        request_timeout (Optional[Union[float, Tuple[float, float]]]): Timeout for requests to OpenAI completion API. Default is 600 seconds.
        max_retries (int): Maximum number of retries to make when generating.
        streaming (bool): Whether to stream the results or not.
        n (int): Number of chat completions to generate for each prompt.
        max_tokens (Optional[int]): Maximum number of tokens to generate.
        frequency_penalty (Optional[float]): Frequency penalty to use.
        presence_penalty (Optional[float]): Presence penalty to use.

    """

    client: Any  #: :meta private:

    model_name: str = "gpt-3.5-turbo-16k"
    """Model name to use."""
    temperature: float = 1
    """What sampling temperature to use."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    openai_api_key: Optional[str] = None

    openai_organization: Optional[str] = None

    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
    max_retries: int = 2
    """Maximum number of retries to make when generating."""
    streaming: bool = True
    """Whether to stream the results or not."""
    n: int = 1
    """Number of chat completions to generate for each prompt."""
    max_tokens: Optional[int] = 3000
    """Maximum number of tokens to generate."""

    frequency_penalty: Optional[float] = 1

    presence_penalty: Optional[float] = 1

    high_similarity_threshold = 0.8

    low_similarity_threshold = 0.4

    high_similarity_buffer = deque(
        maxlen=10
    )  # Cache up to 5 high-similarity user messages
    low_similarity_buffer = deque(
        maxlen=5
    )  # Cache up to 5 low-similarity user messages

    target_tokens = 2000

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.ignore

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = {field.alias for field in cls.__fields__.values()}

        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                logger.warning(
                    f"""WARNING! {field_name} is not default parameter.
                    {field_name} was transferred to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)

        disallowed_model_kwargs = all_required_field_names | {"model"}
        invalid_model_kwargs = disallowed_model_kwargs.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                f"Instead they were passed in as part of `model_kwargs` parameter."
            )

        values["model_kwargs"] = extra
        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        openai_api_key = values.get("openai_api_key", None)

        os.environ["OPENAI_API_KEY"] = openai_api_key
        try:
            import openai

            openai.api_key = openai_api_key
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please it install it with `pip install openai`."
            )
        try:
            values["client"] = openai.ChatCompletion
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")
        if "API_KEYS" in values:
            values["api_keys"] = values["API_KEYS"]
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "model": self.model_name,
            "request_timeout": self.request_timeout,
            "max_tokens": self.max_tokens,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            **self.model_kwargs,
        }

    def _create_retry_decorator(self) -> Callable[[Any], Any]:
        import openai

        min_seconds = 1
        max_seconds = 60
        # Wait 2^x * 1 second between each retry starting with
        # 4 seconds, then up to 10 seconds, then 10 seconds afterwards
        return retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
            retry=(
                retry_if_exception_type(openai.error.Timeout)
                | retry_if_exception_type(openai.error.APIError)
                | retry_if_exception_type(openai.error.APIConnectionError)
                | retry_if_exception_type(openai.error.RateLimitError)
                | retry_if_exception_type(openai.error.ServiceUnavailableError)
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )

    def completion_with_retry(self, **kwargs: Any) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = self._create_retry_decorator()

        @retry_decorator
        def _completion_with_retry(**kwargs: Any) -> Any:
            return self.client.create(**kwargs)

        return _completion_with_retry(**kwargs)

    def _combine_llm_outputs(self, llm_outputs: List[Optional[dict]]) -> dict:
        overall_token_usage: dict = {}
        for output in llm_outputs:
            if output is None:
                # Happens in streaming
                continue
            token_usage = output["token_usage"]
            for k, v in token_usage.items():
                if k in overall_token_usage:
                    overall_token_usage[k] += v
                else:
                    overall_token_usage[k] = v
        return {"token_usage": overall_token_usage, "model_name": self.model_name}

    def _generate(
        self,
        messages: List[Chain],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        message_dicts, params = self._create_message_dicts(messages, stop)
        if self.streaming:
            inner_completion = ""
            role = "assistant"
            params["stream"] = True
            for stream_resp in self.completion_with_retry(
                messages=message_dicts, **params
            ):
                role = stream_resp["choices"][0]["delta"].get("role", role)
                token = stream_resp["choices"][0]["delta"].get("content", "")
                inner_completion += token
                if run_manager:
                    run_manager.on_llm_new_token(token)
            message = _convert_dict_to_message(
                {"content": inner_completion, "role": role}
            )
            return ChatResult(generations=[ChatGeneration(message=message)])
        response = self.completion_with_retry(messages=message_dicts, **params)
        return self._create_chat_result(response)

    def _create_message_dicts(
        self, messages: List[Chain], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params: Dict[str, Any] = {**{"model": self.model_name}, **self._default_params}
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = [_convert_message_to_dict(m) for m in messages]
        return message_dicts, params

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        generations = []
        for res in response["choices"]:
            message = _convert_dict_to_message(res["message"])
            gen = ChatGeneration(message=message)
            generations.append(gen)
        llm_output = {"token_usage": response["usage"], "model_name": self.model_name}
        return ChatResult(generations=generations, llm_output=llm_output)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"model_name": self.model_name}, **self._default_params}

    def get_num_tokens(
        self,
        text: str,
        last_user_msg: Optional[str] = None,
        similarity_weight: float = 0.5,
        use_similarity: bool = False,
        model: Optional[str] = None,
    ) -> int:
        """Calculate number of tokens in a message, adjusted by semantic similarity if provided."""

        # Check Python version
        if sys.version_info[1] <= 7:
            logging.warning(
                "Python version is too low for advanced token counting. Falling back to basic token count."
            )
            return super().get_num_tokens(
                text
            )  # Assuming a parent class exists that implements this function

        # Import tiktoken
        try:
            import tiktoken
        except ImportError:
            logging.error("Could not import tiktoken. Please install it via pip.")
            raise ImportError(
                "Could not import tiktoken. Install it via pip install tiktoken."
            )

        # Tokenize text to calculate base token count
        try:
            enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokenized_text = enc.encode(text)
            base_token_count = len(tokenized_text)
        except Exception as e:
            logging.error(f"Tokenization failed due to: {e}")
            raise RuntimeError(f"Error during tokenization: {e}")

        # If a last_user_msg exists, adjust the token count based on semantic similarity
        if last_user_msg:
            try:
                if use_similarity:
                    similarity = semantic_similarity_cosine(
                        text, last_user_msg, model=model
                    )
                    adjusted_token_count = int(
                        base_token_count * (1 - similarity_weight * similarity)
                    )
                    return adjusted_token_count
                else:
                    return base_token_count

            except Exception as e:
                logging.warning(
                    f"Could not adjust token count due to semantic similarity error: {e}. Falling back to base token count."
                )

        return base_token_count

    def _truncate_conversation_history(
        self,
        conversation_history: List[Any],
        preserve_context: bool = True,
        min_context_tokens: int = 50,
        dynamic_threshold_window: int = 5,
    ) -> List[Dict[str, str]]:
        if not conversation_history:
            log_handler("Conversation history is empty")
            return []

        if self.max_tokens <= 0:
            log_handler("max_tokens should be a positive integer", level="error")
            raise ValueError("max_tokens should be a positive integer.")

        conversation_history_dicts = [
            {
                "role": msg.__class__.__name__.replace("Chain", "").lower(),
                "content": msg.content.text,
            }
            for msg in conversation_history
            if msg.content.text
        ]

        last_user_msgs = [
            msg for msg in reversed(conversation_history_dicts) if msg["role"] == "user"
        ][:dynamic_threshold_window]

        if last_user_msgs:
            avg_similarity = sum(
                self.get_num_tokens(msg["content"], msg["content"])
                for msg in last_user_msgs
            ) / len(last_user_msgs)

            high_similarity_threshold = self.high_similarity_threshold * avg_similarity
            low_similarity_threshold = self.low_similarity_threshold * avg_similarity

        else:
            high_similarity_threshold = self.high_similarity_threshold
            low_similarity_threshold = self.low_similarity_threshold

        last_user_msg = next(
            (
                msg
                for msg in reversed(conversation_history_dicts)
                if msg["role"] == "user"
            ),
            None,
        )

        last_user_msg_content = last_user_msg["content"] if last_user_msg else ""

        adjusted_tokens = [
            {
                **msg,
                "tokens": self.get_num_tokens(msg["content"], last_user_msg_content),
            }
            for msg in conversation_history_dicts
        ]

        truncated_history = []
        tokens_so_far = 0

        for message in reversed(adjusted_tokens):
            if tokens_so_far + message["tokens"] <= min(
                self.target_tokens, self.max_tokens
            ):
                truncated_history.insert(
                    0, {"role": message["role"], "content": message["content"]}
                )
                tokens_so_far += message["tokens"]

                last_assistant_msg_tokens = self.get_num_tokens(
                    last_user_msg_content, last_user_msg_content
                )

                if last_assistant_msg_tokens >= high_similarity_threshold:
                    # Enhance the chain between the user and assistant
                    if self.high_similarity_buffer:
                        last_high_similarity_msg = self.high_similarity_buffer.popleft()
                        truncated_history.insert(0, last_high_similarity_msg)
                        tokens_so_far += self.get_num_tokens(
                            last_high_similarity_msg["content"],
                            last_high_similarity_msg["content"],
                        )

                elif last_assistant_msg_tokens <= low_similarity_threshold:
                    self.low_similarity_buffer.append(
                        {"role": "assistant", "content": message["content"]}
                    )

                    if self.high_similarity_buffer:
                        last_high_similarity_msg = self.high_similarity_buffer.popleft()
                        truncated_history.append(last_high_similarity_msg)

        if len(self.low_similarity_buffer) > 3 and self.high_similarity_buffer:
            self.low_similarity_buffer.popleft()
            last_high_similarity_msg = self.high_similarity_buffer.popleft()
            truncated_history.append(last_high_similarity_msg)

        else:
            if preserve_context and tokens_so_far < min_context_tokens:
                for message in reversed(adjusted_tokens):
                    if message["role"] == "assistant":
                        if tokens_so_far + message["tokens"] <= min(
                            self.target_tokens, self.max_tokens
                        ):
                            truncated_history.insert(
                                0,
                                {
                                    "role": message["role"],
                                    "content": message["content"],
                                },
                            )
                            tokens_so_far += message["tokens"]
                            if tokens_so_far >= min_context_tokens:
                                break

        log_handler(f"Truncated conversation history: {truncated_history}")
        log_handler(f"Tokens used: {tokens_so_far} out of {self.max_tokens}")

        return truncated_history

    async def _agenerate(
        self,
        messages: List[Chain],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        message_dicts, params = self._create_message_dicts(messages, stop)
        if self.streaming:
            inner_completion = ""
            role = "assistant"
            params["stream"] = True
            async for stream_resp in await acompletion_with_retry(
                self, messages=message_dicts, **params
            ):
                role = stream_resp["choices"][0]["delta"].get("role", role)
                token = stream_resp["choices"][0]["delta"].get("content", "")
                inner_completion += token
                if run_manager:
                    await run_manager.on_llm_new_token(token)
            message = _convert_dict_to_message(
                {"content": inner_completion, "role": role}
            )
            return ChatResult(generations=[ChatGeneration(message=message)])
        else:
            response = await acompletion_with_retry(
                self, messages=message_dicts, **params
            )
            return self._create_chat_result(response)


async def acompletion_with_retry(llm: ChatOpenAI, **kwargs: Any) -> Any:
    """Use tenacity to retry the async completion call."""
    retry_decorator = _create_retry_decorator(llm)

    @retry_decorator
    async def _completion_with_retry(**kwargs: Any) -> Any:
        # Use OpenAI's async api https://github.com/openai/openai-python#async-api
        return await llm.client.acreate(**kwargs)

    return await _completion_with_retry(**kwargs)
