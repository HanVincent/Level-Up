def recover_abbr(sent):
    # S + be
    sent = sent.replace("i'm", "i am").replace("i've", "i have").replace("you're", "you are").replace("you've", "you have").replace("we're", "we are").replace("they're", "they are").replace("i'll", "i will").replace("you'll", "you will").replace("we'll", "we will").replace("they'll", "they will").replace("it's", "it is").replace("that's", "that is").replace("i'd", "I would").replace("there's", "there is").replace("there're", "there are")

    # MD + not
    sent = sent.replace("isn't", "is not").replace("aren't", "are not").replace("wasn't", "was not").replace("weren't", "were not").replace("don't", "do not").replace("doesn't", "does not").replace("didn't", "did not").replace("haven't", "have not").replace("hasn't", "has not").replace("hadn't", "had not").replace("can't", "can not").replace("cannot", "can not").replace("couldn't", "could not").replace("won't", "will not").replace("wouldn't", "would not").replace("daren't", "dare not").replace("mayn't", "may not").replace("mightn't", "might not").replace("mustn't", "must not").replace("needn't", "need not").replace("oughtn't", "ought not").replace("shalln't", "shall not").replace("shouldn't", "should not")

    # others
    sent = sent.replace("let's", "let us")

    return sent


def remove_multispace(sent):
    return ' '.join(sent.split())


def recover_i(sent):
    return ' '.join(["I" if tk == "i" else tk for tk in sent.split(' ')])


def normalize(sent):
    sent = sent.strip()
    sent = sent.lower()

    sent = recover_abbr(sent)
    sent = remove_multispace(sent)
    sent = recover_i(sent)
    sent = sent.capitalize()

    return sent
