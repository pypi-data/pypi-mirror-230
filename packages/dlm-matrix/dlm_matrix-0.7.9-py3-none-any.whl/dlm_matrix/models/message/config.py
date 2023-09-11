import ast
from pydantic import create_model, Field, BaseModel, validator
from typing import Any, List, Dict, Optional, Type, Tuple, Literal, Union, Callable
from abc import ABC, abstractmethod
from dlm_matrix.services.interpeter import extract_code_info
from dlm_matrix.embedding.utils import semantic_search

type_mapping = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "List[int]": list,
    "List[float]": list,
    "List[str]": list,
    "Dict[str, int]": dict,
    "Dict[str, float]": dict,
    "Dict[str, str]": dict,
}


class BaseEntity(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def __call__(self, **data: Any) -> BaseModel:
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"


class FieldConfig(BaseModel):
    type: str
    default: Optional[Any] = None
    default_factory: Optional[bool] = None  # Add this line


class MethodConfig(BaseModel):
    code: str = Field(..., description="The Python code of the method.")
    name: str = Field("", description="The name of the method.")
    args: Dict[str, str] = Field({}, description="The types of the method arguments.")
    return_type: Optional[str] = Field(
        None, description="The return type of the method."
    )
    variables: Dict[str, str] = Field({}, description="Variables used in the method.")
    control_flow: List[Dict[str, str]] = Field(
        [], description="Control flow elements in the method."
    )
    docstring: Optional[str] = Field(None, description="The docstring of the method.")

    def __init__(self, *args, **kwargs):
        code = kwargs.get("code", "")
        code_info = extract_code_info(code)

        # Populate the fields based on 'code_info'
        if code_info and "Functions" in code_info and code_info["Functions"]:
            function_info = code_info["Functions"][0]
            kwargs["name"] = function_info.get("name", "")
            kwargs["args"] = {
                arg: "Type" for arg in function_info.get("parameters", [])
            }  # Replace 'Type' with actual type if available
            kwargs["return_type"] = function_info.get("return_value", None)
            kwargs["variables"] = function_info.get("variables", {})
            kwargs["control_flow"] = function_info.get("control_flow", [])
            kwargs["docstring"] = function_info.get("docstring", None)

        super().__init__(*args, **kwargs)


class MethodConfigs(BaseModel):
    configs: List[MethodConfig]


class RelationshipConfig(BaseModel):
    target: str = Field(..., description="The name of the target entity.")

    type: Literal["one-to-one", "one-to-many", "many-to-many", "many-to-one"] = Field(
        ..., description="The type of the relationship."
    )
    back_populates: Optional[str] = Field(
        None, description="The name of the back reference in the target entity."
    )
    uselist: Optional[bool] = Field(
        None,
        description="Specifies if a list or a scalar should be used for the relationship.",
    )
    join_condition: Optional[str] = Field(
        None,
        description="The condition that determines how the entities are related in the relationship.",
    )
    cascade: Optional[str] = Field(
        None, description="The cascading behavior of the relationship."
    )
    single_parent: Optional[bool] = Field(
        None,
        description="If set to True, it ensures that only one parent object is associated with this child object.",
    )


class EntityCreation(BaseModel):
    name: str = Field(..., description="The unique name of the entity to be created.")
    fields: Dict[str, FieldConfig] = Field(..., description="The fields of the entity.")
    methods: List[MethodConfig] = Field(
        default_factory=list, description="The methods of the entity."
    )
    base: Optional[Type[BaseModel]] = Field(
        None, description="The base class of the entity."
    )
    relationships: Dict[str, RelationshipConfig] = Field(
        default_factory=dict, description="The relationships of the entity."
    )

    def create(self) -> BaseEntity:
        return Entity(
            name=self.name,
            fields={
                name: (field.type, field.default) for name, field in self.fields.items()
            },
            methods=self.methods,
            base=self.base,
            relationships=self.relationships,
        )


class Entity(BaseEntity):
    def __init__(
        self,
        name: str,
        fields: Dict[str, Tuple[str, Optional[Any]]],
        methods: Dict[str, MethodConfig],
        base: Optional[BaseEntity] = None,
        relationships: Dict[str, RelationshipConfig] = None,
    ) -> None:
        self.name = name  # initialize self.name first
        self.fields = fields
        self.methods = methods
        self.base = base
        self.relationships = relationships
        self._model = self.__create_model__()  # then initialize self._model

    def __create_model__(self) -> Type[BaseModel]:
        field_definitions = {}

        # Creating fields
        for name, (type_name, default) in self.fields.items():
            if isinstance(default, dict) and default.get("default_factory"):
                field_definitions[name] = (type_mapping[type_name], ...)
            else:
                field_definitions[name] = (type_mapping[type_name], default)

        # Creating the model
        base_model = self.base._model if self.base else BaseModel
        model = create_model(self.name, __base__=base_model, **field_definitions)

        # Fields to be captured by the closure
        captured_fields = self.fields

        # Overriding the __init__ to support default_factory
        def new_init(self, *args, **kwargs):
            for field, (type_name, default) in captured_fields.items():
                if isinstance(default, dict) and default.get("default_factory"):
                    if field not in kwargs:
                        factory_func = type_mapping[
                            type_name
                        ]  # Fetch the factory function
                        kwargs[
                            field
                        ] = (
                            factory_func()
                        )  # Use the factory function to create a new instance
            super(model, self).__init__(*args, **kwargs)

        setattr(model, "__init__", new_init)

        for method_config in self.methods:
            code_tree = ast.parse(method_config.code, mode="exec")
            assert len(code_tree.body) == 1
            assert isinstance(code_tree.body[0], ast.FunctionDef)

            method_name = code_tree.body[0].name  # Extract name from AST

            code_obj = compile(code_tree, filename="<ast>", mode="exec")
            local_scope = {}
            exec(code_obj, None, local_scope)
            func = local_scope[method_name]
            setattr(model, method_name, func)

        return model

    def __call__(self, **data: Any) -> BaseModel:
        return self._model(**data)


class EntityConfig(BaseModel):
    creations: List[EntityCreation] = Field(
        ..., description="The entities to be created."
    )

    class Config:
        arbitrary_types_allowed = True

    def create_entities(self) -> Dict[str, Entity]:
        return {creation.name: creation.create() for creation in self.creations}


class EntityStore:
    def __init__(self):
        self.storage = {}
        self.pending = {}

    def register(self, entity: Entity):
        # Register a newly created entity
        self.storage[entity.name] = entity

    def register_pending(self, name: str, callable_func):
        # Register an entity to be resolved later
        self.pending[name] = callable_func

    def resolve_pending(self):
        # Resolve all pending entities
        for name, callable_func in self.pending.items():
            self.register(callable_func())

    def get(self, name: str) -> Entity:
        return self.storage.get(name)

    def __getitem__(self, name: str) -> Entity:
        return self.storage.get(name)

    def __contains__(self, name: str):
        return name in self.storage


def create_or_update_entity(
    name: str,
    fields: Dict[str, Union[str, Tuple[str, Any], FieldConfig, "BaseEntity"]],
    relationships: Optional[
        Dict[str, Union[str, Dict[str, Any], RelationshipConfig]]
    ] = None,
    methods: Optional[
        Dict[str, Union[str, Tuple[str, Dict[str, str], str], MethodConfig]]
    ] = None,
    validators: Optional[Dict[str, Callable]] = None,
    update: bool = False,
    query: str = None,
    corpus: List[str] = None,
    top_k: int = 2,
    model=None,
) -> Entity:
    """
    Create or update an Entity dynamically.
    """
    # Check if entity already exists for update
    entity_store = EntityStore()

    if update and name in entity_store:
        existing_entity = entity_store.get(name)
    else:
        existing_entity = None

    # Convert simple field definitions to FieldConfig
    field_configs = {}
    for key, value in fields.items():
        if isinstance(value, (BaseEntity, Entity)):
            field_configs[key] = FieldConfig(
                type="BaseEntity"
            )  # or the actual name of the entity
        elif isinstance(value, FieldConfig):
            field_configs[key] = value
        elif isinstance(value, tuple):
            type_str, default_value = value
            field_configs[key] = FieldConfig(type=type_str, default=default_value)
        elif isinstance(value, str):
            field_configs[key] = FieldConfig(type=value)

    # Convert relationship definitions to RelationshipConfig
    relationship_configs = {}
    for key, value in (relationships or {}).items():
        if isinstance(value, RelationshipConfig):
            relationship_configs[key] = value
        elif isinstance(value, dict):
            relationship_configs[key] = RelationshipConfig(**value)
        elif isinstance(value, str):
            relationship_configs[key] = RelationshipConfig(
                target=value, type="many-to-one"
            )

    # Convert method definitions to MethodConfig
    method_configs_list = []

    # If semantic search parameters are provided, find relevant methods
    if query and corpus:
        suggested_methods_with_scores = semantic_search(
            query, corpus, num_results=top_k, model=model
        )

        # Extract only the method strings, ignoring the scores
        suggested_methods = [method for method, _ in suggested_methods_with_scores]

        # Extend the methods list with the suggested methods
        if methods:
            methods.extend(suggested_methods)
        else:
            methods = suggested_methods

    # Create MethodConfig objects for each method
    for code in methods or []:
        method_config = MethodConfig(code=code)
        method_configs_list.append(method_config)

    # Create or update EntityCreation object
    entity_creation = EntityCreation(
        name=name,
        fields=field_configs,
        relationships=relationship_configs,
        methods=method_configs_list,
    )

    # Create and return an Entity
    new_entity = entity_creation.create()

    if validators:
        new_model_with_validators = attach_validators(new_entity._model, validators)
        new_entity._model = new_model_with_validators

    if existing_entity:
        # Update logic (if needed, can be more complex)
        existing_entity._model = new_entity._model
        entity_store.register(existing_entity)
    else:
        entity_store.register(new_entity)

    return entity_store.get(name)


def attach_validators(model: Type[BaseModel], validators: Dict[str, Callable]):
    class ValidatedModel(model):
        for field_name, field_validator in validators.items():
            locals()[f"validate_{field_name}"] = validator(
                field_name, allow_reuse=True
            )(field_validator)

    return ValidatedModel


def create_entity_store(
    entity_config: EntityConfig,
    update: bool = False,
    query: str = None,
    corpus: List[str] = None,
    top_k: int = 2,
    model=None,
) -> EntityStore:
    """
    Create an EntityStore from an EntityConfig.
    """
    entity_store = EntityStore()

    for entity_creation in entity_config.creations:
        create_or_update_entity(
            name=entity_creation.name,
            fields=entity_creation.fields,
            relationships=entity_creation.relationships,
            methods=entity_creation.methods,
            update=update,
            query=query,
            corpus=corpus,
            top_k=top_k,
            model=model,
        )

    return entity_store
