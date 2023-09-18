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
# aroondown, aroonup = AROON(high, low, timeperiod=14)
# 参数说明：high:最高价；low:最低价；close：收盘价；timeperiod：时间周期
#AROON_aroondown,AROON_aroonup = talib.AROON(data['high'].values, data['low'].values, timeperiod=14)

def AROON(data,low=pd.Series(dtype=float),period=14):
    if isinstance(data, pd.DataFrame):
        return talib.AROON(data.high,data.low, timeperiod=period)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.AROON(data,low,timeperiod=period)
    elif 'trader.' in str(type(data)):
        return bt.talib.AROON(data.high,data.low,timeperiod=period)
    else:
        return None



aroon = AROON
#AROON_NP = AROON


