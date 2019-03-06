#!/usr/bin/env python
# coding: utf-8
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

from nltk.tokenize.treebank import TreebankWordDetokenizer

from utils.preprocess import normalize
from utils.grammar import get_lemma, Egp, iterate_pats

from utils.Dictionary import Dictionary

import fileinput
import spacy
import re
import os


def custom_tokenizer(nlp):
    infix_re = re.compile(r'''[.\,\?\:\;\...\‘\’\`\“\”\"\'~]''')
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    return Tokenizer(nlp.vocab,
                     prefix_search=prefix_re.search,
                     suffix_search=suffix_re.search,
                     infix_finditer=infix_re.finditer,
                     token_match=None)


def is_match(parse, pat):
    # rule to catch
    stopwords = re_token.findall(pat.pattern)
    norm_tags = ' '.join([tk.tag_ if tk.norm_ not in stopwords else tk.norm_ for tk in parse])
    lemma_tags = ' '.join([get_lemma(tk, stopwords) for tk in parse])
    origin_tags = ' '.join([tk.tag_ if tk.text not in stopwords else tk.text for tk in parse])

    return pat.search(norm_tags) or pat.search(lemma_tags) or pat.search(origin_tags)


def level_vocab(parse):
    annotate = [(tk.text, Dict.lookup(tk.lemma_)) for tk in parse]
    return annotate


pat_groups = Egp.get_group_patterns()

detokenizer = TreebankWordDetokenizer()

nlp = spacy.load(os.environ.get('SPACY_MODEL', 'en'))
nlp.tokenizer = custom_tokenizer(nlp)

Dict = Dictionary()


# only used for testing
re_token = re.compile('\w+|[,.:;!?]')

pat_dict = Egp.get_patterns()
sent_dict = Egp.get_examples()


def main():
    for line in fileinput.input():
        line = detokenizer.detokenize(line.strip().split())
        parse = nlp(normalize(line))

        gets = iterate_pats(parse, pat_groups)  # match patterns in groups
        for get in gets:
            pattern_id = get['no']
            # pattern = pat_dict[get['no']].pattern

            for tk in get['ngram'].split(' '):
                print(tk, pattern_id, sep='\t')
                # word_pattern_counter[tk][pattern] += 1


if __name__ == "__main__":
    main()
