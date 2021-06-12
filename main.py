#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Models.VocabRecommend import VocabRecommend
from Models.ProfileRecommend import ProfileRecommend
from Models.LanguageModel import LanguageModel
from Models.EVP import EVP
from Models.EGP import EGP
from Models.Parser import Parser
from Models.PatternRecommend import PatternRecommend
from utils.stringUtils import extract_main_content

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

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
    if not request_data:
        return jsonify({'result': 'Should not be empty'})

    content = request_data['content']
    match, suggestions = patternRecommend.suggest(content)

    return jsonify({'match': match, 'suggestions': suggestions})


@app.route('/sentences', methods=['POST'])
def sentences():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'result': 'Should not be empty'})

    ngram = request_data['ngram']
    sentences = list(profileRecommend.get_ngram_sentences(ngram, 1))

    return jsonify({'sentences': sentences})


# post /profiling data: { content: str , access: str}
@app.route('/profiling', methods=['POST'])
def profiling():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'result': 'Should not be empty'})

    if request_data['access'] == 'url':
        content = extract_main_content(request_data['content'])  # url
    else:
        content = request_data['content']

    # print(content)
    sentence_profiles = profileRecommend.profile(content)

    return jsonify({'profiles': sentence_profiles})


# post /vocabulary data: { sentence: str }
@app.route('/vocabulary', methods=['POST'])
def vocabulary():
    request_data = request.get_json()
    if not request_data:
        return jsonify({'result': 'Should not be empty'})

    sentence = request_data['sentence']

    vocabs = vocabRecommend.vocab(sentence)

    return jsonify({'vocabs': vocabs})


if __name__ == "__main__":
    data_directory = './data'

    parser = Parser()
    egp = EGP(data_directory)
    evp = EVP(data_directory)
    lm = LanguageModel(data_directory)

    patternRecommend = PatternRecommend(parser, egp, evp, lm)
    profileRecommend = ProfileRecommend(parser, egp, evp)
    vocabRecommend = VocabRecommend(parser, egp, evp)

    app.run(host='127.0.0.1', port=8888)
