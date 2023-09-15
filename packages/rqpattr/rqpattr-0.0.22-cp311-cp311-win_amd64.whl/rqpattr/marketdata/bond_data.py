import pandas as pd

import rqdatac

from rqpattr.exceptions import MissingData
from rqpattr.utils.pandas_util import maybe_reindex


def get_chinabond_valuation(bond_list, fields, start_date, end_date):
    """
    对于跨银行间-交易所发行，存在数据缺失的债券，以银行间合约估值数据填充交易所合约估值数据

    PARAMETER
    ----------
    bond_list: list 债券列表
    start_date: string 开始日期
    end_Date: string 结束日期

    RETURN
    ----------
    chinabond_data: pandas.DataFrame 填充后中债估值数据（例如到期收益率、日终全价、应计利息等）
    """

    # 对于跨交易所-银行间同时发行债券，中债只提供银行间合约的估值数据。因此对于这类债券，把交易所代码统一转换为银行间代码
    bond_set = set(bond_list)

    try:
        NIB_market_code = rqdatac.bond.get_secu_market_code(bond_list)["NIB"].dropna().to_dict()
    except (TypeError, KeyError):
        NIB_market_code = {i: i for i in bond_list}

    has_converted = {}

    for original_id in bond_list:
        if original_id in NIB_market_code and NIB_market_code[original_id] != original_id:
            bond_set.remove(original_id)
            bond_set.add(NIB_market_code[original_id])
            has_converted[NIB_market_code[original_id]] = original_id

    converted_bond_list = list(bond_set)
    if isinstance(fields, str):
        fields = [fields]

    if "period_of_repayment" in fields:
        fields.remove("period_of_repayment")
        fields.append("time_to_maturity")

    chinabond_data = rqdatac.bond.get_valuation(
        converted_bond_list, start_date, end_date, source="chinabond",
        fields=fields, valuation_type="short",
    )

    if chinabond_data is None:
        raise MissingData("估值数据", converted_bond_list, [start_date, end_date])

    # FIXME: 中债估值有重复数据...
    chinabond_data = chinabond_data[~chinabond_data.index.duplicated()]
    chinabond_data = chinabond_data.reindex(columns=fields)
    chinabond_data.rename(columns={"time_to_maturity": "period_of_repayment"}, inplace=True)

    # 将 chinabond_data 的order_book_id 映射回来
    values_index: list = chinabond_data.index.tolist()
    new_index = []
    for order_book_id, date in values_index:
        if order_book_id in has_converted:
            new_index.append((has_converted[order_book_id], date))
        else:
            new_index.append((order_book_id, date))
    chinabond_data.index = pd.MultiIndex.from_tuples(new_index, names=["order_book_id", "date"])
    return chinabond_data


def get_treasury_bond_yield(dates):
    """获取国债收益率相关数据"""
    dates = pd.to_datetime(dates)
    df = rqdatac.bond.get_yield_curves(
        names="中债国债收益率曲线",
        type="yield_curve",
        start_date=dates[0],
        end_date=dates[-1],
    )
    if df is None:
        raise MissingData('中债国债收益率曲线', dates=dates)

    df = df.droplevel(0).pivot(columns="tenor", values="rate")
    df = maybe_reindex(df, dates)
    df.fillna(method="ffill", inplace=True)
    return df
