#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Author: Bean
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

class biBIAS(bt.Indicator):
    lines = ('bias',)
    params = (
        ('period', 12),
    )

    def __init__(self):
        self.addminperiod(self.p.period * 2)
        self.ave_price_line = bt.indicators.SMA(self.data.close,period=self.p.period)

    def next(self):
        self.lines.bias[0] = (self.data.close[0] - self.ave_price_line[0]) / self.ave_price_line[0] * 100 / 100


def byBIAS(close,period=14):
    
    meanPrice = close.rolling(window=period).mean()
    BIAS = (close - meanPrice) / meanPrice * 100 / 100

    return BIAS
    

def BIAS(data, period = 14):
    if isinstance(data, pd.DataFrame):
        return byBIAS(data.close,period=period)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return byBIAS(data,period=period)
    elif 'trader.' in str(type(data)):
        return biBIAS(data,period=period)
    else:
        return None



bias = BIAS



