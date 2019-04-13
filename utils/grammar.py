from collections import defaultdict
from utils.config import level_table
from utils.egp_rule import extra_rules
from utils.EGP import Egp
from utils.BNC import Bnc

import re
import numpy as np

re_token = re.compile('\w+|[,.:;!?]')


def get_root(parse):
    return [ tk for tk in parse if tk.dep_ == 'ROOT' ][0]


def get_lemma(tk, stopwords):
    lemma = tk.text if tk.lemma_ == '-PRON-' else tk.lemma_
    lemma = lemma.lower()
    return lemma if lemma in stopwords else tk.tag_


# from character span -> token span
def align(re_match, tags):
    start, end = re_match.span()

    length = 0
    for i, token in enumerate(tags.split(' ')):
        if length >= start: break

        length += len(token) + 1  # space len

    match_len = len(re_match.group().split(' '))
    return (i, i+match_len)


def check_matches(no, parse, tags):
    matches = []
    for match in Egp.get_pattern(no).finditer(tags):
        start, end = align(match, tags)

        try:
            if extra_rules(no, parse[start:end]): # extra rule
                matches.append((start, end, match.group()))
        except:
            print([tk.text for tk in parse])
            print(no, start, end)

    return matches


def match_pattern(parse, no):
    matches = []
    stopwords = re_token.findall(Egp.get_pattern(no).pattern)
    
    lemma_tags = ' '.join([get_lemma(tk, stopwords) for tk in parse])
    origin_tags = ' '.join([tk.tag_ if tk.text not in stopwords else tk.text for tk in parse])
    
    matches.extend(check_matches(no, parse, lemma_tags))
    matches.extend(check_matches(no, parse, origin_tags))

    return set(matches)


# Iterate all patterns to match
def iterate_all_patterns(parse, pat_groups=Egp.pattern_groups): 
    gets = []
    for (category, subcategory), group in Egp.pattern_groups.items():
        for no in group:
            if not Egp.pattern_exist(no): continue

            # match pattern
            matches = match_pattern(parse, no)
            if not matches: continue
            
            for (start, end, match) in matches:
                indices = [tk.i for tk in parse[start:end]]
                ngram   = ' '.join([tk.text for tk in parse[start:end]])
                gets.append({'no': no, 'level': Egp.get_level(no), 
                             'indices': indices, 'ngram': ngram, 'match': match, 
                             'category': category, 
                             'subcategory': Egp.get_subcategory(no), 
                             'statement': Egp.get_statement(no)})
                
    return gets


# find all except exact overlap
def remove_overlap(parse, gets):
    overlap_marker = np.asarray([False] * len(parse))
    overlap_level = np.asarray([None] * len(parse))

    # remove duplicate gets
    uniq_gets = []
    [uniq_gets.append(get) for get in gets if get not in uniq_gets]
    gets = uniq_gets
        
    # sort by level first and then length of ngram
    gets = sorted(gets, key=lambda get: len(get['ngram'].split(' ')), reverse=True)
    gets = sorted(gets, key=lambda get: level_table[get['level']], reverse=True)

    new_gets = []
    
    for get in gets:
        # ngram is not all overlapped or the level is same
        if not (all([overlap_marker[index] for index in get['indices']])) and not (all([overlap_level[index] == get['level'] for index in get['indices']])):
            for index in get['indices']:
                overlap_marker[index] = True
                overlap_level[index] = True
            new_gets.append(get)

    return new_gets


def generate_candidates(parse):
    root = get_root(parse)
    layer = [root] # start with root
    sentences = [[root]]
    
    while True:
        children = [child for tk in layer for child in tk.children] # all children
        if not children: break
        
        children.extend([child for tk in children if tk.dep_ in ['prep'] for child in tk.children]) # add prep obj

        sentences.append(sorted(sentences[-1] + children, key=lambda x: x.i))

        layer = [child for child in children if child.dep_ not in ['prep']] # remove prep token in case duplicate
        
    return sentences


############################################################
# Recommend grammar rules
############################################################
def recommend_patterns(get):
    no, match, ngram = get['no'], get['match'], get['ngram']
    
    candidates = Egp.pattern_groups[(Egp.get_category(no), Egp.get_subcategory(no))]

    candidates = filter(lambda can: level_table[Egp.get_level(can)] - level_table[Egp.get_level(no)] > 0, candidates) # only get level higher by 1
    candidates = filter(lambda can: can in Bnc.number_groups, candidates) # filter non-exist

    # find related rules that contains related ngrams
    related_rules = defaultdict(list)
    for num in candidates:
        for pattern in Bnc.number_groups[num].keys():
            for token in ngram.split(' '):
                if token in '.,:!?-\'"': continue
                    
                ngrams = Bnc.ngram_groups[(pattern, num)][token] # set
                if ngrams:
                    related_rules[num].extend(list(ngrams))

    # 找 ngram 相近才對
    if len(related_rules) > 0:
        for num, ngrams in related_rules.items():
            ngram = ngrams[0]
            if len(Bnc.sentences[ngram]) > 0:
                rec_no = num
                rec_sentence = Bnc.sentences[ngram][0]
                break
        
        return {'no': rec_no, 'level': Egp.get_level(rec_no), 
                'category': Egp.get_category(rec_no), 'subcategory': Egp.get_subcategory(rec_no),
                'statement': Egp.get_statement(rec_no), 'example': rec_sentence }
    else: 
        return None


def iterate_all_gets(parse, gets):
    recs = [recommend_patterns(get) for get in gets]
        
    return recs
