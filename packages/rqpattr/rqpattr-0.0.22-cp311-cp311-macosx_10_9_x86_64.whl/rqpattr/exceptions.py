# -*- coding: utf-8 -*-
import itertools
from typing import Iterable, Sequence, Union
from datetime import datetime, date


class AnalysisError(Exception):
    http_response_code = 500

    @property
    def http_response_body(self):
        return str(self)

    @property
    def error_message(self):
        return str(self)

    @property
    def error_detail(self):
        return repr(self)


class MissingData(AnalysisError):
    """Deprecated
    """
    http_response_code = 400

    def __init__(self, wants: str, order_book_ids=None, dates=None):
        """

        Parameters
        ----------
        wants : str
            数据类型
        order_book_ids : Union[str, Iterable[str]]
        dates : Sequence[Union[datetime, date]]
        """
        msg = "缺失"
        if order_book_ids is not None:
            if isinstance(order_book_ids, str):
                msg += " " + order_book_ids + " "
            else:
                o = ",".join(map(str, itertools.islice(order_book_ids, 3)))
                if o:
                    msg = msg + " " + o + '... '
        if dates is not None:
            st = dates[0]
            et = dates[-1]
            st = "%d年%d月%d日" % (st.year, st.month, st.day)
            et = "%d年%d月%d日" % (et.year, et.month, et.day)
            if st == et:
                msg += " %s 的" % st
            else:
                msg += "从 %s 到 %s (%d天)" % (st, et, len(dates))
        msg += wants
        if not msg.endswith("数据"):
            msg += "数据"
        super().__init__(msg)

    # for pickle data correctly, should define the following __reduce__ and __setstate__ methods.
    def __reduce__(self):
        return (type(self), self.args, self.args)

    def __setstate__(self, state):
        self.args = state


class UnknownAssets(AnalysisError):
    http_response_code = 400

    def __init__(self, order_book_ids, asset_type=None):
        o = ",".join(map(str, itertools.islice(order_book_ids, 3)))
        if asset_type:
            msg = "不能识别%s资产: %s" % (asset_type, o)
        else:
            msg = "不能识别资产: %s" % o

        super().__init__(msg)


class InvalidInput(AnalysisError):
    """用户输入数据有误而无法完成分析"""
    http_response_code = 400


class NoData(AnalysisError):
    """数据源无数据，而无法完成分析"""
    http_response_code = 400

    def __init__(self, message, detail=None):
        super().__init__(message)
        self._detail = detail

    @property
    def error_detail(self):
        return self._detail
