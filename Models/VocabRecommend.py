from Models.Recommend import Recommend
from utils.stringUtils import normalize


class VocabRecommend(Recommend):
    def __init__(self, parser, egp, evp):
        super(VocabRecommend, self).__init__(parser, egp, evp)

    def vocab(self, sentence):
        parse = self.parser.parse(normalize(sentence))
        vocabs = self._level_vocab(parse)

        return vocabs

    def _level_vocab(self, sent):
        annotate = [{
            'token': tk.text,
            'level': self.evp.get_level(tk.lemma_),
            'recs': self._recommend_vocabs(tk.lemma_)
        } for tk in sent]
        return annotate

    def _recommend_vocabs(self, vocab):
        if vocab in self.evp.vocab_level:
            level, pos = self.evp.get_level(vocab), self.evp.get_pos(vocab)

            if vocab in self.evp.w2v:
                sims = self.evp.w2v.similar_by_word(vocab, topn=100)
                recs = [{
                    'vocab': sim,
                    'level': self.evp.get_level(sim)
                } for sim, score in sims if sim in self.evp.vocab_level
                    and self.evp.level_mapping[self.evp.get_level(sim)] > self.evp.level_mapping[level]
                    and len(self.evp.get_pos(sim) & pos) > 0]
                recs = sorted(
                    recs[:10], key=lambda rec: self.evp.level_mapping[rec['level']], reverse=True)

                return recs

        return []
