#!/usr/bin/env python
# coding: utf-8
from .config import level_table


# ### Just lookup dictionary directly (ignore POS)

class Dictionary:

    def __init__(self):
        self.vocab_level = {}

        for line in open('./data/dict.slim.txt', 'r', encoding='utf8'):
            vocab, level, poss, gw, href = line.split('\t')

            if (vocab not in self.vocab_level or
               level_table[level] < level_table[self.vocab_level[vocab]]):
                self.vocab_level[vocab] = level

    def lookup(self, vocab):
        if vocab not in self.vocab_level:
            return None

        return self.vocab_level[vocab]


# ### Use POS to categorize

# '''有些還是有誤，像是 everybody: pronoun(spacy: PRON)'''
# vocab_level = defaultdict(lambda: defaultdict(lambda: "C2"))
# pos_set = set()

# for line in open('dict.slim.txt', 'r', encoding='utf8'):
#     vocab, level, poss, gw, href = line.split('\t')

#     for pos in poss.replace(";", ",").split(','):
#         pos_set.add(pos.strip().lower())
#         if level_table[level] < level_table[vocab_level[vocab][pos]]:
#             vocab_level[vocab][pos] = level
