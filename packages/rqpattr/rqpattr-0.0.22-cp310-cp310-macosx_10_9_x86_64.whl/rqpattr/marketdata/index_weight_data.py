# -*- coding: utf-8 -*-
import pandas as pd
import rqdatac

from rqpattr.utils.format import convert_date_to_int
from rqpattr.const import AssetType
from rqpattr.exceptions import MissingData


def _get_index_weight(
        order_book_id, concerned_dates, api, api_name, data_key, o_key, asset_type
) -> pd.DataFrame:
    concerned_dates = pd.to_datetime(concerned_dates)
    start_date, end_date = concerned_dates[0], concerned_dates[-1]
    data = rqdatac.client.get_client().execute(
        api_name, order_book_id, convert_date_to_int(start_date), convert_date_to_int(end_date)
    )
    if not data:
        series = api(order_book_id, start_date)
        if series is None:
            raise MissingData("指数权重数据", order_book_id, concerned_dates)
        # normalize
        s = series / series.sum()
        df = pd.DataFrame.from_dict({d: s for d in concerned_dates}, orient="index")
        df.sort_index(inplace=True)
        df.index.name = 'date'
        df.columns.name = 'order_book_id'
        return df

    value = []
    min_date = None
    for doc in data:
        date = doc['date']
        if min_date is None or date < min_date:
            min_date = date
        for d in doc[data_key]:
            d['date'] = date
        value.extend(doc[data_key])
    if min_date != start_date:
        series = api(order_book_id, start_date)
        if series is None:
            raise MissingData("指数权重数据", order_book_id, concerned_dates)
        # normalize
        s = series / series.sum()
        value.extend({'date': start_date, 'weight': w, o_key: o} for o, w in s.items())

    df = pd.DataFrame(value)
    df = df.pivot(index='date', columns=o_key, values="weight")
    df.fillna(0.0, inplace=True)
    # normalize
    df = df.div(df.sum(axis=1), axis=0)
    df = df.reindex(index=concerned_dates)
    df.sort_index(inplace=True)
    df.ffill(inplace=True)
    df.index.name = 'date'
    df.columns.name = 'order_book_id'
    return df


def get_bond_index_weight(
        order_book_id: str, concerned_dates: pd.DatetimeIndex
) -> pd.DataFrame:
    df = rqdatac.bond.index_weights(
        order_book_id, concerned_dates[0], concerned_dates[-1]
    )
    if df is None:
        raise MissingData("指数权重数据", order_book_id, concerned_dates)

    df.index.names = ["date", "order_book_id"]
    df.name = "weight"
    df = df.unstack()
    df.fillna(0.0, inplace=True)
    df = df.reindex(index=concerned_dates)
    df.sort_index(inplace=True)
    df.ffill(inplace=True)
    df.index.name = 'date'
    df.columns.name = 'order_book_id'
    return df


def get_stock_index_weight(
        order_book_id: str, concerned_dates: pd.DatetimeIndex
) -> pd.DataFrame:
    return _get_index_weight(
        order_book_id,
        concerned_dates,
        rqdatac.index_weights,
        "__internal__index_weights",
        "data",
        "order_book_id",
        AssetType.STOCK,
    )
