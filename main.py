#!/usr/bin/env python
# coding: utf-8

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


# In[135]:


from nltk.tokenize.treebank import TreebankWordDetokenizer

from utils.preprocess import normalize
from utils.grammar import generate_candidates, iterate_all_patterns, iterate_all_gets, remove_overlap
from utils.vocabulary import level_vocab
from utils.extract import clean_content


# ##### http://weedyc.pixnet.net/blog/post/26181706-%E8%8B%B1%E6%96%87%E6%96%87%E6%B3%95%E8%BC%95%E9%AC%86%E5%AD%B8%EF%BC%9A%E4%BA%94%E5%A4%A7%E5%9F%BA%E6%9C%AC%E5%8F%A5%E5%9E%8B
# 
# 1. 主詞 + 動詞 S. V.
# 2. 主詞 + 動詞 + 受詞 S. V. O.
# 3. 主詞 + 動詞 + 補語 S. V. C.
# 4. 主詞 + 動詞 + 受詞 + 受詞 S. V. O1 O2
# 5. 主詞 + 動詞 + 受詞 + 補語 S. V. O. C.

# In[ ]:


from utils.explacy import print_parse_info
# print_parse_info(nlp, 'Unlike many approaches to GEC, this approach does NOT require annotated training data and mainly depends on a monolingual language model')


# In[ ]:


# # approach 1

# # root
# SENTENCE_PATTERNS = {
#     'SV': ['nsubj', 'punct'],
#     'SVO': ['nsubj', 'dobj', 'punct'],
#     'SVC': ['nsubj', 'attr', 'acomp', 'punct'],
#     'SVOO': ['nsubj', 'dative', 'dobj', 'punct'],
#     'SVOC': ['nsubj', 'ccomp', 'dobj', 'oprd', 'punct']
# }
# SENTENCE_PATTERNS = SENTENCE_PATTERNS.items()

 
# def get_first(root):
#     candidates = {}
#     for pattern, deps in SENTENCE_PATTERNS:
#         sent = [root] + [child for child in root.children if child.dep_ in deps]
#         candidates[pattern] = sorted(sent, key=lambda x: x.i)
        
#     return max(candidates.items(), key=lambda el: len(el[1]))

# get_first(get_root(parse))


# In[126]:


def main_profiling(content):
    sentence_profiles = []
    for sent in nlp(content, disable=['ner']).sents:
        # 0. parse sentence
        parse = nlp(normalize(sent.text), disable=['ner'])
        
        # 1. generate possible sentences
        parses = generate_candidates(parse)
        
        # 2. find patterns for each candidate
        gets = [get for parse in parses for get in iterate_all_patterns(parse)]

        # 3. remove duplicate
        gets = remove_overlap(parse, gets)
        
        # 4. recommend related higher pattern in the same group
        recs = iterate_all_gets(gets)
        
        # 5. return
        sentence_profiles.append({'sent': sent.text, 
                                  'parse': [tk.text for tk in parse],
                                  'gets': gets, 'recs': recs })

    return sentence_profiles


def main_vocabuing(sentence):
    sentence = normalize(sentence)
    parse = nlp(sentence)

    # 1. get vocabulary level
    vocabs = level_vocab(parse)
    
    return vocabs
        


# In[132]:


# no = Egp.get_possible("a")

group_gets = iterate_all_patterns(nlp("He is nice and friendly."))

group_recs  = iterate_all_gets(group_gets) # recommend patterns in same group


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
    return render_template('index.html')


# post /profiling data: { content: str , access: str}
@app.route('/profiling', methods=['POST'])
def profiling():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})

    if request_data['access'] == 'url':
        content = clean_content(request_data['content']) # url
    else:
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
    app.run(host='0.0.0.0', port=1316)


# In[ ]:


# egs = []

# for index, entry in Egp.get_examples().items():
#     if index not in Egp.get_patterns(): continue
        
#     eg = []
#     for sent in entry['sents']:
#         level, sent = sent
#         parse = nlp(normalize(sent))
    
#         matches = match_pat(parse, index, Egp.get_patterns()[index])
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

