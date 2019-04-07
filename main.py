#!/usr/bin/env python
# coding: utf-8

from utils.preprocess import normalize
from utils.parser import nlp
from utils.extract import clean_content
from utils.auto_suggest import auto_suggest, suggest_sentences
from utils.grammar import generate_candidates, iterate_all_patterns, iterate_all_gets, remove_overlap
from utils.vocabulary import level_vocab


# In[3]:


def main_suggesting(content):
    content = content.strip()

    if not content: return None # empty content
    if len(content.split(' ')) < 2: return None

    # normalize
    content = normalize(content)
    last_sent = list(nlp(content, disable=['ner']).sents)[-1]
    last_word = last_sent[-1]

    return auto_suggest(last_word.text, last_word.tag_, last_sent.text.rsplit(' ', maxsplit=1)[0])

    
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
    parse = nlp(normalize(sentence))
    vocabs = level_vocab(parse)
    
    return vocabs


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


# post /suggesting data: { content: str }
@app.route('/suggesting', methods=['POST'])
def suggesting():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})

    content = request_data['content']
    suggestions = main_suggesting(content)

    return jsonify({'suggest': suggestions})


@app.route('/examples', methods=['POST'])
def examples():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})

    ngram = request_data['ngram']
    sentences = suggest_sentences(ngram)

    return jsonify({'examples': sentences})


# post /profiling data: { content: str , access: str}
@app.route('/profiling', methods=['POST'])
def profiling():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})

    if request_data['access'] == 'url':
        content = clean_content(request_data['content']) # url
    else:
        content = request_data['content']
        
    # print(content)
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


# In[ ]:





# In[ ]:





# In[ ]:


# print(parse)

# for sent in generate_candidates(parse):
#     print(' '.join([tk.text for tk in sent]))


# In[ ]:




