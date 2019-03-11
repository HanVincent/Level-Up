from utils.config import level_table
from utils.egp_rule import extra_rules
from utils.EGP import EGP

import re
import numpy as np

Egp = EGP()
re_token = re.compile('\w+|[,.:;!?]')


def get_root(parse):
    return [ tk for tk in parse if tk.dep_ == 'ROOT' ][0]


def get_lemma(tk, stopwords):
    lemma = tk.lower_ if tk.lemma_ == '-PRON-' else tk.lemma_
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

        if extra_rules(no, parse[start:end]): # extra rule
            matches.append((start, end, match.group()))

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
def iterate_all_patterns(parse, pat_groups=Egp.get_group_patterns()): 
    gets = []
    for (category, subcategory), group in Egp.group_patterns().items():
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

def recommend_patterns(level, pat_group):
    rec = filter(lambda el: level_table[level] < level_table[el['level']], pat_group)
    
    return [{'no': el['no'], 'level': el['level'], 
             'category': Egp.get_category(el['no']), 'subcategory': Egp.get_subcategory(el['no']),
             'statement': Egp.get_statement(el['no']), 'highlight': Egp.get_highlight(el['no'])} 
            for el in rec]


def iterate_all_gets(gets, pat_groups=Egp.get_group_patterns()):
    recs = []
    for get in gets:
        group, level = get['group'], get['level']
        recs.append(recommend_patterns(level, pat_groups[group]))
        
    return recs
