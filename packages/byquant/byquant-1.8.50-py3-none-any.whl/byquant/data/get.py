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

import os
import time
import ccxt
import platform
import yfinance as yf
import tushare as ts
import akshare as ak
import baostock as bs
import pandas as pd
from datetime import date, datetime, timedelta
# from market import signals as tawSignal
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest, \
    TrailingStopOrderRequest
from alpaca.data.requests import CryptoLatestQuoteRequest

from alpaca.broker.models import Contact, Identity, Disclosures, Agreement
from alpaca.broker.requests import CreateAccountRequest
from alpaca.broker.enums import TaxIdType, FundingSource, AgreementType
from alpaca.broker.requests import CreateJournalRequest
from alpaca.broker.enums import JournalEntryType
from alpaca.broker.client import BrokerClient
from alpaca.broker.requests import CreateACHTransferRequest
from alpaca.broker.enums import TransferDirection, TransferTiming
from alpaca.trading.enums import OrderSide, TimeInForce

from alpaca.broker.requests import CreateACHRelationshipRequest
from alpaca.broker.enums import BankAccountType
# import byquant
from byquant import exchange
from pathlib import Path

# from market import models as marketModels

class Bar():

    def __init__(self, symbol, ktype='quote', freq='1d', renew=True, cachetime=86400, start='', end='', limit=1000,source='',token='', fields=[]):
        print('*** Start ByQuant Data Engine ***')
        self.symbol = symbol
        if self.symbol == 'symbol':
            self.symbol = 'SH600519.SSE' #AAPL.NASDAQ
        elif self.symbol == 'symbol1':
            self.symbol = 'MSFT.NASDAQ'
        elif self.symbol == 'symbol2':
            self.symbol = 'TSLA.NASDAQ'
        elif self.symbol == 'stock':
            self.symbol = 'AAPL.NASDAQ'
        elif self.symbol == 'cnstock':
            self.symbol = 'SH600519.SSE'
        elif self.symbol == 'fund':
            self.symbol = 'AAPL.NASDAQ'
        elif self.symbol == 'future_code':
            self.symbol = 'CL=F.NASDAQ'
        elif self.symbol == 'option':
            self.symbol = 'AAPL.NASDAQ'
        elif self.symbol == 'forex':
            self.symbol = 'EUR~USD.CURRENCYCOM'
        elif self.symbol == 'crypto':
            self.symbol = 'BTC~USDT.OKX'
        elif self.symbol == 'symbola':
            self.symbol = 'BTC~USDT.OKX'
        elif self.symbol == 'symbolb':
            self.symbol = 'BTC~USDT.BINANCE'
        elif self.symbol == 'spot':
            self.symbol = 'BTC~USDT.OKX'
        elif self.symbol == 'future':
            self.symbol = 'BTC~USDT$USDT.OKX'
        elif self.symbol == 'indexus':
            self.symbol = '^IXIC.NASDAQ'
        elif self.symbol == 'indexcn':
            self.symbol = 'SH000300.SSE'
            
        self.market = ''
        self.offset = 0
        self.ktype = ktype
        self.freq = freq
        self.start = start
        self.end = end
        if self.start != '' and self.end == '':
                self.end = date.today()
        #print(self.start)
        #print(self.end)
        self.limit=limit
        self.cachetime = cachetime
        self.renew = renew
        self.fields = fields
        #self.haskey = 'no'
        self.exchange = self.symbol.split('.')[-1]
        self.underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
        
        
        #self.MARKET_DATA_PATH = '~/.byquant/%s/' % (self.ktype)
        self.MARKET_DATA_PATH = '.byquant/%s/' % (self.ktype)
        self.filedir = self.MARKET_DATA_PATH + '%s/%s/' % (self.exchange, self.freq)
        dir_path = Path(self.filedir)
        dir_path.mkdir(parents=True, exist_ok=True)
        self.filepath = self.filedir + '%s.csv' % (self.symbol.replace('.' + self.exchange, ''))
        

        self.underlying_ex = self.underlying
        if self.exchange == 'SSE':
            self.underlying_ex = self.underlying_ex.replace('SH', '') + '.SH'
        elif self.exchange == 'SZSE':
            self.underlying_ex = self.underlying_ex.replace('SZ', '') + '.SZ'
        elif self.exchange == 'BSE':
            self.underlying_ex = self.underlying_ex.replace('BJ', '') + '.BJ'
        elif self.exchange == 'HKEX':
            self.underlying_ex = self.underlying_ex.replace('HK', '') + '.HK'
        
        self.source = source
        self.token = token
        self.tushareKey = 'Your  API  Token'

        # print(self.tushareKey)
        # print(self.market)

    def quote(self):

        file_path = Path(self.filepath)
        if not file_path.exists() or self.cachetime == 0:
            result = self.createQuote()
        #elif self.haskey == 'no':
        #    result = self.createQuote()
        elif self.renew == False:
            result = self.readCSV()
        else:
            stat = file_path.stat()
            fileTime = stat.st_ctime

            #fileTime = int(os.path.getmtime(self.filepath))
            nowTime = time.time()
            expireTime = fileTime + self.cachetime
            if nowTime > expireTime:
                result = self.updateQuote()
            else:
                result = self.readCSV()

        result = self.filterQuote(result)

        return result
    
    def filterQuote(self, data):
        
        data.rename(columns={"quote_time": "datetime"}, inplace=True)
        data['datetime'] = pd.to_datetime(data['datetime'])
        data = data.sort_values('datetime')  # 数据顺序排列

        if self.start != '':
            #print(pd.to_datetime(self.start, format='%Y-%m-%d'))
            #print(pd.to_datetime(data['datetime'], format='%Y%m%d%H%M%S%f'))
            
            if self.freq == '1d':
                data = data[(data['datetime'] >= pd.to_datetime(self.start)) & (data['datetime'] <= pd.to_datetime(self.end))]
            
        if self.limit > 0:
            data = data.tail(self.limit)
        
        if self.fields:
            data = data[self.fields]
        #else:
        #    data = data[['datetime','open','high','low','close','volume']]
        data.set_index('datetime', inplace=True)
        return data
        
        
        

    def quoteTimeSort(self):

        result = self.quote()
        #result.rename(columns={"quote_time": "datetime"}, inplace=True)
        #result['datetime'] = pd.to_datetime(result['datetime'])
        # print(df)
        #result = result.sort_values('datetime')  # 数据顺序排列
        # print(df)

        return result
        
    def checkYfinance(self):
        try:
            data = yf.download('AAPL', start='2023-01-01', end='2023-01-30',progress=False)
            if len(data) > 0:
                return True
            else:
                return False
        except Exception as e:
            return False

    def signal(self):
        self.haskey = self.checkKey()
        if not os.path.exists(self.filepath):
            result = self.createSignal()
        elif self.haskey == 'no':
            result = self.createSignal()
        else:
            result = self.readCSV()
        return result

    def createQuote(self):
        df = {}
        try:

            #print(self.exchange)
            #print(self.source)
            if self.exchange in ['SSE', 'SZSE', 'BSE', 'AMEX', 'ARCA', 'BATS', 'HKEX', 'NASDAQ', 'NYSE', 'OTC',
                                 'NYSEARCA', 'FTXU', 'CBSE', 'GNSS', 'ERSX']:
                # print('yahoo_0')
                if (self.source == 'akshare' or self.source == 'ak' ) and self.freq == '1d':
                    df = self.akshareStockApi()
                elif (self.source == 'baostock' or self.source == 'bs' ):
                    df = self.baostockStockApi()
                elif self.source == 'tushare' or self.source == 'ts':
                    df = self.tushareStockApi()
                elif self.exchange in ['SSE', 'SZSE', 'BSE'] and not self.checkYfinance():
                    df = self.baostockStockApi()
                else:
                    
                    df = self.yahooApi()
    
                    if len(df) < 10:
                        if self.exchange in ['SSE', 'SZSE', 'BSE']:
                            # print('tushare_cn')
                            #if self.market == 'FUND':
                            #    df = self.tushareFundApi()
                            #elif self.market == 'STOCK':
                            #    df = self.tushareStockApi()
                            if self.token != '':
                                df = self.tushareStockApi()
                            elif self.freq == '1d':
                                df = self.akshareStockApi()
                            else:
                                pass
    
    
                        elif self.exchange in ['AMEX', 'ARCA', 'BATS', 'NASDAQ', 'NYSE', 'OTC', 'NYSEARCA', 'FTXU', 'CBSE',
                                               'GNSS', 'ERSX']:
    
                            # print('alpaca_1')
                            if self.token != '':
                                df = self.tushareStockApi()
                            else:
                                pass

                        elif self.exchange in ['HKEX']:
                            if self.token != '':
                                df = self.tushareHKStockApi()  # 没有权限
                            else:
                                pass
            elif self.exchange in ['SSEf', 'SZSEf']:
                # print('yahoo_0')
                if (self.source == 'akshare' or self.source == 'ak' ) and self.freq == '1d':
                    df = self.akshareFundApi()
                #elif (self.source == 'baostock' or self.source == 'bs' ):
                #    df = self.baostockStockApi()
                #elif self.source == 'tushare' or self.source == 'ts':
                #    df = self.tushareStockApi()
                #elif self.exchange in ['SSE', 'SZSE', 'BSE'] and not self.checkYfinance():
                #    df = self.baostockStockApi()
                else:
                    
                    if self.exchange in ['SSEf', 'SZSEf']:
                        # print('tushare_cn')
                        df = self.akshareFundApi()


                    elif self.exchange in ['AMEX', 'ARCA', 'BATS', 'NASDAQ', 'NYSE', 'OTC', 'NYSEARCA', 'FTXU', 'CBSE',
                                           'GNSS', 'ERSX']:

                        # print('alpaca_1')

                        df = self.tushareStockApi()
                    elif self.exchange in ['HKEX']:
                        # print('tushare_hk')
                        df = self.tushareHKStockApi()  # 没有权限
                            
                    else:
                        df = self.yahooApi()
                        


            elif self.exchange == 'ALPACA':
                df = self.alpacaCryptoApi()

            else:
                df = self.ccxtApi()

            if len(df) > 0 and (self.cachetime > 0 or self.renew == True):
                self.saveCSV(df)



        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def yahooApi(self):
        df = {}
        try:
            if self.freq == 'D' or self.freq == '1d':
                periodlUS = '10y'
                intervalUS = '1d'
            elif self.freq == '1min' or self.freq == '1m':
                periodlUS = '7d'
                intervalUS = '1m'
            elif self.freq == '5min' or self.freq == '5m':
                periodlUS = '60d'
                intervalUS = '5m'
            elif self.freq == '15min':
                periodlUS = '60d'
                intervalUS = '15m'
            elif self.freq == '30min':
                periodlUS = '60d'
                intervalUS = '30m'
            elif self.freq == '60min' or self.freq == '1h':
                periodlUS = '1y'
                intervalUS = '1h'
            elif self.freq == 'W':
                periodlUS = '1y'
                intervalUS = '1wk'
            elif self.freq == 'M':
                periodlUS = '1y'
                intervalUS = '1mo'

            self.underlying_ex = self.underlying_ex.replace('.SH', '.SS')
            dfTemp = yf.download(  # or pdr.get_data_yahoo(...
                    tickers=self.underlying_ex,  # tickers list or string as well
                    period=periodlUS,
                    # use "period" instead of start/end # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max# (optional, default is '1mo')
                    interval=intervalUS,
                    # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo  # fetch data by interval (including intraday if period < 60 days) # (optional, default is '1d')
                    ignore_tz=False,
                    # Whether to ignore timezone when aligning ticker data from # different timezones. Default is False.
                    group_by='ticker',  # group by ticker (to access via data['SPY']) # (optional, default is 'column')
                    auto_adjust=True,  # adjust all OHLC automatically # (optional, default is False)
                    repair=False,  # attempt repair of missing data or currency mixups e.g. $/cents
                    prepost=False,  # download pre/post regular market hours data # (optional, default is False)
                    threads=True,
                    # use threads for mass downloading? (True/False/Integer) # (optional, default is True)
                    progress=False,
                    proxy=None  # proxy URL scheme use use when downloading?# (optional, default is None)
                )
            dfTemp.reset_index(drop=False, inplace=True)
            if self.freq == 'D' or self.freq == '1d' or self.freq == 'W' or self.freq == 'M':
                dfTemp['Datetime'] = dfTemp['Date']
                dfTemp['Datetime'] = dfTemp['Datetime'].dt.tz_convert('UTC')
                dfTemp['Datetime'] = dfTemp['Datetime'].dt.tz_localize(None)
            # dfTemp['symbol'] = self.symbol

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['Datetime']
            df['open'] = dfTemp['Open']
            df['high'] = dfTemp['High']
            df['low'] = dfTemp['Low']
            df['close'] = dfTemp['Close']
            df['volume'] = dfTemp['Volume']




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def tushareStockApi(self):
        df = {}
        try:
            pro = ts.pro_api(self.token)
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
            if self.exchange == 'SSE':
                self.underlying_ex = self.underlying_ex.replace('.SS', '.SH')
            # 拉取数据

            """if self.start == '':
                self.start = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                self.start = date.today() + timedelta(days=-15)
            if self.end == '':
                self.end = date.today()"""


            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                startDay = date.today() + timedelta(days=-15)
            startDay = format(startDay.strftime('%Y%m%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y%m%d'))
            # print(startDay)
            # print(toDay)
            # print(self.underlying)
            dfTemp = pro.daily(**{
                "ts_code": self.underlying_ex, "trade_date": "", "start_date": startDay, "end_date": toDay,
                "offset": "",
                "limit": ""
            }, fields=[
                "ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol",
                "amount"
            ])
            # print(dfTemp)

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['trade_date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['vol']




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def tushareHKStockApi(self):
        df = {}
        try:
            pro = ts.pro_api(self.token)
            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                startDay = date.today() + timedelta(days=-15)
            startDay = format(startDay.strftime('%Y%m%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y%m%d'))
            # print(startDay)
            # print(toDay)
            # print(self.underlying)
            dfTemp = pro.hk_daily(**{
                "ts_code": self.underlying, "trade_date": "", "start_date": startDay, "end_date": toDay, "offset": "",
                "limit": ""
            }, fields=[
                "ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol",
                "amount"
            ])
            # print(dfTemp)

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['trade_date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['vol']




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df
        
    def akshareStockApi(self):
        df = {}
        try:
            #pro = ts.pro_api(self.tushareKey)
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
            #if self.exchange == 'SSE':
            #    self.underlying_ex = self.underlying_ex.replace('.SS', '.SH')
            
            self.underlying_num = self.underlying_ex.replace('.SH', '').replace('.SZ', '').replace('.SZ', '')
            



            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                startDay = date.today() + timedelta(days=-15)
            startDay = format(startDay.strftime('%Y%m%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y%m%d'))

            #print(self.underlying_num)
            #print(startDay)
            #print(toDay)
            
            dfTemp = ak.stock_zh_a_hist(symbol=self.underlying_num, period="daily", start_date=startDay, end_date=toDay, adjust="")
            
            dfTemp.rename(columns={"日期": "trade_date"}, inplace=True)
            dfTemp.rename(columns={"开盘": "open"}, inplace=True)
            dfTemp.rename(columns={"收盘": "close"}, inplace=True)
            dfTemp.rename(columns={"最高": "high"}, inplace=True)
            dfTemp.rename(columns={"最低": "low"}, inplace=True)
            dfTemp.rename(columns={"成交量": "vol"}, inplace=True)

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['trade_date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['vol']
            
            #print(df)




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df
        
    def akshareFundApi(self):
        df = {}
        try:
            #pro = ts.pro_api(self.tushareKey)
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
            #if self.exchange == 'SSE':
            #    self.underlying_ex = self.underlying_ex.replace('.SS', '.SH')
            
            self.underlying_num = self.underlying_ex.replace('.SH', '').replace('.SZ', '').replace('.SZ', '')
            



            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                startDay = date.today() + timedelta(days=-15)
            startDay = format(startDay.strftime('%Y%m%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y%m%d'))

            #print(self.underlying_num)
            #print(startDay)
            #print(toDay)
            
            #dfTemp = ak.stock_zh_a_hist(symbol=self.underlying_num, period="daily", start_date=startDay, end_date=toDay, adjust="")
            #ak.fund_etf_hist_sina(symbol="sz169103")
            #print(self.underlying)
            dfTemp = ak.fund_etf_hist_sina(symbol=self.underlying.lower())
            
            #dfTemp = ak.fund_etf_hist_em(symbol=self.underlying_num, period="daily", start_date=startDay, end_date=toDay, adjust="")
            
            if(len(dfTemp)<10):
                dfTemp = ak.fund_etf_hist_em(symbol=self.underlying_num, period="daily", start_date=startDay, end_date=toDay, adjust="")
            
            if(len(dfTemp)<10):
                dfTemp = ak.fund_lof_hist_em(symbol=self.underlying_num, period="daily", start_date=startDay, end_date=toDay, adjust="")
            
            #print(dfTemp)
#print(fund_etf_hist_em_df)

            
            dfTemp.rename(columns={"date": "trade_date"}, inplace=True)
            #dfTemp.rename(columns={"开盘": "open"}, inplace=True)
            #dfTemp.rename(columns={"收盘": "close"}, inplace=True)
            #dfTemp.rename(columns={"最高": "high"}, inplace=True)
            #dfTemp.rename(columns={"最低": "low"}, inplace=True)
            #dfTemp.rename(columns={"成交量": "vol"}, inplace=True)

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['trade_date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['volume']
            
            #print(df)




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df
        
    def baostockStockApi(self):
        df = {}
        try:

            if self.exchange == 'SSE':
                self.underlying_ex = self.underlying_ex.replace('.SS', '.SH')
                
            apiFreq = self.freq
            apiColumns = ''


            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                print('Min Period support than 5min')
            #elif self.freq == '5m':
            #    startDay = date.today() + timedelta(days=-30)
            elif self.freq == '1d':
                startDay = date.today() + timedelta(days=-30)
                apiFreq = 'd'
                apiColumns = 'date,open,high,low,close,volume'
            #elif self.freq == '5m':
            #    startDay = date.today() + timedelta(days=-30)
            elif self.freq == '5m':
                startDay = date.today() + timedelta(days=-30)
                apiFreq = '5'
                apiColumns = 'time,open,high,low,close,volume'
                
            startDay = format(startDay.strftime('%Y-%m-%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y-%m-%d'))

            #### 登陆系统 ####
            lg = bs.login()
            # 显示登陆返回信息
            #print('login respond error_code:'+lg.error_code)
            #print('login respond  error_msg:'+lg.error_msg)
            
            #### 获取沪深A股历史K线数据 ####
            # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
            # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
            # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
            rs = bs.query_history_k_data_plus(self.underlying_ex,apiColumns,
                start_date=startDay, end_date=toDay,
                frequency=apiFreq, adjustflag="3")

            #### 打印结果集 ####
            data_list  = []
            while (rs.error_code == '0') & rs.next():
                # 获取一条记录，将记录合并在一起
                data_list .append(rs.get_row_data())
            dfTemp = pd.DataFrame(data_list , columns=rs.fields)
            if self.freq == '5m':
                #datetime_obj = datetime.strptime(dfTemp['time'], "%Y%m%d%H%M%S%f")
                dfTemp['date'] = pd.to_datetime(dfTemp['time'], format='%Y%m%d%H%M%S%f')
            #print(dfTemp)

            
            #### 登出系统 ####
            bs.logout()


            df = pd.DataFrame()
            df['quote_time'] = dfTemp['date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['volume']
            
            #print(df)




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def tushareFundApi(self):
        df = {}
        try:
            pro = ts.pro_api(self.token)
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
            if self.exchange == 'SSE':
                self.underlying = self.underlying.replace('.SS', '.SH')
            # 拉取数据

            startDay = date.today() + timedelta(days=-1000)
            if self.freq == '1m':
                startDay = date.today() + timedelta(days=-15)
            startDay = format(startDay.strftime('%Y%m%d'))
            # print(LastWeek)
            toDay = date.today()
            toDay = format(toDay.strftime('%Y%m%d'))
            # print(startDay)
            # print(toDay)
            # print(self.underlying)
            dfTemp = pro.fund_daily(**{
                "ts_code": self.underlying, "trade_date": "", "start_date": startDay, "end_date": toDay, "offset": "",
                "limit": ""
            }, fields=[
                "ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol",
                "amount"
            ])
            # print(dfTemp)

            df = pd.DataFrame()
            df['quote_time'] = dfTemp['trade_date']
            df['open'] = dfTemp['open']
            df['high'] = dfTemp['high']
            df['low'] = dfTemp['low']
            df['close'] = dfTemp['close']
            df['volume'] = dfTemp['vol']




        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def ccxtApi(self):
        df = {}
        try:
            # getExchange = tawCCXT(self.exchange)
            # getExchange = byquant.getExchange(self.exchange)
            getExchange = exchange.get(self.exchange)
            getExchange.load_markets()

            strFreq = self.freq
            if strFreq == '1min':
                strFreq = '1m'
            elif strFreq == 'H':
                strFreq = '1h'
            elif strFreq == 'D':
                strFreq = '1d'
            elif strFreq == 'M':
                strFreq = '1M'
            elif strFreq == 'Y':
                strFreq = '1y'
            #limit = 1000
            
            #since_date = datetime.strptime(self.start, "%Y-%m-%d")
            # 将 datetime 对象转换为毫秒级时间戳
            #since_timestamp = int(since_date.timestamp() * 1000)

            if getExchange.has['fetchOHLCV']:
                # time.sleep(getExchange.rateLimit / 1000)  # time.sleep wants seconds
                quotes = []
                df = {}
                # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange, '')
                #ohlcvData = getExchange.fetchOHLCV(self.underlying, timeframe=strFreq, since =since_timestamp, limit=self.limit, params={})
                ohlcvData = getExchange.fetchOHLCV(self.underlying, timeframe=strFreq, limit=self.limit, params={})

                for ohlcv in ohlcvData:
                    quote = {}
                    quoteTime = time.localtime(ohlcv[0] / 1000)
                    quote_time = time.strftime("%Y-%m-%d %H:%M:%S", quoteTime)
                    quote['quote_time'] = quote_time
                    quote['open'] = ohlcv[1]
                    quote['high'] = ohlcv[2]
                    quote['low'] = ohlcv[3]
                    quote['close'] = ohlcv[4]
                    quote['volume'] = ohlcv[5]
                    quotes.append(quote)

                # df['open'] = df['ohlcv'][0]
                df = pd.DataFrame(quotes)





        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def alpacaCryptoApi(self):
        df = {}
        try:
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange.upper(), '')
            # print([freq])
            # toDay = date.today()
            # toDay = format(toDay.strftime('%Y-%m-%d'))
            client = CryptoHistoricalDataClient("Key", "KeyI")
            # strFreq = freq
            if self.freq == '1m':
                # strFreq = '1m'
                startTime = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d %H:%M:%S")
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Minute,
                    start=datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                )
            elif self.freq == '1h':
                startTime = (date.today() + timedelta(days=-90)).strftime("%Y-%m-%d %H:%M:%S")
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Hour,
                    start=datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                )
            elif self.freq == '1d':
                # strFreq = '1d'
                startTime = (date.today() + timedelta(days=-1000)).strftime("%Y-%m-%d")
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Day,
                    start=datetime.strptime(startTime, '%Y-%m-%d')
                )
            else:
                startTime = (date.today() + timedelta(days=-1000)).strftime("%Y-%m-%d")
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Day,
                    start=datetime.strptime(startTime, '%Y-%m-%d')
                )

            barsInfo = client.get_crypto_bars(request_params)
            barsData = barsInfo.data
            # print(type(barData))
            barsList = barsData[self.underlying]

            # print(barsList)
            barList = []
            for bars in barsList:
                barDict = dict(bars)
                barTemp = {}
                barTemp['quote_time'] = str(barDict['timestamp'])
                barTemp['open'] = float(barDict['open'])
                barTemp['high'] = str(barDict['high'])
                barTemp['low'] = float(barDict['low'])
                barTemp['close'] = float(barDict['close'])
                barTemp['volume'] = float(barDict['volume'])
                # barTemp['trade_count'] = float(barDict['trade_count'])
                barTemp['vwap'] = str(barDict['vwap'])

                # print(tickTemp)
                barList.append(barTemp)

            dfTemp = pd.DataFrame(barList)
            # dfTemp['symbol'] = symbol
            df = dfTemp.tail(1000)
            # print(df)





        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def alpacaStockApi(self):
        df = {}
        try:
            # underlying = self.symbol.replace('~', '/').replace('$', ':').replace('.' + self.exchange.upper(), '')
            # print([freq])
            # toDay = date.today()
            # toDay = format(toDay.strftime('%Y-%m-%d'))
            client = StockHistoricalDataClient("KEY", "KEYI")
            # strFreq = freq
            if self.freq == '1m':
                # strFreq = '1m'
                startTime = (date.today() + timedelta(days=-7)).strftime("%Y-%m-%d %H:%M:%S")
                request_params = StockBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Minute,
                    start=datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                )
            elif self.freq == '1h':
                startTime = (date.today() + timedelta(days=-90)).strftime("%Y-%m-%d %H:%M:%S")
                request_params = StockBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Hour,
                    start=datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                )
            elif self.freq == '1d':
                # strFreq = '1d'
                startTime = (date.today() + timedelta(days=-1000)).strftime("%Y-%m-%d")
                request_params = StockBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Day,
                    start=datetime.strptime(startTime, '%Y-%m-%d')
                )
            else:
                startTime = (date.today() + timedelta(days=-1000)).strftime("%Y-%m-%d")
                request_params = StockBarsRequest(
                    symbol_or_symbols=[self.underlying],
                    timeframe=TimeFrame.Day,
                    start=datetime.strptime(startTime, '%Y-%m-%d')
                )

            barsInfo = client.get_stock_bars(request_params)
            barsData = barsInfo.data
            # print(type(barData))
            barsList = barsData[self.underlying]

            # print(barsList)
            barList = []
            for bars in barsList:
                barDict = dict(bars)
                barTemp = {}
                barTemp['quote_time'] = str(barDict['timestamp'])
                barTemp['open'] = float(barDict['open'])
                barTemp['high'] = str(barDict['high'])
                barTemp['low'] = float(barDict['low'])
                barTemp['close'] = float(barDict['close'])
                barTemp['volume'] = float(barDict['volume'])
                # barTemp['trade_count'] = float(barDict['trade_count'])
                barTemp['vwap'] = str(barDict['vwap'])

                # print(tickTemp)
                barList.append(barTemp)

            dfTemp = pd.DataFrame(barList)
            # dfTemp['symbol'] = symbol
            df = dfTemp.tail(1000)
            # print(df)





        except Exception as e:
            print(e.args)
            pass

        ###########

        return df

    def saveHDF(self, data):  # 将放弃
        result = False
        df = data
        try:

            if len(df) > 0:
                result = df
                df.fillna("0", inplace=True)
                df.sort_values(by="quote_time", ascending=False, inplace=True)

                filedir = self.MARKET_DATA_PATH + '%s' % (self.exchange)
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                filepath = self.MARKET_DATA_PATH + '%s/%s.hdf' % (self.exchange, self.symbol)
                df.to_hdf(filepath, mode='a', key='quote_%s' % (self.freq), complevel=9, complib='blosc',
                          format='table')
                result = True



        except Exception as e:
            print(e.args)
            pass

        ###########

        return result

    def saveCSV(self, data):
        result = False
        df = data
        try:

            if len(df) > 0:
                #result = df
                #df.fillna("0", inplace=True)
                df.sort_values(by="quote_time", ascending=True, inplace=True)
                df.to_csv(self.filepath, index=False)
                """filepath = self.MARKET_DATA_PATH + '%s/%s.hdf' % (self.exchange, self.symbol)
                df.to_hdf(filepath, mode='a', key='quote_%s' % (self.freq), complevel=9, complib='blosc',
                          format='table')"""
                result = True



        except Exception as e:
            print(e.args)
            pass

        ###########

        return result

    def createSignal(self):
        result = tawSignal.autoStrategy(self.symbol, self.market, self.freq, self.limit, self.offset, self.cachetime)
        return result

    def updateQuote(self):
        result = self.createQuote()  ##暂定
        return result

    """def read(self):
        readHdf = pd.read_hdf(self.filepath, key='%s_%s' % (self.ktype, self.freq),mode='a')
        result = pd.DataFrame(readHdf)
        return result"""

    def readHDF(self):  # 将放弃
        readResult = pd.read_hdf(self.filepath, key='%s_%s' % (self.ktype, self.freq))
        self.result = pd.DataFrame(readResult)
        return self.result

    def readCSV(self):
        readResult = pd.read_csv(self.filepath)
        self.result = pd.DataFrame(readResult)
        return self.result

    def checkKey(self):
        result = 'no'
        if os.path.exists(self.filepath):
            keyName = '%s_%s' % (self.ktype, self.freq)
            getStore = pd.HDFStore(self.filepath, 'a')
            keyArr = getStore.keys()
            getStore.close()
            if keyName in keyArr:
                result = 'yes'
        return result

    def getSymbolInfo(self):
        result = {}
        result['market'] = 'CRYPTO'
        # try:
        #    result = marketModels.Underlying.objects.filter(symbol = self.symbol).values('market')
        # except Exception as e:
        #    print(e.args)
        #    pass
        return result







