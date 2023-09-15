import time
from collections import defaultdict
from functools import lru_cache
from typing import List, Dict, Optional, Set, Iterable

import rqdatac
from rqdatac.share.errors import BadRequest
import rqdatac_fund

from rqpattr.const import AssetType
from rqpattr.logger import logger


class AssetTypeCache:
    def __init__(self):
        self._typedict: Dict[str, Set[str]] = defaultdict(set)
        self._otypedict: Dict[str, str] = {}
        self._oset: Set[str] = set()
        self._expire = 0

    def put_one(self, order_book_id: Iterable[str], asset_type: str):
        if order_book_id in self._oset:
            return
        self._oset.add(order_book_id)
        self._otypedict[order_book_id] = asset_type
        self._typedict[asset_type].add(order_book_id)

    def put_many(self, order_book_ids: Iterable[str], asset_type: str):
        oset = set(order_book_ids)
        oset = oset - self._oset
        self._oset.update(oset)
        o_dict = self._otypedict
        t_dict = self._typedict
        for o in oset:
            o_dict[o] = asset_type
            t_dict[asset_type].add(o)

    def get_one(self, order_book_id: str) -> Optional[str]:
        assert isinstance(order_book_id, str)
        return self._otypedict.get(order_book_id)

    def get_many(self, order_book_ids: Iterable[str]) -> Dict[str, str]:
        o_dict = self._otypedict
        return {o: o_dict[o] for o in order_book_ids if o in o_dict}

    def get_asset_type(self, asset_type: str) -> List[str]:
        return list(self._typedict[asset_type])

    def __contains__(self, item):
        return item in self._oset

    def set_expire(self, at):
        self._expire = at

    def is_expired(self):
        return self._expire < time.time()


asset_type_map = {
    "CS": AssetType.STOCK,
    "ETF": AssetType.FUND,
    "LOF": AssetType.FUND,
    "Future": AssetType.FUTURES,
    "INDX": AssetType.INDEX,
    "Option": AssetType.OPTION,
}

_type_cache = AssetTypeCache()


def _update_type():
    logger.info("start update instrument asset type cache")
    start = time.time()
    type_cache = _type_cache
    # NOTE: 下掉债券数据, 不需要bond相关cache了
    # bonds = rqdatac.bond.get_bond_list()
    # type_cache.put_many(bonds, AssetType.BOND)
    df = rqdatac.all_instruments()
    df = df[["order_book_id", "type"]]
    for row in df.itertuples(index=False):
        if row.type in asset_type_map:
            type_cache.put_one(row.order_book_id, asset_type_map[row.type])

    # 可能没有公募基金数据，尝试获取一下，如果报错了就不管
    try:
        type_cache.put_many(rqdatac.fund.all_instruments().order_book_id, AssetType.PUBLIC_FUND)
    except BadRequest as e:
        if "can't find" not in str(e).lower():
            raise e

    _type_cache.set_expire(time.time() + 6 * 3600)
    end = time.time()
    logger.info(f"finish update instrument asset type cache, spend {end - start:,} s")


def update_if_needed():
    if _type_cache.is_expired():
        _update_type()


def _get_instrument(order_book_id):
    asset_type = _type_cache.get_one(order_book_id)
    if asset_type is None:
        for getter in instrument_getters:
            try:
                ins = getter(order_book_id)
            except BadRequest as e:
                # 可能对应的品种没有数据，没有部署对应的rqdatad API
                # 在这种情况下，rqdatad 会返回 BadRequest: Can't find xxx
                # 异常，这种情况下忽略掉此异常.
                if "can't find" not in str(e).lower():
                    raise e
                else:
                    ins = None
            if ins is not None:
                return ins
        return
    elif asset_type == AssetType.BOND:
        return rqdatac.bond.instruments(order_book_id)
    elif asset_type == AssetType.CONVERTIBLE:
        return rqdatac.convertible.instruments(order_book_id)
    elif asset_type == AssetType.FUND:
        return rqdatac.fund.instruments(order_book_id)
    else:
        return rqdatac.instruments(order_book_id)


def get_instrument(order_book_id: str):
    update_if_needed()
    return _get_instrument(order_book_id)


instrument_getters = [
    rqdatac.convertible.instruments,
    rqdatac.fund.instruments,
    # rqdatac.bond.instruments,  # NOTE: 下掉债券数据, 不需要这个 instruments 了
    rqdatac.instruments,
]


def get_instruments(order_book_ids: List[str]) -> Dict[str, object]:
    update_if_needed()
    rv = {}
    for o in order_book_ids:
        ins = _get_instrument(o)
        if ins:
            rv[ins.order_book_id] = ins
    return rv


def get_asset_type(order_book_id: str) -> Optional[str]:
    if order_book_id.lower() in ("cash", "cny"):
        return AssetType.CASH
    update_if_needed()
    return _type_cache.get_one(order_book_id)


def get_asset_types(order_book_ids: Iterable[str]) -> Dict[str, str]:
    update_if_needed()
    return _type_cache.get_many(order_book_ids)


@lru_cache(10240)
def maybe_bond_index(order_book_id: str) -> bool:
    if order_book_id.startswith("RQB") and order_book_id.endswith(".INDX"):
        return True
    return False


@lru_cache(10240)
def maybe_bond(order_book_id: str) -> bool:
    return get_asset_type(order_book_id) == AssetType.BOND


@lru_cache(1024)
def is_stock_index_and_have_weight(order_book_id: str) -> bool:
    try:
        return rqdatac.index_weights(order_book_id) is not None
    except ValueError:
        return False


@lru_cache(1024)
def is_stock(order_book_id: str) -> bool:
    ins = rqdatac.instruments(order_book_id)
    if ins is None:
        return False
    return getattr(ins, "type", "") == 'CS'
