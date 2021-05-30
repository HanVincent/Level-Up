from utils.stringUtils import normalize
from Models.MongoDBClient import MongoDBClient

import re
import numpy as np


class Recommend:
    def __init__(self, parser, egp, evp):
        self.mongoDBClient = MongoDBClient()
        self.re_token = re.compile('\w+|[,.:;!?]')
        self.parser = parser
        self.egp = egp
        self.evp = evp

    def match_patterns(self, content, is_parsed_content=False, return_full_sentence_matches=False):
        if is_parsed_content:
            parsed_entry = content
        else:
            content = normalize(content)
            parsed_entry = self.parser.parse(content)

        # 1. generate all possible subsentences via root
                ######  TODO: can remove parsed_entry and last alpha func
        root = next((tk for tk in parsed_entry if tk.dep_ == 'ROOT'), None)
        subsentences = self._gen_subsentences(root)

        # 2. gets all patterns for each candidate
        group_matches = [self._match_all_patterns(
            subsent) for subsent in subsentences]
        matches = [match for group in group_matches for match in group]

        # 3. remove overlapping and duplicate patterns
        matches = self._remove_overlap_matches(parsed_entry, matches)

        if return_full_sentence_matches:
            full_sent_matches = self._remove_overlap_matches(parsed_entry, group_matches[-1])
            return matches, parsed_entry, full_sent_matches
        else:
            return matches, parsed_entry

    def _gen_subsentences(self, root):
        """
        generate sentence candidates by dependency tree layer by layer (using BFS)
        @param: root
        @return: subsentences
        """
        special_deps = set('prep')
        layer = [root]  # start with root
        subsentences = [[root]]

        while True:
            # all children
            children = [child for tk in layer for child in tk.children]
            if not children:
                break

            children.extend([grandchild for child in children if child.dep_ in special_deps
                            for grandchild in child.children])  # add prep obj

            subsentences.append(
                sorted(subsentences[-1] + children, key=lambda x: x.i))

            # remove prep token in case duplicate
            layer = [child for child in children if child.dep_ not in special_deps]

        return subsentences

    def _get_matches(self, sentence, rule_num):

        def get_lemma(tk, words_in_pattern):
            lemma = tk.text if tk.lemma_ == '-PRON-' else tk.lemma_
            lemma = lemma.lower()
            return lemma if lemma in words_in_pattern else tk.tag_

        def align_token_span(match, tags):
            """
            align token span in sentences from character span given by regex match
            @param: match
            @param: tags
            """
            start_i, end_i = match.span()

            length = 0
            for i, token in enumerate(tags):
                if length >= start_i:
                    break
                length += len(token) + 1  # space len

            match_len = len(match.group().split(' '))
            return i, i + match_len

        words_in_pattern = self.re_token.findall(
            self.egp.patterns[rule_num].pattern)
        lemma_tags = [get_lemma(tk, words_in_pattern) for tk in sentence]
        origin_tags = [
            tk.tag_ if tk.text not in words_in_pattern else tk.text for tk in sentence]

        def match_pattern(rule_num, sentence, tags):
            matches = set()
            for match in self.egp.patterns[rule_num].finditer(' '.join(tags)):
                start_i, end_i = align_token_span(match, tags)

                try:
                    # extra rule
                    if self.egp.specific_rules(rule_num, sentence[start_i:end_i]):
                        matches.add((start_i, end_i, match.group()))
                except:
                    print([tk.text for tk in sentence])
                    print(rule_num, start_i, end_i)

            return matches

        all_matches = match_pattern(rule_num, sentence, lemma_tags)
        all_matches.update(match_pattern(rule_num, sentence, origin_tags))
        return all_matches

    def _match_all_patterns(self, sentence):
        """
        iterate all patterns to get grammar matches
        @param sentence
        @return grammar matches
        """
        all_matches_info = []
        for (category, subcategory), group in self.egp.pattern_groups.items():
            for rule_num in group:
                if not self.egp.is_pattern_exists(rule_num):
                    continue

                # match pattern
                matches = self._get_matches(sentence, rule_num)
                if not matches:
                    continue

                # TODO: thinking the return part
                for (start_i, end_i, match) in matches:
                    indices = [tk.i for tk in sentence[start_i:end_i]]
                    ngram = ' '.join(
                        [tk.text for tk in sentence[start_i:end_i]])
                    all_matches_info.append({'rule_num': rule_num, 'level': self.egp.get_level(rule_num),  # TODO: would like to store num not A1
                                            'indices': indices, 'ngram': ngram, 'match': match,
                                             'category': category,
                                             'subcategory': subcategory,
                                             'statement': self.egp.get_statement(rule_num)})

        return all_matches_info

    def _remove_overlap_matches(self, parsed_entry, matches):
        """
        remove overlapping matching patterns
        @param: parsed_entry - parsed sentence
        @param: matches
        """
        # sort by level first and then length of ngram
        matches = sorted(matches, key=lambda match: len(
            match['indices']), reverse=True)
        matches = sorted(
            matches, key=lambda match: self.egp.level_mapping[match['level']], reverse=True)

        new_matches = []
        overlap_marker = np.asarray([False] * len(parsed_entry))
        overlap_level = np.asarray([None] * len(parsed_entry))
        for match in matches:
            # only keep ngram is not all exactly overlapped or the level is same
            # TODO: condition is weird
            if not (np.all(np.take(overlap_marker, match['indices']))) and not (
                    np.all(np.take(overlap_level, match['indices']) == match['level'])):
                overlap_marker[match['indices']] = True
                overlap_level[match['indices']] = match['level']
                new_matches.append(match)

        # sort by category & level
        new_matches = sorted(
            new_matches, key=lambda match: self.egp.level_mapping[match['level']], reverse=True)
        new_matches = sorted(new_matches, key=lambda match: match['category'])

        return new_matches
