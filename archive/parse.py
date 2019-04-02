# -*- coding: utf-8 -*-
import fileinput
from utils.preprocess import normalize

import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

def custom_tokenizer(nlp):
    import re

    infix_re = compile_prefix_regex(nlp.Defaults.infixes)
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=None)


nlp = spacy.load('en_core_web_lg') 
nlp.tokenizer = custom_tokenizer(nlp)


if __name__ == '__main__':
    for text in fileinput.input():
        doc = nlp(normalize(text), disable=['ner'])
        for sent in doc.sents:
            parse = [sent.text]
            
            for token in nlp(sent.text):
                children = ','.join([str(child.i) for child in token.children])
                if token.dep_ == 'ROOT':
                    parse.append('|'.join([str(token.i), token.text, token.lemma_, token.norm_, token.pos_, token.tag_, token.dep_, "-1", children]))
                else:
                    parse.append('|'.join([str(token.i), token.text, token.lemma_, token.norm_, token.pos_, token.tag_, token.dep_, str(token.head.i), children]))
            print('\t'.join(parse))
