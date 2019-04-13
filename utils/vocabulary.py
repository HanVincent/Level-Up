from gensim.models import KeyedVectors
from utils.config import level_table
from utils.EVP import Evp

model = KeyedVectors.load_word2vec_format('data/GoogleNews-vectors-negative300.bin', binary=True)

def level_vocab(sent):
    annotate = [{'token': tk.text, 'level': Evp.get_level(tk.lemma_), 'recs': recommend_vocabs(tk.lemma_)} for tk in sent]
    return annotate

#     annotate = []
#     for tk in sent.split(' '):
#         try:
#             annotate.append({ 'token': tk, 'level': Evp.lookup_by_sense(sent, tk) })
#         except:
#             annotate.append({ 'token': tk, 'level': None })

#     return annotate


def recommend_vocabs(vocab):
    if Evp.vocab_exists(vocab):
        level, poss = Evp.get_level(vocab), Evp.get_pos(vocab)
        
        if vocab in model:
            sims = model.similar_by_word(vocab, topn=100)
            recs = [{ 'vocab': sim, 'level': Evp.get_level(sim) } for sim, score in sims 
                    if Evp.vocab_exists(sim) and level_table[Evp.get_level(sim)] > level_table[level] and len(Evp.get_pos(sim) & poss) > 0]
            recs = sorted(recs[:10], key=lambda rec: level_table[rec['level']], reverse=True)
            
            return recs

    return []
    