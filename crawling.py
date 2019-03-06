#!/usr/bin/env python
# coding: utf-8

# In[4]:


# -*- coding: utf-8 -*-

from lxml import html
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collections import defaultdict
from time import sleep

import requests
import re, json
import tqdm


# In[5]:


USERNAME = 'englishprofile'
PASSWORD = 'vocabulary'

base_url = "http://vocabulary.englishprofile.org"


# In[6]:


re_i_span = re.compile('<span class="i">(.*?)</span>')
re_level_cls = re.compile(r"freq-[ABC][12]" )


# In[7]:


def crawl(endpoint):
    return requests.get(base_url + endpoint, auth=(USERNAME, PASSWORD))


# ### Crawl Vocabulary List

# In[ ]:


# hrefs = []
# indices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# for index in indices:
#     endpoint = "/dictionary/word-list/us/a1_c2/" + index
    
#     response = crawl(endpoint)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     ul = soup.find('div',attrs={'id':'groupResult'}).find('ul')
#     lis = ul.find_all('li')
    
#     print(len(lis))

#     hrefs.extend([li.find('a')['href'] for li in lis])


# In[ ]:


# total_len = len(hrefs)

# ws = open('dict.slim.txt', 'w', encoding='utf8')
# for idx, href in enumerate(hrefs):
#     print("{} / {}".format(idx, total_len))
    
#     response = crawl(href)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     ul = soup.find('div',attrs={'id':'result'}).find('ul')
#     lis = ul.find_all('li')
    
#     for li in lis:
#         a_href = li.find('a')['href']
        
#         main_span = li.find('span', {'class': 'display'})
        
#         vocab = main_span.find('span', {'class': 'base'}).decode_contents()
#         vocab = re_i_span.sub(r'<i>\1</i>', vocab)
        
#         pos = main_span.find_all('span', {'class': 'pos'})
#         pos = ','.join([p.text for p in pos])
        
#         gw  = main_span.find('span', {'class': 'gw'})
#         gw  = gw.text if gw else ""
        
#         level = main_span.find('span', {'class': re_level_cls})
#         level = level.text if level else ""
        
#         entry = {
#             'href': a_href,
#             'vocab': vocab,
#             'pos': pos,
#             'gw': gw,
#             'level': level
#         }
        
#         print(entry['vocab'], entry['level'], entry['pos'], entry['gw'], entry['href'], sep='\t', file=ws)
        
# ws.close()


# ### Crawl detailed dictionary

# In[8]:


def process_gw(gw_block):
    sense_div = gw_block.find('div', attrs={'class': 'sense'}) 
        
    # get phrase information block
    if gw_block.find('div', attrs={'class': 'phraserec'}):
        is_phrase = True
        phrase = gw_block.find('h3', attrs={'class': 'phrase'}).decode_contents()
        phrase = re_i_span.sub(r'<i>\1</i>', phrase)

    # get word definition block
    else:
        is_phrase = False
        gw = gw_block.find('h3', attrs={'class': 'gw'})
        gw = gw.text.strip() if gw else ""

        gram = sense_div.find_all('abbr', {'class': 'gram'})
        gram = ' '.join([g.text for g in gram])

    level = sense_div.find('span', {'class': re_level_cls})
    level = level.text if level else ""   

    definition = sense_div.find('span', attrs={'class': 'def'}).text.strip()
    dic_div = sense_div.find('div', attrs={'class': 'examp-block'})
    if dic_div:
        dic_examples = [ex.text for ex in dic_div.find_all('blockquote', attrs={'class': 'examp'})]
    else:
        dic_examples = []
    
    clc_block = sense_div.find('blockquote', attrs={'class': 'clc'})
    if clc_block:
        clc_block.find('div', attrs={'class': 'clc_before'}).clear()
        src_div = clc_block.find('div', attrs={'class': 'src'})
        if src_div:
            src = src_div.text.strip()
            src_div.clear()
        else:
            src = "NONE"
            
        clc = clc_block.text.strip() + ' (' + src + ')'
    else:
        clc = "NONE (NONE)"
        

    if is_phrase:
        return {'phrase': phrase, 'is_phrase': is_phrase, 'level': level, 
                'definition': definition, 'dic_examples': dic_examples,
                'clc': clc}
    else:
        return {'gw': gw, 'gram': gram, 'is_phrase': is_phrase, 'level': level, 
                'definition': definition, 'dic_examples': dic_examples,
                'clc': clc}


# In[9]:


cache = set()
def is_repeated(href):
    idx = urlparse(href).path.split('/')[-1]
    
    if idx in cache:
        return True
    else:
        cache.add(idx)
        return False


# In[ ]:


dictionary = defaultdict(lambda: defaultdict(lambda: [])) # word -> pos -> entry
phrase_dictionary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))) # word -> pos -> phrase -> entry

file = 'dict.slim.txt'
for i, line in enumerate(open(file, 'r', encoding='utf8')):
    vocab, level, pos, gw, href = line.split('\t')
    # avoid repeated crawling
    if is_repeated(href): continue
    
    try:
        print(i, vocab)
    except:
        print("ERROR: ", i)
        continue

    response = crawl(href)
    sleep(0.5) # Time in seconds.
    
    soup = BeautifulSoup(response.text, 'html.parser')

    main_div = soup.find('div',attrs={'id':'dictionary_entry'}).find('span', attrs={'class': 'entry'})
    
    hw = main_div.find('div', attrs={'class': 'head'}).find('h1', attrs={'class': 'hw'}).text

    pos_blocks = main_div.find_all('div', attrs={'class': 'posblock'})

    for pos_block in pos_blocks:
        ### Phrase or Word
        pos_span = pos_block.find('span', attrs={'class': 'posgram'})
        pos_gram = pos_span.text.strip() if pos_span else ""

        gw_blocks = pos_block.find_all('div', attrs={'class': 'gwblock'})

        for gw_block in gw_blocks:
            entry = process_gw(gw_block)
            dictionary[hw][pos_gram].append(entry)


        ### Phrasal Verbs
        ph_blocks = pos_block.find_all('div', attrs={'class': 'phrasal_verb'})

        for ph_block in ph_blocks:
            phrase = ph_block.find('h3', attrs={'class': 'phrase'}).text.strip()

            gw_blocks = ph_block.find_all('div', attrs={'class': 'gwblock'})

            for gw_block in gw_blocks:
                entry = process_gw(gw_block)                
                phrase_dictionary[hw][pos_gram][phrase].append(entry)
                


# In[ ]:


with open('dict.json', 'w', encoding='utf8') as ws:
    json.dump(dictionary, ws)
    
with open('phrase_dict.json', 'w', encoding='utf8') as ws:
    json.dump(phrase_dictionary, ws)


# In[ ]:





# In[16]:


print('café'.encode('utf8'))


# In[ ]:




