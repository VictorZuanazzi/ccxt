# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 15:48:59 2018

@author: victzuan
"""


import ccxt
from collections import Counter
from itertools import combinations, chain

def parse_pair(raw_pair):
    return raw_pair.split('/')

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
    for i in range(len(u_trair)):
        t_trair = []
        for j in range(len(u_trair[i])):
            t_trair.append(u_trair[i][j][0]+'/'+u_trair[i][j][1])
        print(t_trair)
        trair.append(t_trair)

    return (trair)

exchange = ccxt.kucoin()
market = exchange.load_markets()
exchange_pairs = exchange.symbols

raw_pairs = list(filter(lambda x: not '.d' in x, exchange_pairs))

pairs = map(parse_pair, raw_pairs)
trair_candidates = combinations(pairs, r=3)
#filter the actual trairs from all trair_candidates
u_trair = list(filter(is_trair,trair_candidates)) #unformated trairs.
trair = format_trairs(trairs)#formats the trairs to list of list os strings.


