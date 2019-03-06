def extra_rules(no, segment):
    if no == 10: # hyphenated adj
        for tk in segment:
            if tk.tag_ == 'JJ':
                return '-' in tk.text
        
    elif no == 13: # normal + er
        for tk in segment:
            if tk.tag_ == 'JJR':
                return not (tk.lemma_.endswith('e') or tk.lemma_.endswith('y'))

    elif no == 14: # -y + ier
        for tk in segment:
            if tk.tag_ == 'JJR':
                return tk.lemma_.endswith('y') and tk.text.endswith('ier')
    
    elif no == 17: # repeat + er
        for tk in segment:
            if tk.tag_ == 'JJR':
                return tk.lemma_[-1] != tk.lemma_[-2] and tk.text[-3] == tk.text[-4] and tk.text.endswith('er')
    
    elif no == 18: # ending with e + r
        for tk in segment:
            if tk.tag_ == 'JJR':
                return tk.lemma_.endswith('e') and tk.text.endswith('er')
    
    elif no == 19: # irregular JJR
        for tk in segment:
            if tk.tag_ == 'JJ':
                return not tk.text.startswith(tk.lemma_[:-1])
    
    elif no == 24: # repeated JJR
        return 'more and more' in ' '.join([tk.text for tk in segment]) or len(set([tk.text for tk in segment if tk.tag_ == 'JJR'])) == 1
        
    elif no == 62: # repeat + est
        for tk in segment:
            if tk.tag_ == 'JJS':
                return tk.lemma_[-1] != tk.lemma_[-2] and tk.text[-4] == tk.text[-5] and tk.text.endswith('est')
    
    elif no == 63: # normal + est
        for tk in segment:
            if tk.tag_ == 'JJS':
                return not (tk.lemma_.endswith('e') or tk.lemma_.endswith('y'))

    elif no == 64: # -y + iest
        for tk in segment:
            if tk.tag_ == 'JJS':
                return tk.lemma_.endswith('y') and tk.text.endswith('iest')
    
    elif no == 66: # ending with e + st
        for tk in segment:
            if tk.tag_ == 'JJS':
                return tk.lemma_.endswith('e') and tk.text.endswith('er')
    
    
    
    else:
        return True