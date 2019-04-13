### Reducer
import fileinput
from collections import Counter
from itertools import groupby
from operator import itemgetter


def parse_input(line):
    ngram, count = line.strip().split('\t')
    return ngram, int(count)

iterable = map(parse_input, fileinput.input())
for ngram, records in groupby(iterable, itemgetter(0)):
    total = sum(count for _, count in records)
    print(ngram, total, sep='\t')