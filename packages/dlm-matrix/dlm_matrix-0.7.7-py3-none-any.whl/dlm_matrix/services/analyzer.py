from typing import List, Dict, Mapping, Callable, Union
from collections import Counter
from dlm_matrix.services.base import IMessageAnalyzer, IMessageSearcher
import numpy as np


class MessageAnalyzer(IMessageAnalyzer):
    def __init__(self, message_searcher: IMessageSearcher):
        self.message_searcher = message_searcher

    def count_messages_by_author(self) -> Dict[str, int]:
        authors = [
            msg.message.author.role for msg in self.message_searcher._search_results
        ]
        return dict(Counter(authors))

    def count_messages_by_role(self) -> Dict[str, int]:
        roles = [
            msg.message.author.role for msg in self.message_searcher._search_results
        ]
        return dict(Counter(roles))

    def count_messages_by_content(self) -> Dict[str, int]:
        contents = [
            msg.message.content.text for msg in self.message_searcher._search_results
        ]
        return dict(Counter(contents))

    def count_messages_by_recipient(self) -> Dict[str, int]:
        recipients = [
            msg.message.recipient for msg in self.message_searcher._search_results
        ]
        return dict(Counter(recipients))

    def average_message_length(self) -> float:
        return np.mean(
            [
                len(msg.message.content.text)
                for msg in self.message_searcher._search_results
            ]
        )

    def contains_word(self, msg, word: str) -> bool:
        return word in msg.message.content.text

    def average_message_length_by_author(self) -> Dict[str, float]:
        authors = {}
        for msg in self.message_searcher._search_results:
            if msg.message.author.role not in authors:
                authors[msg.message.author.role] = [len(msg.message.content.text)]
            else:
                authors[msg.message.author.role].append(len(msg.message.content.text))
        return {
            author: sum(lengths) / len(lengths) for author, lengths in authors.items()
        }

    def count_messages_by_depth(self) -> Dict[int, int]:
        depths = [msg.message.depth for msg in self.message_searcher._search_results]
        return dict(Counter(depths))

    def filter_messages_by_condition(
        self, condition_func: Callable[[Mapping], bool]
    ) -> List[Mapping]:
        all_messages = self.message_data.retrieve_all_conversation_messages()
        return [msg for msg in all_messages if condition_func(msg)]
