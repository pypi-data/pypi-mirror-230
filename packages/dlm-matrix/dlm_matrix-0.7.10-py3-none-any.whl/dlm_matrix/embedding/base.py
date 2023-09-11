from typing import List, Tuple, Union
import openai
from tqdm import tqdm
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
)
from functools import wraps
import os
from loguru import logger


class InvalidAPIKey(Exception):
    pass


class BaseEmbedding:
    def __init__(self, api_key: str = None, batch_size: int = 128):
        if api_key is None or not isinstance(api_key, str):
            raise InvalidAPIKey("API Key is either missing or invalid.")
        self._semantic_vectors = []
        self.keywords = []
        self._openai_api_key = api_key
        self.batch_size = batch_size
        self.show_progress_bar = True
        self.MAX_RETRIES = 3
        self.engine = "text-embedding-ada-002"

    def _check_and_set_openai_api(self):
        """Check and set OpenAI API."""
        if not self._openai_api_key:
            raise ValueError("OpenAI API key not set")
        openai.api_key = self._openai_api_key

    def _create_retry_decorator(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            retry_decorator = retry(
                stop=stop_after_attempt(self.MAX_RETRIES),
                wait=wait_exponential(multiplier=1, min=2, max=6),
                retry=(
                    retry_if_exception_type(openai.error.Timeout)
                    | retry_if_exception_type(openai.error.APIError)
                    | retry_if_exception_type(openai.error.APIConnectionError)
                    | retry_if_exception_type(openai.error.RateLimitError)
                    | retry_if_exception_type(openai.error.ServiceUnavailableError)
                ),
                before_sleep=before_sleep_log(logger, logger.level("INFO")),
            )
            return retry_decorator(func)(*args, **kwargs)

        return wrapped_func

    def _create_embedding(self, text: Union[str, List[str]]) -> List[float]:
        @self._create_retry_decorator
        def inner_function(*args, **kwargs):
            try:
                self._check_and_set_openai_api()
                if not text:
                    logger.info("Empty text received. Returning an empty list.")
                    return []

                logger.info(f"Creating embeddings for text using engine {self.engine}")
                response = openai.Embedding.create(
                    input=text[: self.batch_size],
                    engine=self.engine,
                )
                return [item["embedding"] for item in response["data"]]
            except openai.error.OpenAIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise e
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                raise e

        return inner_function(self, text)

    def _embed_text_batch(self, keywords: List[str]) -> List[List[float]]:
        """Embed a list of keywords as a list of lists of floats using the OpenAI API."""
        all_embeddings = []

        # Display progress bar if the flag is True
        iterable = tqdm(keywords) if self.show_progress_bar else keywords

        for i in range(0, len(iterable), self.batch_size):
            embeddings = self._create_embedding(keywords[i : i + self.batch_size])
            all_embeddings.extend(embeddings)

        return all_embeddings

    def _embed_keywords(self, keywords: List[str]) -> List[List[float]]:
        """Embed a list of keywords as a list of lists of floats using a specified language model."""
        return [self._embed_text(keyword) for keyword in keywords]

    def _embed_text(self, text: str) -> List[float]:
        """Embed a piece of text as a list of floats using the OpenAI API."""
        embeddings = self._create_embedding(text)
        return embeddings[0] if embeddings else []

    def _compute_semantic_vectors(
        self, keywords: List[str]
    ) -> List[Tuple[str, List[float]]]:
        """Compute semantic vectors for a list of keywords."""
        return [(keyword, self._embed_text(keyword)) for keyword in keywords]

    def fit(self, keywords: List[str]) -> "BaseEmbedding":
        """Compute semantic vectors for a list of keywords."""
        if not isinstance(keywords, list) or not all(
            isinstance(k, str) for k in keywords
        ):
            raise ValueError("Keywords must be a list of strings.")
        self._semantic_vectors = self._compute_semantic_vectors(keywords)
        self.keywords = keywords
        return self  # conventionally, fit returns self


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to get the embeddings
    # NOTE: Azure Open AI requires deployment id
    deployment = os.environ.get("OPENAI_EMBEDDINGMODEL_DEPLOYMENTID")

    response = {}
    if deployment == None:
        response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    else:
        response = openai.Embedding.create(input=texts, deployment_id=deployment)

    # Extract the embedding data from the response
    data = response["data"]  # type: ignore

    # Return the embeddings as a list of lists of floats
    return [result["embedding"] for result in data]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion(
    messages,
    model="gpt-3.5-turbo",  # use "gpt-4" for better results
    deployment_id=None,
):
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
        messages: The list of messages in the chat history.
        model: The name of the model to use for the completion. Default is gpt-3.5-turbo, which is a fast, cheap and versatile model. Use gpt-4 for higher quality but slower results.

    Returns:
        A string containing the chat completion.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    # Note: Azure Open AI requires deployment id
    response = {}
    if deployment_id == None:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
    else:
        response = openai.ChatCompletion.create(
            deployment_id=deployment_id,
            messages=messages,
        )

    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    logger.info(f"Completion: {completion}")
    return completion
