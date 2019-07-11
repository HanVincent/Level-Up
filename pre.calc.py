
from utils.parser import nlp


# In[3]:


import gzip, pickle

from utils.grammar import generate_candidates, iterate_all_patterns, remove_overlap


# In[ ]:


class DotDict(dict):
    
    def __init__(self, token, doc):
        index, text, lemma, norm, pos, tag, dep, head, children = token.split('|')
        children = children.strip()

        self.i = int(index)
        ###
        self.text = text.lower()
        self.norm_ = norm.lower()
        self.lemma_ = lemma.lower()
        ###
        
        self.dep_ = dep
        self.pos_ = pos
        self.tag_ = tag
        self.head_ = int(head)
        self.children_ = children
        self.doc = doc
    
    def __getattr__(self, name):
        if name == 'head':
            return self.doc[head_]
        elif name == 'children':
            return [self.doc[int(e)] for e in self.children_.split(',')] if self.children_ else []
        else:
            return self[name]
    
    
class Parse(list):

    def __init__(self, entry):
        tokens = [token for token in entry.strip().split('\t') if token]
        text, tokens = tokens[0], tokens[1:]
        
        self.extend([DotDict(token, self) for token in tokens])


# In[ ]:


from utils.preprocess import duplicate_sent
from itertools import product
import json

def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    results = [s for result in results for sent in result for s in duplicate_sent(sent) ] # flatten
    
    return results


# In[ ]:


fs = gzip.open('bnc.parse.txt.gz', 'rt', encoding='utf8')


# In[ ]:


from collections import defaultdict, Counter

counts = Counter()
ngrams = defaultdict(Counter)
sentences = defaultdict(list)

for i, entry in enumerate(fs):
# for i, sentence in enumerate(dict_sentences):
    parse = Parse(entry)
#     parse = nlp(sentence, disable=['ner'])

    # 1. generate possible sentences
    parses = generate_candidates(parse)

    # 2. find patterns for each candidate
    gets = [get for parse in parses for get in iterate_all_patterns(parse)]

    # 3. remove duplicate
    gets = remove_overlap(parse, gets)

    text = ' '.join([tk.text for tk in parse])
    for get in gets:
        counts[(get['match'], get['no'])] += 1
        ngrams[(get['match'], get['no'])][get['ngram']] += 1

    # for sentences
    gets = iterate_all_patterns(parses[-1])
    gets = remove_overlap(parse, gets)
    for get in gets:
        text = ' '.join([ '<w>' + tk.text + '</w>' if i in get['indices'] else tk.text for i, tk in enumerate(parse)])
        sentences[ get['ngram'] ].append(text)

        
    if i % 20000 == 0:
        print(i)
        with open('recommend.prune.pickle', 'wb') as handle:
            pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[ ]:


with open('recommend.prune.pickle', 'wb') as handle:
    pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[ ]:





# In[ ]:





# In[2]:


from collections import Counter, defaultdict

import pickle

with open('recommend.prune.pickle', 'rb') as handle:
    info = pickle.load(handle)
    counts, ngrams, sentences = info['counts'], info['ngrams'], info['sentences']


number_groups = defaultdict(Counter)
pattern_groups = defaultdict(set)
ngram_groups = defaultdict(lambda: defaultdict(set))

for pattern, no in counts.keys():
    number_groups[no][pattern] += 1

    for key in pattern.split(' '):
        pattern_groups[key].add((pattern, no))

    for ngram in ngrams[(pattern, no)]:
        for n_key in ngram.split(' '):
            ngram_groups[(pattern, no)][n_key].add(ngram)


# In[3]:


to_remove = []
for key in ngrams:
    for ngram in ngrams[key]:
        if ngrams[key][ngram] <= 2:
            to_remove.append((key, ngram))
            counts[key] -= ngrams[key][ngram]


# In[6]:


for to in to_remove:
    del ngrams[to[0]][to[1]]
    
for ngram in sentences:
    sentences[ngram] = sentences[ngram][:1]


# In[7]:


with open('recommend.prune.slim.pickle', 'wb') as handle:
    pickle.dump({ 'counts': counts, 'ngrams': ngrams, 'sentences': sentences }, handle, protocol=pickle.HIGHEST_PROTOCOL)


# In[ ]:




