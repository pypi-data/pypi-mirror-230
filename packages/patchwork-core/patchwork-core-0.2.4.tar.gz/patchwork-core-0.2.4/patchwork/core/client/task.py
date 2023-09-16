# -*- coding: utf-8 -*-
import uuid as uuid
from datetime import datetime
from typing import Mapping, Optional, Any, Union, Dict

from frozendict import frozendict
from pydantic import BaseModel, UUID4, Field, PrivateAttr, ConfigDict


class TaskDecodeError(ValueError):
    """
    Received message cannot be decoded into task.
    """

    def __init__(self, payload: bytes, meta: Mapping, exc: Exception, handled: bool):
        """
        :param payload: Received payload
        :param meta:    Received meta
        :param exc:     Raised exception
        :param handled: True if exception has been handled by client and this is just a notification exception,
                        handled means that task is not lost on the queue. If False, this case is not handled
                        and worker should take care of logging and administrator notification in the same
                        way as other task processing messages are handled.
        """
        self.payload = payload
        self.meta = meta
        self.exception = exc
        self.is_handled = handled

    def __str__(self):
        return ("Handled" if self.is_handled else "Unhandled") + f" {self.__class__.__name__}({self.exception})"


class TaskMetadata(BaseModel):
    not_before: Optional[datetime] = None
    expires: Optional[datetime] = None
    max_retries: Optional[int] = None
    attempt: int = 0
    scheduled: Optional[datetime] = None
    received: Optional[datetime] = None
    queue_name: Optional[str] = None
    extra: Optional[Mapping[str, Union[int, float, bool, str, None]]] = None

    def freeze(self):
        return FrozenTaskMetadata.model_construct(**self.model_dump())


class FrozenTaskMetadata(TaskMetadata):
    model_config = ConfigDict(frozen=True)


class Task(BaseModel):
    uuid: UUID4 = Field(default_factory=uuid.uuid4)
    meta: TaskMetadata = TaskMetadata()
    task_type: str
    correlation_id: Optional[str] = None
    payload: Optional[Any] = None

    # this field SHOULD NOT be transferred
    _local: Dict = PrivateAttr(default_factory=dict)

    def freeze(self):
        data = self.model_dump(exclude={'meta'})
        data['meta'] = self.meta.freeze()
        data['_local'] = frozendict(self._local)
        return FrozenTask.model_construct(**data)


class FrozenTask(Task):
    model_config = ConfigDict(frozen=True)

