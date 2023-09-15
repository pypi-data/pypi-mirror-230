# -*- coding: utf-8 -*-
from typing import Sequence

import pandas as pd
import numpy as np

import rqdatac

from rqpattr.types import DateConvertible
from rqpattr.utils.pandas_util import maybe_reindex
from rqpattr.exceptions import MissingData


def _not_found_behave(dates: Sequence[DateConvertible], order_book_ids: Sequence[str]):
    raise MissingData("价格数据", order_book_ids, dates)


def _get_price(order_book_ids: Sequence[str], dates: pd.DatetimeIndex, field) -> pd.DataFrame:
    dates = pd.to_datetime(dates)
    if not rqdatac.get_trading_dates(dates[0], dates[0]):
        pre = pd.to_datetime(rqdatac.get_previous_trading_date(dates[0]))
        full_dates = dates.insert(0, pre)
    else:
        full_dates = dates

    price = rqdatac.get_price(
        order_book_ids,
        full_dates[0],
        full_dates[-1],
        fields=field,
        expect_df=True,
        adjust_type="post",
    )
    if price is None:
        return _not_found_behave(dates, order_book_ids)
    price = price[field].unstack(level=0)
    df = maybe_reindex(price, dates)
    df = maybe_reindex(df, order_book_ids, axis=1)
    df.iloc[0] = price.iloc[0]
    df.ffill(inplace=True)

    df.index.name = "date"
    df.columns.name = "order_book_id"
    return df


def get_equity_price(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    return _get_price(order_book_ids, dates, "close")


def get_futures_price(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    """价格"""
    return _get_price(order_book_ids, dates, "settlement")
