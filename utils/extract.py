import re
import nltk
import requests
from bs4 import BeautifulSoup 
from readability import Document

re_url = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def remove_sometag(text):
    soup = BeautifulSoup(text, 'html.parser')
        
    # remove underline and hyperlink
    invalid_tags = ['u', 'a', 'strong']
    for tag in invalid_tags: 
        for match in soup.findAll(tag):
            match.replaceWithChildren() 
    return str(soup)


def clean_content(url):
    
    # remove all attributes
    def _remove_all_attrs(soup):
        for tag in soup.find_all(True): 
            tag.attrs = {}
        return soup
    
    if not re_url.match(url): return url
    
    new_content = []
    response = requests.get(url)
    # doc = remove_sometag(Document(response.text).summary())
    doc = Document(response.text).summary()
    soup = BeautifulSoup(doc)
    text = soup.get_text()

    return text