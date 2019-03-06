#!/usr/bin/env python
# coding: utf-8
from collections import Counter
from itertools import groupby
from operator import itemgetter
import fileinput
import json


def parse_input(line):
    # word, pid = line.strip.rsplit(maxsplit=1)
    return line.strip().rsplit(maxsplit=1)


if __name__ == "__main__":
    input_iterator = map(parse_input, fileinput.input())
    for word, records in groupby(input_iterator, key=itemgetter(0)):
        pattern_counter = Counter(pid for _, pid in records)
        output_obj = {'word': word, 'counter': list(pattern_counter.most_common())}
        print(json.dumps(output_obj))
