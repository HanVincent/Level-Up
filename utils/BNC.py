#!/usr/bin/env python
# coding: utf-8
from collections import Counter, defaultdict
import pickle

class BNC:

    def __init__(self):
        with open('coca.recommend.prune.pickle', 'rb') as handle:
            info = pickle.load(handle)
            self.counts, self.ngrams, self.sentences = info['counts'], info['ngrams'], info['sentences']
            
        self.number_groups = defaultdict(Counter)
        self.pattern_groups = defaultdict(set)
        self.ngram_groups = defaultdict(lambda: defaultdict(set))

        for pattern, no in self.counts.keys():
            self.number_groups[no][pattern] += 1
            
            for key in pattern.split(' '):
                self.pattern_groups[key].add((pattern, no))

            for ngram in self.ngrams[(pattern, no)]:
                for n_key in ngram.split(' '):
                    self.ngram_groups[(pattern, no)][n_key].add(ngram)


Bnc = BNC()