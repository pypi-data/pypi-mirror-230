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

def KDJ(data,fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype,low=pd.Series(dtype=float),close=pd.Series(dtype=float)):
    if isinstance(data, pd.DataFrame):
        return talib.STOCH(data.high,data.low,data.close,fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=slowk_matype, slowd_period=slowd_period, slowd_matype=slowd_matype)
    elif isinstance(data, (pd.Series,np.ndarray)):
        return talib.STOCH(data,low,close,fastk_period=fastk_period, slowk_period=slowk_period, slowk_matype=slowk_matype, slowd_period=slowd_period, slowd_matype=slowd_matype)
    elif 'trader.' in str(type(data)):
        return bt.indicators.Stochastic(data,period=fastk_period, period_dfast=slowk_period, period_dslow=slowd_period)
    else:
        return None
            

STOCH = KDJ
kdj = KDJ

