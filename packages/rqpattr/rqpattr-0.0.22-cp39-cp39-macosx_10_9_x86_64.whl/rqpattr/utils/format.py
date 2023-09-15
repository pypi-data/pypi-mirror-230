# -*- coding: utf-8 -*-
import re
import itertools
import json
import uuid
from datetime import datetime, date
from typing import Iterable, List, Union

import pandas as pd

from rqpattr.types import DateConvertible


def convert_to_datetime(dt: DateConvertible) -> datetime:
    if isinstance(dt, datetime):
        return dt
    if hasattr(dt, "year"):
        return datetime(dt.year, dt.month, dt.day)

    return pd.to_datetime(dt).to_pydatetime()


def convert_date_to_int(dt):
    if hasattr(dt, "year"):
        return dt.year * 10000 + dt.month * 100 + dt.day
    return convert_date_to_int(convert_to_datetime(dt))


timestamp_regexp = re.compile(
    """^(?P<year>[0-9][0-9][0-9][0-9])
      -(?P<month>[0-9][0-9]?)
      -(?P<day>[0-9][0-9]?)
      (?:((?P<t>[Tt])|[ \\t]+)   # explictly not retaining extra spaces
      (?P<hour>[0-9][0-9]?)
      :(?P<minute>[0-9][0-9])
      :(?P<second>[0-9][0-9])
      (?:\\.(?P<fraction>[0-9]*))?
      (?:[ \\t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9][0-9]?)
      (?::(?P<tz_minute>[0-9][0-9]))?))?)?$""",
    re.X,
)


def is_datetime_string(v):
    return timestamp_regexp.match(v)


number_regex = re.compile(r"-?/d+\.?\d*")


def is_number_string(v):
    return number_regex.match(v)


float_regex = re.compile(r"-?/d+\.\d*")


def is_float_string(v):
    return float_regex.match(v)


integer_regex = re.compile(r"-?/d+")


def is_integer_string(v):
    return integer_regex.match(v)


# fmt: off
BOOLEAN_STATES = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}
# fmt: on


def is_bool_string(v):
    return v.lower() in BOOLEAN_STATES


def is_true_string(v):
    return BOOLEAN_STATES.get(v, False)


def union(*it: Iterable) -> List:
    return list(set(itertools.chain(*it)))


yield_rate_regex = re.compile(r"(?P<number>\d+)(M|Y)$")


def get_terms_in_year(s: str) -> Union[float, int]:
    match = yield_rate_regex.search(s)
    if not match:
        raise ValueError(f'invalid string: {s}')
    n = match['number']
    f = s[-1]
    if f == "Y":
        return int(n)
    return int(n) / 12


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            if o.hour == 0 and o.minute == 0 and o.second == 0:
                return o.date().isoformat()
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, uuid.UUID):
            return str(o)
        return json.JSONEncoder.default(self, o)
