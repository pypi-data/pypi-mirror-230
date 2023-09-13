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

import backtrader as bt
import numpy as np
import pandas as pd
import scipy.stats as stats


        
def isCross(line1,line2):
    if line1[0] > line2[0] and line1[-1] < line2[-1]:
        return True
    else:
        return False
crossOver = isCross
        
def crossUp(line1,line2):
    return line1[0] > line2[0] and line1[-1] < line2[-1]

def crossDown(line1,line2):
    return line1[0] < line2[0] and line1[-1] > line2[-1]
    
        
def num2date(datetime):
    return bt.num2date(datetime)
    
def regularSTD(data):
    return (data - data.mean()) / data.std()
    
def regularMM(data):
    return (data - data.min()) / (data.max() - data.min())

def scoreatpercentile(data,percent=38.2): #黄金分割 38.2、61.8
    return stats.scoreatpercentile(data,percent=percent)
    
def corr(data1,data2):
    if isinstance(data1, pd.DataFrame):
        arr1 = np.array(data1.close)
    elif isinstance(data1, pd.Series):
        arr1 = np.array(data1)
    elif isinstance(data1, list):
        arr1 = data1
    else:
        arr1 = data1
        
    if isinstance(data2, pd.DataFrame):
        arr2 = np.array(data2.close)
    elif isinstance(data2, pd.Series):
        arr2 = np.array(data2)
    elif isinstance(data2, list):
        arr2 = data2
    else:
        arr2 = data2
        
    return np.corrcoef(arr1,arr2)[0,1]
    
def spearmanr(data1,data2):
    if isinstance(data1, pd.DataFrame):
        arr1 = np.array(data1.close)
    elif isinstance(data1, pd.Series):
        arr1 = np.array(data1)
    elif isinstance(data1, list):
        arr1 = data1
    else:
        arr1 = data1
        
    if isinstance(data2, pd.DataFrame):
        arr2 = np.array(data2.close)
    elif isinstance(data2, pd.Series):
        arr2 = np.array(data2)
    elif isinstance(data2, list):
        arr2 = data2
    else:
        arr2 = data2
        
    spearmanr = stats.spearmanr(arr1,arr2)
    return spearmanr.statistic
