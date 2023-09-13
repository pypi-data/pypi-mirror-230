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
import backtrader as bt
import numpy as np
import empyrical as emp
#from analysis import *
from . import analysis as analysis
import pandas as pd
from . import tool as tool

haveByBot = tool.check('bybot/vip',warn=False)
if haveByBot :
    #from . import bybot as bybot
    from byquant.bybot import lib as bybot_lib
    

class SMA_Signal(bt.Indicator):
    lines = ('bs',)
    params = (
        ('period', 15),
    )

    def __init__(self):
        self.lines.bs = self.data.close - bt.indicators.SMA(self.data.close,period=self.p.period)

        
class Backtest():

    
    def __init__(self,datasets,strategy='',signal='',out='',style='candle',warn=False,**params):
        #print('*** Start ByQuant Backtest Engine ***')
        self.warn = warn
        if not self.warn:
            import warnings
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            warnings.filterwarnings('ignore', category=UserWarning)
        if 'cash' in params:
            self.cash = params['cash']
        else:
            self.cash = 1000000
            
        if 'commission' in params:
            self.commission = params['commission']
        else:
            self.commission = 0.0005
        
        if 'figheigth' in params:
            self.figheigth = params['figheigth']
        else:
            self.figheigth = 4
            
            
            
        self.datasets = datasets
        #self.params = params
        
        #data.index=pd.to_datetime(data['datetime'])
        #self.data = bt.feeds.PandasData(dataname=data, datetime='datetime')
        
        self.strategy = strategy
        self.style = style
        self.out = out
        self.signal = signal
        self.freqo = '1d'
        
        
        
    
    def feedData(self,data,freq):
        if freq == '1m':
            params = dict(
                #fromdate = datetime.datetime(2011,1,4),
                #todate = datetime.datetime(2021,3,20),
                timeframe = bt.TimeFrame.Minutes, #bt.TimeFrame.Minutes,
                compression = 1,
                #dtformat=('%Y-%m-%d %H:%M:%S'),
                #tmformat=('%H:%M:%S'),
                #datetime=0,
                open=0,
                high=1,
                low=2,
                close=3,
                volume=4
            )
        else:
            params = dict(
                #fromdate = datetime.datetime(2011,1,4),
                #todate = datetime.datetime(2021,3,20),
                timeframe = bt.TimeFrame.Days, #bt.TimeFrame.Minutes,
                compression = 1,
                #dtformat=('%Y-%m-%d %H:%M:%S'),
                #tmformat=('%H:%M:%S'),
                #datetime=0,
                open=0,
                high=1,
                low=2,
                close=3,
                volume=4
            )
        data = data[['open','high','low','close','volume']]
        feed_result = bt.feeds.PandasData(dataname=data,**params)
        
        return feed_result
        
    def run(self):
        return self.byrun()


    def byrun(self):
        import matplotlib.pyplot as plt
        plt.style.use("default") #default、ggplot is also fine
        #plt.rcParams["figure.figsize"] = (9,8)
        #print(plt.style.available)
        cerebro = bt.Cerebro(stdstats=False)
        #cerebro.addobserver(bt.observers.BuySell)
        #cerebro.addobserver(bt.observers.Broker)
        
        if haveByBot:
        
            cerebro.addobserver(bybot_lib.backtest.Backtest_ByQuant)
            cerebro.addobserver(bybot_lib.backtest.Orders)
            cerebro.addobserver(bybot_lib.backtest.Trades)
            cerebro.addobserver(bybot_lib.backtest.Balance)
            cerebro.addobserver(bybot_lib.backtest.DrawDown)
            #if type(self.datasets) == list and len(self.datasets)>1:
            #    cerebro.addobserver(bt.observers.BuySell)
            #else:
            #    cerebro.addobserver(bybot_lib.backtest.ByQuant_com)
            cerebro.addobserver(bybot_lib.backtest.ByQuant_com)
        else:
            cerebro.addobserver(bt.observers.Broker)
            cerebro.addobserver(bt.observers.BuySell)
            cerebro.addobserver(bt.observers.DrawDown)
            cerebro.addobserver(bt.observers.TimeReturn)
        
        #cerebro.addobserver(bt.observers.Benchmark, data=banchdata)
        
        
        #
        
        #
        
        if self.signal == '':
            cerebro.addstrategy(self.strategy)
        else:
            cerebro.add_signal(bt.SIGNAL_LONGSHORT,SMA_Signal,period=15)
            cerebro.signal_strategy(self.strategy)
        
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='_Pyfolio')
        
        #cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')  # 夏普比率
        #cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns')  # 用对数法计算总、平均、复合、年化收益率
        #cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')  # 回撤
        #cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
            
            
        
        cerebro.broker.setcash(self.cash)
        
        cerebro.broker.setcommission(commission=self.commission)
        assetnum = 1
        #self.figheigth = 4
        benchmark_rets_data = None
        #bench_data={}
        if type(self.datasets) == list:
            assetnum = len(self.datasets)
            for dataset in self.datasets:
                data = dataset['data']
                symbol = dataset['symbol']
                freq = dataset['freq']
                self.freqo = dataset['freq']
                feed_data = self.feedData(data,freq)
                #tag = dataset['tag']
                if 'tag' in dataset:
                    tag = dataset['tag']
                else:
                    tag = ''
                cerebro.adddata(feed_data, name = symbol)
                #bench_data = feed_data
                #assetnum = assetnum +1
                if tag == 'benchmark' or tag == 'index':
                    benchmark_data = cerebro.datasbyname[symbol]
                    cerebro.addobserver(bt.observers.Benchmark, data=benchmark_data, timeframe = bt.TimeFrame.NoTimeFrame)
                    #cerebro.addobserver(bt.observers.Benchmark, data=benchmark_data, timeframe = bt.TimeFrame.Days)
                    self.figheigth = self.figheigth + 1
                    benchmark_rets_temp = dataset['data']
                    benchmark_rets_temp.rename(columns={"close": "benchmark"}, inplace=True)
                    benchmark_rets_data = benchmark_rets_temp.benchmark.pct_change().dropna()
                
                
        else :
            #assetnum = 1
            data = self.datasets
            symbol = 'Symbol'
            freq = self.freqo
            feed_data = self.feedData(data,freq)
            cerebro.adddata(feed_data, name = symbol)
        
        
        plt.rcParams["figure.figsize"] = (9,self.figheigth+2*assetnum)
        #print(len(self.datasets))
            
        results = cerebro.run()
        datadict={}
        pyfoliozer = results[0].analyzers.getbyname('_Pyfolio')
        datadict['timereturn'], datadict['positions'], datadict['transactions'], datadict['grosslev'] = pyfoliozer.get_pf_items()

        #if benchmark_rets_data is None:
        #    index_gspc_returns = emp.utils.get_symbol_returns_from_yahoo('^GSPC',
        #                                              start='1950-01-01').dropna()
        #    index_gspc_returns.index = index_gspc_returns.index.strftime('%Y-%m-%d')
        #    index_gspc_returns.index = pd.to_datetime(index_gspc_returns.index, format='%Y-%m-%d')
        #    index_gspc_returns.rename(columns={"^GSPC": "benchmark"}, inplace=True)
        #    benchmark_rets_data = index_gspc_returns
        

                                                  
        datadict['benchrets'] = benchmark_rets_data

        datadict['freqo'] = self.freqo

        if 'plot' == self.out or 'a' == self.out or 'all' == self.out:
            
            
            if haveByBot:
                pkwargs = bybot_lib.backtest.getPkwargs()
                cerebro.plot(**pkwargs)
            else:
                cerebro.plot()
            
            
            if 'all' == self.out:
                return datadict
            #img = cerebro.plot(style='line', plotdist=0.1, grid=True)
            #img[0][0].savefig(f'cerebro_123.png')
            
            #cerebro.plot(style = self.style,figsize=figsize)

        elif 'bokeh' == self.out or 'b' == self.out:
            from backtrader_plotting import Bokeh
            from backtrader_plotting.schemes import Tradimo,Blackly
            b = Bokeh(
                #title='symbol',
                tabs='single',  # single 和 multi
                plot=True,  # 关闭K线
                style='line',  # style='line'
                plot_mode='single',
                scheme=Tradimo(),
                # scheme=Blackly(),
                output_mode='show',  # output_mode “show”,“save”,"memory"
                #filename='filepath',
                show_headline=False
            )
            cerebro.plot(b)

            
        elif self.out in ['list','dict','data']:
            return datadict

        elif self.freqo == '1d':
            analysis.Analysis(datadict,out =self.out).show()
        else:
            """returns = results[0].analyzers._Returns.get_analysis()
            sharpe_ratio = results[0].analyzers._SharpeRatio.get_analysis()
            draw_down = results[0].analyzers._DrawDown.get_analysis()
            #print('Value: %.2f' % cerebro.broker.getvalue())
            print('Returns:%s' % returns)
            print('Sharpe Ratio: %s' % sharpe_ratio)
            print('Draw Down: %s' % draw_down)"""
            print('Only Support Daily Freq')
            
            
            
        
        #returns, positions, transactions, grosslev = pyfoliozer.get_pf_items()
        
        #byresults['returns'] = returns
        #byresults['positions'] = returns
        #byresults['transactions'] = returns
        #byresults['grosslev'] = returns
            
        

