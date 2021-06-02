from Models.Recommend import Recommend
import string


class ProfileRecommend(Recommend):
    def __init__(self, parser, egp, evp):
        super(ProfileRecommend, self).__init__(parser, egp, evp)
        self.skip_patterns = set([46])
        self.punctuations = set(string.punctuation)

    def profile(self, content):
        sentence_profiles = []
        # TODO: need to re-parse again?
        for sent in self.parser.parse(content).sents:
            matches, parsed_entry = self.match_patterns(sent.text)

            # 4. recommend related higher pattern in the same group
            recs = [self._recommend_patterns(match) for match in matches]

            sentence_profiles.append({'sentence': sent.text,
                                      'tokens': [tk.text for tk in parsed_entry],
                                      'matches': matches, 'recs': recs})
        return sentence_profiles

    def _recommend_patterns(self, match):
        rule_num, match, ngram = match['rule_num'], match['match'], match['ngram']

        # TODO: would like to store in DB as well and get it from DB
        same_group_rule_nums = self.egp.pattern_groups[(
            self.egp.get_category(rule_num), self.egp.get_subcategory(rule_num))]
        same_group_rule_nums = filter(
            lambda can: can not in self.skip_patterns and can not in self.egp.patterns, same_group_rule_nums)
        same_group_rule_nums = filter(
            lambda can: self.egp.get_level(can) in self.egp.get_higher_levels(self.egp.get_level(rule_num)), same_group_rule_nums)

        # 1. get current non-punct tokens
        # 2. find rule_num with tokens
        tokens = [tk for tk in ngram.split(' ') if tk not in self.punctuations]
        for rule_num in same_group_rule_nums:
            sentence = 'No sentence example'
            for ngram in self.mongoDBClient.get_ngrams(rule_num, tokens):
                # TODO: Only get the first element, should find similar ngram
                sentence = self.mongoDBClient.get_sentences(ngram, count=1)
                if sentence:
                    break

            return {'rule_num': rule_num, 'level': self.egp.get_level(rule_num),
                    'category': self.egp.get_category(rule_num),
                    'subcategory': self.egp.get_subcategory(rule_num),
                    'statement': self.egp.get_statement(rule_num),
                    'sentence': sentence}
        return None

    def get_ngram_sentences(self, ngram, count=0):
        return self.mongoDBClient.get_sentences(ngram, count)
