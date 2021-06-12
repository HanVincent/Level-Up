from Models.RawProcessor import RawProcessor

if __name__ == '__main__':
    data_directory = './data'
    
    rawProcessor = RawProcessor(data_directory)
    rawProcessor.calc_ngram_and_count('bnc.parse.txt.gz')


# if __name__ == '__main__':
#     import json, os
#     from tqdm import tqdm
#     from gensim.models import KeyedVectors
#     from Models.EVP import EVP
    
#     data_directory = 'data'
#     evp = EVP(data_directory)
#     w2v = KeyedVectors.load_word2vec_format(os.path.join(data_directory, 'gensim_glove_vectors.txt'), binary=False)

#     sims = {}
#     for key in tqdm(evp.vocab_level.keys()):
#         if key in w2v.key_to_index:
#             sims[key] = evp.get_higher_sims(key, w2v.similar_by_word(key, topn=100))

#     with open(os.path.join(data_directory, 'sims.json'), 'w', encoding='utf8') as ws:
#         json.dump(sims, ws)
