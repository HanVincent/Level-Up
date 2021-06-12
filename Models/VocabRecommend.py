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
            sims = self.evp.sims[vocab]
            recs = [
                {'vocab': sim, 'level': self.evp.get_level(sim)} for sim in sims]
            recs = sorted(
                recs[:10], key=lambda rec: self.evp.level_mapping[rec['level']], reverse=True)

            return recs

        return []
