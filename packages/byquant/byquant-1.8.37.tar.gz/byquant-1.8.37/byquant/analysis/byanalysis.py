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

import pandas as pd
import pyfolio as pf
import numpy as np

class Analysis():

    def __init__(self,datadict,out='',warn = False):
        print('*** Start ByQuant Analysis Engine ***')
        self.warn = warn
        if not self.warn:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            warnings.filterwarnings('ignore', category=UserWarning)
            
        self.datadict = datadict
        if self.datadict is None:
            print('Data is None')
            return
        
        if 'timereturn' in datadict:
            self.timereturn = datadict['timereturn']
        else:
            self.timereturn = []
        
        if 'positions' in datadict:
            self.positions = datadict['positions']
        else:
            self.positions = []
        
        if 'transactions' in datadict:
            self.transactions = datadict['transactions']
        else:
            self.transactions = []
        
        if 'grosslev' in datadict:
            self.grosslev = datadict['grosslev']
        else:
            self.grosslev = []
            
        if 'benchrets' in datadict:
            self.benchrets = datadict['benchrets']
        else:
            self.benchrets = None
            
        if 'freqo' in datadict:
            self.freqo = datadict['freqo']
        else:
            self.freqo = None
        
        #self.timereturn = returns
        #self.positions = positions
        #self.transactions = transactions
        #self.grosslev = grosslev
        self.out = out
        
        
                
    
    def show(self):
        if self.datadict is None:
            print('Data is None')
            return
        if 'plotly' == self.out or 'o' == self.out:
            import matplotlib.pyplot as plt

            self.timereturn.plot()  # 使用label参数指定线的标签
            plt.legend()  # 添加图例
            
        elif 'pyfolio' == self.out or 'p' == self.out:
            
            self.timereturn.index = self.timereturn.index.tz_convert(None)
            if self.benchrets is not None:
                self.benchrets.index = self.benchrets.index.strftime('%Y-%m-%d')
                self.benchrets.index = pd.to_datetime(self.benchrets.index, format='%Y-%m-%d')

            #pf.create_returns_tear_sheet(self.timereturn,benchmark_rets=self.benchrets)
            pf.create_full_tear_sheet(self.timereturn, self.positions, self.transactions,benchmark_rets=self.benchrets)
            #pf.create_full_tear_sheet(self.timereturn)

        elif 'quantstats' == self.out or 'q' == self.out: 
            import quantstats as qs
            self.timereturn.index = self.timereturn.index.tz_convert(None)
            qs.reports.full(self.timereturn, benchmark=self.benchrets, mode='full')
            

        elif 'seaborn' == self.out or 's' == self.out:
            import seaborn as sns
            sns.lineplot(self.timereturn)

        else:
            #import pyfolio as pf
            # 提取收益序列
            
            
            #pnlTemp = pd.Series(results[0].analyzers._returns.get_analysis())
            #pnlTemp = pd.Series(results[0].analyzers._returns.get_analysis())
            pnlTemp = self.timereturn
            pnl = pnlTemp.dropna()
            # 计算累计收益
            cumulative = (pnl + 1).cumprod()
            
            # 计算回撤序列
            max_return = cumulative.cummax()

            drawdown = (cumulative - max_return) / max_return
            # 计算收益评价指标
            # 按年统计收益指标
            pnl_cleaned = pnl.dropna()
            perf_stats_year = pnl_cleaned.groupby(pnl_cleaned.index.to_period('y')).apply(lambda data: pf.timeseries.perf_stats(data)).unstack()
            # 统计所有时间段的收益指标
            perf_stats_all = pf.timeseries.perf_stats((pnl)).to_frame(name='all')
            perf_stats = pd.concat([perf_stats_year, perf_stats_all.T], axis=0)
            perf_stats_ = round(perf_stats,4).reset_index()
            
            print(perf_stats_)
    def returns(self):
        if self.datadict is None:
            #print('Data is None')
            return
        self.timereturn.index = self.timereturn.index.tz_convert(None)
        self.benchrets.index = self.benchrets.index.strftime('%Y-%m-%d')
        self.benchrets.index = pd.to_datetime(self.benchrets.index, format='%Y-%m-%d')

        pf.create_returns_tear_sheet(self.timereturn,benchmark_rets=self.benchrets)

    
    def position(self):
        if self.datadict is None:
            #print('Data is None')
            return
        pf.create_position_tear_sheet(self.timereturn, positions=self.positions, transactions=self.transactions)  # 生成持仓相关的图表

    def trading(self):
        if self.datadict is None:
            #print('Data is None')
            return
        pf.create_txn_tear_sheet(self.timereturn, self.positions, self.transactions)  # 生成交易相关的图表

    def trip(self):
        if self.datadict is None:
            #print('Data is None')
            return
        pf.create_round_trip_tear_sheet(self.timereturn, self.positions, self.transactions)  # 生成轮次相关的图表
