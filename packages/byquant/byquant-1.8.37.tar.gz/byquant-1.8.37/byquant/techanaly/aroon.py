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

#该指标待修改
#class byAROON(bt.Indicator):
#    lines = ('aroonup','aroondown','sma',)
#    params = (('period', 14),)
#    def __init__(self):
#        self.addminperiod(self.p.period)
        

#    def next(self):
        #代码需修正
#        self.aroonup, self.aroondown = talib.AROON(np.asarray(self.data.high), np.asarray(self.data.low), timeperiod=self.p.period)
        
        #print(self.aroondown)
#        if len(self) <= self.p.period:
#            self.lines.aroondown[0] = np.nan
#            self.lines.aroonup[0] = np.nan
#        elif len(self.aroondown) > self.p.period:
            #print(len(self))
            #print(self.aroondown)
#            self.lines.aroondown[0] = np.roll(self.aroondown, -self.p.period)[0]
#            self.lines.aroonup[0] = np.roll(self.aroonup, -self.p.period)[0]
#        else:
#            self.lines.aroondown[0] = np.nan
#            self.lines.aroonup[0] = np.nan
        
        
 #       
        
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


