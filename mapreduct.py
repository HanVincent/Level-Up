word_pattern_counter = defaultdict(Counter)

for line in lines[:100]:
    line = detokenizer.detokenize(line.strip().split(' '))
    parse = nlp(normalize(line))

    gets = iterate_pats(parse, pat_groups) # match patterns in groups
    for get in gets:
        pattern = pat_dict[get['no']].pattern
        
        tokens = get['ngram'].split(' ')
        for tk in tokens:
            word_pattern_counter[tk][pattern] += 1