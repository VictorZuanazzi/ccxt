# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 15:53:23 2018

@author: VICTZUAN

ccxt documentation: https://github.com/ccxt/ccxt/wiki/Manual
"""

import ccxt
import time

DELAY = 1 #seconds.

def find_trairs(exchange):
    ''' Find possible triplece of pairs that can be traded for unbalance.
    
    'ETC/BTC' 'ETC/ETH' 'ETH/BTC'
    'BCH/BTC' 'BCH/EUR' 'BTC/EUR
    
    '''
    exchange_pairs = exchange.symbols #loads all pairs from the exchange.
    pairs = list(filter(lambda x: not '.d' in x, exchange_pairs)) #filters off the darkpool pairs.
    pair = ['', '', '']
    coin = ['', '', '']
    trair = []
    
    #Semi-optimized loop to look for triplece of pairs.
    #Example:['BCH/BTC', 'BCH/EUR', 'BTC/EUR']
    for i in range(len(pairs)-3):
        pair[0] = pairs[i]
        coin[0] = pairs[i][0:3]
        coin[1] = pairs[i][-3:]
        for j in range(i+1, len(pairs)-2):
            if (coin[0] in pairs[j]):
                pair[1] = pairs[j]
                coin[2] = pairs[j][-3:]
                for k in range(j+1, len(pairs)-1):
                    if coin[1] in pairs[k] and coin[2] in pairs[k]:
                        pair[2]= pairs[k]
                        trair.append([pair[0], pair[1], pair[2]])
                        break
    return trair



def main():
    exchange = ccxt.kraken()
    market = exchange.load_markets()
    
    trair = find_trairs(exchange)
    print (trair)
    
    #print (exchange.fetch_order_book('BTC/EUR'))
    #print (exchange.symbols)
    
    
    
    ask = []
    bid = []
    #for i in range


main()

                    
    


