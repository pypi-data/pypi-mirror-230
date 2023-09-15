# -*- coding: utf-8 -*-
from typing import List


class Enum:
    _members = None

    def __init__(self):
        raise RuntimeError('enum not callable')

    @classmethod
    def members(cls):
        if cls._members is None:
            members = []
            for k in dir(cls):
                if k.startswith('_'):
                    continue
                v = getattr(cls, k)
                if callable(v):
                    continue
                members.append(k)
            cls._members = tuple(getattr(cls, k) for k in members)
        return list(cls._members)

    @classmethod
    def contains(cls, k):
        return k in cls.members()


class AssetType(Enum):
    BOND = "bond"
    STOCK = "stock"
    FUND = "fund"
    FUTURES = "futures"
    INDEX = "index"
    CASH = "cash"
    PUBLIC_FUND = "public_fund"
    OPTION = 'option'
    CONVERTIBLE = "convertible"
    HK_STOCK = 'hk_stock'
    OTC = 'otc'

    @classmethod
    def is_equity(cls, asset_type: str) -> bool:
        return asset_type == cls.STOCK or asset_type == cls.FUND or asset_type == cls.INDEX

    @classmethod
    def equity(cls) -> List[str]:
        return [cls.STOCK, cls.FUND, cls.INDEX]

    @classmethod
    def chinese(cls, asset_type):
        tp = AssetTypeChinese.get(asset_type)
        if tp is not None:
            return tp

        if asset_type.endswith("_otc"):
            return "非标资产"

        if "hk_stock" in asset_type:
            return "港股"

        print(asset_type)
        return '其他'


AssetTypeChinese = {
    "fixed_income": '债券',
    AssetType.BOND: "债券",
    AssetType.FUND: "基金",
    AssetType.FUTURES: "期货",
    AssetType.INDEX: "指数",
    AssetType.CASH: "现金",
    AssetType.STOCK: "股票",
    AssetType.OPTION: "期权",
    AssetType.PUBLIC_FUND: "基金",
    AssetType.CONVERTIBLE: "可转债",
    AssetType.HK_STOCK: "港股",
    AssetType.OTC: "非标资产",
}


class BenchmarkType(Enum):
    INDEX = "index"
    MIXED_INDEX = "mixed_index"
    YIELD_RATE = "yield_rate"
    CASH = "cash"


class AnalysisModel(Enum):
    BRINSON = "equity/brinson"
    FACTOR = "equity/factor"
    FACTOR_V2 = "equity/factor_v2"
    BOND_FACTOR = 'fixed_income/factor'  # 债券因子
    CAMPISI = 'fixed_income/campisi'  # 债券 Campisi 归因
    HEDGING = 'equity/hedging'  # 对冲归因


class StockFactorModel(Enum):
    V1 = "v1"
    V2 = "v2"


class MongoCollections(Enum):
    BENCHMARK_HOLDING_RETURNS = 'benchmark_holding_returns'
    BENCHMARK_FACTOR = "benchmark_factor"
    BENCHMARK_FACTOR_V2 = "benchmark_factor_v2"
    BENCHMARK_CAMPISI = 'benchmark_campisi'
    BENCHMARK_BOND_FACTOR = "benchmark_bond_factor_attributions"

    @classmethod
    def all_members(cls):
        return cls.members() + ["brinson_industry_" + s for s in BrinsonStandard.members()]


class BrinsonStandard(Enum):
    SHENWAN = "sws"
    ZHONGXIN = "citics"
    TRANSACTION_TYPE = "transaction_type"
    ASSET_CLASS = "asset_class"
    NATION_ECON = "nation_economic"  # 国民经济行业
    BOND_SECTOR1 = 'bond_sector1'
    BOND_SECTOR2 = "bond_sector2"
    FUTURES_VARIETIES = 'futures_varieties'


class IndustryStandard:
    sws = 'sws'
    citics = 'citics'


if __name__ == '__main__':
    print(MongoCollections.all_members())

    print(BrinsonStandard.members())
