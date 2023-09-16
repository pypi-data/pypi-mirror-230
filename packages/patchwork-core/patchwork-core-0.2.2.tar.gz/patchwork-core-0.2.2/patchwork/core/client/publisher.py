# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop, get_event_loop

import pytz
import uuid
import sys
import warnings
from datetime import datetime
from typing import Mapping, Any, Callable, Union, Type
from importlib.metadata import version

from .serializers.base import BaseTaskSerializer
from .serializers.betterproto import BetterprotoSerializer
from .task import Task, TaskMetadata
from ..component import Component

try:
    from prometheus_client import Histogram, Info, Summary
except ImportError:
    from ..stubs.prometheus import Histogram, Info, Summary


serialization_time = Summary('publisher_serialization', "Task serialization time")

send_time = Histogram('publisher_send_time', "Publisher send time")
publisher_info = Info("publisher_info", "Publisher info")


class PatchworkPublisher(Component):
    """
    Common code for sync and async publishers
    """

    class Config(Component.Config):
        """
        Settings schema for each Patchwork Client.
        :cvar max_message_size:     Maximum allowed message size (on the wire) in bytes
        """
        max_message_size: int = 1024*1024       # 1MB
        serializer: Type[BaseTaskSerializer] = BetterprotoSerializer

    settings: Config
    asynchronous: bool
    routing: list

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routing = []
        self.task_serializer = self.settings.serializer()
        publisher_info.info(self._get_info())

    def __repr__(self):
        return super().__repr__().replace('Component', 'Publisher')

    def _get_info(self):
        return {
            'patchwork_version': version('patchwork-core') if 'patchwork-core' in sys.modules else ""
        }

    def add_router(self, router: Callable[[Task], Union[str, None]]):
        """
        Add a task router for the publisher. Routers will be executed in the reverse order of adding
        (the most newly added - firstly executed)
        :param router: callable which for given task returns a name of queue for it or None if this router
        does not support this task
        :return:
        """
        self.routing.insert(0, router)

    def remove_router(self, router: Callable[[Task], Union[str, None]]):
        """
        Removes previously added router
        :param router:
        :return:
        """
        self.routing.remove(router)

    @serialization_time.time()
    def _serialize_task(self, task: Task) -> bytes:
        """
        Take task and returns serialized task payload as bytes.
        :param task:    Task instance
        :return:    Serialized task
        """
        return self.task_serializer.encode(task)

    def _prepare_task(self, task: Task) -> bytes:
        """
        Prepares task to be send. Makes validation tests on the task and returns serialized payload.
        Internally this method calls _serialize_task()
        :param task:
        :raise ValueError: if task validation fails
        :return: payload of serialized task if validation pass
        """
        if not task.uuid:
            task.uuid = str(uuid.uuid4())
        task.meta.scheduled = datetime.now(pytz.UTC)

        if task.meta.expires and task.meta.expires < task.meta.scheduled:
            raise ValueError('unable to send task which is already expired')

        if not task.meta.queue_name:
            for router in self.routing:
                queue_name = router(task)
                if queue_name is not None:
                    break

        payload = self._serialize_task(task)
        if len(payload) > self.settings.max_message_size:
            raise ValueError('message is too big')

        return payload

    def _build_task(self, payload: Any, meta: Union[Mapping, TaskMetadata], cause: Task = None, task_type: str = None):
        if not isinstance(meta, TaskMetadata):
            meta = dict(meta)
            metadata = TaskMetadata()

            if 'not_before' in meta:
                metadata.not_before = meta.pop('not_before')
            if 'expires' in meta:
                metadata.expires = meta.pop('expires')
            if 'max_retries' in meta:
                metadata.max_retries = meta.pop('max_retries')
            if 'queue_name' in meta:
                metadata.queue_name = meta.pop('queue_name')

            if meta:
                metadata.extra = dict(meta)
        else:
            metadata = meta

        task = Task(
            uuid=uuid.uuid4(),
            meta=metadata,
            task_type=task_type or payload.__class__.__name__,
            payload=payload
        )

        if cause is not None:
            task.correlation_id = cause.correlation_id or str(cause.uuid)

        return task

    def __del__(self):
        if self.is_running:
            warnings.warn(f"Destroying unstopped publisher may leads to data loss! stop() didn't finished or called")


class AsyncPublisher(PatchworkPublisher):
    """
    Patchwork asynchronous pubslisher
    """

    is_asynchronous = True

    def __init__(self, *, parent=None, loop: AbstractEventLoop = None, **options):
        super().__init__(parent=parent, **options)

        if loop is None:
            loop = get_event_loop()

        self.loop = loop

    async def send(self, payload: Any, *, timeout: float = None, cause: Task = None, task_type: str = None, **meta):
        task = self._build_task(payload, meta, cause=cause, task_type=task_type)
        await self.send_task(task, timeout=timeout)
        return task

    async def send_task(self, task: Task, *, timeout: float = None):
        """
        Sends given task, if operation fail in given timeout raises TimeoutError.
        When this method returns it's considered as task has been delivered successfully and it's guaranteed
        that won't be lost (eg queue backend committed the message)
        :param task:
        :param timeout: send operation timeout, None means no timeout. 0 means immediatelly
        :return:
        """
        payload = self._prepare_task(task)
        with send_time.time():
            await self._send(payload, task, timeout=timeout)

    async def _send(self, payload: bytes, task: Task, *, timeout: float = None):
        """
        Sends given payload

        :param payload: Task payload to send
        :param task: Task instance to send, it should be considered as **immutable**
        :param timeout: Requested send operation timeout, None means no timeout, 0 means immediately
        :return:
        """
        raise NotImplementedError()
