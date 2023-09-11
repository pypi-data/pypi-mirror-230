from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    root_validator,
    validator,
    create_model,
    PrivateAttr,
)
from typing import List, Union, Dict, Any, Callable, Type, Optional, TypeVar, Generic
from dlm_matrix.type import TaskType
import json
import logging
import threading


logging.basicConfig(level=logging.INFO)
T = TypeVar("T")


class Task(BaseModel):
    name: Optional[str]
    description: Optional[str]
    details: Optional[str]


class DynamicModel(BaseModel, Generic[T]):
    name: str

    class Config:
        arbitrary_types_allowed = True

    _model: Any = PrivateAttr(default=None)
    _history: List[Dict[str, Any]] = PrivateAttr(default_factory=list)

    def _update_history(self) -> None:
        self._history.append(self.dict())

    def __call__(self, **data: Any) -> BaseModel:
        updated_model = self._model(**data)
        self._update_history()
        return updated_model

    def get_history(self) -> List[Dict[str, Any]]:
        return self._history

    def flatten(self, **data: Any) -> Dict[str, Any]:
        return self(**data).dict()


# Component Class
class Component(DynamicModel[T]):
    dimensions: Dict[str, Optional[int]] = Field(default_factory=dict)

    def __init__(self, name: str, dimensions: List[str], **data: Optional[int]) -> None:
        super().__init__(name=name)
        self.dimensions = {
            f"dim_{dim}": data.get(f"dim_{dim}", None) for dim in dimensions
        }
        self._model = self._create_model(name, dimensions=dimensions, **data)
        self._update_history()

    @staticmethod
    def _create_model(
        name: str, dimensions: List[str], **data: Optional[int]
    ) -> Type[BaseModel]:
        return create_model(
            name,
            **{
                f"dim_{dim}": (Optional[int], data.get(f"dim_{dim}", None))
                for dim in dimensions
            },
        )

    def update_dimension(self, dimension: str, value: Optional[int]) -> None:
        if dimension in self.dimensions:
            self.dimensions[dimension] = value
            self._update_history()
        else:
            raise ValueError(f"Dimension {dimension} not found.")

    def validate_dimensions(self) -> None:
        for dim, value in self.dimensions.items():
            if value is not None and value <= 0:
                raise ValueError(f"Dimension {dim} must be greater than zero.")


class Attribute(DynamicModel[T]):
    attributes: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, name: str, attributes: List[str], **data: Any) -> None:
        super().__init__(name=name)
        self.attributes = {attr: data.get(attr, None) for attr in attributes}
        self._model = self._create_model(name, attributes=attributes, **data)
        self._update_history()

    @classmethod
    def _create_model(
        cls, name: str, attributes: List[str], **data: Any
    ) -> Type[BaseModel]:
        return create_model(
            name,
            **{
                f"{attribute}": (Any, data.get(f"{attribute}", None))
                for attribute in attributes
            },
        )

    def add_attribute(self, attribute: str, value: Any) -> None:
        self.attributes[attribute] = value
        self._update_history()

    def remove_attribute(self, attribute: str) -> None:
        if attribute in self.attributes:
            del self.attributes[attribute]
            self._update_history()
        else:
            raise ValueError(f"Attribute {attribute} not found.")

    def validate_attributes(self) -> None:
        for attr, value in self.attributes.items():
            if value is None:
                raise ValueError(f"Attribute {attr} must have a value.")


class TripleLayeredExplorationFramework(BaseModel):
    description: str
    purpose: str
    tasks: List[Union[Component, Attribute]] = Field(default_factory=list)
    version: int = 0
    last_modified: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(
            self,
            "event_hooks",
            {
                "task_added": [],
                "task_removed": [],
                "task_updated": [],
                "framework_loaded": [],
            },
        )
        object.__setattr__(self, "_lock", threading.Lock())

    def _execute_hooks(self, hook_type: str, task: Any):
        for hook in self.event_hooks.get(hook_type, []):
            hook(task)

    def __call__(self, **data: Any) -> BaseModel:
        updated_framework = self.__class__(**data)
        self._execute_hooks("framework_loaded", updated_framework)
        return updated_framework

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "purpose": self.purpose,
            "tasks": [task.dict() for task in self.tasks],
            "version": self.version,
            "last_modified": self.last_modified,
        }

    @root_validator(pre=True)
    def check_purpose_and_description(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        purpose = values.get("purpose")
        description = values.get("description")
        if purpose and description and purpose.lower() == description.lower():
            raise ValueError("Purpose and description should not be identical.")
        return values

    @validator("tasks", pre=True, each_item=True)
    def validate_tasks(
        cls, task: Union[Component, Attribute]
    ) -> Union[Component, Attribute]:
        if not isinstance(task, (Component, Attribute)):
            raise ValueError(
                f"Invalid task type. Expected Component or Attribute but got {type(task).__name__}"
            )
        return task

    def add_task(self, task: Union[Task, Component, Attribute]) -> None:
        with self._lock:
            self.tasks.append(task)
            self.version += 1
            self.last_modified = datetime.utcnow()
            self._execute_hooks("task_added", task)

    def remove_task(self, task_name: str) -> None:
        task_to_remove = next(
            (task for task in self.tasks if task.name == task_name), None
        )
        if task_to_remove:
            self.tasks.remove(task_to_remove)

    def update_task(
        self, task_name: str, new_task: Union[Component, Attribute]
    ) -> None:
        index = next(
            (i for i, task in enumerate(self.tasks) if task.name == task_name), None
        )
        if index is not None:
            self.tasks[index] = new_task

    def find_tasks_by_type(
        self, task_type: TaskType
    ) -> List[Union[Component, Attribute]]:
        return [task for task in self.tasks if isinstance(task, eval(task_type.value))]

    def export_to_json(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(self.dict(), f)

    def summarize(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "purpose": self.purpose,
            "task_summary": [task.dict() for task in self.tasks],
        }

    def add_hook(self, hook_type: str, hook_fn: Callable) -> None:
        if hook_type in self.event_hooks:
            self.event_hooks[hook_type].append(hook_fn)
        else:
            raise ValueError(f"Invalid hook type: {hook_type}.")

    # in TripleLayeredExplorationFramework
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "purpose": self.purpose,
            "tasks": [task.dict() for task in self.tasks],
            "version": self.version,
            "last_modified": self.last_modified.isoformat(),
        }


class CompositeSystemModel(BaseModel):
    framework: TripleLayeredExplorationFramework
    version: str = Field(..., description="The version of the model")
    created_by: str = Field(..., description="User who created this model")
    updated_by: str = Field(..., description="User who last updated this model")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Time of the last update"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="The timestamp when the model instance was created",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        arbitrary_types_allowed = True

    _hooks: Dict[str, List[Callable]] = PrivateAttr(default_factory=dict)

    # in CompositeSystemModel
    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework.to_dict(),
            "version": self.version,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at.isoformat(),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def add_component(self, component: Union[Component, Attribute]) -> None:
        self.framework.add_task(component)
        self._execute_hooks("component_added", component)

    def remove_component(self, component_name: str) -> None:
        self.framework.remove_task(component_name)
        self._execute_hooks("component_removed", component_name)

    def add_attribute(self, attribute: Attribute) -> None:
        self.framework.add_task(attribute)
        self._execute_hooks("attribute_added", attribute)

    def remove_attribute(self, attribute_name: str) -> None:
        self.framework.remove_task(attribute_name)
        self._execute_hooks("attribute_removed", attribute_name)

    def add_hook(self, hook_name: str, hook_fn: Callable) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(hook_fn)

    def _execute_hooks(self, hook_name: str, *args, **kwargs) -> None:
        for hook in self._hooks.get(hook_name, []):
            hook(*args, **kwargs)

    def update_framework(
        self, new_framework: TripleLayeredExplorationFramework
    ) -> None:
        self.framework = new_framework

    def summary(self) -> Dict[str, Any]:
        return {
            "framework_summary": self.framework.summarize(),
            "version": self.version,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "updated_at": self.updated_at,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def export_to_json(self, filename: str) -> None:
        def default_serialize(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return o.__dict__

        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, default=default_serialize, indent=4)

    def __call__(self, **data: Any) -> BaseModel:
        updated_model = self.__class__(**data)
        self._execute_hooks("model_loaded", updated_model)
        return updated_model
