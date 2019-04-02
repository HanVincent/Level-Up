from textdistance import LCSSeq
from collections import defaultdict, Counter
from utils.preprocess import normalize
from utils.config import level_table
import re, json
import numpy as np
import pandas as pd

class EGP:
    '''#	SuperCategory	SubCategory	Level	Lexical Range	guideword	Can-do statement	Example'''
    def __init__(self, filename='English_Grammar_Profile.csv'):
        column_names = ["Index", "Category", "Subcategory", "Level",
                        "Guideword", "Statement", "Example"]
        self.df = pd.read_csv(filename,
                              header=0,
                              usecols=[0, 1, 2, 3, 5, 6, 7],
                              names=column_names,
                              index_col="Index")

        self.df = self.df.replace(np.nan, '', regex=True)
        self.df['Example'] = self.df['Example'].apply(lambda el: '|||'.join(el.split('\n\n')))
        
        self.pattern_groups = self.df.groupby(['Category', 'Subcategory']).groups
        
        self.pat_dict = self.read_patterns('egp.regex.pattern.txt')

        self.lcs = LCSSeq()        
        
        with open('counters.json', 'r', encoding='utf8') as f:
            self.counters = json.load(f)
            self.counters = {no: Counter(self.counters[no]) for no in self.counters}

        with open('sentences.json', 'r', encoding='utf8') as f:
            self.sentences = json.load(f)
        

    def save_csv(self):
        self.df.to_csv('egp.new.csv')

    def get_category(self, index):
        return self.df.loc[index]['Category']

    def get_subcategory(self, index):
        return self.df.loc[index]['Subcategory']

    def get_level(self, index):
        return self.df.loc[index]['Level']

    def get_statement(self, index):
        return self.df.loc[index]['Statement']

    def pattern_exist(self, index):
        return index in self.pat_dict
    
    def get_pattern(self, index):
        return self.pat_dict[index]
    
    def get_patterns(self):
        return self.pat_dict

    def get_recommend(self, no: int, match: str, ngram: str):
        candidates = self.pattern_groups[(self.get_category(no), self.get_subcategory(no))]
        candidates = filter(lambda can: level_table[self.get_level(can)] - level_table[self.get_level(no)] == 1, candidates) # only get level higher by 1
        candidates = map(lambda can: str(can), candidates) # to str
        candidates = filter(lambda can: can in self.counters, candidates) # filter non-exist

        match, ngram = match.split(' '), ngram.split(' ')
        
        def max_lcs(key):
            key_match, key_ngram = key.split('|')
            score = self.lcs.similarity(match, key_match.split(' ')) + self.lcs.similarity(ngram, key_ngram.split(' '))
            return score
        
        max_no, max_key, max_value = None, '', 0
        for num in candidates:
            key = max( self.counters[num].keys(), key=max_lcs )
            value = self.counters[num][key]

            if value > max_value:
                max_key, max_value = key, value
                max_no = num

        if max_no:
            return (max_no, self.sentences[max_no][max_key][0]) # return (max_no, max_key)
        else:
            return (None, '')

    
    def read_patterns(self, filename='egp.regex.pattern.txt'):
        adv_dict = {}
        for line in open('dict.lexicon.txt', 'r', encoding='utf8'):
            key, vocabs = line.strip().split('\t')
            if key in adv_dict: continue

            adv_dict[key] = vocabs.replace(',', '|')

        keys = adv_dict.keys()

        pat_dict = {}
        for line in open(filename, 'r', encoding='utf8'):
            try:
                no, pat = line.strip().split('\t')
            except Exception:
                print("Exception:", line)

            for key in keys:
                if key in pat:
                    pat = pat.replace(key, '(' + adv_dict[key] + ')')

            pat_dict[int(no)] = re.compile(pat)

        return pat_dict