# -*- coding: utf-8 -*-
"""
Created on Friday Jun 29 07:53:23 2018

@author: VICTZUAN

ccxt documentation: https://github.com/ccxt/ccxt/wiki/Manual
"""

import ccxt
import time
import datetime
from collections import Counter
from itertools import combinations, chain

DELAY = 1 #seconds.
FEE = 0.001

def get_time_stamp():
    return datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

def parse_pair(raw_pair):
    return raw_pair.split('/')

def wait(delay = DELAY):
    time.sleep(DELAY)

def is_trair(trair_candidate):
    # assuming that all currencies appear twice means we have a trair
    currency_counts = Counter(chain.from_iterable(trair_candidate))
    return set(currency_counts.values()) == {2}

def format_trairs(u_trair):
    '''fortmat the trairs to the correct format. List of List of str.
    
    input:
        u_trair: trairs in the format List of Tuples of list of strings.
        eg.:[(['ABT','BTC'],['ABT',ETH'],['ETH','BTC])]
    output:
        trair: trais in the format List of list of str.
        ['ABT/BTC', 'ABT/ETH', 'ETH/BTC']   
    '''
    trair= [] #stores the trairs in the correct format.
    for one_trair in u_trair:
        t_trair = [] #temporary trair. 
        for one_pair in one_trair:
            t_trair.append(one_pair[0]+'/'+one_pair[1])
        trair.append(t_trair)
    return trair

def find_trairs(exchange):
    ''' Find possible triplece of pairs (trairs) that can be traded for unbalance.
    
    Example of trairs:
    'ETC/BTC' 'ETC/ETH' 'ETH/BTC'
    'BCH/BTC' 'BCH/EUR' 'BTC/EUR'
    
    '''
    exchange_pairs = exchange.symbols #loads all pairs from the exchange.
    raw_pairs = list(filter(lambda x: not '.d' in x, exchange_pairs))

    pairs = map(parse_pair, raw_pairs)
    trair_candidates = combinations(pairs, r=3)
    #filter the actual trairs from all trair_candidates
    u_trair = list(filter(is_trair,trair_candidates)) #unformated trairs.
    trair = format_trairs(u_trair) #formats the trairs to list of list os strings.
    
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
    
    ask = ['','','']
    bid = ['','','']
    
    #load the relevant orderbook information:
    try:
        for i in range(len(pairs)):
            ask[i] = exchange.fetch_order_book(pairs[i])['asks'][0] #price to buy
            bid[i] = exchange.fetch_order_book(pairs[i])['bids'][0] #price to sell
    except ccxt.RequestTimeout:
        print('Pairs: ', pairs, 'Time out.')
        wait()
        return False

    
    unbalance_factor = [0,0] # stores the unbalance of both paths.
    profit_coin_position_start = pairs[0].find(profit_coin)
    profit_coin_position_end = pairs[2].find(profit_coin)
    if profit_coin_position_start > 1:
        if profit_coin_position_end < 1:
            #format 1: ['xxx/profit_coin', 'xxx/yyy', 'profit_coin/yyy']
            print('format 1')
            unbalance_factor[0] = bid[1][0]/(ask[0][0]*ask[2][0])
            if unbalance_factor[0] > 1 +3*FEE:
                volume_restrictor = min(ask[0][0]*ask[0][1], bid[1][1]*ask[0][0], ask[2][1])
                good_trade = {
                        'profit_coin': profit_coin, 
                        'trair': pairs, 
                        'Unbalance factor': unbalance_factor[0],
                        'Volume': volume_restrictor,
                        'Sequence': 0,
                        'Time Stamp': get_time_stamp()
                        }
                print (good_trade)
                return good_trade
            unbalance_factor[1] = bid[2][0]*bid[0][0]/(ask[1][0])
            if unbalance_factor[1] > 1 +3*FEE:
                volume_restrictor = min(bid[0][0]*bid[0][1], ask[1][1]*bid[0][0], bid[2][1]) 
                good_trade={
                        'profit_coin': profit_coin, 
                        'trair': pairs, 
                        'Unbalance factor': unbalance_factor[1],
                        'Volume': volume_restrictor,
                        'Sequence': 1,
                        'Time Stamp': get_time_stamp()
                        }
                print (good_trade)
                return good_trade
        else:
            #format 2: ['xxx/profit_coin', 'xxx/yyy', 'yyy/profit_coin']
            print('format 2')
            unbalance_factor[0] = bid[1][0]*bid[2][0]/(ask[0][0])
            unbalance_factor[1] = bid[0][0]/(ask[1][0]*ask[2][0])
    elif profit_coin_position_start > 1:
        if profit_coin_position_end < 1:
            #format 3: ['profit_coin/xxx', 'xxx/yyy', 'profit_coin/yyy']
            print('format 3')
            unbalance_factor[0] = bid[0][0]*bid[1][0]/(ask[2][0])
            unbalance_factor[1] = bid[2][0]/(ask[1][0]*ask[0][0])
        else:
            print('format 4')
            #format 4: ['profit_coin/xxx', 'xxx/yyy', 'yyy/profit_coin']
            #This is very unlikely to happen, but just in case.
            unbalance_factor[0] = bid[0][0]*bid[1][0]*bid[2][0]
            unbalance_factor[1] = 1/(ask[0][0]*ask[1][0]*ask[2][0])
    
    print('trair: ', pairs, '## protif coin:', profit_coin)
    print('unbalance factor 0:', unbalance_factor[0],
          'unbalance factor 1:', unbalance_factor[1])
    
    return False
    
def load_exchange():
    try:
        exchange = ccxt.kucoin()
        market = exchange.load_markets()
    except ccxt.RequestTimeout:
        wait()
        exchange, market = load_exchange()
        
    return exchange, market 

def save_oportunities(oportunities = [], file_name= '', action = 'append'):
    if action == 'new file':
        time_stamp = get_time_stamp()
        file_name = time_stamp +'_good_unbalances.txt'
        file_oportunities = open(file_name, 'w')
        file_oportunities.write('### Possibly profitable unbalances ###\n')
        file_oportunities.close()
    else:
        try: 
            file_oportunities = open(file_name, 'a')
            file_oportunities.write(str(oportunities)+'\n')
            file_oportunities.close()
        except IOError:
            wait()
            file_name = save_oportunities(oportunities, file_name) 
            
    return file_name
    
def main():
    # 1- Load exchange.
    exchange, market = load_exchange()
    
    # 2- Find possible tri-pairs (trairs) within the exchange.
    trair = find_trairs(exchange)
    
    # Define the coin of interest for each trair.
    # The coin of interest is the coin we want to profit on with the trade.
    interesting_coins = ['BTC', 'EUR', 'ETH', 'BTC', 'USDT']
    # define_coins_of_insterest, set one coin of interest for each trair.
    coins_of_interest = define_coins_of_interest(exchange, trair, interesting_coins)

    trair = sort_pairs(trair, coins_of_interest)
    # 3. Seek for unbalances in the trairs.
    oportunities = []
    file_name = save_oportunities(action = 'new file')
    try:
        while True:
            for t in range(len(trair)):
                unbalance = find_unbalance(exchange, trair[t], coins_of_interest[t])
                if unbalance:
                    print('unbalance')
                    oportunities.append(unbalance)
                    file_name = save_oportunities(unbalance, file_name)
    except KeyboardInterrupt:
        try:
            save_oportunities.close()
        except:
            pass
       
    # 4. Trade profitable unbalances.
    
    input ('End of the application, press enter to finish')


main()

                    
    


