# -*- coding: utf-8 -*-
from asyncio import AbstractEventLoop, get_event_loop

import pytz
import warnings
import sys
from datetime import datetime
from typing import Tuple, Mapping, Any, Iterable, Type
from importlib.metadata import version

from .serializers.base import BaseTaskSerializer
from .serializers.betterproto import BetterprotoSerializer
from .task import Task, TaskDecodeError, FrozenTask
from ..component import Component

try:
    from prometheus_client import Histogram, Info, Summary
except ImportError:
    from ..stubs.prometheus import Histogram, Info, Summary


deserialize_time = Summary("subscriber_deserialization", "Task deserialization time")

fetch_time = Histogram('subscriber_fetch_time', "Subscriber fetch time")
subscriber_info = Info("subscriber_info", "Subscriber info")


class PatchworkSubscriber(Component):

    class Config(Component.Config):
        """
        Settings schema for each Patchwork Client.
        """
        serializer: Type[BaseTaskSerializer] = BetterprotoSerializer

    settings: Config
    asynchronous: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_serializer = self.settings.serializer()
        subscriber_info.info(self._get_info())

    def __repr__(self):
        return super().__repr__().replace('Component', 'Subscriber')

    def _get_info(self):
        return {
            'patchwork_version': version('patchwork-core') if 'patchwork-core' in sys.modules else ""
        }

    @deserialize_time.time()
    def _deserialize_task(self, payload: bytes, meta: Mapping) -> Task:
        """
        Deserialize given payload as a Task.
        :param payload:
        :param meta:    Additional data passed by receiver
        :return:        Deserialized task instance
        """
        return self.task_serializer.decode(payload)

    def _process_received_task(self, payload: bytes, meta: Mapping) -> Task:
        """
        Processes received payload and converts into task. Internally this method calls _deserialize_task()
        :param payload:
        :param meta:    additional informaction passed by a receiver
        :return:  deserialized task instance
        """
        try:
            task = self._deserialize_task(payload, meta)
        except Exception as exc:
            handled = self._handle_deserialize_error(payload, meta, exc)
            raise TaskDecodeError(payload, meta, exc, handled) from exc

        task.meta.received = datetime.now(pytz.UTC)
        task.meta.queue_name = meta.get('queue_name', None)
        return task

    def _handle_deserialize_error(self, payload: bytes, meta: Any, exc: Exception) -> bool:
        """
        Called when exception is raised during message deserialization and task initialization.
        This method is responsible of making sure that task won't be lost, however simple resending
        to the queue might be not accurate because if error happens once it probably will happen
        every time.
        :param payload:
        :param meta:
        :param exc:
        :return: True if message has been somehow handled and worker should not take any action. Otherwise
                 return False, so worker may report this issue using own logging mechanism
        """
        return False

    def __del__(self):
        if self.is_running:
            warnings.warn(f"Destroying unstopped subscriber may leads to data loss! stop() didn't finished or called")


class AsyncSubscriber(PatchworkSubscriber):

    is_asynchronous = True

    def __init__(self, *, parent=None, loop: AbstractEventLoop = None, **options):
        super().__init__(parent=parent, **options)

        if loop is None:
            loop = get_event_loop()

        self.loop = loop

    async def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.get()
        except EOFError:
            raise StopAsyncIteration()

    async def subscribe(self, queue_name: Iterable[str]):
        raise NotImplementedError()

    async def unsubscribe(self, queue_name: Iterable[str]):
        raise NotImplementedError()

    def subscription(self) -> Iterable[str]:
        raise NotImplementedError()

    async def get(self, *, timeout: float = None) -> FrozenTask:
        """
        Waits given time for next task and when arrived returns it.
        :param timeout:
        :raise TimeoutError: no task came in given timeout
        :return:
        """
        with fetch_time.time():
            payload, meta = await self._fetch_one(timeout=timeout)

        return self._process_received_task(payload, meta).freeze()

    async def commit(self, task: Task, *, timeout: float = None):
        """
        Commits given task returned by get() method.
        Meaning of "commit" depends on queue backend, but should be considered as success of task handling
        (which is not the same as success of task execution). Success of task handling means that task
        has been executed successfully or rescheduled successfully and given task can be safely removed
        from the queue. Whatever happens task won't be lost.

        :param task:
        :raise TimeoutError: commit timeout exceeded
        :param timeout:
        :return:
        """
        raise NotImplementedError()

    async def rollback(self, task: Task, *, timeout: float = None):
        """
        Rollback given task returned by get() method.
        Meaning of "rollback" depends on queue backend, but after this operation exactly the same task should
        be delivered again. Use this with caution as exactly the same is strict, so your code will receive
        the same bytes again and again. Make sure that it doesn't lead to infinite loop.

        For retries, it's recommended to store some retries counter in task meta, send retry task explicitly
        with bumped counter and commit the failed one.
        :param task:
        :param timeout:
        :return:
        """
        raise NotImplementedError()

    async def _fetch_one(self, *, timeout: float = None) -> Tuple[bytes, Mapping]:
        """
        Fetch one incoming message from the queue.
        :param timeout: Waits given time for message, if there is no message in given timeout raises TimeoutError.
                        None means no timeout, `0` means no wait.
        :return: payload of fetched message and additional information which should be passed to task deserializer
        """
        raise NotImplementedError()
