# -*- coding: utf-8 -*-
from typing import Iterable, Union
from datetime import datetime, date
import pandas as pd
from pandas import DatetimeIndex

import rqdatac


def shift1_by_trading_date(
    dates: DatetimeIndex, exchange=True, right=True
) -> DatetimeIndex:
    dates = pd.to_datetime(dates)
    if right:
        if exchange:
            insert_day = rqdatac.get_next_trading_date(dates[-1])
        else:
            insert_day = rqdatac.bond.get_next_trading_date(dates[-1])
        if len(dates) == 1:
            return DatetimeIndex(
                [pd.Timestamp(insert_day)], freq=dates.freq, copy=False, name="date"
            )
        return dates[1:].insert(len(dates) - 1, pd.Timestamp(insert_day))

    if exchange:
        insert_day = rqdatac.get_previous_trading_date(dates[0])
    else:
        insert_day = rqdatac.bond.get_previous_trading_date(dates[0])
    if len(dates) == 1:
        return DatetimeIndex(
            [pd.Timestamp(insert_day)], freq=dates.freq, copy=False, name="date"
        )
    return dates[:-1].insert(0, pd.Timestamp(insert_day))


def convert_to_datetime_index(dates: Iterable) -> DatetimeIndex:
    if isinstance(dates, (str, date, datetime, pd.Timestamp)):
        return pd.to_datetime([dates])
    if isinstance(dates, DatetimeIndex):
        return dates.copy()
    return pd.to_datetime(dates)


def append_level_in_multi_index(
    index: pd.MultiIndex, level_name: str, level_value
) -> pd.MultiIndex:
    tmp = (level_value,)
    new_index = pd.MultiIndex.from_tuples([i + tmp for i in index])
    new_index.names = index.names + [level_name]
    return new_index


def maybe_reindex(old: Union[pd.Series, pd.DataFrame], index: Iterable, axis=0):
    if axis == 0:
        if set(old.index) ^ set(index):
            return old.reindex(index, copy=False)
    else:
        if set(old.columns) ^ set(index):
            return old.reindex(columns=index, copy=False)
    return old
