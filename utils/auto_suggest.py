import pickle
from collections import Counter

with open('recommend.pickle', 'rb') as handle:
    info = pickle.load(handle)
    counts, ngrams, sentences = info['counts'], info['ngrams'], info['sentences']
    

### NOT GOOD
from utils.EGP import EGP
Egp = EGP()
### NOT GOOD


def auto_suggest(headword, pos):
    # TODO: filter
    related_patterns = filter(lambda el: el[0].split(' ')[0] in [headword, pos] , ngrams) # get first pattern is headword or pos
    related_patterns = filter(lambda el: any( [headword == ngram.split(' ')[0] for ngram in ngrams[el].keys()] ), related_patterns) # remove ngrams doesn't have headword
    related_patterns = list(related_patterns)
    
    # merge same number rule
    total = Counter()
    for ngram, no in related_patterns: 
        total[no] += counts[(ngram, no)]
    top_k_keys = dict(total.most_common(3))

    # get top k patterns
    target_patterns = filter(lambda key: key[1] in top_k_keys, related_patterns)

    # retrieve related ngrams
    target_ngrams = []
    for pattern in target_patterns:
        for ngram in ngrams[pattern]:
            if ngram.split(' ')[0] == headword:
                target_ngrams.append((*pattern, ngram))
                break

    # return info
    return [{'pattern': pattern, 'no': no, 'level': Egp.get_level(no),
             'category': Egp.get_category(no), 'subcategory': Egp.get_subcategory(no),
             'count': counts[(pattern, no)], 
             'ngram': ngram, 
             'sentence': sentences[ngram][0] } for pattern, no, ngram in target_ngrams]