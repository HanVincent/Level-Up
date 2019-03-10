from .Dictionary import Dictionary

Dict = Dictionary()

def level_vocab(parse):
    annotate = [{'token': tk.text, 'level': Dict.lookup(tk.lemma_)} 
                for tk in parse]
    return annotate