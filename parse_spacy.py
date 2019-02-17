# -*- coding: utf-8 -*-
import fileinput
import spacy


if __name__ == '__main__':
    nlp = spacy.load('en')

    for text in fileinput.input():
        text = text.strip()
        doc = nlp(text)
        for sent in doc.sents:
            print('# text = {}'.format(sent.text))
            for token in nlp(sent.text):
                if token.dep_ == 'ROOT':
                    print(token.i+1, token.text, token.lemma_, token.pos_, token.tag_, 0, token.dep_, sep='\t')
                else:
                    print(token.i+1, token.text, token.lemma_, token.pos_, token.tag_, token.head.i+1, token.dep_, sep='\t')
            print()
