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
    '''return the time stamp in the format yy-mm-dd-hh-MM' 
    '''
    return datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

def parse_pair(raw_pair):
    ''' for a string with a '/' returns the str before and after it in a list.
    
    Input:
        'aaa/bbb'
    Return:
        ['aaa','bbb']
    '''
    return raw_pair.split('/')

def wait(delay = DELAY):
    '''pauses the program for delay in seconds.
    '''
    time.sleep(delay)

def is_trair(trair_candidate):
    # When all currencies appear twice means we have a trair
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
        print(t_trair)
    
    return trair

def find_trairs(exchange):
    ''' Find possible triplece of pairs (trairs) that can be traded for unbalance.
    
    Example of trairs:
    'ETC/BTC' 'ETC/ETH' 'ETH/BTC'
    'BCH/BTC' 'BCH/EUR' 'BTC/EUR'
    
    '''
    print ('Loading trairs...')
    
    exchange_pairs = exchange.symbols #loads all pairs from the exchange.
    raw_pairs = list(filter(lambda x: not '.d' in x, exchange_pairs))

    pairs = map(parse_pair, raw_pairs)
    trair_candidates = combinations(pairs, r=3)
    #filter the actual trairs from all trair_candidates.
    #this filter takes an awful long time to run.
    print ('This may take a while...')
    u_trair = list(filter(is_trair,trair_candidates)) #unformated trairs.
    print('...almost finished...')
    trair = format_trairs(u_trair) #formats the trairs to list of list os strings.
    
    print('Trairs are loaded.')
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
def load_order_book(exchange, pairs):
    '''load first layer of asks and bids from the order book.
    
    Input:
        exchange: ccxt.object, the exchange in question.
        pairs: the pairs that must have its orderbook loaded.
        deepth: the relevant number of orders. 
    
    Return:
        ask, bid : tuple containing the 
    '''
    ask = ['','','']
    bid = ['','','']
    #load the relevant orderbook information:
    try:
        for i in range(len(pairs)):
            ask[i] = exchange.fetch_order_book(pairs[i])['asks'][0] #price to buy
            bid[i] = exchange.fetch_order_book(pairs[i])['bids'][0] #price to sell
        return ask, bid
    except (ccxt.RequestTimeout, ccxt.ExchangeNotAvailable, ccxt.ExchangeError) as error:
        print('Pairs: ', pairs, 'Time out.')
        print('Error:', error)
        wait()
        return False, False


def generate_sequence(trair, profit_coin):
    '''Defines the sequence of trades that must happen for each trair. 
    It only computes the straight sequence, the inverse sequence is directly 
    deducted.
    
    Return:
        path = [['bid','bid','ask'],...], same lengh as trair
    '''

    path = []
    for i in range(len(trair)):
        pair_path = []
        trade_coin = profit_coin[i]
        for j in range(len(trair[i])):
            one_pair = parse_pair(trair[i][j])
            if one_pair[1] == trade_coin:
                #trade_coin is not the base coin, the trade direction is to buy.
                pair_path.append('ask')
                #trade_coin becomes the other coin of the pair.
                trade_coin = one_pair[0] 
            else:
                #trade_coin is the base coin, the trade direction is to sell.
                pair_path.append('bid')
                #trade_coin becomes the other coin of the pair.
                trade_coin = one_pair[1] 
        path.append(pair_path)
        
    return path

def trade_mode(mode):
    '''
        There are two trade modes:
            straight: executes the trades in the straight order,
            inverse: executes the trader in inverse order.
        return:
            'ask' if mode is 'straight'
            'bid' if mode is 'inverse'
    '''
    if mode == 'straight':
        trade = 'ask'
    else:
        trade = 'bid'
    return trade
        
def calculate_factor(ask, bid, trade_path, mode = 'straight'):
    '''returns the unbalance factor of the sequence of trades.
    
    Inputs:
        ask: [[price, volume],...], volume in the base currency.
        bid: [[price, volume],...], bolume in the base currency.
        trade_path: ['ask', 'bid', 'ask'], list of str with the straight orders,
            if followed the trade is profitable.
        mode: 'straight' or 'inverse'. 'inverse' mode executes 'bid' when 'ask 
            is given and the other way around.
    Return:
        a number around 1 that indicates if the trade is profitable. 
    '''
    unbalance_factor = 1
    trade = trade_mode(mode)
    
    for action in range(len(trade_path)):
        if trade_path[action] == trade:
            unbalance_factor = unbalance_factor/ask[action][0]
        else:
            unbalance_factor = unbalance_factor*bid[action][0]
            
    return unbalance_factor

def calculate_volume(ask, bid, trade_path, pairs, profit_coin, mode = 'straight'):
    ''' returns the max volume possible for the trade.
    
    it looks too complicated for what it does. there is a better way to do it.
    '''
    volume = [0,0,0]
    trade = trade_mode(mode)
    t_coin = ''
    print ('ask:', ask, '\nbid:',bid)
    
    for i in range(len(volume)):
        coin = parse_pair(pairs[i])
        if coin[0] == profit_coin:
            if trade_path[i] == trade:
                volume[i] = ask[i][1]
            else:
                volume[i] = bid[i][1]
            if t_coin == '':
                t_coin = coin[1]
        elif coin[1] == profit_coin:
            if trade_path[i] == trade:
                volume[i] = ask[i][0]*ask[i][1]
            else:
                volume[i] = bid[i][0]*bid[i][1]
            if t_coin == '':
                t_coin = coin[0]
        else:
            if trade_path[i] == trade:
                volume[i] = ask[0][0]*ask[i][1]
            else:
                volume[i] = bid[0][0]*bid[i][1]
        print('volume[',i,']:', volume[i])
        
    volume_restrictor = min(volume)
    return volume_restrictor 

def find_unbalance(exchange, pairs, profit_coin, trade_path):
    '''Finds unbalances when trading 3 currencies in an especific direction.
    
    BHC/BTC BCH/EUR BTC/EUR
    Return:
        False if no profitable unbalances are found.
        good_trade: relevant information about the profitable trade.
            profit_coin: coin in which we are building our position.
            trair: the profitable triplet of pairs.
            unbalance_factor: the profit factor by making the trade.
            volume: the max volume possible for this trade.
            sequence(mode): straight or inverse, the direction of the trades 
                that must happen to be profitable.
            Tima Stamp: date and time of the profitable trade.
        
    '''
    # Does not check trairs where there are no coins to profit from.
    if profit_coin == '':
        return False
    
    ask, bid = load_order_book(exchange, pairs)
    #In case there was a problem loading the orderbook, instance is stoped.
    if ask == False:
        return False
    
    # stores the unbalance of both paths.
    unbalance_factor = {
            'straight': calculate_factor(ask, bid, trade_path), 
            'inverse': calculate_factor(ask, bid, trade_path, mode = 'inverse')}

    for mode in unbalance_factor:
        if unbalance_factor[mode] > 1 + 3*FEE:
            volume_restrictor = calculate_volume(
                    ask, 
                    bid, 
                    trade_path, 
                    pairs, 
                    profit_coin, 
                    mode)
            
            good_trade = {
                    'profit_coin': profit_coin, 
                    'trair': pairs, 
                    'Unbalance factor': unbalance_factor[mode],
                    'Volume': volume_restrictor,
                    'Sequence': mode,
                    'Time Stamp': get_time_stamp()
                    }
            print(good_trade)
            return good_trade
    
    print('trair: ', pairs, '## protif coin:', profit_coin)
    print('straight unbalance factor:', unbalance_factor['straight'],
          '\ninverse unbalance factor :', unbalance_factor['inverse']) 
    return False
    
def load_exchange():
    '''loads exchange and the market information.
    '''
    try:
        exchange = ccxt.kucoin()
        market = exchange.load_markets()
        print('Exchange successfully loaded: ', exchange)
    except (ccxt.RequestTimeout, ccxt.ExchangeError) as error:
        print("Be patient, we are trying to connect to the exchange.")
        print("In the mean while, check your internet connection.")
        print("Error:", error)
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
            print('Problems to save:', file_name, '\nPlease check if the file is closed.')
            wait()
            file_name = save_oportunities(oportunities, file_name)            
    return file_name
    
        
def main():
    # 1- Load exchange.
    print('Triangulo Amoroso')
    exchange, market = load_exchange()
    
    # 2- Find possible tri-pairs (trairs) within the exchange.
    trair = find_trairs(exchange)
    
    # Define the coin of interest for each trair.
    # The coin of interest is the coin we want to profit on with the trade.
    interesting_coins = ['BTC', 'EUR', 'ETH', 'BTC', 'USDT', 'KCS']
    # define_coins_of_insterest, set one coin of interest for each trair.
    coins_of_interest = define_coins_of_interest(exchange, trair, interesting_coins)

    trair = sort_pairs(trair, coins_of_interest)
    trade_path = generate_sequence(trair, coins_of_interest)
    # 3. Seek for unbalances in the trairs.
    oportunities = []
    file_name = save_oportunities(action = 'new file')
    
    print('Looking for unbalances...')
    try:
        while True:
            for t in range(len(trair)):
                unbalance = find_unbalance(
                        exchange, 
                        trair[t], 
                        coins_of_interest[t], 
                        trade_path[t])
                if unbalance:
                    print('unbalance')
                    oportunities.append(unbalance)
                    file_name = save_oportunities(unbalance, file_name)
                    #check again if this coin is profitable.
    except KeyboardInterrupt:
        try:
            save_oportunities.close()
        except:
            pass
       
    # 4. Trade profitable unbalances.
    
    input ('End of the application, press enter to finish')


main()

                    
    


