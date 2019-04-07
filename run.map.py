### Mapper
from collections import Counter
from itertools import combinations
from utils.preprocess import normalize
import fileinput


for line in fileinput.input():
    tokens = normalize(line).split()

    for n in range(1, 8):
        ngram_count = Counter(list(combinations(tokens, n)))
        for ngram, count in ngram_count.items():
            ngram = sorted(ngram)
            print('{}\t{}'.format(' '.join(ngram), count))
