#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2022-2023 ByQuant.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import talib
import pandas as pd
import backtrader as bt
import numpy as np

#SAR：抛物线指标
# SAR(high, low, acceleration=0, maximum=0)
# 参数说明：high：最高价；low:最低价；acceleration：加速因子；maximum：极点价

def SAR(data, low=pd.Series(dtype=float),acceleration=0,maximum=0):
    if isinstance(data, pd.DataFrame):
        return talib.SAR(data.high, data.low, acceleration=acceleration, maximum=maximum)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.SAR(data, low, acceleration=acceleration, maximum=maximum)
    elif 'trader.' in str(type(data)):
        return bt.indicators.PSAR(data,af=acceleration,afmax=maximum)
    else:
        return None



sar = SAR


