#!/usr/bin/env python
# coding: utf-8


from utils.config import tag2pos_table
from collections import Counter, defaultdict
from multiprocessing import Pool
import pickle, itertools
import kenlm

model = kenlm.Model('/home/nlplab/jjc/gec/lm/coca.prune.bin')


# In[155]:


with open('recommend.pickle', 'rb') as handle:
    info = pickle.load(handle)
    counts, ngrams, sentences = info['counts'], info['ngrams'], info['sentences']


# In[156]:


count_groups = defaultdict(list)
ngram_groups = defaultdict(lambda: defaultdict(list))

for pattern_group_name, pattern_group_items in itertools.groupby(counts, lambda el: el[0].split(' ')[0]):
    pattern_group_items = list(pattern_group_items)
    count_groups[pattern_group_name].extend(pattern_group_items)
    
    for key in pattern_group_items:
        for ngram_group_name, ngram_group_items in itertools.groupby(ngrams[key], lambda el: el.split(' ')[0]):
            ngram_groups[key][ngram_group_name].extend(list(ngram_group_items))


# In[157]:


### NOT GOOD
from utils.EGP import EGP
Egp = EGP()
### NOT GOOD


# In[158]:


def lm(last_sent, ngram):
    ngs = ngram.split(' ', maxsplit=1)
    if len(ngs) > 1: sentence = last_sent + ' ' + ngram.split(' ', maxsplit=1)[1]
    else:            sentence = last_sent
    score = model.score(sentence, bos=True, eos=False)
    return (ngram, score)



def normalize_tag(tag):
#     return tag
    return tag2pos_table[tag] if tag in tag2pos_table else tag


def normalize_pattern(headword, pattern):
    tags = pattern.split(' ')
    
    norm_pattern = [headword]
    for tag in tags[1:]:
        norm_pattern.append(normalize_tag(tag))
    
    return ' '.join(norm_pattern)
    
    
def auto_suggest(headword, pos, last_sent):
    related_patterns = count_groups[headword] + count_groups[pos] # get headword matched POS and first word
    related_patterns = filter(lambda related_pat: headword in ngram_groups[related_pat], related_patterns)

    related_patterns = list(related_patterns)

    ### 不需要用 count?
    # merge same number rule
    total = Counter()
    for pattern, no in related_patterns: 
        for ngram in ngram_groups[(pattern, no)][headword]:
            total[no] += ngrams[(pattern, no)][ngram]
    top_k_keys = dict(total.most_common(3))

    # get top k patterns
    target_patterns = filter(lambda key: key[1] in top_k_keys, related_patterns)

    # normalize patterns
    target_norm_patterns = defaultdict(list)
    for pattern, no in target_patterns:
        target_norm_patterns[normalize_pattern(headword, pattern)].append((pattern, no))
        
    # retrieve ngrams example
    target_ngrams = []
    total = 0
    for norm_pattern in target_norm_patterns: # (pattern, no)
        scores = [lm(last_sent, ng) for pattern, no in target_norm_patterns[norm_pattern] 
                  for ng in ngram_groups[(pattern, no)][headword]] # get ngram in given patterns
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:3]

        t_ngrams = [ng[0] for ng in scores]
        avg = 1 / abs(sum([s[1] for s in scores]) / len(scores))
        total += avg        

        target_ngrams.append({
            'pattern': norm_pattern, 'pos': normalize_tag(pos),
            'no': no, 'level': Egp.get_level(no), 
            # 'count': counts[(pattern, no)], 
            'lm': avg,
            'category': Egp.get_category(no), 'subcategory': Egp.get_subcategory(no),
            'ngrams': t_ngrams, 
            'sentence': sentences[t_ngrams[0]][0] })

    # get means and sorted
    for ng in target_ngrams: 
        ng['lm'] = ng['lm'] / total
        
    return target_ngrams
