# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 17:46:10 2018

@author: victzuan
"""

import ccxt


exchange = ccxt.kraken()
markets = exchange.load_markets()

#matplotlibmatplotl  inline
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
from datetime import datetime

plt.rcParams['figure.figsize'] = (20,10)

fig = plt.figure()
ax = plt.subplot()

ohlc = [ [x[0] / 1000] + x[1:] for x in exchange.fetch_ohlcv("BTC/USD", '1d')[-30:]]
plt.xticks([x[0] for x in ohlc[::2]], [datetime.utcfromtimestamp(x[0]).strftime("%m/%d") for x in ohlc[::2]])

# ohlc のフォーマットが想定通りじゃなさそう
mpf.candlestick_ohlc(ax, ohlc, width= 4, colorup='g', colordown='r', alpha = 1.0)

ax.grid()
fig.autofmt_xdate()


print (ohlc)