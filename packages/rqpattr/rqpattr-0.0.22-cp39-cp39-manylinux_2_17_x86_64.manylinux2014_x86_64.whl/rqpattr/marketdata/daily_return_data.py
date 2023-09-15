# -*- coding: utf-8 -*-
import bisect
from typing import Sequence

import pandas as pd
import numpy as np

import rqdatac

from rqpattr.types import DateConvertible
from rqpattr.exceptions import MissingData, UnknownAssets


def _not_found_behave(dates: Sequence[DateConvertible], order_book_ids: Sequence[str]):
    raise MissingData("日收益率", order_book_ids, dates)


def _get_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex, field, adjust_dividend=False,
) -> pd.DataFrame:
    try:
        price = rqdatac.get_price(
            order_book_ids,
            rqdatac.get_previous_trading_date(dates[0]),
            dates[-1],
            fields=field,
            expect_df=True,
            adjust_type="none",
        )
    except ValueError:
        price = None

    if price is None:
        return _not_found_behave(dates, order_book_ids)
    price = price[field].unstack(level=0)
    if adjust_dividend:
        daily_return = _adjust_daily_return(price)
    else:
        daily_return = price.pct_change().iloc[1:]

    if set(daily_return.index) ^ set(dates):
        daily_return = daily_return.reindex(dates)

    if set(daily_return.columns) ^ set(order_book_ids):
        daily_return = daily_return.reindex(columns=order_book_ids)

    daily_return.fillna(0.0, inplace=True)
    daily_return.index.name = "date"
    daily_return.columns.name = "order_book_id"
    return daily_return


def _adjust_daily_return(price: pd.DataFrame) -> pd.DataFrame:
    daily_return = price.pct_change()

    try:
        splits = rqdatac.get_split(price.columns, price.index[1], price.index[-1])
    except ValueError:
        splits = None

    if splits is not None and not splits.empty:
        splits = splits.reset_index()
        factor = splits["split_coefficient_to"] / splits["split_coefficient_from"]

        splits = pd.DataFrame.from_dict({
            "date": splits["ex_dividend_date"].values,
            "order_book_id": splits["order_book_id"].values,
            "factor": factor.values,
        })
        splits = splits.groupby(["order_book_id", "date"], as_index=False).sum()
        splits = splits.pivot(index="date", columns="order_book_id", values="factor")
        adjust = splits.reindex(index=price.index, columns=price.columns, fill_value=np.nan)
        adjust = price * adjust
        adjust_returns = adjust.fillna(price).pct_change()
        daily_return[~adjust.isna()] = adjust_returns

    try:
        dividends = rqdatac.get_dividend(price.columns, price.index[1], price.index[-1])
    except ValueError:
        dividends = None

    if dividends is not None and not dividends.empty:
        dividends = dividends.reset_index()
        cash = dividends["dividend_cash_before_tax"] / dividends["round_lot"]

        dividends = pd.DataFrame.from_dict({
            "date": dividends["ex_dividend_date"].values,
            "order_book_id": dividends["order_book_id"].values,
            "cash": cash.values,
        })
        dividends = dividends.groupby(["order_book_id", "date"], as_index=False).sum()
        dividends = dividends.pivot(index="date", columns="order_book_id", values="cash").fillna(0.0)
        adjust = dividends.reindex(index=price.index, columns=price.columns, fill_value=0.0)
        adjust = pd.DataFrame(adjust.values / price.shift(1).values, price.index, price.columns)
        daily_return = daily_return + adjust

    return daily_return.iloc[1:]


def get_equity_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    return _get_daily_returns(order_book_ids, dates, "close", adjust_dividend=True)


def get_option_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    return _get_daily_returns(order_book_ids, dates, "close")


def get_future_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    return _get_daily_returns(order_book_ids, dates, "settlement")


def get_bond_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex, with_payment=True
) -> pd.DataFrame:
    """ 获取债券收益率数据. """
    pre_date = rqdatac.bond.get_previous_trading_date(dates[0])

    chinabond_valuations = rqdatac.bond.get_valuation(
        order_book_ids, pre_date, dates[-1],
        fields=["dirty_price_eod", "accrued_interest_intraday", "accrued_interest_eod", "residual_principal"],
        valuation_type="short",
    )
    if chinabond_valuations is None or chinabond_valuations.empty:
        return _not_found_behave(dates, order_book_ids)

    # the return is duplicated in sometimes.
    chinabond_valuations = chinabond_valuations[
        ~chinabond_valuations.index.duplicated(keep='first')]  # type: pd.DataFrame
    chinabond_valuations.index = chinabond_valuations.index.set_levels(pd.to_datetime(chinabond_valuations.index.levels[1]), level=1)

    shift_valuation = chinabond_valuations.groupby(level='order_book_id', group_keys=False).apply(lambda x: x.shift(1))

    # 本计息周期内一日应计利息 = 当日日终应计利息 - 当日日间应计利息
    daily_interest_accrual = chinabond_valuations["accrued_interest_eod"] - chinabond_valuations[
        "accrued_interest_intraday"]

    principal_payments = shift_valuation["residual_principal"] - chinabond_valuations["residual_principal"]
    # 两日应计利息差值
    accrued_interest_diff = chinabond_valuations["accrued_interest_eod"] - shift_valuation["accrued_interest_eod"]

    def _get_days_interval(index):
        return [(pd.Timestamp(index[i][1]) - pd.Timestamp(index[i - 1][1])).days if i != 0 else 1 for i in
                range(len(index))]

    # 如果票息支付日是周末/法定节假日，则票息支付会相应后延至下一个交易日。中债的应计利息摊分，会把延后的天数考虑在内。因此现金支付也需把延后天数考虑在内
    day_interval = chinabond_valuations['accrued_interest_eod'].groupby(level="order_book_id", group_keys=False).apply(
        lambda x: pd.Series(_get_days_interval(x.index), x.index, name="day_interval")
    )
    day_interval.name = "day_interval"

    # 周末/节假日应计利息 = （当前和前一易日之间的自然天数间隔 - 1）* 本计息周期内一日应计利息
    remaining_accrued_interest = (day_interval - 1) * daily_interest_accrual

    # 利息支付总额 = 前一交易日累计应计利息 + 跨周末/节假日产生的应计利息
    # 若应计利息变动大于0，则认为当日无付息；反之认为当日已付息
    coupon_payment = pd.Series(index=accrued_interest_diff.index,
                               data=np.where((accrued_interest_diff > 0),
                                             0,
                                             shift_valuation["accrued_interest_eod"] + remaining_accrued_interest -
                                             chinabond_valuations["accrued_interest_intraday"]))
    coupon_payment.fillna(0.0, inplace=True)

    holding_return = (
            (chinabond_valuations['dirty_price_eod'] + principal_payments + coupon_payment - shift_valuation[
                'dirty_price_eod'])
            / shift_valuation['dirty_price_eod']
    )
    holding_return.name = "holding_return"
    holding_return = holding_return.groupby(level='order_book_id', group_keys=False).apply(lambda x: x.iloc[1:].droplevel(0))
    result = holding_return.unstack(0)
    result = result.reindex(index=dates, columns=order_book_ids)
    result.fillna(0.0, inplace=True)
    result.index.set_names('date', inplace=True)
    result.columns.set_names("order_book_id", inplace=True)
    return result


def get_cash_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex, returns=0.0
) -> pd.DataFrame:
    """日收益率"""
    rv = pd.DataFrame(returns, index=dates, columns=order_book_ids)
    rv.index.name = "date"
    rv.columns.name = "order_book_id"
    return rv


def _get_public_fund_daily_profit_return(
        odf: pd.DataFrame, dates: pd.DatetimeIndex
) -> pd.DataFrame:
    df = rqdatac.fund.get_nav(odf.index, dates[0], dates[-1], 'daily_profit', expect_df=True)
    if df is None or df.empty:
        raise MissingData("公募基金日收益率", odf.index, dates)
    df = df['daily_profit']
    df = df.unstack(0, 0.0)
    indates = df.reindex(dates)
    indates.fillna(0.0, inplace=True)
    notindates = df[~df.index.isin(dates)].copy()
    notindates.fillna(0.0, inplace=True)
    if not notindates.empty:
        for date, series in notindates.iterrows():
            key = dates[bisect.bisect_right(dates, date)]
            indates.loc[key] += series

    return indates.multiply(0.0001, axis=1)


def _get_public_fund_unit_net_value_return(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    df = rqdatac.fund.get_nav(
        order_book_ids,
        rqdatac.get_previous_trading_date(dates[0]),
        dates[-1],
        'adjusted_net_value',
        expect_df=True,
    )
    if df is None or df.empty:
        raise MissingData("公募基金净值", order_book_ids, dates)
    df = df['adjusted_net_value']
    df = df.unstack(0)
    daily_return = df.pct_change()
    daily_return = daily_return.reindex(dates)
    daily_return.fillna(0.0, inplace=True)
    return daily_return


def get_public_fund_daily_returns(
        order_book_ids: Sequence[str], dates: pd.DatetimeIndex
) -> pd.DataFrame:
    dates = pd.to_datetime(dates)

    odf = rqdatac.fund.all_instruments()
    odf.set_index('order_book_id', inplace=True)
    odf = odf.loc[order_book_ids].dropna(how='all')
    odf = odf[~odf.index.duplicated(False)]
    if odf.empty:
        raise UnknownAssets(order_book_ids, "公募基金")
    daily_profit_fund = odf[odf.accrued_daily.apply(bool)]
    net_value_fund = odf[odf.accrued_daily.apply(lambda x: not bool(x))]
    concated = []
    if not daily_profit_fund.empty:
        concated.append(_get_public_fund_daily_profit_return(daily_profit_fund, dates))

    if not net_value_fund.empty:
        concated.append(
            _get_public_fund_unit_net_value_return(net_value_fund.index, dates)
        )

    daily_return = pd.concat(concated, axis=1)
    daily_return.fillna(0.0, inplace=True)
    daily_return.index.name = "date"
    daily_return.columns.name = "order_book_id"
    return daily_return
