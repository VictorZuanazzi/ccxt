# -*- coding: utf-8 -*-
"""
Created on Friday Jun 29 07:53:23 2018

@author: VICTZUAN

ccxt documentation: https://github.com/ccxt/ccxt/wiki/Manual
"""

import ccxt
import time

DELAY = 1 #seconds.
FEE = 0.0026

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
    Ex.: 
        >>> coins_of_interest = ['BTC']
        >>> trair = ['ETC/ETH','BTC/ETH','ETC/BTC']
        >>> trair = sort_pairs(trair, coins_of_interest)
        >>> trair
        >>> ['BTC/ETH','ETC/ETH','ETC/BTC']
    
    '''
    
    trair
    for i in range(len(coins_of_interest)):
        if not coins_of_interest[i] in trair[i][0]:
            aux_pair = trair[i][0]
            trair[i][0] = trair[i][1]
            trair[i][1] = aux_pair 
        elif not coins_of_interest[i] in trair[i][2]:
            aux_pair = trair[i][2]
            trair[i][2] = trair[i][1]
            trair[i][1] = aux_pair
            
    return trair

def take_unbalance(exchange, sequence):
    '''Trades the three pairs in the profitable sequence.
    '''
    
    pass


def find_unbalance(exchange, pairs, profit_coin):
    '''Finds unbalances when trading 3 currencies in an especific direction.
    
    BHC/BTC BCH/EUR BTC/EUR
        
    '''
    trade = [[-1,-1],[-1,1],[-1,-1]]
    
    ask = ['','','']
    bid = ['','','']
    
    #load the relevant orderbook information:
    for i in range(len(pairs)):
        ask[i] = exchange.fetch_order_book(pairs[i])['asks'][0] #price to buy
        bid[i] = exchange.fetch_order_book(pairs[i])['bids'][0] #price to sell

    
    unbalance_factor = [0,0] # stores the unbalance of both paths.
    profit_coin_position_start = pairs[0].find(profit_coin)
    profit_coin_position_end = pairs[2].find(profit_coin)
    if profit_coin_position_start > 3:
        if profit_coin_position_end < 3:
            #format 1: ['xxx/profit_coin', 'xxx/yyy', 'profit_coin/yyy']
            print('format 1')
            unbalance_factor[0] = bid[1][0]/(ask[0][0]*ask[2][0])
            if unbalance_factor[0] > 1+3*FEE:
                volume_restrictor = min(ask[0][0]*ask[0][1], bid[1][1]*ask[0][0], ask[2][1]) 
                print ("Volume (" + profit_coin + "): ", volume_restrictor)
                
            unbalance_factor[1] = bid[2][0]*bid[0][0]/(ask[1][0])
            if unbalance_factor[1] > 1+3*FEE:
                volume_restrictor = min(bid[0][0]*bid[0][1], ask[1][1]*bid[0][0], bid[2][1]) 
                print ("Volume (" + profit_coin + "): ", volume_restrictor)
        else:
            #format 2: ['xxx/profit_coin', 'xxx/yyy', 'yyy/profit_coin']
            print('format 2')
            unbalance_factor[0] = bid[1][0]*bid[2][0]/(ask[0][0])
            unbalance_factor[1] = bid[0][0]/(ask[1][0]*ask[2][0])
    elif profit_coin_position_start < 3:
        if profit_coin_position_end < 3:
            #format 3: ['profit_coin/xxx', 'xxx/yyy', 'profit_coin/yyy']
            unbalance_factor[0] = bid[0][0]*bid[1][0]/(ask[2][0])
            unbalance_factor[1] = bid[2][0]/(ask[1][0]*ask[0][0])
        else:
            #format 4: ['profit_coin/xxx', 'xxx/yyy', 'yyy/profit_coin']
            #This is very unlikely to happen, but just in case.
            unbalance_factor[0] = bid[0][0]*bid[1][0]*bid[2][0]
            unbalance_factor[1] = 1/(ask[0][0]*ask[1][0]*ask[2][0])
    
    print('trair: ', pairs, '## protif coin:', profit_coin)
    print('unbalance factor 0:', unbalance_factor[0],
          'unbalance factor 1:', unbalance_factor[1])
    
        
    return trade
    
def main():
    # 1- Load exchange.
    exchange = ccxt.kraken()
    market = exchange.load_markets()
    
    # 2- Find possible tri-pairs (trairs) within the exchange.
    trair = find_trairs(exchange)
    #print (trair)
    # Define the coin of interest for each trair.
    # The coin of interest is the coin we want to profit on with the trade.
    # define_coins_of_insterest, set one coin of interest for each trair.
    interesting_coins = ['BTC', 'EUR', 'ETH']
    coins_of_interest = define_coins_of_interest(exchange, trair, interesting_coins)
    #print(coins_of_interest)
    trair = sort_pairs(trair, coins_of_interest)
    #print (trair)
    # 3. Seek for unbalances in the trairs.
    try:
        while True:
            for t in range(len(trair)):
                unbalance = find_unbalance(exchange, trair[t], coins_of_interest[t])
                time.sleep(DELAY) 
    except KeyboardInterrupt:
        pass
       
    # 4. Trade profitable unbalances.
    
    input ('End of the application, press enter to finish')


main()

                    
    


