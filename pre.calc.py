#!/usr/bin/env python
# coding: utf-8

from utils.parser import nlp
from utils.grammar import generate_candidates, iterate_all_patterns, remove_overlap
from collections import defaultdict, Counter
import gzip, pickle

name = 'new.recommend.prune.pickle'  

class DotDict(dict):
    
    def __init__(self, token, doc):
        index, text, lemma, norm, pos, tag, dep, head, children = token.split('|')
        children = children.strip()

        self.i = int(index)
        ###
        self.text = text.lower()
        self.norm_ = norm.lower()
        self.lemma_ = lemma.lower()
        ###
        
        self.dep_ = dep
        self.pos_ = pos
        self.tag_ = tag
        self.head_ = int(head)
        self.children_ = children
        self.doc = doc
    
    def __getattr__(self, name):
        if name == 'head':
            return self.doc[head_]
        elif name == 'children':
            return [self.doc[int(e)] for e in self.children_.split(',')] if self.children_ else []
        else:
            return self[name]
    
    
class Parse(list):

    def __init__(self, entry):
        tokens = [token for token in entry.strip().split('\t') if token]
        text, tokens = tokens[0], tokens[1:]
        
        self.extend([DotDict(token, self) for token in tokens])



from itertools import product
import json

def duplicate_sent(sent):
    sent = sent.replace('\\', '')
    tokens = []
    for token in sent.split():
        tokens.append(token.split('/') if '/' in token else [token])

    composes = product(*tokens)
    sents = [' '.join(compose) for compose in composes]
    
    return sents

def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    results = [s for result in results for sent in result for s in duplicate_sent(sent) ] # flatten
    
    return results


fs = gzip.open('bnc.parse.txt.gz', 'rt', encoding='utf8')

counts = Counter()
ngrams = defaultdict(Counter)
sentences = defaultdict(list)

for i, entry in enumerate(fs):
    parse = Parse(entry)
    
    gets = iterate_all_patterns(parse)

    gets = remove_overlap(parse, gets)

    text = ' '.join([tk.text for tk in parse])
    for get in gets:
        counts[(get['match'], get['no'])] += 1
        ngrams[(get['match'], get['no'])][get['ngram']] += 1

        text = ' '.join([ '<w>' + tk.text + '</w>' if i in get['indices'] else tk.text for i, tk in enumerate(parse)])
        sentences[ get['ngram'] ].append(text)

    if i % 20000 == 0:
        print(i)
        with open(name, 'wb') as handle:
            pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(name, 'wb') as handle:
    pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)


### Clean sentences
        
HiFreWords = open('data/HiFreWords', 'r').read().split('\t')

def clean(sents):
    def score(tks):
        return sum([t in HiFreWords for t in tks]) / len(tks)

    sents = map(lambda sent: (sent, sent.replace('<w>', '').replace('</w>', '').split()), sents)
    sents = sorted(sents, key=lambda each: score(each[1]), reverse=True)
    
    less_sents = [sent for sent in sents if len(sent[1]) >= 10 and len(sent[1]) <= 25]
    if len(less_sents) > 0:
        sents = less_sents
    sents = [sent[0] for sent in sents]
    return sents


for ngram in sentences:
    new_sents = clean(sentences[ngram])
    sentences[ngram] = new_sents
    
    
with open(name, 'wb') as handle:
    pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)