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