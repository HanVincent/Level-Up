import spacy, en_core_web_lg
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


try:
    nlp = spacy.load('en_core_web_lg') 
except:
    nlp = en_core_web_lg.load()
    
nlp.tokenizer = custom_tokenizer(nlp)