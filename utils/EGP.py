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
        
        self.pat_dict, self.lexicon = self.read_patterns('egp.regex.pattern.txt')
        
        self.norm_pat_dict = {}
        for line in open('egp.norm.pattern.txt', 'r', encoding='utf8'):
            no, norm_pattern = line.strip().split('\t')
            self.norm_pat_dict[int(no)] = norm_pattern
    

    def read_patterns(self, filename='egp.regex.pattern.txt'):
        adv_dict = {}
        for line in open('data/lexicon.txt', 'r', encoding='utf8'):
            key, vocabs = line.strip().split('\t')
            if key in adv_dict: continue

            adv_dict[key] = vocabs.split(',') 
            
        keys = adv_dict.keys()

        pat_dict = {}
        for line in open(filename, 'r', encoding='utf8'):
            no, pat = line.strip().split('\t')

            for key in keys:
                if key in pat:
                    pat = pat.replace(key, '(' + '|'.join(adv_dict[key]) + ')')

            pat_dict[int(no)] = re.compile(pat)

        return pat_dict, adv_dict

    
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
    
    def get_norm_pattern(self, index):
        return self.norm_pat_dict[index]

Egp = EGP()
