#!/usr/bin/env python
# coding: utf-8


from collections import Counter, defaultdict
from utils.config import tag2pos_table, level_table
from utils.EGP import Egp
from utils.EVP import Evp
from utils.BNC import Bnc
import kenlm

model = kenlm.Model('/home/nlplab/jjc/gec/lm/coca.prune.bin')


# In[10]:


def lm(last_sent, ngram):
    sentence = last_sent + ' ' + ngram
    score = model.score(sentence, bos=True, eos=False) / len(sentence.split())
    return score


def level_score(ngram):
    levels = [Evp.get_level(token) for token in ngram.split()]
    score = sum([level_table[level] if level else 0 for level in levels]) / len(levels)
    return score


def normalize_tag(tag):
    return tag2pos_table[tag]+'.' if tag in tag2pos_table else tag


# def normalize_pattern(headword, pos, pattern):
#     tags = pattern.split(' ')
#     if headword in tags: 
#         # return ' '.join([normalize_tag(tag) for tag in tags])
#         return ' '.join([normalize_tag(tag) if tag != headword else normalize_tag(pos).upper() for tag in tags])
#     else:
#         index = tags.index(pos)
#         # return ' '.join([normalize_tag(tag) if i != index else headword for i, tag in enumerate(tags)])
#         return ' '.join([normalize_tag(tag) if i != index else normalize_tag(tag).upper() for i, tag in enumerate(tags)])
    
# def normalize_pattern(headword, pattern):
#     tags = pattern.split(' ')
#     if headword in tags: 
#         return ' '.join([normalize_tag(tag) for tag in tags])
#     else:
#         norm_pattern = [headword]
#         for tag in tags[1:]:
#             norm_pattern.append(normalize_tag(tag))

#         return ' '.join(norm_pattern)


# In[11]:


def suggest_patterns(related_patterns, headword, pos, last_sent, top_k=3):
    related_patterns = [related_pat for related_pat in related_patterns 
                        if headword in Bnc.ngram_groups[related_pat]] # filter patterns containing headword ngram

    # group patterns by number
    pattern_groups = defaultdict(list)
    for pattern, no in related_patterns:
        pattern_groups[no].append(pattern)

    # maybe need some filter
    
    # calc LM and get top k
    targets = []
    for no in pattern_groups:
        scores = [(ng, level_score(ng), lm(last_sent, ng)) for pattern in pattern_groups[no] for ng in Bnc.ngram_groups[(pattern, no)][headword]]
        scores = sorted(scores, key=lambda x: x[2], reverse=True)[:10]
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        
        print(scores)
        
        target_ngrams = [ng[0] for ng in scores]
        # sentence = Bnc.sentences[target_ngrams[0]][0]
        targets.append({'no': no, 'level': Egp.get_level(no), 'pos': normalize_tag(pos), 
                        'pattern': Egp.get_norm_pattern(no), 'ngrams': target_ngrams,
                        'category': Egp.get_category(no), 'subcategory': Egp.get_subcategory(no),
                        'statement': Egp.get_statement(no) } )
    
    # sort by level
    targets.sort(key=lambda t: level_table[t['level']], reverse=True)
    
    return targets


def suggest_sentences(ngram):
    return Bnc.sentences[ngram][:3]


# In[12]:


def auto_suggest(headword, pos, last_sent):
    patterns = suggest_patterns(Bnc.pattern_groups[pos], headword, pos, last_sent)
    collocations = suggest_patterns(Bnc.pattern_groups[headword], headword, pos, last_sent)
    
    return {'patterns': patterns, 'collocations': collocations}



# def auto_suggest(headword, pos, last_sent):
#     related_patterns = pattern_groups[headword] + pattern_groups[pos] # get headword matched POS and first word
#     related_patterns = [related_pat for related_pat in related_patterns if headword in ngram_groups[related_pat]]

#     # merge same number rule
#     total = Counter()
#     for pattern, no in related_patterns: 
#         for ngram in ngram_groups[(pattern, no)][headword]:
#             total[no] += ngrams[(pattern, no)][ngram]
#     top_k_keys = dict(total.most_common(3))

#     # get top k patterns
#     target_patterns = filter(lambda key: key[1] in top_k_keys, related_patterns)

#     # normalize patterns
#     target_norm_patterns = defaultdict(list)
#     for pattern, no in target_patterns:
#         target_norm_patterns[normalize_pattern(headword, pattern)].append((pattern, no))
        
#     # retrieve ngrams example
#     total = 0
#     target_ngrams = []
#     for norm_pattern in target_norm_patterns: # (pattern, no)
#         scores = [lm(last_sent, ng) for pattern, no in target_norm_patterns[norm_pattern] 
#                   for ng in ngram_groups[(pattern, no)][headword]] # get ngram in given patterns
#         scores = sorted(scores, key=lambda x: x[1], reverse=True)[:3]

#         t_ngrams = [ng[0] for ng in scores]
#         avg = 1 / abs(sum([s[1] for s in scores]) / len(scores))
#         total += avg        

#         target_ngrams.append({
#             'pattern': norm_pattern, 'pos': normalize_tag(pos),
#             'no': no, 'level': Egp.get_level(no), 
#             # 'count': counts[(pattern, no)], 
#             'lm': avg,
#             'category': Egp.get_category(no), 'subcategory': Egp.get_subcategory(no),
#             'ngrams': t_ngrams, 
#             'sentence': sentences[t_ngrams[0]][0] })

#     # get means and sorted
#     for ng in target_ngrams: 
#         ng['lm'] = ng['lm'] / total
        
#     return target_ngrams

