# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Type

import pytest
from pydantic import BaseModel, ValidationError

from patchwork.core import Component
from patchwork.core.config.base import ClassConfig, ComponentConfig
from patchwork.core.typing import ClassPath


@dataclass
class Test:
    foo: int
    bar: str


@pytest.mark.asyncio
async def test_classconfig_default():

    class M(BaseModel):
        klass: ClassConfig = ClassConfig(engine=ClassPath('tests.core.test_config:Test'), options={'foo': 4, 'bar': 'Alice'})

    m = M()
    inst = m.klass.instantiate()
    assert inst.foo == 4
    assert inst.bar == 'Alice'


@pytest.mark.asyncio
async def test_classconfig():

    class M(BaseModel):
        klass: ClassConfig

    m = M(klass=ClassConfig(engine='tests.core.test_config:Test', options={'foo': 4, 'bar': 'Alice'}))
    inst = m.klass.instantiate()
    assert inst.foo == 4
    assert inst.bar == 'Alice'


class TestComponent(Component):
    pass


class TestComponentAnother(Component):
    pass


@pytest.mark.asyncio
async def test_componentconfig_no_type_default_extra_opts():

    class M(BaseModel):
        klass: ComponentConfig

    with pytest.raises(ValidationError):
        M(
            klass=ComponentConfig(engine=ClassPath('tests.core.test_config:TestComponent'), options={'foo': 4, 'bar': 'Alice'})
        )


@pytest.mark.asyncio
async def test_componentconfig_no_type_default_no_opts():

    class M(BaseModel):
        klass: ComponentConfig

    m = M(
        klass=ComponentConfig(engine=ClassPath('tests.core.test_config:TestComponent'))
    )
    inst = m.klass.instantiate()
    assert isinstance(inst, TestComponent)
    assert inst.settings.enabled


@pytest.mark.asyncio
async def test_componentconfig_no_type_default():

    class M(BaseModel):
        klass: ComponentConfig = ComponentConfig(engine=ClassPath('tests.core.test_config:TestComponent'), options={'enabled': False})

    m = M()
    inst = m.klass.instantiate()
    assert isinstance(inst, TestComponent)
    assert inst.settings.enabled is False


@pytest.mark.asyncio
async def test_componentconfig_type():

    class M(BaseModel):
        klass: ComponentConfig[Type[TestComponent]]

    m = M(
        klass=ComponentConfig(engine=ClassPath('tests.core.test_config:TestComponent'), options={'enabled': False})
    )
    inst = m.klass.instantiate()
    assert isinstance(inst, TestComponent)
    assert inst.settings.enabled is False


class TestSettings(BaseModel):
    publisher: ComponentConfig

@pytest.mark.asyncio
async def test_settings_usage():
    settings = TestSettings(publisher={
        'engine': 'tests.core.test_config:TestComponent',
        'options': {
            'enabled': False
        }
    })

    assert settings.publisher.engine is TestComponent
    assert isinstance(settings.publisher.options, BaseModel)
