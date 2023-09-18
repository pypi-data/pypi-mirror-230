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

# 参数说明：talib.BBANDS(close, timeperiod, matype)
# close:收盘价；timeperiod:周期；matype:平均方法(bolling线的middle线 = MA，用于设定哪种类型的MA)
# MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
#out = upper, middle, lower

def BBands(data,period,matype = talib.MA_Type.EMA):
    if isinstance(data, pd.DataFrame):
        return talib.BBANDS(data.close, timeperiod=period,matype = matype)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.BBANDS(data, timeperiod=period,matype = matype)
    elif 'trader.' in str(type(data)):
        by_result = bt.indicators.BBands(data,period=period,)
        by_result.plotlines = dict(
            upper=dict(_name='Top',linestyle='-', linewidth=0.5, color='purple', alpha=0.5),
            midle=dict(_name='Mid',linestyle='-', linewidth=0.5, color='blue', alpha=0.5),
            lower=dict(_name='Bot',linestyle='-', linewidth=0.5, color='green', alpha=0.5),
        )
        return by_result
    else:
        return None



boll = BBands
BOLL = BBands
BollingerBands = BBands
bbands = BBands
BBANDS = BBands

        

    
    
    
