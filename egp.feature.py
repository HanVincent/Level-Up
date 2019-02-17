#!/usr/bin/env python
import sys, os, re
from itertools import product
from collections import defaultdict
from collections import Counter
from nltk.corpus import stopwords
from math import log
import spacy
nlp = spacy.load('en')

def read_pats(filename):
    patdict = {}
    for line in open(filename).readlines():
        try:
            nos, pat = line.strip().split('\t')
            for no in nos.split(','):
                patdict[int(no)] = pat
        except:
            pass
    return patdict

def parse_sent(text):
    text = text.strip()
    doc = nlp(text)
    '''for sent in doc.sents:
        print('# text = {}'.format(sent.text))
        for token in nlp(sent.text):
            if token.dep_ == 'ROOT':
                print(token.i+1, token.text, token.lemma_, token.pos_, token.tag_, 0, token.dep_, sep='\t')
            else:
                print(token.i+1, token.text, token.lemma_, token.pos_, token.tag_, token.head.i+1, token.dep_, sep='\t')
        print()'''
    return [ (token.text, token.lemma_, token.tag_) for sent in doc.sents for token in nlp(sent.text) ]
    

if __name__ == '__main__':
    patdict = read_pats('egp.pattern.txt')
    pats = ['a lot JJR', '^in addition ,', '((RB )?([A-Z]+ HYPH )?(JJ|VBN)( ,| and)? ){3,}', 'much JJR NN']
    for line in open('egp.train.txt').readlines():
        no, level, sents = line.strip().split('\t')
        no = int(no)
        if no not in [11, 107, 108, 109, 110] or no not in patdict: continue
        for sent in sents.split(' ||| '):
            sent = sent[:sent.index('(') if '(' in sent else -1]
            parse = parse_sent(sent)
            words =  ' '.join([x for x, y, z in parse])
            lemmas = ' '.join([y.lower() for x, y, z in parse])
            tags = ' '.join([z for x, y, z in parse])
            #print (no, lemmas)
            #print (no, tags)
            pat = patdict[no]
            stopwords = re.findall('[a-z]+', pat)
            tags = ' '.join([z if y not in stopwords else y for x, y, z in parse])
            if re.findall(pat, tags): # or re.findall(pat, lemmas):
                print (no, level, words, re.findall(pat, tags))
            else:
                print (no, words)
                print (no, tags)
                print (no, pat)
            
    '''            sent = "In addition, remember that a bike, even a good one, is a lot cheaper than a car."
    #sent = 'A timid, shy, self-conscious, over-sensitive and vulnerable person can yearn to make friends with someone who is very self-assured, confident, decisive, even bossy.'
    sent = 'Although it is a second-hand computer which one of my colleagues sold me, it is a much better investment than the bicycle, I think.'''
