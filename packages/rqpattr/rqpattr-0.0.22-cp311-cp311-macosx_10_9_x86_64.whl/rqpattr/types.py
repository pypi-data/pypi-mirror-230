# -*- coding: utf-8 -*-
from datetime import datetime, date
from typing import Union, Sequence

import pandas as pd
import numpy as np

DateConvertible = Union[datetime, date, str, pd.Timestamp]

DateLike = Union[datetime, date, pd.Timestamp]

SingleOrMany = Union[str, Sequence[str]]
