# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Type, Mapping, Any, get_origin, Union

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic_core.core_schema import ValidatorFunctionWrapHandler
from typing_extensions import get_args

from patchwork.core import Component, AsyncPublisher, AsyncSubscriber
from patchwork.core.typing import ClassPath


class ImproperlyConfigured(Exception):
    """
    Invalid configuration detected
    """
    pass


ClassType = TypeVar("ClassType", bound=Type[object])


@dataclass
class ClassConfig(Generic[ClassType]):

    engine: ClassPath[ClassType]
    options: Mapping = field(default_factory=dict)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        origin = get_origin(source_type)
        if origin is None:
            origin = source_type
            item_tp = object
        else:
            item_tp = get_args(source_type)[0]

        engine_schema = handler.generate_schema(ClassPath[item_tp])
        opts_schema = handler.generate_schema(dict)

        def engine_item(v: Any, handler: ValidatorFunctionWrapHandler):
            v.engine = handler(v.engine)
            return v

        def opts_item(v: Any, handler: ValidatorFunctionWrapHandler):
            v.options = handler(v.options)
            return v

        def dict_item(v: Any):
            if isinstance(v, dict):
                return cls(engine=v['engine'], options=v['options'])
            return v

        python_schema = core_schema.chain_schema([
            core_schema.no_info_before_validator_function(
                dict_item, core_schema.is_instance_schema(cls)
            ),
            core_schema.no_info_wrap_validator_function(
                opts_item, opts_schema
            ),
            core_schema.no_info_wrap_validator_function(
                engine_item, engine_schema
            ),
        ])

        return python_schema

    def instantiate(self, **init_kwargs):
        return self.engine(**self.options, **init_kwargs)


ComponentType = TypeVar("ComponentType", bound=Type[Component])


@dataclass
class ComponentConfig(Generic[ComponentType]):
    """
    pydantic custom type for Dependencies.
    A dependency is a configuration of another component. Configuration must have at least `engine`
    defined which points to class and optionally may have a dict of `options` which will be passed
    to the engine. Options must follow engine `Settings`.
    """

    engine: ClassPath[ComponentType]
    options: BaseModel = field(default_factory=dict)

    def __init__(self, engine: Union[str, ComponentType], options: Union[BaseModel, dict] = None):
        self.engine = ClassPath(engine)
        if options is None:
            options = {}

        if isinstance(options, dict):
            self.options = self.engine.Config(**options)
        else:
            self.options = options

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        origin = get_origin(source_type)
        if origin is None:
            origin = source_type
            item_tp = Component
        else:
            item_tp = get_args(source_type)[0]

        engine_schema = handler.generate_schema(type(item_tp))
        opts_schema = handler.generate_schema(item_tp.Config)

        def engine_item(v: Any, handler: ValidatorFunctionWrapHandler):
            v.engine = handler(v.engine)
            return v

        def opts_item(v: Any, handler: ValidatorFunctionWrapHandler):
            v.options = handler(v.options)
            return v

        def dict_item(v: Any):
            if isinstance(v, dict):
                return cls(engine=v['engine'], options=v['options'])
            return v

        python_schema = core_schema.chain_schema([
            core_schema.no_info_before_validator_function(
                dict_item, core_schema.is_instance_schema(cls)
            ),
            core_schema.no_info_wrap_validator_function(
                opts_item, opts_schema
            ),
            core_schema.no_info_wrap_validator_function(
                engine_item, engine_schema
            ),
        ])

        return python_schema

    def instantiate(self, parent=None, **init_kwargs):
        return self.engine(**({"parent": parent} if parent is not None else {}), **self.options.model_dump(), **init_kwargs)


PublisherConfig = ComponentConfig[Type[AsyncPublisher]]
SubscriberConfig = ComponentConfig[Type[AsyncSubscriber]]
