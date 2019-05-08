import gzip
fs = gzip.open('../coca.spacy.dep.txt.gz', 'rt', encoding='utf8')
ws = gzip.open('coca.parse.txt.gz', 'wt', encoding='utf8')

entries = fs.read().split('\n\n')
for entry in entries:
    if not entry: continue
    lines = entry.split('\n')

    new_line = []
    for line in lines:
        if not line: continue
        
        index, token, lemma, dep, tag, pos, head, children = line.split('\t')
        if head == index: 
            head = '-1'
        new_line.append('|'.join((index, token, lemma, pos, tag, dep, head, children)))
    print('\t'.join(new_line), file=ws)

ws.close()
