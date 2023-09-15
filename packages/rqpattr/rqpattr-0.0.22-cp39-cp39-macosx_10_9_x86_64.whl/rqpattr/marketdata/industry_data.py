# -*- coding: utf-8 -*-
import time
import os
import pickle
from collections import defaultdict
from datetime import datetime as Datetime, date as Date

import numpy as np
import pandas as pd

import rqdatac
from rqdatac.client import get_client

from rqpattr.utils.decorators import ttl_cache

here = os.path.dirname(__file__)


def _to_date_int(dt):
    return dt.year * 10000 + dt.month * 100 + dt.day


END_DATE = Date(9999, 12, 31)
START_DATE = Date(1990, 1, 1)


def _cvtdate(ds, default):
    if ds is None or ds.startswith('0') or ds.startswith('9'):
        return default
    return Datetime.strptime(ds, '%Y-%m-%d').date()


@ttl_cache(3600)
def get_listing_date_and_delisting_date(order_book_id: str):
    ins = rqdatac.instruments(order_book_id)
    if ins is None:
        return START_DATE, END_DATE
    return _cvtdate(ins.listed_date, START_DATE), _cvtdate(ins.de_listed_date, END_DATE)


class Cache:
    __slots__ = ("expire", 'data')

    def __init__(self, data):
        self.data = data
        self.expire = time.time()


_sw_cache: Cache = Cache({})
_zx_cache: Cache = Cache({})


def _get_sw_cache():
    # 老版本的行业分类, 可以在新版本(申万2021分类)找到映射关系
    _SW_OLD_TO_NEW_MAPPING = {
        "餐饮旅游": "社会服务",
        "化工": "基础化工",
        "休闲服务": "社会服务",
        "电气设备": "电力设备",
        "纺织服装": "纺织服饰",
        "黑色金属": "钢铁",
        "商业贸易": "商贸零售",
        "采掘": "煤炭",
    }
    # 这些行业分类属于老版本的行业分类, 且无法在新版本(申万2021分类)找到映射关系
    # 所以将其设为非法行业分类, 当遇到这些分类时, 直接跳过.
    _NOT_VALID_INDUSTRY = {
        "交运设备", "信息服务", "信息设备", "建筑建材", "金融服务"
    }
    data = defaultdict(list)
    for doc in get_client().execute('__internal__shenwan_industry'):
        if doc['version'] != 3 or doc["index_name"] in _NOT_VALID_INDUSTRY:
            continue

        # 取到的行业数据中, 有可能还是旧的行业分类, 这里映射到新的分类过去
        doc["index_name"] = _SW_OLD_TO_NEW_MAPPING.get(doc["index_name"], doc["index_name"])
        data[doc['order_book_id']].append(doc)

    for o, d in data.items():
        a = [(e['start_date'].date(), e['index_name']) for e in d]
        data[o] = a

    for d in data.values():
        d.sort(key=lambda x: x[0], reverse=True)

    return data


def _get_zx_cache():
    data = defaultdict(list)
    for doc in get_client().execute('__internal__zx2019_industry'):
        data[doc['order_book_id']].append(doc)

    for o, d in data.items():
        a = [(e['start_date'].date(), e['first_industry_name']) for e in d]
        a.sort(key=lambda x: x[0], reverse=True)
        data[o] = a
    return data


def _industry_cache(standard):
    if standard == 'sws':
        cache = _sw_cache
    else:
        cache = _zx_cache

    if cache.expire > time.time():
        return cache.data

    if standard == 'sws':
        data = _sw_cache.data = _get_sw_cache()
        _sw_cache.expire = time.time() + 3600
    else:
        data = _zx_cache.data = _get_zx_cache()
        _zx_cache.expire = time.time() + 3600
    return data


def _one_industry(data, order_book_id: str, date: Date):
    a = data[order_book_id]
    if not a:
        return
    s, e = get_listing_date_and_delisting_date(order_book_id)
    if date > e or date < s:
        return
    for s, v in a:
        if s <= date:
            return v


def _industry_idx(order_book_ids, dates, standard):
    data = _industry_cache(standard)
    getter = _one_industry
    rv = defaultdict(list)

    for d in dates:
        d = d.date()
        for o in order_book_ids:
            v = getter(data, o, d)
            if v is None:
                continue
            rv[v].append((d, o))

    return rv


def get_stock_industry(order_book_ids, dates, standard):
    assert standard == 'sws' or standard == 'citics'
    dates = pd.to_datetime(dates)
    industries = _industry_idx(order_book_ids, dates, standard)

    index = pd.MultiIndex.from_product([dates, order_book_ids])
    df = pd.DataFrame(0, index, list(industries.keys()), dtype='i1')
    for i, a in industries.items():
        idx = pd.MultiIndex.from_tuples(a)
        df.loc[idx, i] = 1
    df.index.names = ['date', 'order_book_id']
    df.fillna(0.0, inplace=True)
    return df
