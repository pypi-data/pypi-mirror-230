from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union
from dlm_matrix.models.message.chain import Chain
from pydantic import BaseModel, root_validator, Field
import torch


class BaseMessage(BaseModel):
    """Message object."""

    content: str
    additional_kwargs: dict = Field(default_factory=dict)

    @property
    @abstractmethod
    def type(self) -> str:
        """Type of the message, used for serialization."""


class Generation(BaseModel):
    """Output of a single generation."""

    text: str
    """Generated text output."""

    generation_info: Optional[Dict[str, Any]] = None
    """Raw generation info response from the provider"""
    """May include things like reason for finishing (e.g. in OpenAI)"""
    # TODO: add log probs


class ChatGeneration(Generation):
    """Output of a single generation."""

    text = ""
    message: Chain

    @root_validator
    def set_text(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["text"] = values["message"].content
        return values


class ChatResult(BaseModel):
    """Class that contains all relevant information for a Chat Result."""

    generations: List[ChatGeneration]
    """List of the things generated."""
    llm_output: Optional[dict] = None
    """For arbitrary LLM provider specific output."""


class LLMResult(BaseModel):
    """Class that contains all relevant information for an LLM Result."""

    generations: List[List[Generation]]
    """List of the things generated. This is List[List[]] because
    each input could have multiple generations."""
    llm_output: Optional[dict] = None
    """For arbitrary LLM provider specific output."""


class PromptValue(BaseModel, ABC):
    @abstractmethod
    def to_string(self) -> str:
        """Return prompt as string."""

    @abstractmethod
    def to_chain(self) -> List[Chain]:
        """Return prompt as messages."""


class BaseLanguageModel(BaseModel, ABC):
    @abstractmethod
    def generate_prompt(
        self,
        prompts: List[PromptValue],
        stop: Optional[List[str]] = None,
        callbacks: object = None,
    ) -> LLMResult:
        """Take in a list of prompt values and return an LLMResult."""

    @abstractmethod
    async def agenerate_prompt(
        self,
        prompts: List[PromptValue],
        stop: Optional[List[str]] = None,
        callbacks: object = None,
    ) -> LLMResult:
        """Take in a list of prompt values and return an LLMResult."""

    def get_token_ids(self, text: str) -> List[int]:
        """Get the token present in the text."""
        return _get_token_ids_default_method(text)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text."""
        return len(self.get_token_ids(text))

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """Get the number of tokens in the message."""
        return sum([self.get_num_tokens(get_buffer_string([m])) for m in messages])

    @classmethod
    def all_required_field_names(cls) -> Set:
        all_required_field_names = set()
        for field in cls.__fields__.values():
            all_required_field_names.add(field.name)
            if field.has_alias:
                all_required_field_names.add(field.alias)
        return all_required_field_names


def get_buffer_string(
    messages: List[Dict[str, Any]], human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    """Get buffer string of messages."""
    string_messages = []
    for m in messages:
        if "role" in m and "content" in m:
            if m["role"] == "user":
                role = human_prefix
            elif m["role"] == "assistant":
                role = ai_prefix
            elif m["role"] == "system":
                role = "System"
            else:
                raise ValueError(f"Got unsupported message type: {m}")

            string_messages.append(f"{role}: {m['content']}")
        else:
            raise ValueError(f"Invalid message format: {m}")

    return "\n".join(string_messages)


def _get_token_ids_default_method(
    text: str,
    verbose: bool = False,
    model_name: str = "distilbert-base-uncased",
    embeddings: bool = False,
    to_list: bool = True,
) -> Union[Dict, List[int]]:
    try:
        from transformers import AutoModel, GPT2TokenizerFast
    except ImportError:
        raise ValueError(
            "Could not import transformers python package. "
            "This is needed to tokenize the text. "
            "Please install it with `pip install transformers`."
        )

    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    model = AutoModel.from_pretrained(model_name) if embeddings else None

    if verbose or embeddings:
        split_texts = text.split("\n\n") if "\n\n" in text else [text]

        aggregated_tokens = []
        aggregated_token_ids = []
        aggregated_token_count = 0
        aggregated_embeddings = []

        for split_text in split_texts:
            inputs = tokenizer(split_text, return_tensors="pt")
            tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
            token_ids = inputs.input_ids[0].tolist()
            token_count = inputs.input_ids[0].shape[0]

            if embeddings:
                with torch.no_grad():
                    outputs = model(**inputs)
                last_hidden_states = outputs.last_hidden_state
                aggregated_embeddings.append(last_hidden_states)

            aggregated_tokens.extend(tokens)
            aggregated_token_ids.extend(token_ids)
            aggregated_token_count += token_count

        result = {
            "tokens": aggregated_tokens,
            "token_ids": aggregated_token_ids,
            "token_count": aggregated_token_count,
        }

        if embeddings:
            aggregated_embeddings = torch.cat(aggregated_embeddings, dim=0)
            result["embedding"] = (
                aggregated_embeddings.tolist() if to_list else aggregated_embeddings
            )

        return result

    else:
        return tokenizer.encode(text)
