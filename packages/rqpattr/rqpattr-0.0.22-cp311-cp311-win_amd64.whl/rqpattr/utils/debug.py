# -*- coding: utf-8 -*-
import sys
import unittest
import os
from functools import wraps, partial

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

import pandas as pd
from pandas import testing as _testing

_dummy_test = unittest.TestCase()

_DEBUG = False


def set_debug(flag: bool):
    global _DEBUG

    _DEBUG = bool(flag)
    if _DEBUG:
        print('DEBUG MODE IS ON !!!')


if os.getenv('RQPATTR_DEBUG', 'off').upper() in ("ON", "TRUE", "Y", "YES"):
    print('DEBUG MODE IS ON !!!')
    _DEBUG = True


def check_debug_on(user_func=None, rv=None):
    if user_func is None:
        return partial(check_debug_on, rv=rv)

    @wraps(user_func)
    def wrapper(*args, **kwargs):
        if _DEBUG:
            return user_func(*args, **kwargs)
        return rv

    return wrapper


assert_series_equal = check_debug_on(_testing.assert_series_equal)
assert_index_equal = check_debug_on(_testing.assert_index_equal)
assert_frame_equal = check_debug_on(_testing.assert_frame_equal)
assert_almost_equal = check_debug_on(_dummy_test.assertAlmostEqual)
assert_dict_equal = check_debug_on(_dummy_test.assertDictEqual)
assert_set_equal = check_debug_on(_dummy_test.assertSetEqual)


def is_debug_on():
    return _DEBUG


@check_debug_on
def assert_sequence_equal(right, left, check_type=False, check_exact=True, delta=10 ** -8, msg=""):
    if check_type:
        assert type(right) != type(left), f"{type(right)} != {type(left)}. " + msg

    assert len(right) == len(left), f"length not equal {len(left)} != {len(right)}. " + msg

    if isinstance(right, pd.Series) and isinstance(left, pd.Series):
        assert_series_equal(right, left, check_names=False, check_exact=False)

    if isinstance(right, pd.Index) and isinstance(left, pd.Index):
        assert_index_equal(right, left, check_names=False, check_exact=True)
    if check_exact:
        for idx in range(len(right)):
            assert right[idx] == left[idx], (
                f"{right[idx]} != {left[idx]} item {idx} not equal. " + msg
            )
        return
    for idx in range(len(right)):
        _dummy_test.assertAlmostEqual(
            right[idx], left[idx], msg=f"item {idx} not equal. " + msg, delta=delta
        )


@check_debug_on
def assert_every_element_equal(seq, ele, exact=False, delta=10 ** -8):
    if exact:
        for idx, item in enumerate(seq):
            assert item == idx, f"{item} != {ele}, item {idx} not equal"
        return
    is_series = isinstance(seq, pd.Series)
    for idx, item in enumerate(seq):
        _dummy_test.assertAlmostEqual(item, ele, delta=delta, msg=f"element at {idx if not is_series else seq.index[idx]}")


@check_debug_on
def asset_not_null(seq, key=None):
    with pd.option_context("mode.use_inf_as_na", True):
        if isinstance(seq, pd.DataFrame):
            rv = seq.isnull()
            assert not rv.any().any(), seq[rv]
            return
        elif isinstance(seq, pd.Series):
            rv = seq.isnull()
            assert not rv.any(), seq[rv]
            return
        elif isinstance(seq, Iterable):
            for ele in seq:
                if key is not None:
                    assert not pd.isnull(key(ele)), ele
                else:
                    assert not pd.isnull(ele), ele
            return
        else:
            if key is not None:
                rv = pd.isnull(key(seq))
            else:
                rv = pd.isnull(seq)
            assert not rv, seq
