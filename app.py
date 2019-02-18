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


# post /correct data: { content: str }
@app.route('/profiling', methods=['POST'])
def correct():
    request_data = request.get_json()
    if not request_data: return jsonify({'edit': 'Should not be empty'})
    
    content = request_data['content']
    print(content)
        
#     edit_line, meta = edit(content)

    return jsonify({'edit': edit_line, 'meta': meta})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1315)