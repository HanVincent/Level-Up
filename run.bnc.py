#!/usr/bin/env python
# coding: utf-8

# In[8]:


#!/usr/bin/env python
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


from math import log
from itertools import groupby
from collections import defaultdict, Counter

import spacy
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex

def custom_tokenizer(nlp):
    import re
    
    infix_re  = re.compile(r'''[.\,\?\:\;\...\‘\’\`\“\”\"\'~]''')
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=None)

nlp = spacy.load('en_core_web_lg') 
nlp.tokenizer = custom_tokenizer(nlp)


# In[36]:


from utils.preprocess import *
from utils.grammar import *


# In[10]:


from utils.Dictionary import Dictionary
Dict = Dictionary()


# In[11]:


# only used for testing
import re
re_token = re.compile('\w+|[,.:;!?]')
def is_match(parse, pat):
    ### rule to catch
    stopwords = re_token.findall(pat.pattern)
    norm_tags  = ' '.join([tk.tag_ if tk.norm_ not in stopwords else tk.norm_ for tk in parse])
    lemma_tags  = ' '.join([get_lemma(tk, stopwords) for tk in parse])
    origin_tags = ' '.join([tk.tag_ if tk.text not in stopwords else tk.text for tk in parse])

    return pat.search(norm_tags) or pat.search(lemma_tags) or pat.search(origin_tags)
    


# In[12]:


def level_vocab(parse):
    annotate = [(tk.text, Dict.lookup(tk.lemma_)) for tk in parse]
    return annotate


# In[13]:


def main_profiling(content):
    # content = normalize(content)
    
    sent_profiles = []
    for sent in nlp(content).sents:
        parse = nlp(normalize(sent.text))
        
        # 1. find non-overlapped matches
        gets = iterate_pats(parse, pat_groups) # match patterns in groups
        # print(gets)
        # if not gets: continue # non-match
        
        # 2. recommend related higher pattern in the same group
        recs  = recommend_pats(gets, pat_groups)
        # print(recs)
        
        sent_profiles.append({'sent': sent.text, 'parse': ' '.join([tk.text for tk in parse]), 
                              'gets': gets, 'recs': recs })

    return sent_profiles


# In[14]:


pat_dict  = Egp.get_patterns()
sent_dict = Egp.get_examples()

### TEMP
# delete = [no for no in pat_dict] # no < 1020 or no > 1050
# for no in delete: del pat_dict[no]
delete = [no for no in sent_dict if no not in pat_dict]
for no in delete: del sent_dict[no]
###

pat_groups = Egp.get_group_patterns()


# In[15]:


from nltk.tokenize.treebank import TreebankWordDetokenizer


# In[23]:


detokenizer = TreebankWordDetokenizer()
detokenizer.detokenize("I 'm handsome".split(' '))


# In[30]:


lines = open('/atom/corpus/general/BNC/bnc.txt', 'r').readlines()


# In[37]:


word_pattern_counter = defaultdict(Counter)

for line in lines[:100]:
    line = detokenizer.detokenize(line.strip().split(' '))
    parse = nlp(normalize(line))

    gets = iterate_pats(parse, pat_groups) # match patterns in groups
    for get in gets:
        pattern = pat_dict[get['no']].pattern
        
        tokens = get['ngram'].split(' ')
        for tk in tokens:
            word_pattern_counter[tk][pattern] += 1


# In[29]:


word_pattern_counter


# In[39]:


4880000 / 100 * 3.46 / 3600


# In[ ]:




