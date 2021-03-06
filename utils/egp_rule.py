from utils.EGP import Egp

def extra_rules(no, segment):
    if no == 7: # hyphenated adj
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
            if tk.tag_ == 'JJR' and tk.text.endswith('er') and len(tk.text) > 4:
                return tk.lemma_[-1] != tk.lemma_[-2] and tk.text[-3] == tk.text[-4]
    
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
    
    elif no == 31: # very GRADABLE_JJ
        return segment[1].text in Egp.lexicon['GRADABLE_JJ']
    
    elif no == 32: # DEGREE_RB GRADABLE_JJ
        return segment[0].text in Egp.lexicon['DEGREE_RB'] and segment[1].text in Egp.lexicon['GRADABLE_JJ']
    
    elif no == 33: # JJ_IN
        return ' '.join([tk.text for tk in segment]) in Egp.lexicon['JJ_IN']
    
    elif no == 34: # too GRADABLE_JJ
        return segment[1].text in Egp.lexicon['GRADABLE_JJ']
    
    elif no == 46: # LIMITING_JJ NN
        return segment[0].text in Egp.lexicon['LIMITING_JJ']
    
    elif no == 48: # LINKING_VB JJ
        return segment[0].lemma_ in Egp.lexicon['LINKING_VB']
    
    elif no == 49: # PREFIX_JJ
        return segment[0].text in Egp.lexicon['PREFIX_JJ']
    
    elif no == 53: # DEGREE_JJ( JJ)? NN[^\n ]{,2}
        return segment[0].text in Egp.lexicon['DEGREE_JJ']
        
    elif no == 62: # repeat + est
        for tk in segment:
            if tk.tag_ == 'JJS' and tk.text.endswith('est') and len(tk.text) > 5:
                return tk.text[-4] == tk.text[-5] and tk.lemma_[-1] != tk.lemma_[-2]
    
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
    
    elif no == 81: # PLACE_RB
        return segment[0].text in Egp.lexicon['PLACE_RB']
    
    elif no == 82: # FREQUENCY_RB
        return segment[0].text in Egp.lexicon['FREQUENCY_RB']
    
    elif no == 85: # TIME_RB
        return segment[0].text in Egp.lexicon['TIME_RB']
    
    elif no == 87: # DEGREE_RB JJ
        return segment[0].text in Egp.lexicon['DEGREE_RB']
    
    elif no == 88: # DEGREE_RB
        return segment[0].text in Egp.lexicon['DEGREE_RB']
    
    elif no == 89: # MANNER_RB
        return segment[0].text in Egp.lexicon['MANNER_RB']
    
    elif no == 90: # LINKING_RB
        return segment[0].text in Egp.lexicon['LINKING_RB']
    
    elif no == 91: # FOCUS_RB
        return segment[0].text in Egp.lexicon['FOCUS_RB']
    
    elif no == 93: # CERTAINTY_RB
        return segment[0].text in Egp.lexicon['CERTAINTY_RB']
    
    elif no == 94: # STANCE_RB
        return segment[0].text in Egp.lexicon['STANCE_RB']
    
    elif no == 102: # SEQUENCE_RB
        return segment[0].text in Egp.lexicon['SEQUENCE_RB']
    
    elif no == 110: # DISTANCE_RB
        return segment[0].text in Egp.lexicon['DISTANCE_RB']
    
    elif no == 112: # very TIME_RB
        return segment[1].text in Egp.lexicon['TIME_RB']
    
    elif no == 113: # TIME_RB|DEGREE_RB
        return segment[0].text in Egp.lexicon['TIME_RB'] or segment[0].text in Egp.lexicon['DEGREE_RB']
    
    elif no == 115: # DEGREE_RB GRADABLE_JJ
        return segment[0].text in Egp.lexicon['DEGREE_RB'] and segment[1].text in Egp.lexicon['GRADABLE_JJ']
    
    elif no == 116: # (MANNER_RB VB[^\n ]{,1})|(VB[^\n ]{,1} MANNER_RB)
        return segment[0].text in Egp.lexicon['MANNER_RB'] or segment[1].text in Egp.lexicon['MANNER_RB']
    
    elif no == 117: # TIME_RB|SEQUENCE_RB
        return segment[0].text in Egp.lexicon['TIME_RB'] or segment[0].text in Egp.lexicon['SEQUENCE_RB']
    
    elif no == 118: # DEGREE_RB RB
        return segment[0].text in Egp.lexicon['DEGREE_RB']
    
    elif no == 120: # STANCE_RB
        return segment[0].text in Egp.lexicon['STANCE_RB'] 

    elif no == 121: # DEGREE_RB (PRP\$ |DT )?(JJ )?(NN[^\n ]{,2}|PRP)
        return segment[0].text in Egp.lexicon['DEGREE_RB'] 
    
    elif no == 122: # DEGREE_RB PRONOUN
        return segment[0].text in Egp.lexicon['DEGREE_RB'] 
    
    elif no == 123: # DEGREE_RB DETERMINER
        return segment[0].text in Egp.lexicon['DEGREE_RB'] 
    
    elif no == 125: # DEGREE_RB (JJR|more JJ|less JJ)
        return segment[0].text in Egp.lexicon['DEGREE_RB'] 
    
    elif no == 126: # DEGREE_RB JJ
        return segment[0].text in Egp.lexicon['DEGREE_RB'] 
    
    elif no == 127: # (NN[^\n ]{,2}|PRP) FREQUENCY_RB VB[^\n ]{,1}
        return segment[1].text in Egp.lexicon['FREQUENCY_RB'] 
    
    elif no == 130: # TIME_RB (IN|CC|[,.!?;])
        return segment[0].text in Egp.lexicon['TIME_RB'] 
    
    elif no == 131: # PLACE_RB (IN|CC|[,.!?;])
        return segment[0].text in Egp.lexicon['PLACE_RB'] 
    
    elif no == 135: # MANNER_RB (IN|CC|[,.!?;])
        return segment[0].text in Egp.lexicon['MANNER_RB']
    
    elif no == 136: # DEGREE_RB (IN|CC|[,.!?;])
        return segment[0].text in Egp.lexicon['DEGREE_RB']
    
    elif no == 137: # ^(CERTAINTY_RB|STANCE_RB|SEQUENCE_RB)
        return segment[0].text in Egp.lexicon['CERTAINTY_RB'] or segment[0].text in Egp.lexicon['STANCE_RB'] or segment[0].text in Egp.lexicon['SEQUENCE_RB']
    
    elif no == 140: # DISTANCE_RB
        return segment[0].text in Egp.lexicon['DISTANCE_RB']
    
    elif no == 141: # very (TIME_RB|DEGREE_RB)
        return segment[1].text in Egp.lexicon['TIME_RB'] or segment[1].text in Egp.lexicon['DEGREE_RB']
    
    else:
        return True