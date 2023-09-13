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


class biEMV(bt.Indicator):
    lines = ('em',)
    params = (
        ('period', 14),
    )

    def __init__(self):
        self.addminperiod(self.p.period)
        #self.lines.emv = bt.ind.SumN(em,period=self.p.period)

    def next(self):
        emFront = (self.data.high[0] + self.data.low[0]) / 2
        emFrontSub = (self.data.high[-1] + self.data.low[-1]) / 2
        emEnd = (self.data.high[0] - self.data.low[0]) / self.data.volume[0]
        #em = (emFront - emFrontSub) * emEnd * 10000
        self.lines.em[0] = (emFront - emFrontSub) * emEnd * 10000
        #累加及均值待考虑

        


def byEMV(high,low,volume,period=14):
    subv = high.copy()
    subv.values[:]=2
    emFront=talib.DIV(talib.ADD(high,low),subv)
    emFrontSub=talib.DIV(talib.ADD(high.shift(1),low.shift(1)),subv)
    emEnd=talib.DIV(talib.SUB(high,low),volume)
    em= talib.SUB(emFront,emFrontSub) * emEnd * 10000
    #EMV=talib.SUM(em,timeperiod=period)

    return em
    

def EMV(data,low=pd.Series(dtype=float),volume=pd.Series(dtype=float), period = 14):
    if isinstance(data, pd.DataFrame):
        return byEMV(data.high,data.low,data.volume,period=period)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return byEMV(data,low,volume,period=period)
    elif 'trader.' in str(type(data)):
        return biEMV(data,period=period)
    else:
        return None



emv = EMV
#AROON_NP = AROON


