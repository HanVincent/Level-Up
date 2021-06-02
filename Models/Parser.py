import spacy
import en_core_web_lg
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex


class Parser:

    def __init__(self, model_size='en_core_web_lg'):
        try:
            self.nlp = spacy.load(model_size)
        except:
            self.nlp = en_core_web_lg.load()
        finally:
            self.nlp.tokenizer = self.custom_tokenizer(self.nlp)

    def parse(self, text):
        return self.nlp(text, disable=['ner'])

    def custom_tokenizer(self, nlp):
        infix_re = compile_prefix_regex(nlp.Defaults.infixes)
        prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
        suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

        return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer,
                         token_match=None)

    def preparse_format(self, text):
        # please normalize first
        doc = self.parse(text)
        for sent in doc.sents:
            result = [sent.text]
            for token in self.parse(sent.text):
                children = ','.join([str(child.i) for child in token.children])
                if token.dep_ == 'ROOT':
                    result.append('|'.join([str(token.i), token.text, token.lemma_, token.norm_, token.pos_, token.tag_, token.dep_, "-1", children]))
                else:
                    result.append('|'.join([str(token.i), token.text, token.lemma_, token.norm_, token.pos_, token.tag_, token.dep_, str(token.head.i), children]))
            yield '\t'.join(result)
