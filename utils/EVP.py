#!/usr/bin/env python
# coding: utf-8

from collections import defaultdict
from utils.config import level_table

class EVP:

    def __init__(self):
        self.vocab_level = {}
        self.vocab_pos = defaultdict(set)

        for line in open('./data/cambridge.dict.slim.txt', 'r', encoding='utf8'):
            vocab, level, poss, gw, href = line.split('\t')

            for pos in poss.split(','):
                self.vocab_pos[vocab].add(pos)

            if (vocab not in self.vocab_level or level_table[level] < level_table[self.vocab_level[vocab]]):
                self.vocab_level[vocab] = level


    def vocab_exists(self, vocab):
        return vocab in self.vocab_level
    
    
    def get_pos(self, vocab):
        return self.vocab_pos[vocab]

    
    def get_level(self, vocab):
        if vocab not in self.vocab_level:
            return None

        return self.vocab_level[vocab]

    
Evp = EVP()