import re
import nltk
from bs4 import BeautifulSoup 
from readability import Document


def getPublishDate(html):
     # 1 year; 3 month; 5 date; 6 time  (?is)(\d{4}|\d{2})(\-|\/)(\d{1,2})(\-|\/)(\d{1,2})\s?(\d{2}:\d{2}?)
    search_result = re.search("(?is)(\d{4}|\d{2})(\-|\/)(\d{1,2})(\-|\/)(\d{1,2})", html)
    if search_result != None:
        return search_result.group(1) + '-' + search_result.group(3) + '-' + search_result.group(5)
    else:
        return ''

def remove_sometag(text):
    soup = BeautifulSoup(text, 'html.parser')
        
    # 移除底線與超連結，但保留其內部html
    invalid_tags = ['u', 'a']
    for tag in invalid_tags: 
        for match in soup.findAll(tag):
            match.replaceWithChildren() 
    return str(soup)
    
def clean_content(content, inputType):
    def sentence_tokenize(content):
        sent_text = nltk.sent_tokenize(content) 
        sent_text = [sent for sent in sent_text if '\n' not in sent]
        #sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
        return sent_text
    
    # remove all attributes
    def _remove_all_attrs(soup):
        for tag in soup.find_all(True): 
            tag.attrs = {}
        return soup
    
    new_content = []
    
    if inputType == 'url':
        soup = BeautifulSoup(content, 'html.parser')
        
        soup = _remove_all_attrs(soup)
        soup = [sub for sub in soup.find_all(['p', 'h2', 'h3']) if sub.h2 == None and sub.h3 == None]
        
        for sub_content in soup:
            tag = sub_content.name
            sub_content = re.sub('<p>|</p>|<h2>|</h2>|<h3>|</h3>', '', str(sub_content))
            new_content += [[tag, list(filter(None, sentence_tokenize(sub_content)))]]

    elif inputType == 'youtube':
        v_id = content[0]
        if '\n' not in content[1]:
            new_content.append(['p', [content[1]]])
        else:
            content = content[1].split('\n\n')
            for p in content:
                if '-->' in p:
                    p = p.split(' --> ', 1)
                    time = p[0].strip().split(':')
                    time[-1] = time[-1].split('.')[0]
                    while len(time) < 3:
                        time.insert(0, 0)
                    p[0] = '<a class="youtube-time" href="https://youtu.be/'+v_id+'?t='+time[-3]+'h'+time[-2]+'m'+time[-1]+'s" target="blank_">'+p[0].split('.', 1)[0]+'</a>'
                    p[1] = p[1].split('\n', 1)[1].replace('\n', ' ')
                    new_content.append(['p', p]) # .split('\n', 1)[-1].replace('\n', ' ')
    else:
        content = content.split('\n')
        for p in content:
            p = p.strip()
            if p:
                temp = ['p', [p]]
                new_content.append(temp)
    return new_content