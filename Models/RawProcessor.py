from collections import Counter
import datetime
from Models.Parser import Parser
from Models.EGP import EGP
from Models.EVP import EVP
from Models.Recommend import Recommend
from Objects.ParsedEntry import ParsedEntry
from Models.MongoDBClient import MongoDBClient
from tqdm import tqdm
import os
import gzip


class RawProcessor:

    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.recommend = Recommend(Parser(), EGP(
            data_directory), EVP(data_directory))
        self.mongoDBClient = MongoDBClient()
        self.mongoDBClient.create_indexes()

    def calc_ngram_and_count(self, filename):
        with gzip.open(os.path.join(self.data_directory, filename), 'rt', encoding='utf8') as fs:
            local_cache_cnt = Counter()
            local_cache_sents = []
            for i, entry in enumerate(tqdm(fs), 1):
                parsed_entry = ParsedEntry(entry)

                matches, parsed_entry, full_sent_matches = self.recommend.match_patterns(
                    parsed_entry, is_parsed_content=True, return_full_sentence_matches=True)

                for match in matches:
                    key = (match['match'], match['rule_num'],
                           match['level'], match['ngram'])
                    local_cache_cnt[key] += 1

                # collect example sentences and only care for full sentences
                for match in full_sent_matches:
                    indices = set(match['indices'])
                    sentence = ' '.join(
                        '<w>' + tk.text + '</w>' if tk.i in indices else tk.text for tk in parsed_entry)
                    local_cache_sents.append(
                        {'ngram': match['ngram'], 'sentence': sentence})

                if i % 50000 == 0:
                    print(i, "Uploading to MongoDB.")

                    documents = [({
                        'match': match, 'rule_num': rule_num, 'level': level, 'ngram': ngram, 'tokens': ngram.split(' ')
                    }, count) for (match, rule_num, level, ngram), count in local_cache_cnt.items()]

                    print("Start to update ngram counts in bulk.")
                    start_time = datetime.datetime.now()
                    self.mongoDBClient.bulk_inc_ngram_count(documents)
                    local_cache_cnt = Counter()
                    end_time = datetime.datetime.now()
                    print("End update ngram counts in bulk with elapsed seconds: " +
                          str((end_time-start_time).total_seconds()))

                    print("Start to insert ngram sentences in bulk.")
                    start_time = datetime.datetime.now()
                    self.mongoDBClient.add_sentences(local_cache_sents)
                    local_cache_sents.clear()
                    end_time = datetime.datetime.now()
                    print("End insert ngram sentences in bulk with elapsed seconds: " +
                          str((end_time-start_time).total_seconds()))

                # if i == 1000000:
                #     break
