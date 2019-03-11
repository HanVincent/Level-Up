from .EVP import EVP

Evp = EVP()

def level_vocab(parse):
    annotate = [{'token': tk.text, 'level': Evp.lookup(tk.lemma_)} 
                for tk in parse]
    return annotate