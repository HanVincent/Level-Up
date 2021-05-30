import re
import requests
from itertools import product
from bs4 import BeautifulSoup
from readability import Document


def recover_abbreviation(sent):
    # S + be
    sent = sent.replace("i'm", "i am").replace("i've", "i have").replace("you're", "you are").replace("you've", "you have").replace("we're", "we are").replace("they're", "they are").replace("i'll", "i will").replace(
        "you'll", "you will").replace("we'll", "we will").replace("they'll", "they will").replace("it's", "it is").replace("that's", "that is").replace("i'd", "I would").replace("there's", "there is").replace("there're", "there are")

    # MD + not
    sent = sent.replace("isn't", "is not").replace("aren't", "are not").replace("wasn't", "was not").replace("weren't", "were not").replace("don't", "do not").replace("doesn't", "does not").replace("didn't", "did not").replace("haven't", "have not").replace("hasn't", "has not").replace("hadn't", "had not").replace("can't", "can not").replace("cannot", "can not").replace(
        "couldn't", "could not").replace("won't", "will not").replace("wouldn't", "would not").replace("daren't", "dare not").replace("mayn't", "may not").replace("mightn't", "might not").replace("mustn't", "must not").replace("needn't", "need not").replace("oughtn't", "ought not").replace("shalln't", "shall not").replace("shouldn't", "should not")

    # others
    sent = sent.replace("let's", "let us")  # .replace("n't", " not")

    return sent


def remove_multispace(sent):
    return ' '.join(sent.split())


def recover_lowercase_i(sent):
    return ' '.join(["I" if tk == "i" else tk for tk in sent.split(' ')])


def normalize(sent):
    sent = sent.strip()
    sent = sent.lower()

    sent = recover_abbreviation(sent)
    sent = remove_multispace(sent)
    sent = recover_lowercase_i(sent)
    # sent = sent.capitalize()

    return sent


def duplicate_sent(sent):
    sent = sent.replace('\\', '')
    tokens = []
    for token in sent.split():
        tokens.append(token.split('/') if '/' in token else [token])

    sents_compositions = product(*tokens)
    sents = [' '.join(sent) for sent in sents_compositions]

    return sents


re_url = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def extract_main_content(url):

    def _remove_all_attrs(soup):
        for tag in soup.find_all(True):
            tag.attrs = {}
        return soup

    def _remove_sometag(text):
        soup = BeautifulSoup(text, 'html.parser')

        # remove underline and hyperlink
        invalid_tags = ['u', 'a', 'strong']
        for tag in invalid_tags:
            for match in soup.findAll(tag):
                match.replaceWithChildren()
        return str(soup)

    if not re_url.match(url):
        return url

    response = requests.get(url)
    # doc = _remove_sometag(Document(response.text).summary())
    doc = Document(response.text).summary()
    soup = BeautifulSoup(doc, features="lxml")
    text = soup.get_text()

    return text
