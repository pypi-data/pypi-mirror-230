from typing import Optional, Dict, Any, Type
from dlm_matrix.models import Content, Chain

from dlm_matrix.chaintrees.interface import IChainFactory
from dlm_matrix.transformation.coordinate import Coordinate
from dlm_matrix.utils import (
    InvalidChainTypeException,
    InvalidIdException,
    InvalidContentException,
    InvalidCoordinateException,
)
from dlm_matrix.chaintrees.base import (
    AssistantChain,
    UserChain,
    SystemChain,
)
import threading
import logging


class ChainFactory(IChainFactory):
    _instance = None
    _lock = threading.Lock()
    chain_classes = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.initialize_chain_classes()
        return cls._instance

    def initialize_chain_classes(self):
        self.register_chain_class("system", SystemChain)
        self.register_chain_class("assistant", AssistantChain)
        self.register_chain_class("user", UserChain)

    @classmethod
    def register_chain_class(cls, chain_type: str, chain_class: Type[Chain]):
        if chain_type in cls.chain_classes:
            logging.warning(f"Overwriting existing chain type: {chain_type}")
        cls.chain_classes[chain_type] = chain_class

    @classmethod
    def unregister_chain_class(cls, chain_type: str):
        if chain_type not in cls.chain_classes:
            raise ValueError(f"Chain type {chain_type} is not registered")
        del cls.chain_classes[chain_type]

    def create_chain(
        self,
        chain_type: str,
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Chain:
        if (
            chain_type is None
            or not isinstance(chain_type, str)
            or chain_type.strip() == ""
        ):
            raise InvalidChainTypeException("Chain type must be a non-empty string")

        chain_class = self.chain_classes.get(chain_type)
        if chain_class is None:
            message = f"Invalid chain type: {chain_type}"
            logging.error(message)
            raise InvalidChainTypeException(message)

        if id is None or not isinstance(id, str) or id.strip() == "":
            raise InvalidIdException("Id must be a non-empty string")

        if not isinstance(content, Content):
            raise InvalidContentException(
                "Content must be an instance of the Content class"
            )

        if not isinstance(coordinate, Coordinate):
            raise InvalidCoordinateException(
                "Coordinate must be an instance of the Coordinate class"
            )

        try:
            return chain_class(
                id=id, content=content, coordinate=coordinate, metadata=metadata
            )
        except Exception as e:
            message = f"Error occurred while creating chain: {str(e)}"
            logging.error(message)
            raise

    def create_system_chain(
        self,
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SystemChain:
        return self.create_chain(
            chain_type="system",
            id=id,
            content=content,
            coordinate=coordinate,
            metadata=metadata,
        )

    def create_assistant_chain(
        self,
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssistantChain:
        return self.create_chain(
            chain_type="assistant",
            id=id,
            content=content,
            coordinate=coordinate,
            metadata=metadata,
        )

    def create_user_chain(
        self,
        id: str,
        content: Content,
        coordinate: Coordinate,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UserChain:
        return self.create_chain(
            chain_type="user",
            id=id,
            content=content,
            coordinate=coordinate,
            metadata=metadata,
        )

    def create_chain_from_dict(self, chain_dict: Dict[str, Any]) -> Chain:
        chain_type = chain_dict.get("chain_type")
        if chain_type is None:
            raise InvalidChainTypeException("Chain type is not specified")
        chain_class = self.chain_classes.get(chain_type)
        if chain_class is None:
            raise InvalidChainTypeException(f"Invalid chain type: {chain_type}")
        return chain_class.from_dict(chain_dict)
