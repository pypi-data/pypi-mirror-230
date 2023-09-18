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
#global SIGNAL_LONG = bt.SIGNAL_LONG
#global SIGNAL_SHORT = bt.SIGNAL_SHORT
class Strategy(bt.Strategy):
    
    def log(self, txt, dt=None): #log信息的功能
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def __init__(self):
        super().__init__()
    
    def notifyOrder(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status == order.Rejected:
            self.log(f"Order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Margin:
            self.log(f"Order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Cancelled:
            self.log(f"Order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Partial:
            self.log(f"Order is partial : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Completed:
            if order.isbuy():
                self.log("Buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                
            elif order.issell():
                self.log("Sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                
            else:  # Sell
                self.log("Close result : close_price : {} , close_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                            
    def notifyTrade(self, trade):
        if trade.isclosed:
            self.log('Closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
        if trade.isopen:
            self.log('Open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))

class Signal(bt.SignalStrategy):
    
    def log(self, txt, dt=None): #log信息的功能
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        super().__init__()
        
    def notifyOrder(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status == order.Rejected:
            self.log(f"Order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Margin:
            self.log(f"Order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Cancelled:
            self.log(f"Order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Partial:
            self.log(f"Order is partial : order_ref:{order.ref}  order_info:{order.info}")
        elif order.status == order.Completed:
            if order.isbuy():
                self.log("Buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                
            elif order.issell():
                self.log("Sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                
            else:  # Sell
                self.log("Close result : close_price : {} , close_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
                            
    def notifyTrade(self, trade):
        if trade.isclosed:
            self.log('Closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
        if trade.isopen:
            self.log('Open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))
        
class Order(bt.Order):

    def __init__(self):
        super().__init__()
        
class Indicator(bt.Indicator):

    def __init__(self):
        super().__init__()