# -*- coding: utf-8 -*-

import asyncio
import pytest
import pytest_asyncio

from patchwork.core import Task
from patchwork.core.client.local import AsyncLocalPublisher, AsyncLocalSubscriber, AsyncLocalBroker, MissingBehaviour
from patchwork.core.client.serializers.betterproto import BetterprotoSerializer
from patchwork.core.client.task import FrozenTask


@pytest.fixture
def broker():
    return AsyncLocalBroker(
        ('test', ),
        publish_missing=MissingBehaviour.EXCEPTION,
        subscribe_missing=MissingBehaviour.EXCEPTION
    )


@pytest_asyncio.fixture
async def subscriber(broker):
    client = AsyncLocalSubscriber(broker=broker, queue_names=['test'])
    async with client:
        yield client


@pytest.mark.asyncio
async def test_send(broker):
    client = AsyncLocalPublisher(broker=broker)

    await client.send(b'payload', some_extra=1, queue_name='test')

    assert broker.get_queue('test').qsize() == 1, \
        "Sent message missing on the queue"

    payload = broker.get_queue('test').get_nowait()
    serializer = BetterprotoSerializer()
    task = serializer.decode(payload)

    assert task.payload == b'payload'
    assert task.meta.extra['some_extra'] == 1


@pytest.mark.asyncio
async def test_send_payload(broker):
    client = AsyncLocalPublisher(broker=broker)

    task = Task(task_type='test', payload=b'')
    task.meta.queue_name = 'test'
    await client._send(b'payload', task)

    assert broker.get_queue('test').qsize() == 1, \
        "Sent message missing on the queue"

    payload = broker.get_queue('test').get_nowait()
    assert payload == b'payload'


@pytest.mark.asyncio
async def test_send_timeout():
    broker = AsyncLocalBroker(['test'], max_queue_size=1)
    # put something to fill the queue
    broker.get_queue('test').put_nowait(None)

    client = AsyncLocalPublisher(broker=broker)

    with pytest.raises(TimeoutError):
        task = Task(task_type='test', payload=b'')
        task.meta.queue_name = 'test'
        await client._send(b'payload', task, timeout=0.01)


@pytest.mark.asyncio
async def test_shared_default_queue():
    """
    Test if all local async client instances share the same default broker instance
    :return:
    """
    client_1 = AsyncLocalPublisher()
    client_2 = AsyncLocalSubscriber(queue_names=['test'])

    task = Task(task_type='test', payload=b'')
    task.meta.queue_name = 'test'
    await client_1._send(b'payload', task)
    async with client_2:
        payload, meta = await client_2._fetch_one()

    assert payload == b'payload'
    assert meta == {'queue_name': 'test'}


@pytest.mark.asyncio
async def test_fetch_one(subscriber, broker):
    broker.get_queue('test').put_nowait(b'payload')

    payload, meta = await subscriber._fetch_one()

    assert payload == b'payload'
    assert meta == {'queue_name': 'test'}


@pytest.mark.asyncio
async def test_fetch_one_timeout(subscriber):
    with pytest.raises(TimeoutError):
        _payload, _meta = await subscriber._fetch_one(timeout=0.01)


@pytest.mark.asyncio
async def test_unstarted_subscriber(broker):
    client = AsyncLocalSubscriber(broker=broker, queue_names=['test'])

    with pytest.raises(RuntimeError):
        _ = await client._fetch_one()


@pytest.mark.asyncio
async def test_subscribe_on_missing():
    """
    Test if subscriber subscribed on missing queue will receive a message when queue will be created
    :return:
    """
    broker = AsyncLocalBroker()
    client_1 = AsyncLocalPublisher(broker=broker)
    client_2 = AsyncLocalSubscriber(broker=broker, queue_names=['test-missing'])

    async def send():
        task = Task(task_type='test', payload=b'')
        task.meta.queue_name = 'test-missing'
        await client_1._send(b'payload', task)

    # create a background task to send task on missing queue (will be created)
    asyncio.create_task(send())

    async with client_2:
        # await on subscribed queue which does not exists yet
        assert not client_2.broker.has_queue('test-missing')
        payload, meta = await client_2._fetch_one()

    assert payload == b'payload'
    assert meta == {'queue_name': 'test-missing'}


@pytest.mark.asyncio
async def test_task_freeze():
    t = Task(task_type='test')
    t._local['foo'] = 'bar'

    frozen = t.freeze()
    assert frozen.task_type == t.task_type
    assert frozen._local['foo'] == t._local['foo']

    assert hash(frozen)