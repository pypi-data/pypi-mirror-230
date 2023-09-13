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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .okx import by_okx                                              
from .ace import by_ace                                              
from .alpaca import by_alpaca                                        
from .ascendex import by_ascendex                                    
from .bequant import by_bequant                                      
from .bigone import by_bigone                                        
from .binance import by_binance                                      
from .binancecoinm import by_binancecoinm                            
from .binanceus import by_binanceus                                  
from .binanceusdm import by_binanceusdm                              
from .bit2c import by_bit2c                                          
from .bitbank import by_bitbank                                      
from .bitbay import by_bitbay                                        
from .bitbns import by_bitbns                                        
from .bitcoincom import by_bitcoincom                                
from .bitfinex import by_bitfinex                                    
from .bitfinex2 import by_bitfinex2                                  
from .bitflyer import by_bitflyer                                    
from .bitforex import by_bitforex                                    
from .bitget import by_bitget                                        
from .bithumb import by_bithumb                                      
from .bitmart import by_bitmart                                      
from .bitmex import by_bitmex                                        
from .bitopro import by_bitopro                                      
from .bitpanda import by_bitpanda                                    
from .bitrue import by_bitrue                                        
from .bitso import by_bitso                                          
from .bitstamp import by_bitstamp                                    
from .bitstamp1 import by_bitstamp1                                  
from .bittrex import by_bittrex                                      
from .bitvavo import by_bitvavo                                      
from .bkex import by_bkex                                            
from .bl3p import by_bl3p                                            
from .blockchaincom import by_blockchaincom                          
from .btcalpha import by_btcalpha                                    
from .btcbox import by_btcbox                                        
#from .btcex import by_btcex                                          
from .btcmarkets import by_btcmarkets                                
from .btctradeua import by_btctradeua                                
from .btcturk import by_btcturk                                      
from .bybit import by_bybit                                          
from .cex import by_cex                                              
from .coinbase import by_coinbase                                    
from .coinbaseprime import by_coinbaseprime                          
from .coinbasepro import by_coinbasepro                              
from .coincheck import by_coincheck                                  
from .coinex import by_coinex                                        
from .coinfalcon import by_coinfalcon                                
from .coinmate import by_coinmate                                    
from .coinone import by_coinone                                      
from .coinsph import by_coinsph                                      
from .coinspot import by_coinspot                                    
from .cryptocom import by_cryptocom                                  
from .currencycom import by_currencycom                              
from .delta import by_delta                                          
from .deribit import by_deribit                                      
from .digifinex import by_digifinex                                  
from .exmo import by_exmo                                            
from .fmfwio import by_fmfwio                                        
from .gate import by_gate                                            
from .gateio import by_gateio                                        
from .gemini import by_gemini                                        
from .hitbtc import by_hitbtc                                        
from .hitbtc3 import by_hitbtc3                                      
from .hollaex import by_hollaex                                      
from .huobi import by_huobi                                          
from .huobijp import by_huobijp                                      
from .huobipro import by_huobipro                                    
from .idex import by_idex                                            
from .independentreserve import by_independentreserve                
from .indodax import by_indodax                                      
from .kraken import by_kraken                                        
from .krakenfutures import by_krakenfutures                          
from .kucoin import by_kucoin                                        
from .kucoinfutures import by_kucoinfutures                          
from .kuna import by_kuna                                            
from .latoken import by_latoken                                      
from .lbank import by_lbank                                          
from .lbank2 import by_lbank2                                        
from .luno import by_luno                                            
from .lykke import by_lykke                                          
from .mercado import by_mercado                                      
from .mexc import by_mexc                                            
from .mexc3 import by_mexc3                                          
from .ndax import by_ndax                                            
from .novadax import by_novadax                                      
from .oceanex import by_oceanex                                      
from .okcoin import by_okcoin                                        
from .okex import by_okex                                            
from .okex5 import by_okex5                                          
#from .okx import by_okx                                                Uakeey
from .paymium import by_paymium                                      
from .phemex import by_phemex                                        
from .poloniex import by_poloniex                                    
from .poloniexfutures import by_poloniexfutures                      
from .probit import by_probit                                        
#from .stex import by_stex                                            
from .tidex import by_tidex                                          
from .timex import by_timex                                          
from .tokocrypto import by_tokocrypto                                
from .upbit import by_upbit                                          
from .wavesexchange import by_wavesexchange                          
from .wazirx import by_wazirx                                        
from .whitebit import by_whitebit                                    
from .woo import by_woo                                              
#from .xt import by_xt                                                
from .yobit import by_yobit                                          
from .zaif import by_zaif                                            
from .zonda import by_zonda                                          

#from .buda import by_buda                                            
from .flowbtc import by_flowbtc                                      
#from .itbit import by_itbit                                          
#from .ripio import by_ripio                                          
#from .zb import by_zb                                                


def get(exName):
    #print(exName)
    exName=exName.lower()
    if exName == 'ace': result = by_ace()
    elif exName == 'alpaca': result = by_alpaca()
    elif exName == 'ascendex': result = by_ascendex()
    elif exName == 'bequant': result = by_bequant()
    elif exName == 'bigone': result = by_bigone()
    elif exName == 'binance': result = by_binance()
    elif exName == 'binancecoinm': result = by_binancecoinm()
    elif exName == 'binanceus': result = by_binanceus()
    elif exName == 'binanceusdm': result = by_binanceusdm()
    elif exName == 'bit2c': result = by_bit2c()
    elif exName == 'bitbank': result = by_bitbank()
    elif exName == 'bitbay': result = by_bitbay()
    elif exName == 'bitbns': result = by_bitbns()
    elif exName == 'bitcoincom': result = by_bitcoincom()
    elif exName == 'bitfinex': result = by_bitfinex()
    elif exName == 'bitfinex2': result = by_bitfinex2()
    elif exName == 'bitflyer': result = by_bitflyer()
    elif exName == 'bitforex': result = by_bitforex()
    elif exName == 'bitget': result = by_bitget()
    elif exName == 'bithumb': result = by_bithumb()
    elif exName == 'bitmart': result = by_bitmart()
    elif exName == 'bitmex': result = by_bitmex()
    elif exName == 'bitopro': result = by_bitopro()
    elif exName == 'bitpanda': result = by_bitpanda()
    elif exName == 'bitrue': result = by_bitrue()
    elif exName == 'bitso': result = by_bitso()
    elif exName == 'bitstamp': result = by_bitstamp()
    elif exName == 'bitstamp1': result = by_bitstamp1()
    elif exName == 'bittrex': result = by_bittrex()
    elif exName == 'bitvavo': result = by_bitvavo()
    elif exName == 'bkex': result = by_bkex()
    elif exName == 'bl3p': result = by_bl3p()
    elif exName == 'blockchaincom': result = by_blockchaincom()
    elif exName == 'btcalpha': result = by_btcalpha()
    elif exName == 'btcbox': result = by_btcbox()
    #elif exName == 'btcex': result = by_btcex()
    elif exName == 'btcmarkets': result = by_btcmarkets()
    elif exName == 'btctradeua': result = by_btctradeua()
    elif exName == 'btcturk': result = by_btcturk()
    #elif exName == 'buda': result = by_buda()
    elif exName == 'bybit': result = by_bybit()
    elif exName == 'cex': result = by_cex()
    elif exName == 'coinbase': result = by_coinbase()
    elif exName == 'coinbaseprime': result = by_coinbaseprime()
    elif exName == 'coinbasepro': result = by_coinbasepro()
    elif exName == 'coincheck': result = by_coincheck()
    elif exName == 'coinex': result = by_coinex()
    elif exName == 'coinfalcon': result = by_coinfalcon()
    elif exName == 'coinmate': result = by_coinmate()
    elif exName == 'coinone': result = by_coinone()
    elif exName == 'coinspot': result = by_coinspot()
    elif exName == 'cryptocom': result = by_cryptocom()
    elif exName == 'currencycom': result = by_currencycom()
    elif exName == 'delta': result = by_delta()
    elif exName == 'deribit': result = by_deribit()
    elif exName == 'digifinex': result = by_digifinex()
    elif exName == 'exmo': result = by_exmo()
    elif exName == 'flowbtc': result = by_flowbtc()
    elif exName == 'fmfwio': result = by_fmfwio()
    elif exName == 'gate': result = by_gate()
    elif exName == 'gateio': result = by_gate() #gateio
    elif exName == 'gemini': result = by_gemini()
    elif exName == 'hitbtc': result = by_hitbtc()
    elif exName == 'hitbtc3': result = by_hitbtc3()
    elif exName == 'hollaex': result = by_hollaex()
    elif exName == 'huobi': result = by_huobi()
    elif exName == 'huobijp': result = by_huobijp()
    elif exName == 'huobipro': result = by_huobipro()
    elif exName == 'idex': result = by_idex()
    elif exName == 'independentreserve': result = by_independentreserve()
    elif exName == 'indodax': result = by_indodax()
    #elif exName == 'itbit': result = by_itbit()
    elif exName == 'kraken': result = by_kraken()
    elif exName == 'krakenfutures': result = by_krakenfutures()
    elif exName == 'kucoin': result = by_kucoin()
    elif exName == 'kucoinfutures': result = by_kucoinfutures()
    elif exName == 'kuna': result = by_kuna()
    elif exName == 'latoken': result = by_latoken()
    elif exName == 'lbank': result = by_lbank()
    elif exName == 'lbank2': result = by_lbank2()
    elif exName == 'luno': result = by_luno()
    elif exName == 'lykke': result = by_lykke()
    elif exName == 'mercado': result = by_mercado()
    elif exName == 'mexc': result = by_mexc()
    elif exName == 'mexc3': result = by_mexc3()
    elif exName == 'ndax': result = by_ndax()
    elif exName == 'novadax': result = by_novadax()
    elif exName == 'oceanex': result = by_oceanex()
    elif exName == 'okcoin': result = by_okcoin()
    elif exName == 'okex': result = by_okex()
    elif exName == 'okex5': result = by_okex5()
    elif exName == 'okx': result = by_okx()
    elif exName == 'paymium': result = by_paymium()
    elif exName == 'phemex': result = by_phemex()
    elif exName == 'poloniex': result = by_poloniex()
    elif exName == 'poloniexfutures': result = by_poloniexfutures()
    elif exName == 'probit': result = by_probit()
    #elif exName == 'ripio': result = by_ripio()
#    elif exName == 'stex': result = by_stex()
    elif exName == 'tidex': result = by_tidex()
    elif exName == 'timex': result = by_timex()
    elif exName == 'tokocrypto': result = by_tokocrypto()
    elif exName == 'upbit': result = by_upbit()
    elif exName == 'wavesexchange': result = by_wavesexchange()
    elif exName == 'wazirx': result = by_wazirx()
    elif exName == 'whitebit': result = by_whitebit()
    elif exName == 'woo': result = by_woo()
    elif exName == 'yobit': result = by_yobit()
    elif exName == 'zaif': result = by_zaif()
    #elif exName == 'zb': result = by_zb()
    elif exName == 'zonda': result = by_zonda()
    else:
        print('No %s' % (exName))
    return result


