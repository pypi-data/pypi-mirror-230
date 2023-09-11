from dlm_matrix.models import Content, Chain, AuthorList, Author, RoleType
from dlm_matrix.transformation.coordinate import Coordinate
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid


def _convert_dict_to_message(message_dict: dict) -> Chain:
    role = message_dict["role"]
    content = Content(raw=message_dict["content"])
    coordinate = Coordinate(x=0, y=0, z=0, t=0)  # Use default coordinates for now

    if role == "user":
        return UserChain(id=str(uuid.uuid4()), content=content, coordinate=coordinate)
    elif role == "assistant":
        return AssistantChain(
            id=str(uuid.uuid4()), content=content, coordinate=coordinate
        )
    elif role == "system":
        return SystemChain(id=str(uuid.uuid4()), content=content, coordinate=coordinate)
    else:
        raise ValueError(f"Got unknown role {role}")


class SynthesisTechnique(ABC):
    def __init__(
        self,
        epithet: str,
        name: str,
        technique_name: str,
        imperative: str,
        prompts: Dict[str, Any],
    ):
        self.epithet = epithet
        self.name = name
        self.technique_name = technique_name
        self.imperative = imperative
        self.prompts = prompts

    @abstractmethod
    def execute(self, *args, **kwargs) -> None:
        pass

    def get_options(self) -> Dict[str, Any]:
        return {
            "epithet": self.epithet,
            "name": self.name,
            "technique_name": self.technique_name,
            "imperative": self.imperative,
            "prompts": self.prompts,
        }


class RoleChain(Chain):
    def __init__(
        self,
        id: str,
        content: Content,
        coordinate: Optional[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        author_roles: Optional[
            AuthorList
        ] = None,  # You can pass it or let the subclasses define it
    ):
        super().__init__(
            id=id,
            content=content,
            coordinate=coordinate,
            metadata=metadata,
            author_roles=author_roles,
        )


class AssistantChain(RoleChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            author_roles=AuthorList(authors=[Author(role=RoleType.ASSISTANT)]),
        )


class UserChain(RoleChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            author_roles=AuthorList(authors=[Author(role=RoleType.USER)]),
        )


class SystemChain(RoleChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            author_roles=AuthorList(authors=[Author(role=RoleType.SYSTEM)]),
        )


# For a chain with multiple authors:
class MultiAuthorChain(RoleChain):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            author_roles=AuthorList(
                authors=[Author(role=RoleType.USER), Author(role=RoleType.ASSISTANT)]
            ),
        )
