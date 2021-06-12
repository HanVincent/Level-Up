import os
from pymongo import ASCENDING, TEXT, MongoClient
from pymongo.operations import UpdateOne


class MongoDBClient:

    def __init__(self):
        username = os.environ['MONGODB_USERNAME']
        password = os.environ['MONGODB_PASSWORD']
        client = MongoClient(
            f'mongodb+srv://{username}:{password}@cluster0.wvqgg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

        database = client.grammar_rules

        self.ngram_collection = database.ngram_counts  # collection = table
        self.sentence_collection = database.sentences

    def create_indexes(self):
        self.ngram_collection.create_index('level')
        self.ngram_collection.create_index([('token', TEXT)])
        self.ngram_collection.create_index(
            [('rule_num', ASCENDING), ('match', ASCENDING), ('ngram', ASCENDING)])

        self.sentence_collection.create_index([('ngram', TEXT)])

    def bulk_inc_ngram_count(self, documents):
        operations = [
            UpdateOne({'rule_num': document['rule_num'], 'match': document['match'], 'ngram': document['ngram']},
                      {'$set': document, '$inc': {'count': count}},
                      upsert=True) for document, count in documents
        ]
        res = self.ngram_collection.bulk_write(operations, ordered=False)
        print(res)

    def add_sentences(self, documents):
        res = self.sentence_collection.insert_many(documents, ordered=False)
        print(res)

    def get_ngram_candidates(self, higher_levels, skip_rule_nums, headword):
        return self.ngram_collection.find({
            'level': {
                '$in': higher_levels
            },
            'rule_num': {
                '$nin': skip_rule_nums
            },
            'tokens': headword
        }, sort=[('rule_num', ASCENDING)])

    def get_ngrams(self, rule_num, tokens):
        return map(lambda entry: entry['ngram'], self.ngram_collection.find({
            'rule_num': rule_num,
            'tokens': {
                '$elemMatch': {
                    '$in': tokens
                }
            }
        }, {'ngram': 1}))

    def get_sentences(self, ngram, count=0):
        return map(lambda entry: entry['sentence'], self.sentence_collection.find({'ngram': ngram}, {'sentence': 1}).limit(count))
