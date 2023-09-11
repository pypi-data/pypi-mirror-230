from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from dlm_matrix.models import (
    Content,
    Chain,
)
from dlm_matrix.transformation.coordinate import Coordinate


class ChainBuilder(ABC):
    @abstractmethod
    def build_system_chain(self, content: Content, coordinate: Coordinate):
        pass

    @abstractmethod
    def build_assistant_chain(self, content: Content, coordinate: Coordinate):
        pass

    @abstractmethod
    def build_user_chain(self, content: Content, coordinate: Coordinate):
        pass

    def get_result(self):
        return self.chain_tree


class IChainTree(ABC):
    @abstractmethod
    def add_chain(
        self,
        chain_type: Type[Chain],
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]],
    ):
        pass

    @abstractmethod
    def get_chains(self):
        pass

    @abstractmethod
    def get_chain(self, id: str):
        pass

    @abstractmethod
    def get_last_chain(self):
        pass

    @abstractmethod
    def get_chains_by_type(self, chain_type: str):
        pass

    @abstractmethod
    def get_chains_by_coordinate(self, coordinate: Coordinate):
        pass

    @abstractmethod
    def remove_chain(self, id: str):
        pass

    @abstractmethod
    def update_chain(
        self,
        id: str,
        new_content: Optional[Content] = None,
        new_coordinate: Optional[Coordinate] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ):
        pass

    def add_link(self, link: dict):
        pass


class IChainFactory(ABC):
    @abstractmethod
    def create_chain(
        self,
        chain_type: str,
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]],
    ) -> Chain:
        pass
