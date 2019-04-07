### Reducer
import fileinput
from collections import Counter


ngram_counts = Counter()
for line in fileinput.input():
    ngram, count = line.split('\t', 1)
    ngram_counts[ngram] += int(count)

for ngram, count in ngram_counts.items():
    print('{}\t{}'.format(ngram, count))