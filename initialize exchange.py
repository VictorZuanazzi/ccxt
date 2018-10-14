# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 23:53:11 2018

@author: VICTZUAN
ccxt documentation: https://github.com/ccxt/ccxt/wiki/Manual
"""

import ccxt
def initiate_exchange():
    exchange = ccxt.okcoinusd () # default id
    okcoin1 = ccxt.okcoinusd ({ 'id': 'okcoin1' })
    okcoin2 = ccxt.okcoinusd ({ 'id': 'okcoin2' })
    id = 'btcchina'
    btcchina = eval ('ccxt.%s ()' % id)
    gdax = getattr (ccxt, 'gdax') ()

def okcoin_example():
    okcoin = ccxt.okcoinusd ()
    markets = okcoin.load_markets ()
    print (okcoin.id, "\n", markets)