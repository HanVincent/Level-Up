### Mapper
from collections import Counter
from itertools import combinations
from utils.preprocess import normalize
import fileinput


for line in fileinput.input():
    tokens = normalize(line).split()

    for n in range(1, 6):
        ngram_count = Counter(combinations(tokens, n))
        for ngram, count in ngram_count.items():
            ngram = sorted(ngram)
            print(' '.join(ngram), count, sep='\t')
