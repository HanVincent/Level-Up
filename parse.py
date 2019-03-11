# -*- coding: utf-8 -*-
import fileinput
import spacy
from utils.preprocess import normalize


if __name__ == '__main__':
    nlp = spacy.load('en_core_web_lg')

    for text in fileinput.input():
        doc = nlp(normalize(text))
        for sent in doc.sents:
            print('# text = {}'.format(sent.text))
            for token in nlp(sent.text):
                
                children = ','.join([str(child.i) for child in token.children])
                if token.dep_ == 'ROOT':
                    print(token.i, token.text, token.lemma_, token.pos_, token.tag_, token.dep_, -1, children, sep='\t')
                else:
                    print(token.i, token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.head.i, children, sep='\t')
            print()
