import kenlm
import os


class LanguageModel:
    def __init__(self, data_directory):
        self.model = kenlm.Model(os.path.join(data_directory, 'lm.slim.bin'))

    def score(self, pre_sent, ngram):
        sentence = pre_sent + ' ' + ngram
        score = self.model.score(sentence, bos=True, eos=False)
        # score = model.score(sentence, bos=True, eos=False) / len(sentence.split())
        return score
