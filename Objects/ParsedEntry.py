class ParsedEntry(list):
    '''
    @param: entry - Factsheet what is aids ?	0|Factsheet|factsheet|factsheet|PROPN|NNP|ROOT|-1|2,4	1|what|what|what|NOUN|WP|nsubj|2|	2|is|be|is|VERB|VBZ|relcl|0|1,3	3|aids|aid|aids|NOUN|NNS|attr|2|	4|?|?|?|PUNCT|.|punct|0|
    '''

    def __init__(self, entry):
        parts = [part for part in entry.strip().split('\t') if part]
        origin_text, tokens = parts[0], parts[1:]

        self.extend([DotDict(token, self) for token in tokens])


class DotDict(dict):

    def __init__(self, token, doc):
        index, text, lemma, norm, pos, tag, dep, head, children = token.split(
            '|')
        children = children.strip()

        self.i = int(index)

        # normalize text
        self.text = text.lower()
        self.norm_ = norm.lower()
        self.lemma_ = lemma.lower()

        self.dep_ = dep
        self.pos_ = pos
        self.tag_ = tag
        self.head_ = int(head)
        self.children_ = children
        self.doc = doc

    def __getattr__(self, name):
        if name == 'head':
            return self.doc[self.head_]
        elif name == 'children':
            return [self.doc[int(e)] for e in self.children_.split(',')] if self.children_ else []
        else:
            return self[name]

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"
