# -*- coding: utf-8 -*-
import datetime
from typing import List

import rqdatac
from rqpattr.types import DateConvertible


def _to_datetime(dt: datetime.date) -> datetime.datetime:
    return datetime.datetime(dt.year, dt.month, dt.day)


def is_bank_trading_date(self, dt: DateConvertible) -> bool:
    pre_date = rqdatac.bond.get_previous_trading_date(dt)
    pre_next_date = rqdatac.bond.get_next_trading_date(pre_date)
    return dt == pre_next_date


def is_exchange_trading_date(dt: DateConvertible) -> bool:
    return rqdatac.is_trading_date(dt)


def get_exchange_previous_trading_date(
        dt: DateConvertible, n: int = 1
) -> datetime.datetime:
    return _to_datetime(rqdatac.get_previous_trading_date(dt, n))


def get_exchange_next_trading_date(
        dt: DateConvertible, n: int = 1
) -> datetime.datetime:
    return _to_datetime(rqdatac.get_next_trading_date(dt, n))


def get_exchange_trading_dates(
        start_date: DateConvertible, end_date: DateConvertible
) -> List[datetime.datetime]:
    return [_to_datetime(t) for t in rqdatac.get_trading_dates(start_date, end_date)]


def get_bank_previous_trading_date(
        dt: DateConvertible, n: int = 1
) -> datetime.datetime:
    return _to_datetime(rqdatac.bond.get_previous_trading_date(dt, n))


def get_bank_next_trading_date(dt: DateConvertible, n: int = 1) -> datetime.datetime:
    return _to_datetime(rqdatac.bond.get_next_trading_date(dt, n))


def get_bank_trading_dates(
        start_date: DateConvertible, end_date: DateConvertible
) -> List[datetime.datetime]:
    return [_to_datetime(t) for t in rqdatac.bond.get_trading_dates(start_date, end_date)]
