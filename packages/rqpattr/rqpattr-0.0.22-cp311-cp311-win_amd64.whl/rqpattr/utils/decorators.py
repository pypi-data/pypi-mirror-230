# -*- coding: utf-8 -*-
import time
from functools import wraps, update_wrapper
from typing import Callable, Any, Tuple, Optional

_ERROR_CALLBACK = Callable[[Exception, tuple, dict], Any]


def exception_capture(callback: _ERROR_CALLBACK) -> Callable:
    def decorator(user_func):
        @wraps(user_func)
        def wrapper(*args, **kwargs):
            try:
                return user_func(*args, **kwargs)
            except Exception as e:
                return callback(e, args, kwargs)

        return wrapper

    return decorator


def retry(
    n: int, exceptions: Tuple[Exception], callback: Optional[_ERROR_CALLBACK] = None
) -> callable:
    assert n > 1

    def decorator(user_func):
        @wraps(user_func)
        def wrapper(*args, **kwargs):
            ex = None
            for _ in range(n):
                try:
                    return user_func(*args, **kwargs)
                except exceptions as e:
                    ex = e
                    if callback is not None:
                        callback(e, args, kwargs)
            raise ex

        return wrapper

    return decorator


_missing = object()


class cached_property(property):
    def __init__(self, func, name=None, doc=None):
        super().__init__(doc=doc)
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


# copy from functools
class _HashedSeq(list):
    """make sure hash called once"""

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed, kwd_mark=(object(),), fasttypes=frozenset([int, str])):
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for v in kwds.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


def ttl_cache(ttl, typed=False):
    if not isinstance(ttl, int) or not ttl > 0:
        raise TypeError("Expected ttl to be a positive integer")

    def decorating_function(user_function):
        wrapper = _ttl_cache_wrapper(user_function, ttl, typed)
        return update_wrapper(wrapper, user_function)

    return decorating_function


def _ttl_cache_wrapper(user_function, ttl, typed):
    sentinel = object()
    cache = {}
    cache_get = cache.get  # bound method to lookup a key or return None

    def wrapper(*args, **kwargs):
        key = _make_key(args, kwargs, typed)

        # in cpython, dict.get is thread-safe
        result = cache_get(key, sentinel)
        if result is not sentinel:
            expire_at, value = result
            if expire_at > time.time():
                return value
        value = user_function(*args, **kwargs)
        cache[key] = (time.time() + ttl, value)
        return value

    wrapper.clear_cache = cache.clear

    return wrapper


def update_doc(fr, annotation=True):
    def decorator(to):
        attrs = ("__doc__",)
        if annotation:
            attrs += ('__annotations__',)
        for attr in attrs:
            try:
                value = getattr(fr, attr)
            except AttributeError:
                pass
            else:
                setattr(to, attr, value)
        return to

    return decorator
