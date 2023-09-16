# -*- coding: utf-8 -*-
from ..task import Task


class BaseTaskSerializer:

    def encode(self, task: Task) -> bytes:
        raise NotImplementedError()

    def decode(self, data: bytes) -> Task:
        raise NotImplementedError()
