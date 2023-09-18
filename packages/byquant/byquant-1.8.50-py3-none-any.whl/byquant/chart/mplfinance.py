#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Author : Trabi
# Email : info@byquant.com
# Copyright (C) 2022-2023 ByQuant.com
#
#  ███████   ██    ██   ██████   ██    ██    ████    ██    ██  ████████  
#  ██    ██   ██  ██   ██    ██  ██    ██   ██  ██   ███   ██     ██     
#  ███████     ████    ██    ██  ██    ██  ████████  ██ ██ ██     ██         █████  █████  █████
#  ██    ██     ██     ██   ██   ██    ██  ██    ██  ██   ███     ██         █      █   █  █ █ █
#  ███████      ██      ███████   ██████   ██    ██  ██    ██     ██     ██  █████  █████  █ █ █
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
import mplfinance as mpf
import pandas as pd

def plot(data,title='',type='candle',style='yahoo',volume=False,addplot=[]):
    return mpf.plot(data, title=title,type=type,style=style,volume=volume,addplot=addplot,warn_too_much_data=10000)
    
#def kline(data,title='',type='candle',style='yahoo',volume=True,addplot=[]):
#    return mpf.plot(data, title=title,type=type,style=style,volume=volume,addplot=addplot)

def make_addplot(data, type='scatter', markersize=100, marker='v', color='red'):
    return mpf.make_addplot(data, type=type, markersize=markersize, marker=marker, color=color)


ohlc = plot
kline = plot
addplot = make_addplot
