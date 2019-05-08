#!/usr/bin/env python
# coding: utf-8

from utils.preprocess import normalize
from utils.parser import nlp
from utils.extract import clean_content
from utils.auto_suggest import auto_suggest, suggest_sentences
from utils.grammar import generate_candidates, iterate_all_patterns, iterate_all_gets, remove_overlap
from utils.vocabulary import level_vocab


# In[80]:


def main_suggesting(content):
    content = content.strip()
    if not content: return None, [] # empty content
    # if len(content.split(' ')) < 2: return None

    # get sentences
    sentences = list(nlp(content, disable=['ner']).sents)
    last_sent = sentences[-1]
    
    # normalize
    content = normalize(last_sent.text)
    parse = nlp(content, disable=['ner'])

    # 1. generate possible sentences
    parses = generate_candidates(parse)
    
    # 2. find patterns for each candidate
    gets = [get for parse in parses for get in iterate_all_patterns(parse)]

    # 3. remove duplicate
    gets = remove_overlap(parse, gets)

    # 4. recommend related higher pattern in the same group
    get, sugs = auto_suggest(parse, gets)
    
    return get, sugs

    
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
        recs = iterate_all_gets(parse, gets)
        
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
    get, suggestions = main_suggesting(content)

    return jsonify({'get': get, 'suggestions': suggestions})


@app.route('/examples', methods=['POST'])
def examples():
    request_data = request.get_json()
    if not request_data: return jsonify({'result': 'Should not be empty'})

    ngram = request_data['ngram']
    sentences = suggest_sentences(ngram)

    return jsonify({'ngram': ngram, 'examples': sentences})


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

