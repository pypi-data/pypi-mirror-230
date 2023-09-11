from typing import List, Callable, Any, Tuple, Dict, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from dlm_matrix.services.base import IMessageExtractor, IMessageSearcher
from sentence_transformers import SentenceTransformer
from dlm_matrix.models import ChainMap
import random
from collections import Counter
from scipy.sparse import csr_matrix
import re


class MessageSearcher(IMessageSearcher):
    def __init__(self, message_extractor: IMessageExtractor):
        super().__init__(message_extractor.message_data)
        self._search_results = message_extractor.search_results
        self.message_extractor = message_extractor
        self.stopwords = ["Apologize"]
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(
            [message.message.content.text for message in self._search_results]
        )
        self.messages = [
            message.message.content.text for message in self._search_results
        ]
        self.model = SentenceTransformer("paraphrase-distilroberta-base-v1")

    @property
    def search_results(self) -> List[ChainMap]:
        return self._search_results

    def filter_messages_by_word_count(
        self, min_words: int, max_words: int, role: str = "user"
    ) -> List[str]:
        messages = self.message_extractor.get_messages_by_role(role)
        return [
            message
            for message in messages
            if min_words <= len(message.split()) <= max_words
        ]

    def find_messages_by_author(self, author: str) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: msg.message.author.role == author
        )

    def find_similar(self, message_id: str, top_k: int = 5) -> List[ChainMap]:
        message_index = next(
            (
                index
                for index, message in enumerate(self.messages)
                if message.message.id == message_id
            ),
            None,
        )
        if message_index is None:
            raise ValueError(f"Could not find message with ID {message_id}")

        cosine_similarities = linear_kernel(
            self.tfidf_matrix[message_index], self.tfidf_matrix
        ).flatten()
        related_message_indices = cosine_similarities.argsort()[:-top_k:-1]
        return [self.messages[i] for i in related_message_indices]

    def filter_messages_by_condition(
        self, condition_func: Callable[[ChainMap], bool]
    ) -> List[ChainMap]:
        return [msg for msg in self.messages if condition_func(msg)]

    def find_messages_by_author(self, author: str) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: msg.message.author.role == author
        )

    def filter_messages_by_condition(
        self, condition_func: Callable[[ChainMap], bool]
    ) -> List[ChainMap]:
        all_messages = self.message_data.retrieve_all_conversation_messages()
        return [msg for msg in all_messages if condition_func(msg)]

    def find_messages_by_content(
        self, search_phrase: str, exact_match: bool = False
    ) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: msg.message.content.text == search_phrase
            if exact_match
            else search_phrase in msg.message.content.text
        )

    def find_messages_by_metadata(self, key: str, value: Any) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: key in msg.message.metadata
            and msg.message.metadata[key] == value
        )

    def find_messages_by_custom_func(
        self, custom_func: Callable[[ChainMap], bool]
    ) -> List[ChainMap]:
        return self.filter_messages_by_condition(custom_func)

    def find_messages_by_regex(self, pattern: str) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: bool(re.search(pattern, msg.message.content.text))
        )

    def find_messages_by_regex_in_metadata(
        self, key: str, pattern: str
    ) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: key in msg.message.metadata
            and bool(re.search(pattern, msg.message.metadata[key]))
        )

    def find_messages_by_author_role(self, role: str) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: msg.message.author.role == role
        )

    def find_messages_in_time_range(
        self, start_time: float, end_time: float
    ) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: start_time <= msg.message.create_time <= end_time
        )

    def find_messages_by_recipient(self, recipient: str) -> List[ChainMap]:
        return self.filter_messages_by_condition(
            lambda msg: msg.message.recipient == recipient
        )

    def find_messages_by_depth(self, depth: int) -> List[ChainMap]:
        return self.filter_messages_by_condition(lambda msg: msg.message.depth == depth)

    def get_random_messages(
        self, n: int, role: str = "both"
    ) -> Union[List[str], Dict[str, List[str]]]:
        if role == "both":
            return {
                "user": random.sample(self.get_user_messages(), n),
                "assistant": random.sample(self.get_assistant_messages(), n),
            }
        messages = self.message_extractor.get_messages_by_role(role)
        return random.sample(messages, n)

    def count_occurrences(self, word: str, role: str = "user") -> int:
        if role == "both":
            messages = " ".join(
                self.get_user_messages() + self.get_assistant_messages()
            )
        else:
            messages = " ".join(self.message_extractor.get_messages_by_role(role))
        return Counter(messages.split())[word]

    def create_message_matrix(self, role: str = "user") -> csr_matrix:
        vectorizer = TfidfVectorizer()
        messages = self.message_extractor.get_messages_by_role(role)
        return vectorizer.fit_transform(messages)

    def find_similar(
        self, base_message: str, threshold: float = 0.0, top_n: int = None
    ) -> List[ChainMap]:
        base_message_word_set = self._get_filtered_word_set(base_message)
        similarity_scores = []

        for msg in self._search_results:
            message_word_set = self._get_filtered_word_set(msg.message.content.text)
            common_elements = len(base_message_word_set.intersection(message_word_set))
            total_elements = len(base_message_word_set.union(message_word_set))
            similarity_score = common_elements / total_elements

            if similarity_score > threshold:
                similarity_scores.append((similarity_score, msg))

        # Sort the messages by similarity score in descending order
        similarity_scores.sort(key=lambda x: x[0], reverse=True)

        # If top_n is specified, only return that many results
        if top_n is not None:
            similarity_scores = similarity_scores[:top_n]

        # Extract the message contents from the sorted results
        similar_messages = [msg.message.content.text for _, msg in similarity_scores]

        return similar_messages

    def filter_messages(self, word: str, role: str = "user") -> List[str]:
        messages = self.message_extractor.get_messages_by_role(role)
        return [message for message in messages if word in message]

    def _get_filtered_word_set(self, message: str) -> set:
        words = re.findall(r"\w+", message.lower())
        return set(word for word in words if word not in self.stopwords)

    def get_unique_messages(
        self, role: str = "both"
    ) -> Union[List[str], Dict[str, List[str]]]:
        if role == "both":
            return {
                "user": list(set(self.get_user_messages())),
                "assistant": list(set(self.get_assistant_messages())),
            }
        messages = self.message_extractor.get_messages_by_role(role)
        return list(set(messages))

    def similar(self, text: str, top_n: int = 1, role: str = "assistant") -> List[str]:
        """Finds the top_n most similar data to the input text based on TF-IDF cosine similarity"""
        if not isinstance(text, str) or len(text.strip()) == 0:
            raise ValueError("Invalid text input. Please provide non-empty string.")
        if not isinstance(top_n, int) or top_n < 1:
            raise ValueError(
                "Invalid top_n input. Please provide an integer greater than 0."
            )
        if role not in ["user", "assistant"]:
            raise ValueError("Invalid role. Choose from 'user', 'assistant'")

        messages = self.message_extractor.get_messages_by_role(role)

        if not messages:
            return []  # No messages available to compare with

        vectorizer = TfidfVectorizer().fit_transform(messages + [text])

        # If only one message and the text are available, we have nothing to compare with
        if vectorizer.shape[0] <= 1:
            return []

        cosine_similarities = cosine_similarity(vectorizer[-1], vectorizer).flatten()[
            :-1
        ]

        # If there are fewer messages than top_n
        if len(cosine_similarities) < top_n:
            top_n = len(cosine_similarities)

        similar_indices = cosine_similarities.argsort()[-top_n:][::-1]
        return [messages[i] for i in similar_indices]

    def get_user_messages(self) -> List[str]:
        return self.message_extractor.get_messages_by_role("user")

    def get_assistant_messages(self) -> List[str]:
        return self.message_extractor.get_messages_by_role("assistant")

    def get_message_pairs(self) -> List[Tuple[str, str]]:
        return [
            (user, assistant)
            for user, assistant in zip(
                self.get_user_messages(), self.get_assistant_messages()
            )
        ]

    def get_message_pairs_by_role(self, role: str) -> List[Tuple[str, str]]:
        if role == "user":
            return [
                (user, assistant)
                for user, assistant in zip(
                    self.get_user_messages(), self.get_assistant_messages()
                )
            ]
        elif role == "assistant":
            return [
                (assistant, user)
                for user, assistant in zip(
                    self.get_user_messages(), self.get_assistant_messages()
                )
            ]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant'")

    def get_message_pairs_by_role_and_depth(
        self, role: str, depth: int
    ) -> List[Tuple[str, str]]:
        if role == "user":
            return [
                (user, assistant)
                for user, assistant in zip(
                    self.get_user_messages(), self.get_assistant_messages()
                )
                if self.message_extractor.find_message_by_id(user.id).message.depth
                == depth
            ]
        elif role == "assistant":
            return [
                (assistant, user)
                for user, assistant in zip(
                    self.get_user_messages(), self.get_assistant_messages()
                )
                if self.message_extractor.find_message_by_id(user.id).message.depth
                == depth
            ]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant'")

    def get_message_pairs_by_depth(self, depth: int) -> List[Tuple[str, str]]:
        return [
            (user, assistant)
            for user, assistant in zip(
                self.get_user_messages(), self.get_assistant_messages()
            )
            if self.message_extractor.find_message_by_id(user.id).message.depth == depth
        ]

    def get_messages_by_role(self, role: str) -> List[str]:
        return self.message_extractor.get_messages_by_role(role)

    def get_first_n_messages(
        self, n: int, role: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        if role == "both":
            pairs = self.get_message_pairs()
            return pairs[:n]
        elif role in ["user", "assistant"]:
            messages = self.get_messages_by_role(role)
            return messages[:n]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant', 'both'")

    def search_messages(
        self, keyword: str, role: str = "both"
    ) -> Union[List[str], List[Tuple[str, str]]]:
        if role == "both":
            pairs = self.get_message_pairs()
            return [pair for pair in pairs if keyword in pair[0] or keyword in pair[1]]
        elif role in ["user", "assistant"]:
            messages = self.get_messages_by_role(role)
            return [message for message in messages if keyword in message]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant', 'both'")

    def get_message_lengths(
        self, role: str = "both"
    ) -> Union[List[int], Dict[str, List[int]]]:
        if role == "both":
            return {
                "user": [len(msg) for msg in self.get_user_messages()],
                "assistant": [len(msg) for msg in self.get_assistant_messages()],
            }
        elif role in ["user", "assistant"]:
            return [len(msg) for msg in self.get_messages_by_role(role)]
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant', 'both'")

    def count_keyword_in_messages(
        self, keyword: str, role: str = "both"
    ) -> Union[int, Dict[str, int]]:
        if role == "both":
            return {
                "user": sum(
                    message.lower().count(keyword.lower())
                    for message in self.get_user_messages()
                ),
                "assistant": sum(
                    message.lower().count(keyword.lower())
                    for message in self.get_assistant_messages()
                ),
            }
        elif role in ["user", "assistant"]:
            return sum(
                message.lower().count(keyword.lower())
                for message in self.get_messages_by_role(role)
            )
        else:
            raise ValueError("Invalid role. Choose from 'user', 'assistant', 'both'")

    def get_message_pairs(self) -> List[Tuple[str, str]]:
        user_messages = self.get_user_messages()
        assistant_messages = self.get_assistant_messages()
        return list(zip(user_messages, assistant_messages))

    def get_random_message_pairs(self) -> List[Tuple[str, str]]:
        return random.sample(self.get_message_pairs(), len(self.get_message_pairs()))

    def get_random_pair(self) -> Tuple[str, str]:
        return random.choice(self.get_random_message_pairs())

    def get_random_message_by_role(self, role: str) -> str:
        return random.choice(self.get_messages_by_role(role))

    def get_random_user_message(self) -> str:
        return self.get_random_message_by_role("user")

    def get_random_assistant_message(self) -> str:
        return self.get_random_message_by_role("assistant")


class MessageSearcherWithSentenceTransformer(MessageSearcher):
    def __init__(self, message_extractor: IMessageExtractor):
        super().__init__(message_extractor)
        self.model = SentenceTransformer("paraphrase-distilroberta-base-v1")

    def similar(self, text: str, top_n: int = 1, role: str = "assistant") -> List[str]:
        """Finds the top_n most similar data to the input text based on sentence transformer cosine similarity"""
        if not isinstance(text, str) or len(text.strip()) == 0:
            raise ValueError("Invalid text input. Please provide non-empty string.")
        if not isinstance(top_n, int) or top_n < 1:
            raise ValueError(
                "Invalid top_n input. Please provide an integer greater than 0."
            )
        if role not in ["user", "assistant"]:
            raise ValueError("Invalid role. Choose from 'user', 'assistant'")

        messages = self.message_extractor.get_messages_by_role(role)

        if not messages:
            return []  # No messages available to compare with

        embeddings = self.model.encode(messages + [text])

        # If only one message and the text are available, we have nothing to compare with
        if len(embeddings) <= 1:
            return []

        cosine_similarities = cosine_similarity(
            embeddings[-1].reshape(1, -1), embeddings
        ).flatten()[:-1]

        # If there are fewer messages than top_n
        if len(cosine_similarities) < top_n:
            top_n = len(cosine_similarities)

        similar_indices = cosine_similarities.argsort()[-top_n:][::-1]
        return [messages[i] for i in similar_indices]
