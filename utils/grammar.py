from utils.config import level_table
from utils.egp_rule import extra_rules
from utils.EGP import EGP

import re
import numpy as np

Egp = EGP()


def get_lemma(tk, stopwords):
    lemma = tk.lower_ if tk.lemma_ == '-PRON-' else tk.lemma_
    
    if lemma in stopwords: return lemma
    else: return tk.tag_
    

# return the index of start token and end token
def align(re_match, tags):
    start, end = re_match.span()

    length = 0
    for i, token in enumerate(tags.split(' ')):
        if length >= start: break
            
        length += len(token) + 1 # space len
            
    match_len = len(re_match.group().split(' '))
    return (i, i+match_len)
    

def iterate_match(no, parse, pat, tags):
    matches = []
    for match in pat.finditer(tags):
        start, end = align(match, tags)
        
        is_match = extra_rules(no, parse[start:end]) # extra rule
        if is_match: matches.append((start, end))

    return matches


re_token = re.compile('\w+|[,.:;!?]')
def match_pat(parse, no, pat):
    matches = []
    
    stopwords = re_token.findall(pat.pattern)
    norm_tags  = ' '.join([tk.tag_ if tk.norm_ not in stopwords else tk.norm_ for tk in parse])
    lemma_tags  = ' '.join([get_lemma(tk, stopwords) for tk in parse])
    origin_tags = ' '.join([tk.tag_ if tk.text not in stopwords else tk.text for tk in parse])

    matches.extend(iterate_match(no, parse, pat, norm_tags))
    matches.extend(iterate_match(no, parse, pat, lemma_tags))
    matches.extend(iterate_match(no, parse, pat, origin_tags))
    
    # unique and in order
    uniq_matches = []
    for match in matches:
        if match not in uniq_matches:
            uniq_matches.append(match)
    return uniq_matches


# find all less overlap and return dict type
def remove_overlap(parse, gets):
    overlap = np.asarray([False] * len(parse))
    overlap_level = np.asarray([None] * len(parse))
    
    gets = sorted(gets, key=lambda get: len(get['ngram'].split(' ')), reverse=True)
    gets = sorted(gets, key=lambda get: level_table[get['level']], reverse=True)

    new_gets = []
    for get in gets:
        start, end = get['range']
        # ngram is not all overlapped
        if not all(overlap[start:end]) or all(overlap_level[start:end] == get['level']) : 
            overlap[start:end] = True
            overlap_level[start:end] = get['level']
            new_gets.append(get)

    return new_gets


def iterate_pats(parse, pat_groups):      
    gets = []
    for i, group in enumerate(pat_groups):
        for each in group:
            no, level, pat = each['no'], each['level'], each['pat']

            # 1. if match pattern
            matches = match_pat(parse, no, pat)
            if not matches: continue
            
            for (start, end) in matches:
                ngram = ' '.join([el.text for el in parse[start:end]])
                gets.append({'group': i, 'no': no, 'level': level, 'range': (start, end), 'ngram': ngram})
 
    gets = remove_overlap(parse, gets)
    
    gets = [{'no': get['no'], 'group': get['group'], 'level': get['level'], 'ngram': get['ngram'], 
             'category': Egp.get_category(get['no']), 'subcategory': Egp.get_subcategory(get['no']),
             'statement': Egp.get_statement(get['no'])} for get in gets]

    return gets


### Recommend

def recommend_pats(gets, pat_groups):
    recs = []
    for get in gets:
        group, level = get['group'], get['level']

        rec = filter(lambda el: level_table[level] < level_table[el['level']], pat_groups[group])
        recs.append( [{'no': el['no'], 'level': el['level'], 
                       'category': Egp.get_category(el['no']), 'subcategory': Egp.get_subcategory(el['no']),
                       'statement': Egp.get_statement(el['no']), 'highlight': Egp.get_highlight(el['no'])} for el in rec] )
        
    return recs