# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 17:46:10 2018

@author: victzuan
"""

import ccxt

#print (ccxt.exchanges)
print('--------------- LOAD KRAKEN --------------')
kraken = ccxt.kraken({
    'apiKey': 'JVfh8ajAL357p1CKput2btQRgy9crL2naMZf0zTWRtPRsUwcsi0nG/0r',
    'secret': 'ptmYjw0k0i6M9C7517TRqY+Gve+Ltvn6Q1yod6QteoRC5Y4tW0Cp42HPf/wyxgR3u2fxsuXmMOuLJxQU3KE2ag==',
})
print('--------------- MARKETS --------------')
kraken_markets = kraken.load_markets()
print(kraken.id, kraken_markets)


print('--------------- ORDER BOOK --------------')
print(kraken.fetch_order_book(kraken.symbols[0]))
print(kraken.fetch_ticker('BTC/EUR'))
print(kraken.fetch_balance())

