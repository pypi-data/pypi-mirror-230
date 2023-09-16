# -*- coding: utf-8 -*-
from typing import Type

import pytest
from pydantic import BaseModel, ValidationError

from patchwork.core.typing import ClassPath


class Test:
    pass


class TestAnother:
    pass


def test_without_type():
    class M(BaseModel):
        path: ClassPath

    m = M(path='tests.core.test_classpath:Test')
    assert m.path is Test


def test_with_type():
    class M(BaseModel):
        path: ClassPath[Type[Test]]

    m = M(path='tests.core.test_classpath:Test')
    assert m.path is Test


def test_with_type_invalid():
    class M(BaseModel):
        path: ClassPath[Type[Test]]

    with pytest.raises(ValidationError):
        m = M(path='tests.core.test_classpath:TestAnother')


def test_default_class():
    class M(BaseModel):
        path: ClassPath[Type[Test]] = ClassPath(Test)

    m = M()
    assert m.path is Test


def test_default_str():
    class M(BaseModel):
        path: ClassPath[Type[Test]] = ClassPath('tests.core.test_classpath:Test')

    m = M()
    assert m.path is Test