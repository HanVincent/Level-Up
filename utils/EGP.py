from collections import defaultdict, Counter
from .preprocess import normalize
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

        self.pat_dict = self.read_patterns('egp.regex.pattern.txt')
        self.pat_groups = self.group_patterns()
        self.recommend_flow = self.read_recommend_flow('egp.recommend.txt')
        
        self.counters, self.sentences = self.read_counters()
        ### 
        
        self.highlight_dict = self.read_highlights('egp.highlights.txt')
        self.inverted_dict = self.invert_index(self.pat_dict)
        self.word_pattern_counter = self.read_word_pattern()
        

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

    def get_highlight(self, no):
        return self.highlight_dict[no]
    
    def pattern_exist(self, index):
        return index in self.pat_dict
    
    def get_pattern(self, index):
        return self.pat_dict[index]
    
    def get_patterns(self):
        return self.pat_dict

    def get_group_patterns(self):
        return self.pat_groups

    def get_recommend(self, no: int, ngram: str):
        numbers = self.recommend_flow[str(no)] # string num -> get str set
        tokens = set(ngram.split(' '))
        
        max_no, max_key, max_value = None, '', 0
        for num in numbers:
            if self.get_level(int(num)) > self.get_level(no) and num in self.counters:
                key = max( self.counters[num].keys(), key=lambda key: len(set(key.split(' ')) & set(tokens)) )
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
            if line.startswith('#'):
                continue
            if line.startswith('*'):
                line = line[1:]

            try:
                no, pat = line.strip().split('\t')
            except Exception:
                print("Exception:", line)

            for key in keys:
                if key in pat:
                    pat = pat.replace(key, '(' + adv_dict[key] + ')')

            pat_dict[int(no)] = re.compile(pat)

        return pat_dict

    def group_patterns(self):
        from .config import level_table

        category_groups = self.df.groupby(['Category', 'Subcategory'])
        return category_groups.groups

    def read_recommend_flow(self, file='egp.recommend.txt'):
        flow = defaultdict(set)
        for line in open(file, 'r', encoding='utf8'):
            heads, tails = line.split('\t')
            for head in heads.split(','):
                flow[head] |= set(tails.strip().split(','))
                
        return flow
    
    def read_counters(self):
        with open('tmp_counters.json', 'r', encoding='utf8') as f:
            counters = json.load(f)
            
        for no in counters:
            counters[no] = Counter(counters[no])

        with open('tmp_sentences.json', 'r', encoding='utf8') as f:
            sentences = json.load(f)
        
        return counters, sentences
    
    ###############
    
    # refactor
    def get_examples(self):
        re_parentheses = re.compile('\((?P<info>.*)\)?')
        re_level = re.compile('([ABC][12])')

        sent_dict = {}
        for index, row in self.df.iterrows():
            level = row['Level']

            new_sents = []
            for sent in row['Example'].split('|||'):
                sent = sent.strip()
                match = re_parentheses.search(sent)

                if match:
                    info = match.groupdict()['info']
                    origin_level = re_level.findall(info)
                    origin_level = origin_level[0] if origin_level else None
                    sent = sent[:match.start()]
                else:
                    origin_level = None
                    sent = sent

                new_sents.append((origin_level, normalize(sent)))

            sent_dict[index] = {'level': level, 'sents': new_sents}

        return sent_dict

    def invert_index(self, pat_dict):
        re_token = re.compile(r'\w+')

        inverted_dict = defaultdict(set)
        for number, regex in pat_dict.items():
            for tk in re_token.findall(regex.pattern):
                inverted_dict[tk].add(number)

        return inverted_dict

    def get_possible(self, word):
        if word not in self.word_pattern_counter:
            return None

        no, count = self.word_pattern_counter[word][0]
        return no
    
    def read_highlights(self, file='egp.highlights.txt'):
        highlight_dict = {}
        for line in open(file, 'r', encoding='utf8'):
            no, eg = line.strip().split('\t')
            highlight_dict[int(no)] = eg

        return highlight_dict

        
    def read_word_pattern(self, file='/home/nlplab/jjc/English_Grammar_Profile/egp_stat.jsonl'):
        import jsonlines

        with jsonlines.open(file) as reader:
            word_pattern_counter = {obj['word']: obj['counter'] for obj in reader}
        
        return word_pattern_counter
    
