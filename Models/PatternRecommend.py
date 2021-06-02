from Models.Recommend import Recommend
from itertools import groupby


class PatternRecommend(Recommend):
    def __init__(self, parser, egp, evp, lm):
        super(PatternRecommend, self).__init__(parser, egp, evp)
        self.language_model = lm
        self.skip_patterns = [9, 12]

    def _get_vocab_level_score(self, ngram):
        levels = [self.evp.get_level(token) for token in ngram.split()]
        score = sum([self.evp.level_mapping[level]
                    if level else 0 for level in levels]) / len(levels)
        return score

    def _normalize_tag(self, tag):
        return self.egp.tag2pos_mapping[tag]+'.' if tag in self.egp.tag2pos_mapping else tag

    def _suggest_patterns(self, ngram_candidates, pre_sent, pos):
        pattern_suggestions = []
        for rule_num, ngram_group in groupby(ngram_candidates, lambda pattern: pattern['rule_num']):
            ngram_group = filter(lambda ngram: len(
                ngram['tokens']) < 7, ngram_group)
            # ngram_group = filter(lambda ngram: len(Bnc.sentences[ngram]) > 1, ngram_group)

            # 1. sort by language model
            # 2. sort by vocab level
            scores = map(lambda ngram: (ngram['ngram'],
                                        self.language_model.score(pre_sent, ngram['ngram'])),
                         ngram_candidates)
            scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
            scores = map(lambda score: (*score,
                                        self._get_vocab_level_score(score[0])),
                         scores)
            scores = sorted(scores, key=lambda x: x[2], reverse=True)[:5]
            ngrams = [score[0] for score in scores]
            ngrams_avg_lm_score = sum(score[1]
                                      for score in scores) / len(scores)
            # TODO: ngram is necessary?
            pattern_suggestions.append({'rule_num': rule_num,
                                        'level': self.egp.get_level(rule_num),
                                        'pos': self._normalize_tag(pos),
                                        'lm': ngrams_avg_lm_score,
                                        'pattern': self.egp.get_norm_pattern(rule_num),
                                        'ngrams': ngrams, 
                                        'ngram': ngrams[0],
                                        'category': self.egp.get_category(rule_num),
                                        'subcategory': self.egp.get_subcategory(rule_num),
                                        'statement': self.egp.get_statement(rule_num)})

        # sort by lm
        pattern_suggestions = sorted(
            pattern_suggestions, key=lambda t: t['lm'], reverse=True)

        return pattern_suggestions

    def _get_suggestions(self, target_word, pre_sent, matches):
        matches = [
            match for match in matches if target_word.i in match['indices']]

        patterns = []
        target_match = max(
            matches, key=lambda match: self.egp.level_mapping[match['level']], default=None)
        if target_match:
            target_match['pattern'] = self.egp.get_norm_pattern(
                target_match['rule_num'])

            # 1. higher level than current one
            # 2. not the same rule num or not in skip_patterns
            # 3. target word in ngram tokens
            ngram_candidates = self.mongoDBClient.get_ngram_candidates(
                self.egp.get_higher_levels(target_match['level']),
                self.skip_patterns + [target_match['rule_num']],
                target_word.text)

            patterns = self._suggest_patterns(
                ngram_candidates, pre_sent, target_word.tag_)

        return target_match, {'patterns': patterns, 'collocations': []}

    def suggest(self, content):
        content = content.strip()
        if not content:
            return content, []  # empty content

        # get sentences
        # TODO: is it necessary to re-parse last sentence?
        sentences = list(self.parser.parse(content).sents)
        last_sent = sentences[-1]

        matches, parsed_entry = self.match_patterns(last_sent.text)

        target_word = next(
            (tk for tk in list(parsed_entry)[::-1] if tk.is_alpha), parsed_entry[-1])
        pre_sent = ' '.join(tk.text for tk in parsed_entry[:target_word.i])
        target_match, suggestions = self._get_suggestions(
            target_word, pre_sent, matches)

        return target_match, suggestions
