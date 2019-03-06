#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')


from math import log
from itertools import groupby
from collections import defaultdict, Counter

import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

def custom_tokenizer(nlp):
    import re
    
    infix_re  = re.compile(r'''[.\,\?\:\;\...\‘\’\`\“\”\"\'~]''')
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=None)

nlp = spacy.load('en_core_web_lg') 
nlp.tokenizer = custom_tokenizer(nlp)


# In[2]:


from utils.preprocess import *
from utils.grammar import *


# In[3]:


from utils.Dictionary import Dictionary
Dict = Dictionary()


# In[4]:


# only used for testing
import re
re_token = re.compile('\w+|[,.:;!?]')
def is_match(parse, pat):
    ### rule to catch
    stopwords = re_token.findall(pat.pattern)
    norm_tags  = ' '.join([tk.tag_ if tk.norm_ not in stopwords else tk.norm_ for tk in parse])
    lemma_tags  = ' '.join([get_lemma(tk, stopwords) for tk in parse])
    origin_tags = ' '.join([tk.tag_ if tk.text not in stopwords else tk.text for tk in parse])

    return pat.search(norm_tags) or pat.search(lemma_tags) or pat.search(origin_tags)
    


# In[ ]:


def level_vocab(parse):
    annotate = [(tk.text, Dict.lookup(tk.lemma_)) for tk in parse]
    return annotate


# In[ ]:


def main_profiling(content):
    # content = normalize(content)
    
    sent_profiles = []
    for sent in nlp(content).sents:
        parse = nlp(normalize(sent.text))
        
        # 1. find non-overlapped matches
        gets = iterate_pats(parse, pat_groups) # match patterns in groups
        # print(gets)
        # if not gets: continue # non-match
        
        # 2. recommend related higher pattern in the same group
        recs  = recommend_pats(gets, pat_groups)
        # print(recs)
        
        sent_profiles.append({'sent': sent.text, 'parse': ' '.join([tk.text for tk in parse]), 
                              'gets': gets, 'recs': recs })

    return sent_profiles


def main_vocabuing(sentence):
    sentence = normalize(sentence)
    parse = nlp(sentence)

    # 1. get vocabulary level
    vocabs = level_vocab(parse)
    
    return vocabs
        


# In[ ]:


pat_dict  = Egp.get_patterns()
sent_dict = Egp.get_examples()

### TEMP
# delete = [no for no in pat_dict] # no < 1020 or no > 1050
# for no in delete: del pat_dict[no]
delete = [no for no in sent_dict if no not in pat_dict]
for no in delete: del sent_dict[no]
###

pat_groups = Egp.get_group_patterns()


# In[ ]:


# group_gets = iterate_pats(nlp("long"), pat_groups)

# # group_recs  = recommend_pats(group_gets, pat_groups) # recommend patterns in same group


# In[ ]:


# %%time

# if __name__ == '__main__':
#     for no, entry in sent_dict.items():
#         level = entry['level']
#         sents = entry['sents']
        
#         # if no not in patterns_number: continue

#         for origin_level, sent in sents:
# #             parse = nlp(sent)
# #             if is_match(parse, pat_dict[no]):
# #                 pass
# #             else:
# #                 print(no, pat_dict[no].pattern, sent)
                
#             # main process
#             print(sent)
#             group_gets = iterate_pats(parse, pat_groups) # match patterns in groups
#             print(group_gets)
#             group_recs  = recommend_pats(group_gets, pat_groups) # recommend patterns in same group
#             print(group_recs)


# In[ ]:


# doc = nlp("it is the biggest and oldest museum in libya . … it is the biggest and <w> oldest museum </w> in libya .")
# for a in doc:
#     print(a.text, a.lemma_, a.norm_, a.tag_, a.pos_, a.i)
# doc.text


# In[ ]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)


@app.route('/')
def index():
    pass


# post /profiling data: { content: str }
@app.route('/profiling', methods=['POST'])
def profiling():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})
    
    content = request_data['content']
    print(content)
    
    sent_profiles = main_profiling(content)

    return jsonify({'profiles': sent_profiles})


# post /vocabuing data: { sentence: str }
@app.route('/vocabuing', methods=['POST'])
def vocabuing():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})
    
    sentence = request_data['sentence']
    
    vocabs = main_vocabuing(sentence)

    return jsonify({'vocabs': vocabs})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1315)


# In[ ]:





# In[ ]:


# egs = []

# for index, entry in Egp.get_examples().items():
#     if index not in pat_dict: continue
        
#     eg = []
#     for sent in entry['sents']:
#         level, sent = sent
#         parse = nlp(normalize(sent))
    
#         matches = match_pat(parse, index, pat_dict[index])
#         if not matches: continue
            
#         sent = []
#         for tk in parse:
#             starts = [match[0] for match in matches]
#             ends = [match[1] for match in matches]                

#             if tk.i in starts:
#                 sent.extend(['<w>', tk.text])
#             elif tk.i in ends:
#                 sent.extend(['</w>', tk.text])
#             else:
#                 sent.append(tk.text)
        
#         sent = ['I' if tk == 'i' else tk for tk in sent]
#         sent = ' '.join(sent)
#         eg.append(sent)

#     if not eg: egs.append((index, entry['sents'][0][1]))
#     else:      egs.append((index, eg[0]))
        
# with open('egp.highlights.txt', 'w', encoding='utf8') as ws:
#     for line in egs:
#         print(*line, sep='\t', file=ws)


# In[ ]:




