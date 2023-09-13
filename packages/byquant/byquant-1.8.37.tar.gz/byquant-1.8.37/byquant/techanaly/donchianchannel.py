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

class byDonchian(bt.Indicator):

    alias = ('DCH', 'DonchianChannel',)
    lines = ('top', 'mid', 'bot')
    params = dict(
        period=20,
        lookback=-1,  # consider current bar or not
    )
    
    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        top=dict(_samecolor=True),  # use same color as prev line (dcm)
        mid=dict(ls='--'),  # dashed line
        bot=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    

    def __init__(self):
        self.addminperiod(self.params.period)
        
        hi, lo = self.data.high, self.data.low
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)

        self.l.top = bt.ind.Highest(hi, period=self.p.period)
        self.l.bot = bt.ind.Lowest(lo, period=self.p.period)
        self.l.mid = (self.l.top + self.l.bot) / 2.0  # avg of the above

    #def next(self):
    #    highest = max(self.data.high.get(-self.p.period, 0))
    #    lowest = min(self.data.low.get(-self.p.period, 0))
    #    self.lines.top[0] = highest
    #    self.lines.bot[0] = lowest
    #    self.lines.mid[0] = (highest + lowest) / 2
        
def Donchian(data,low=pd.Series(dtype=float),period=14):
    if isinstance(data, pd.DataFrame):
        top = talib.MAX(data.high, timeperiod=period)
        bot = talib.MIN(data.low, timeperiod=period)
        mid = (top + bot) / 2
        return top,mid,bot
    elif isinstance(data, (pd.Series,np.ndarray)):
        top = talib.MAX(data, timeperiod=period)
        bot = talib.MIN(low, timeperiod=period)
        mid = (top + bot) / 2
        return top,mid,bot
    elif 'trader.' in str(type(data)):
        return byDonchian(data,period=period)
    else:
        return None



donchianchannel = Donchian
donchian = Donchian
DonchianChannel = Donchian
#AROON_NP = AROON


