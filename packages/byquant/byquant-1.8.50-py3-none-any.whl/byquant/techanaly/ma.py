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

from __future__ import (absolute_import, division, print_function,unicode_literals)
import talib
import pandas as pd
import backtrader as bt
import numpy as np

#- `0`: 简单移动平均线(Simple Moving Average, SMA)
#- `1`: 指数移动平均线(Exponential Moving Average, EMA)
#- `2`: 加权移动平均线(Weighted Moving Average, WMA)
#- `3`: 双指数移动平均线(Double Exponential Moving Average, DEMA)
#- `4`: 三指数移动平均线(Triple Exponential Moving Average, TEMA)
#- `5`: T3移动平均线(Triple Exponential Moving Average, T3)
#- `6`: KAMA平均线(Kaufman Adaptive Moving Average, KAMA)
#- `7`: MAMA平均线(MESA Adaptive Moving Average, MAMA)
#- `8`: 波动指标(Volatility Indicator, VIDYA)


def MA(data,period,matype=0):
    if isinstance(data, pd.DataFrame):
        return talib.MA(data.close, timeperiod=period,matype=matype)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.MA(data, timeperiod=period,matype=matype)
    elif 'trader.' in str(type(data)):
        return bt.indicators.MA(data,period=period,matype=matype)
    else:
        return None
            
ma = MA




