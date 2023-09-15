# -*- coding: utf-8 -*-
from patchwork.core.client.serializers.base import BaseTaskSerializer
from patchwork.core.proto.google.protobuf import Value, NullValue
from patchwork.core.proto.task import ProtoTask, ProtoTaskMetadata
from patchwork.core.proto.google.protobuf import StringValue, BytesValue, Struct

try:
    import betterproto
except ImportError:
    betterproto = None

from ..task import Task, TaskMetadata


class BetterprotoSerializer(BaseTaskSerializer):

    def __init__(self):
        if betterproto is None:
            raise Exception("`betterproto` not installed")

    @classmethod
    def _encode_meta_extra(cls, v):
        if v is None:
            return Value(null_value=NullValue.NULL_VALUE)
        elif isinstance(v, (int, float)):
            return Value(number_value=v)
        elif isinstance(v, str):
            return Value(string_value=v)
        elif isinstance(v, bool):
            return Value(bool_value=v)
        else:
            raise NotImplementedError()

    @classmethod
    def _encode_payload(cls, payload):
        if isinstance(payload, str):
            wrapper = StringValue(value=payload)
            return 'google.protobuf.StringValue', bytes(wrapper)
        elif isinstance(payload, bytes):
            wrapper = BytesValue(value=payload)
            return 'google.protobuf.BytesValue', bytes(wrapper)
        else:
            try:
                return f'custom', bytes(payload)
            except TypeError:
                raise ValueError('unsupported payload type')

    @classmethod
    def _decode_payload(cls, payload):
        if payload.type_url == 'google.protobuf.StringValue':
            w = StringValue()
            w.parse(payload.value)
            return w.value
        elif payload.type_url == 'google.protobuf.BytesValue':
            w = BytesValue()
            w.parse(payload.value)
            return w.value
        elif payload.type_url == 'custom':
            # actual decoding needs to be done on client code depending on actual transfer protocol and encoding
            return payload.value
        else:
            raise ValueError(f'unsupported payload type: {payload.type_url}')

    def encode(self, task: Task) -> bytes:

        proto_task = ProtoTask(
            uuid=str(task.uuid),
            task_type=task.task_type,
            correlation_id=task.correlation_id,
        )

        proto_task.payload.type_url, proto_task.payload.value = self._encode_payload(task.payload)

        task_meta_fields = {
            'expires',
            'max_retries',
            'queue_name',
            'not_before',
            'attempt',
            'received',
            'scheduled'
        }

        raw = task.meta.model_dump(include=task_meta_fields)
        proto_task.meta = ProtoTaskMetadata(**raw)

        if task.meta.extra:
            extra = Struct()
            meta = {k: self._encode_meta_extra(v) for k, v in task.meta.extra.items()}
            extra.fields.update(meta)
            proto_task.meta.extra.type_url = 'google.protobuf.Struct'
            proto_task.meta.extra.value = bytes(extra)

        return bytes(proto_task)

    def decode(self, data: bytes) -> Task:
        task_proto = ProtoTask()
        task_proto.parse(data)

        proto_extra = task_proto.meta.extra
        extra = {}

        if proto_extra.type_url == 'google.protobuf.Struct':
            s = Struct()
            s.parse(proto_extra.value)
            extra = {k: betterproto.which_one_of(v, 'kind')[1] for k, v in s.fields.items()}

        task = Task(
            uuid=task_proto.uuid,
            task_type=task_proto.task_type,
            correlation_id=task_proto.correlation_id,
            payload=self._decode_payload(task_proto.payload),
            meta=TaskMetadata(
                not_before=task_proto.meta.not_before if task_proto.meta.not_before.timestamp() > 0 else None,
                expires=task_proto.meta.expires if task_proto.meta.expires.timestamp() > 0 else None,
                max_retries=task_proto.meta.max_retries,
                attempt=task_proto.meta.attempt,
                scheduled=task_proto.meta.scheduled if task_proto.meta.scheduled.timestamp() > 0 else None,
                received=task_proto.meta.received if task_proto.meta.received.timestamp() > 0 else None,
                queue_name=task_proto.meta.queue_name,
                extra=extra
            )
        )

        return task
