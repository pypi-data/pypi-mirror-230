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

def STDDEV(data,period=14,nbdev=1):
    if isinstance(data, pd.DataFrame):
        return talib.STDDEV(data.close, timeperiod=period,nbdev=nbdev)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.STDDEV(data, timeperiod=period,nbdev=nbdev)
    elif 'trader.' in str(type(data)):
        return bt.indicators.StandardDeviation(data,period=period)
    else:
        return False



stddev = STDDEV
StandardDeviation = STDDEV





