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

    def get_higher_sims(self, vocab, candidates):
        pos = self.get_pos(vocab)
        level = self.get_level(vocab)
        candidates = filter(lambda entry: entry[1] > 0.3, candidates)
        candidates = map(lambda entry: entry[0], candidates)
        candidates = filter(lambda can: can in self.vocab_level, candidates)
        candidates = filter(lambda can: self.level_mapping[self.get_level(can)] > self.level_mapping[level], candidates)
        candidates = filter(lambda can: len(self.get_pos(can) & pos) > 0, candidates)
        return list(candidates)
