# -*- coding: utf-8 -*-
from contextlib import contextmanager


class DummyMetric:
    def labels(self, *args, **kwargs):
        return self


class Counter(DummyMetric):
    def __init__(self, *args, **kwargs):
        pass

    def inc(self, *args, **kwargs):
        pass


class Gauge(DummyMetric):
    def __init__(self, *args, **kwargs):
        pass

    def inc(self, *args, **kwargs):
        pass

    def dec(self, *args, **kwargs):
        pass

    def set(self, *args, **kwargs):
        pass


class Info(DummyMetric):
    def __init__(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass


class Timer():

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, f):
        return f


class Summary(DummyMetric):
    def __init__(self, *args, **kwargs):
        pass

    def observe(self, *args, **kwargs):
        pass

    def time(self, *args, **kwargs):
        return Timer()


class Histogram(DummyMetric):
    def __init__(self, *args, **kwargs):
        pass

    def observe(self, *args, **kwargs):
        pass

    def time(self, *args, **kwargs):
        return Timer()
