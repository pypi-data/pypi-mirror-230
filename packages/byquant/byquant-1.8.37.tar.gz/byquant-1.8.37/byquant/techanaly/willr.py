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

def WILLR(data,low=pd.Series(dtype=float),close=pd.Series(dtype=float),period=14):
    if isinstance(data, pd.DataFrame):
        return talib.WILLR(data.high,data.low,data.close, timeperiod=period)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.WILLR(data,low,close, timeperiod=period)
    elif 'trader.' in str(type(data)):
        return bt.talib.WILLR(data.high,data.low,data.close,period=period)
    else:
        return None
            
willr = WILLR


