from typing import List, Optional, Tuple, Dict, Callable, Any
from dlm_matrix.models import (
    ChainMap,
    Chain,
    ChainTreeIndex,
    ChainTree,
    Content,
)
from datetime import datetime


class MessageFilter:
    def __init__(
        self,
        date_range: Optional[Tuple[str, str]] = None,
        keyword_filter: Optional[List[str]] = None,
        exclude_participants: Optional[List[str]] = None,
        case_sensitive: bool = False,
        message_length: Optional[int] = None,
        message_contains: Optional[List[str]] = None,
    ):
        self.date_range = self._convert_date_range(date_range) if date_range else None
        self.keyword_filter = keyword_filter
        self.case_sensitive = case_sensitive
        self.exclude_participants = exclude_participants
        self.message_length = message_length
        self.message_contains = message_contains

    @staticmethod
    def _convert_date_range(date_range: Tuple[str, str]) -> Tuple[float, float]:
        start_date_str, end_date_str = date_range
        start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
        end_date = datetime.strptime(end_date_str, "%m/%d/%Y")
        return (
            start_date.timestamp(),
            end_date.timestamp(),
        )

    def filter_messages(self, messages: List[Chain]) -> List[Chain]:
        filtered_messages = []
        for message in messages:
            if not self._within_date_range(message):
                continue
            if not self._within_keyword_filter(message):
                continue
            if not self._within_message_length(message):
                continue
            filtered_messages.append(message)
        return filtered_messages

    def _within_date_range(self, message: Chain) -> bool:
        if not self.date_range:
            return True
        start_date, end_date = self.date_range
        return start_date <= message.create_time <= end_date

    def _within_keyword_filter(self, message: Chain) -> bool:
        if not self.keyword_filter:
            return True
        if self.case_sensitive:
            return any(
                keyword in message.content.text for keyword in self.keyword_filter
            )

        return any(
            keyword.lower() in message.content.text.lower()
            for keyword in self.keyword_filter
        )

    def _within_message_length(self, message: Chain) -> bool:
        if not self.message_length:
            return True
        return len(message.content.text) <= self.message_length

    def _within_message_contains(self, message: Chain) -> bool:
        if not self.message_contains:
            return True
        return any(keyword in message.content.text for keyword in self.message_contains)


class DepthFilter:
    def __init__(self, depth_range: Optional[Tuple[int, int]]):
        self.depth_range = depth_range

    def filter_tree_by_depth(self, depth: int) -> bool:
        tree_depth = depth

        if self.depth_range:
            min_depth, max_depth = self.depth_range
            if not self._within_depth_range(tree_depth, min_depth, max_depth):
                return False

        return True

    def _within_depth_range(
        self, tree_depth: int, min_depth: int, max_depth: int
    ) -> bool:
        return min_depth <= tree_depth <= max_depth


class TreeFilter:
    def __init__(self, message_range: Optional[Tuple[int, int]]):
        self.message_range = message_range

    def filter_tree_by_message_count(self, conversation_tree: ChainTreeIndex) -> bool:
        if self.message_range:
            min_messages, max_messages = self.message_range
            if not self._within_message_range(
                conversation_tree, min_messages, max_messages
            ):
                return False

        return True

    def _within_message_range(
        self, conversation_tree: ChainTreeIndex, min_messages: int, max_messages: int
    ) -> bool:
        num_messages = len(conversation_tree.conversation.mapping)
        return min_messages <= num_messages <= max_messages


class RangeFilter:
    def __init__(
        self,
        title_range: Optional[Tuple[int, int]] = None,
        index_range: Optional[Tuple[int, int]] = None,
        custom_filter: Optional[Dict[str, Tuple[int, int]]] = None,
        content_filter: Optional[Callable[[str], bool]] = None,
    ):
        self.title_range = title_range
        self.index_range = index_range
        self.custom_filter = custom_filter if custom_filter else {}
        self.content_filter = content_filter

    def filter_by_title(self, conversation: ChainTree):
        if self.title_range is None:
            return True

        try:
            title = int(conversation.title)
        except ValueError:
            return False

        return self.title_range[0] <= title <= self.title_range[1]

    def filter_by_index(self, idx, total):
        if self.index_range is None:
            return True

        start, end = self.index_range
        if end is None:
            end = total

        return start <= idx <= end

    def filter_custom(self, conversation: ChainTree):
        for attribute, (lower, upper) in self.custom_filter.items():
            attr_value = getattr(conversation, attribute, None)
            if attr_value is None or not (lower <= attr_value <= upper):
                return False
        return True

    def filter_content(self, conversation: ChainTree):
        if self.content_filter is None:
            return True

        return self.content_filter(conversation.mapping)

    def filter_chain(self, chain: Chain):
        if self.content_filter is None:
            return True

        return self.content_filter(chain.content.text)


class ChainIndexer:
    def __init__(self, conversation_trees: List[ChainTreeIndex]):
        self.conversation_trees = conversation_trees
        self._build_mapping()

    def _build_mapping(self):
        for conversation_tree in self.conversation_trees:
            conversation_tree.conversation.mapping = self._build_message_mapping(
                conversation_tree.conversation.mapping
            )

    def _build_message_mapping(self, mapping: Dict[str, ChainMap]) -> Dict[str, Chain]:
        return {
            node_id: self._build_message(mapping[node_id].message)
            for node_id in mapping
        }

    def _build_message(self, message: Chain) -> Chain:
        return Chain(
            id=message.id,
            author=message.author,
            create_time=message.create_time,
            content=Content(
                content_type=message.content.content_type,
                parts=message.content.parts,
                text=message.content.text,
            ),
            end_turn=message.end_turn,
            weight=message.weight,
            metadata=message.metadata,
            recipient=message.recipient,
        )


class ChainFilter:
    def __init__(
        self,
        message_range: Optional[Tuple[int, int]] = None,
        depth_range: Optional[Tuple[int, int]] = None,
        date_range: Optional[Tuple[float, float]] = None,
        keyword_filter: Optional[List[str]] = None,
        exclude_participants: Optional[List[str]] = None,
        case_sensitive: bool = False,
        range_filter: Optional[RangeFilter] = None,
        custom_filter: Optional[Callable[[ChainTree], bool]] = None,
    ):
        self.tree_filter = TreeFilter(message_range)
        self.depth_filter = DepthFilter(depth_range)
        self.message_filter = MessageFilter(
            date_range,
            keyword_filter,
            exclude_participants,
            case_sensitive,
        )
        self.range_filter = range_filter
        self.custom_filter = custom_filter

    def is_valid(
        self, idx, total: int, conversation_tree: ChainTreeIndex, tree_depth: int
    ) -> bool:
        if not self.tree_filter.filter_tree_by_message_count(conversation_tree):
            return False

        if not self.depth_filter.filter_tree_by_depth(tree_depth):
            return False

        if self.range_filter is not None:
            if not self.range_filter.filter_by_index(idx, total):
                return False
            if not self.range_filter.filter_by_title(conversation_tree.conversation):
                return False
            if not self.range_filter.filter_custom(conversation_tree.conversation):
                return False
            if not self.range_filter.filter_content(conversation_tree.conversation):
                return False

        if self.custom_filter is not None:
            if not self.custom_filter(conversation_tree.conversation):
                return False

        valid_messages = [
            m
            for m in conversation_tree.conversation.mapping.values()
            if self.message_filter.filter_messages(m)
        ]

        if not valid_messages:
            return None

        # Create a new ConversationTree with only the order messages
        valid_message_ids = {m.id for m in valid_messages}
        new_mapping = {}
        for message in valid_messages:
            new_mapping[message.id] = ChainMap(
                id=message.id,
                message=message.message,
                parent=message.parent if message.parent in valid_message_ids else None,
                children=[
                    child for child in message.children if child in valid_message_ids
                ],
                references=message.references,
            )

        valid_tree = ChainTreeIndex(
            conversation=ChainTree(
                title=conversation_tree.conversation.title,
                create_time=conversation_tree.conversation.create_time,
                update_time=conversation_tree.conversation.update_time,
                mapping=new_mapping,
                moderation_results=conversation_tree.conversation.moderation_results,
                current_node=conversation_tree.conversation.current_node,
            )
        )

        return valid_tree
