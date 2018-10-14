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

def format_trairs(trairs):
    trair= []
    for i in range(len(trairs)):
        t_trair = []
        for j in range(len(trairs[i])):
            t_trair.append(trairs[i][j][0]+'/'+trairs[i][j][1])
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
trairs = list(filter(is_trair,trair_candidates))
trair = format_trairs(trairs)


