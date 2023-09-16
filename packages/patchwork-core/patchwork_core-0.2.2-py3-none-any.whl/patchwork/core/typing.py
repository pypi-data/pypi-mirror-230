# -*- coding: utf-8 -*-
from importlib import import_module
from typing import Union, Any, TypeVar, Generic, Callable

import sys
from pydantic import GetCoreSchemaHandler

from pydantic_core import CoreSchema, core_schema
from pydantic_core.core_schema import ValidatorFunctionWrapHandler
from typing_extensions import get_origin, get_args

StandardTypes = Union[None, bytes, str, tuple, list, dict, int, float, bool]


T = TypeVar('T')


def import_module_item(path: str):
    mod_name, class_name = path.split(':')
    try:
        mod = import_module(mod_name)
    except Exception as e:
        raise ValueError(f'unable to import {mod_name}: {e.__class__.__name__}({e})')

    for module_name, module in sys.modules.items():
        # skip empty modules and ones without actual file
        if not module or not hasattr(module, '__file__'):
            continue

        if mod.__file__ == module.__file__:
            # if same module has been imported use imported one
            # this allows to use issubclass or isinstance checks on previously imported module and
            # class returned by this method (note: same class code imported in different way creates
            # different class types)
            if mod != module:
                sys.modules.pop(mod.__name__)
                mod = module
            break

    if not hasattr(mod, class_name):
        raise ValueError(f"module '{mod_name}' has no member '{class_name}'")

    return getattr(mod, class_name)


class ClassPath(Generic[T]):
    """
    String which represents a path to class, contains module path and class name delimited by a colon.
    In Pydantic returns imported class

    !!! example
        `foo.bar:MyClass`
    """

    def __new__(cls, path: Union[str, T]):
        if isinstance(path, str):
            klass = import_module_item(path)
        else:
            klass = path
        return klass

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        origin = get_origin(source_type)
        if origin is None:
            origin = source_type
            item_tp = object
        else:
            item_tp = get_args(source_type)[0]

        instance_schema = core_schema.is_instance_schema(cls)

        item_schema = handler.generate_schema(item_tp)
        str_schema = handler.generate_schema(str)

        def val_item(v: Any, handler: ValidatorFunctionWrapHandler):
            klass = import_module_item(v)
            handler(klass)
            return klass

        def path_format(v: Any):
            if v.count(':') != 1:
                raise ValueError(f"'{v}' is not a valid path to class. Path should be a Python "
                                 f"module and class name joined by colon, eg: foo.bar:MyClass")
            return v

        python_schema = core_schema.chain_schema([
            core_schema.no_info_after_validator_function(path_format, str_schema),
            core_schema.no_info_wrap_validator_function(val_item, item_schema)
        ])

        return core_schema.union_schema([
            instance_schema,
            python_schema
        ])


class FuncPath(Callable):
    """
    String which represents a path to function, contains module path and class name delimited by a colon.
    In Pydantic returns imported function

    !!! example
        `foo.bar:my_func`
    """

    def __init__(self, path: Union[str, Callable]):
        if isinstance(path, str):
            fn = import_module_item(path)
        else:
            fn = path
        self.v = fn

    def __call__(self, *args, **kwargs):
        return self.v(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.v

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:

        item_schema = handler.generate_schema(Callable)
        str_schema = handler.generate_schema(str)

        def val_item(v: Any, handler: ValidatorFunctionWrapHandler):
            fn = import_module_item(v)
            handler(fn)
            return fn

        def path_format(v: Any):
            if v.count(':') != 1:
                raise ValueError(f"'{v}' is not a valid path to function. Path should be a Python "
                                 f"module and function name joined by colon, eg: foo.bar:MyClass")
            return v

        python_schema = core_schema.chain_schema([
            core_schema.no_info_after_validator_function(path_format, str_schema),
            core_schema.no_info_wrap_validator_function(val_item, item_schema)
        ])

        return python_schema
