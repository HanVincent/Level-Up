#!/usr/bin/env python
# coding: utf-8

from collections import Counter, defaultdict
from utils.config import tag2pos_table, level_table
from utils.EGP import Egp
from utils.EVP import Evp
from utils.BNC import Bnc
import kenlm

model = kenlm.Model('/home/nlplab/jjc/gec/lm/coca.prune.bin')


def lm(last_sent, ngram):
    sentence = last_sent + ' ' + ngram
    score = model.score(sentence, bos=True, eos=False) # / len(sentence.split())
    return score


def level_score(ngram):
    levels = [Evp.get_level(token) for token in ngram.split()]
    score = sum([level_table[level] if level else 0 for level in levels]) / len(levels)
    return score


def normalize_tag(tag):
    return tag2pos_table[tag]+'.' if tag in tag2pos_table else tag


# In[169]:

def suggest_patterns(related_patterns, text_sent, headword, pos, top_k=1):
    # not containing related ngram patterns
    related_patterns = filter(lambda ptn: ptn[1] not in [9, 12] and headword in Bnc.ngram_groups[ptn], related_patterns)

    # group patterns by number
    pattern_groups = defaultdict(list)
    for pattern, no in related_patterns:
        pattern_groups[no].append(pattern)
        
    # calc LM and get top k
    targets = []
    for no in pattern_groups:
        candidates = [ng for pattern in pattern_groups[no] for ng in Bnc.ngram_groups[(pattern, no)][headword]]
        candidates = filter(lambda ng: len(ng.split()) < 7, candidates)
        candidates = filter(lambda ng: len(Bnc.sentences[ng]) > 1, candidates)
        scores = [(ng, level_score(ng), lm(text_sent, ng)) for ng in candidates]
        scores = sorted(scores, key=lambda x: x[2], reverse=True)[:10]

        if len(scores) > 0:
            scores = sorted(scores, key=lambda x: x[1], reverse=True)[:5]
            ngrams = [score[0] for score in scores]
            ngram = ngrams[0]
            # ngram = max(scores, key=lambda x: x[1])[0]
            lm_score = sum(score[2] for score in scores) / len(scores)
            targets.append({'no': no, 'level': Egp.get_level(no), 'pos': normalize_tag(pos), 
                            'lm': lm_score, 'pattern': Egp.get_norm_pattern(no), 'ngrams': ngrams, 'ngram': ngram, 
                            'category': Egp.get_category(no), 'subcategory': Egp.get_subcategory(no),
                            'statement': Egp.get_statement(no) } )
    
    # sort by lm
    targets = sorted(targets, key=lambda t: t['lm'], reverse=True)
    
    return targets



def suggest_sentences(ngram):
    return Bnc.sentences[ngram][:1]


# In[174]:


# from utils.grammar import iterate_all_patterns

def auto_suggest(parse_sent, gets):
    last_word, last_index = parse_sent[-1], len(parse_sent) - 1
    if last_word.is_punct and len(parse_sent) > 1:
        last_word, last_index = parse_sent[-2], len(parse_sent) - 2
        
    headword, pos = last_word.text, last_word.tag_
    text_sent = parse_sent.text.rsplit(' ', maxsplit=1)[0] # to text
    
    # get max get
    gets = [get for get in gets if last_index in get['indices']]
    get = None
    
    related_patterns = Bnc.pattern_groups[pos].union(Bnc.pattern_groups[headword])
    if len(gets) > 0:
        get = max(gets, key=lambda get: level_table[get['level']])
        get['pattern'] = Egp.get_norm_pattern(get['no'])
        related_patterns = filter(lambda ptn: level_table[Egp.get_level(ptn[1])] > level_table[get['level']] and get['no'] != ptn[1], related_patterns)
        # related_patterns = filter(lambda ptn: get['no'] != ptn[1], related_patterns)
    
    patterns = suggest_patterns(related_patterns, text_sent, headword, pos)
    
    return get, { 'patterns': patterns, 'collocations': [] }
