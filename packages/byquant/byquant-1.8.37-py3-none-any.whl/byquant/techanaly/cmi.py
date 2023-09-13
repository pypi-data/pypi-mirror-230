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

class biCMI(bt.Indicator):
    lines = ('cmi',)
    params = (
        ('period', 14),
    )

    def __init__(self):
        self.addminperiod(self.p.period * 2)
        self.hh_line = bt.indicators.Highest(self.data.high,period=self.p.period)
        self.ll_line = bt.indicators.Lowest(self.data.low,period=self.p.period)


    def next(self):
        ABSv = np.abs(self.data.close[0]-self.data.close[1-self.p.period])
        self.lines.cmi[0] = ABSv / (self.hh_line[0] - self.ll_line[0]) * 100


def byCMI(high,low,close,period=14):
    
    ABSv = np.abs(close-close.shift(period-1))
    HHVv = high.rolling(window=period).max()
    LLVv = low.rolling(window=period).min()
    CMI = ABSv / (HHVv-LLVv) * 100

    return CMI
    

def CMI(data,low=pd.Series(dtype=float),close=pd.Series(dtype=float), period = 14):
    if isinstance(data, pd.DataFrame):
        return byCMI(data.high,data.low,data.close,period=period)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return byCMI(data,low,close,period=period)
    elif 'trader.' in str(type(data)):
        return biCMI(data,period=period)
    else:
        return None



cmi = CMI



