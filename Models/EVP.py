import os
import json
from Models.BaseRule import BaseRule
from collections import defaultdict


class EVP(BaseRule):

    def __init__(self, data_directory):
        super(EVP, self).__init__()

        self.vocab_level = {}
        self.vocab_pos = defaultdict(set)

        with open(os.path.join(data_directory, 'cambridge.dict.txt'), 'r', encoding='utf8') as fs:
            for line in fs:
                vocab, level, poss, gw, href = line.split('\t')

                for pos in poss.split(','):
                    self.vocab_pos[vocab].add(pos)

                if (vocab not in self.vocab_level or self.level_mapping[level] < self.level_mapping[self.vocab_level[vocab]]):
                    self.vocab_level[vocab] = level

        with open(os.path.join(data_directory, 'sims.json'), 'r', encoding='utf8') as fs:
            self.sims = json.load(fs)

    def get_pos(self, vocab):
        return self.vocab_pos[vocab]

    def get_level(self, vocab):
        if vocab not in self.vocab_level:
            return None

        return self.vocab_level[vocab]
