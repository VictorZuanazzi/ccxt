# -*- coding: utf-8 -*-
"""
Created on Friday Jun 29 07:53:23 2018

@author: VICTZUAN

ccxt documentation: https://github.com/ccxt/ccxt/wiki/Manual
"""

import ccxt
import time

DELAY = 1 #seconds.

def find_trairs(exchange):
    ''' Find possible triplece of pairs (trairs) that can be traded for unbalance.
    
    Example of trairs:
    'ETC/BTC' 'ETC/ETH' 'ETH/BTC'
    'BCH/BTC' 'BCH/EUR' 'BTC/EUR'
    
    '''
    exchange_pairs = exchange.symbols #loads all pairs from the exchange.
    pairs = list(filter(lambda x: not '.d' in x, exchange_pairs)) #filters off 
    #the darkpool pairs.
    
    pair = ['', '', '']
    coin = ['', '', '']
    trair = []
    
    #Semi-optimized loop to look for triplece of pairs.
    #Example:['BCH/BTC', 'BCH/EUR', 'BTC/EUR']
    for i in range(len(pairs)-3):
        #not all coins are 3 digits long, we must find the slash that separetes
        #each coin in order to have a robust algorithm.
        slash_position = pairs[i].find('/') 
        coin[0] = pairs[i][0:slash_position]
        coin[1] = pairs[i][slash_position+1:]
        for j in range(i+1, len(pairs)-2):
            if (coin[0] in pairs[j]):
                slash_position = pairs[j].find('/') 
                coin[2] = pairs[j][slash_position+1:]
                for k in range(j+1, len(pairs)-1):
                    if coin[1] in pairs[k] and coin[2] in pairs[k]:
                        trair.append([pairs[i], pairs[j], pairs[k]])
                        break
                    
    return trair

def define_coins_of_interest(exchange, trair, interesting_coins = ['BTC', 'EUR', 'ETH']):
    '''
    
        Return a list the same size as trairs with the corresponding coins of 
        interest.
    '''
    #it is necessary to know the currencies of interest.
    coin_of_interest = []
    
    #looks for the most interesting coin of each trair and build a list to store 
    #tehm.
    for p in range(len(trair)):
        coin_of_interest.append('')
        i = 0
        #iterats over the all the interesting_coins until there one in the trair 
        #that is of interest.
        while (coin_of_interest[p] == '') and (i < len(interesting_coins)):
            for j in trair[p]:
                if interesting_coins[i] in j:
                    coin_of_interest[p] = interesting_coins[i]
            i = i+1
    return coin_of_interest

def sort_pairs(trair, coins_of_interest):
    '''Sort pairs so the coin of interest is always in the first and in the 
    last pairs.
    '''
    
    sorted_trair= trair
    for i in range(len(coins_of_interest)):
        if not coins_of_interest[i] in sorted_trair[i][0]:
            sorted_trair[i][0] = trair[i][1]
            sorted_trair[i][1] = trair[i][0]
        elif not coins_of_interest[i] in sorted_trair[i][2]:
            sorted_trair[i][2] = trair[i][1]
            sorted_trair[i][1] = trair[i][2]
            
    return sorted_trair

def find_unbalance(exchange, pairs, profit_coin):
    '''Finds unbalances when trading 3 currencies in an especific direction.
    
    BHC/BTC BCH/EUR BTC/EUR
    
    
    '''
    
    ask = ['','','']
    bid = ['','','']
    
    #load the relevant orderbook information:
    for i in range(len(pairs)):
        ask[i] = exchange.fetch_order_book(pairs[i])['asks'][0]
        bid[i] = exchange.fetch_order_book(pairs[i])['bids'][0]

    
    unbalance_factor = [0,0] # stores the unbalance of both paths.
    #format: ['xxx/profit_coin', 'xxx/yyy', 'profit_coin/yyy']
    unbalance_factor[0] = bid[1]/(ask[0]*ask[2])
    unbalance_factor[1] = bid[2]*bid[0]/(ask[1])
    #format: ['xxx/profit_coin', 'xxx/yyy', 'yyy/profit_coin']
    unbalance_factor[0] = bid[1]*bid[2]/(ask[0])
    unbalance_factor[1] = bid[0]/(ask[1]*ask[2])
    
    
def main():
    # 1- Load exchange.
    exchange = ccxt.kraken()
    market = exchange.load_markets()
    
    # 2- Find possible tri-pairs (trairs) within the exchange.
    trair = find_trairs(exchange)
    print (trair)
    # Define the coin of interest for each trair.
    # The coin of interest is the coin we want to profit on with the trade.
    # define_coins_of_insterest, set one coin of interest for each trair.
    interesting_coins = ['BTC', 'EUR', 'ETH']
    coins_of_interest = define_coins_of_interest(exchange, trair, interesting_coins)
    print(coins_of_interest)
    trair = sort_pairs(trair, coins_of_interest)
    print (trair)
    # 3. Seek for unbalances in the trairs.
    
    # 4. Trade profitable unbalances.
    
    
    
    
    ask = []
    bid = []
    #for i in range


main()

                    
    


