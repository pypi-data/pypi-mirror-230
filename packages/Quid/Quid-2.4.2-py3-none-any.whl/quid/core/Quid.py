from typing import List, Dict

from quid.core.InternalMatch import InternalMatch
from quid.core.QuidMatcher import QuidMatcher
from quid.core.QuidMerger import QuidMerger
from quid.match.Match import Match
from quid.match.MatchSpan import MatchSpan
from quid.core.Text import Text
import re
from quid.core.Token import Token
from datasketch import MinHash, MinHashLSH
import warnings
from itertools import product
import multiprocessing
from tqdm import tqdm


def work(source_text, target_text, tokens, initial_match_length, look_back_limit, look_ahead_limit,
         min_levenshtein_similarity, lsh_threshold, min_length_match_positions, hashes):
    quid = QuidMatcher(initial_match_length, look_back_limit, look_ahead_limit, min_levenshtein_similarity,
                       lsh_threshold)
    result = quid.compare(source_text, target_text, tokens, min_length_match_positions, hashes)
    return result


# noinspection PyMethodMayBeStatic
# This algorithm is based on the algorithm by Dick Grune, see https://dickgrune.com/Programs/similarity_tester/.
# And a Javascript implementation, see
# https://people.f4.htw-berlin.de/~weberwu/simtexter/522789_Sofia-Kalaidopoulou_bachelor-thesis.pdf
class Quid:
    tokens: List[Token]
    texts: List[Text]
    list_of_split_matches: List[InternalMatch]
    num_of_splits: int
    num_of_done_splits: int
    # Value relevant for fuzzy matching
    HASH_PERM: int = 128

    SENTENCE_DELIMITER = '\u2190'
    RESERVED_CHARACTERS = ['\u2190', '\u2191']

    def __init__(self, min_match_length: int = 5,
                 look_back_limit: int = 10,
                 look_ahead_limit: int = 3,
                 max_merge_distance: int = 2,
                 max_merge_ellipse_distance: int = 10,
                 include_text_in_result: bool = True,
                 keep_ambiguous_matches: bool = False,
                 min_levenshtein_similarity: float = 0.85,
                 split_long_texts: bool = False,
                 split_length: int = 30000,
                 max_num_processes: int = 1,
                 show_progress: bool = False):

        """
        :param min_match_length: The minimum number of tokens of a match
        :param look_back_limit: The maximum number of tokens to skip when extending a match backwards
        :param look_ahead_limit: The maximum number of tokens to skip when extending a match forwards
        :param max_merge_distance: The maximum distance in tokens between to matches considered for merging
        :param max_merge_ellipse_distance: The maximum distance in tokens between two matches considered for merging
        where the target text contains an ellipses between the matches
        :param include_text_in_result: Include matched text in the returned data structure
        :param keep_ambiguous_matches: If False, for a match with multiple matched segments in the source text,
        multiple matches will be returned. Otherwise, only the first match will be returned.
        :param min_levenshtein_similarity: The threshold for the minimal levenshtein similarity between tokens (and the
        initial n-grams) to be accepted as a match
        :param split_long_texts: If True, texts longer than the split_length will be split in subtexts of length
        split_length for faster processing
        :param split_length: Texts, which are longer than this threshold, are split into subtexts of this length, if
        split_long_texts is set to True
        :param max_num_processes: The maximum number of processes for parallel processing when split_long_texts is set
        to True
        """

        if min_match_length < 1:
            raise ValueError('min match length must be >= 1')

        if look_back_limit < 0:
            raise ValueError('look back limit must be positive')

        if look_ahead_limit < 0:
            raise ValueError('look ahead limit must be positive')

        if max_merge_distance < 0:
            raise ValueError('max merge distance must be positive')

        if max_merge_ellipse_distance < 0:
            raise ValueError('max merge ellipse distance must be positive')

        if min_levenshtein_similarity < 0 or min_levenshtein_similarity > 1:
            raise ValueError('min levenshtein similarity must be between 0 and 1')

        if split_length < 0:
            raise ValueError('split length must be positive')

        if max_num_processes < 0:
            raise ValueError('max number of processes must be positive')

        if max_num_processes == 1 and split_long_texts:
            warnings.warn('Split long texts does not have any effect if the maximum number of processes is one')

        self.initial_match_length = min(3, min_match_length)
        self.min_match_length = min_match_length
        self.look_back_limit = look_back_limit
        self.look_ahead_limit = look_ahead_limit
        self.max_merge_distance = max_merge_distance
        self.max_merge_ellipse_distance = max_merge_ellipse_distance
        self.forward_references = {}
        self.texts = []
        self.tokens = []
        self.include_text_in_result = include_text_in_result
        self.keep_ambiguous_matches = keep_ambiguous_matches
        self.min_levenshtein_similarity = min_levenshtein_similarity
        self.lsh_threshold = max(0.0, min_levenshtein_similarity - 0.15)
        self.split_long_texts = split_long_texts
        self.split_length = split_length
        self.max_num_processes = max_num_processes
        self.list_of_split_matches = []
        self.show_progress = show_progress
        self.progress_bar = None

    def __matcher_callback(self, result):
        self.list_of_split_matches.extend(result)
        if self.show_progress:
            self.progress_bar.update(1)

    def prepare_source_data(self, source_text: str):
        """
        Takes a source text and returns a tuple consisting of a map and a list of hashes. The map maps strings to their
        starting positions in the text.
        :param source_text: The source text
        :return: A tuple consisting of a map of strings and their starting positions and a list of hashes of the strings
        in the map.
        """
        input_texts: List[str] = [source_text]
        self.texts, self.tokens = self.__read_input(input_texts)
        return self.__prepare_source_data(self.texts[0])

    def __prepare_source_data(self, text: Text):
        min_length_match_positions: Dict[str, List[int]]
        hashes: MinHashLSH
        min_length_match_positions, hashes = self.__make_min_length_match_starting_positions(text)
        return min_length_match_positions, hashes

    def compare(self, source_text: str, target_text: str,
                cached_min_length_match_positions: Dict[str, List[int]] = None,
                cached_hashes: MinHashLSH = None) -> List[Match]:
        """
        Compare the two input texts and return a list of matching sequences.
        :param source_text: A source text
        :param target_text: A target text
        :param cached_min_length_match_positions: A map of strings to their starting positions in the source text
        :param cached_hashes: A MinHashLSH object
        :return: A list of found matches
        """

        if not source_text or not target_text:
            return []

        self.list_of_split_matches = []
        input_texts: List[str] = [source_text, target_text]
        self.texts, self.tokens = self.__read_input(input_texts)

        if self.split_long_texts:
            source_end_token = self.texts[0].tk_end_pos
            target_start_token = self.texts[1].tk_start_pos
            target_end_token = self.texts[1].tk_end_pos

            source_texts = []
            target_texts = []

            quot, rem = divmod(source_end_token, self.split_length)

            for i in range(0, quot):
                sub_start = max(0, (i * self.split_length) - self.initial_match_length)
                sub_end = min(source_end_token, ((i + 1) * self.split_length) + self.initial_match_length)
                source_texts.append(Text(sub_start, sub_end))

            sub_start = quot * self.split_length
            sub_end = sub_start + rem
            source_texts.append(Text(sub_start, sub_end))

            quot, rem = divmod(target_end_token - target_start_token, self.split_length)

            for i in range(0, quot):
                sub_start = target_start_token + max(0, (i * self.split_length) - self.initial_match_length)
                sub_end = target_start_token + min(target_end_token, ((i + 1) * self.split_length) +
                                                   self.initial_match_length)
                target_texts.append(Text(sub_start, sub_end))

            sub_start = target_start_token + (quot * self.split_length)
            sub_end = sub_start + rem

            target_texts.append(Text(sub_start, sub_end))

            text_combos = product(source_texts, target_texts)
            if self.show_progress:
                num_of_splits = len(source_texts) * len(target_texts)
                self.progress_bar = tqdm(total=num_of_splits)

            pool = multiprocessing.Pool(self.max_num_processes)

            for c in text_combos:
                min_length_match_positions, hashes = self.__prepare_source_data(c[0])
                pool.apply_async(work, args=(c[0], c[1], self.tokens, self.initial_match_length,
                                             self.look_back_limit, self.look_ahead_limit,
                                             self.min_levenshtein_similarity, self.lsh_threshold,
                                             min_length_match_positions, hashes),
                                 callback=self.__matcher_callback)

            pool.close()
            pool.join()

            if self.show_progress:
                self.progress_bar.close()

            quid_merger = QuidMerger(self.min_match_length, self.max_merge_distance, self.max_merge_ellipse_distance,
                                     self.keep_ambiguous_matches)
            merged_matches = quid_merger.compare(self.list_of_split_matches, self.tokens, self.texts)
        else:
            if not cached_min_length_match_positions or not cached_hashes:
                min_length_match_positions, hashes = self.__prepare_source_data(self.texts[0])
            else:
                min_length_match_positions = cached_min_length_match_positions
                hashes = cached_hashes

            quid_matcher = QuidMatcher(self.initial_match_length, self.look_back_limit, self.look_ahead_limit,
                                       self.min_levenshtein_similarity, self.lsh_threshold)
            internal_matches = quid_matcher.compare(self.texts[0], self.texts[1], self.tokens,
                                                    min_length_match_positions, hashes)

            quid_merger = QuidMerger(self.min_match_length, self.max_merge_distance, self.max_merge_ellipse_distance,
                                     self.keep_ambiguous_matches)
            merged_matches = quid_merger.compare(internal_matches, self.tokens, self.texts)

        result: List[Match] = []
        for internal_match in merged_matches:
            source_match_span = MatchSpan(internal_match.source_match_span.character_start,
                                          internal_match.source_match_span.character_end)
            target_match_span = MatchSpan(internal_match.target_match_span.character_start,
                                          internal_match.target_match_span.character_end)

            if self.include_text_in_result:
                segment_source_text = source_text[source_match_span.start:
                                                  source_match_span.end]
                segment_target_text = target_text[target_match_span.start:
                                                  target_match_span.end]

                source_match_span.text = segment_source_text
                target_match_span.text = segment_target_text

            result.append(Match(source_match_span, target_match_span))

        return result

    def __read_input(self, input_texts: List[str]) -> (List[Text], List[Token]):
        texts: List[Text] = []
        tokens: List[Token] = []

        for input_text in input_texts:
            tk_start_pos = len(tokens)
            tokens.extend(self.__tokenize_text(input_text))
            tk_end_pos = len(tokens)
            text = Text(tk_start_pos, tk_end_pos)
            texts.append(text)

        return texts, tokens

    def __tokenize_text(self, input_text: str) -> List[Token]:
        cleaned_text = self.__clean_text(input_text)
        tokens = []

        for match in re.finditer(r'\S+', cleaned_text):
            token = self.__clean_word(match.group())

            if len(token) > 0:
                text_begin_pos = match.start()
                text_end_pos = match.end()
                tokens.append(Token(token, text_begin_pos, text_end_pos))

        return tokens

    def __clean_text(self, input_text: str) -> str:

        for char in self.RESERVED_CHARACTERS:
            if char in input_text:
                warnings.warn(f'Text contains reserved character {char}. This might lead to unwanted behaviour.')

        input_text = re.sub('(\\[\\.\\.\\.]|\\[…]|\\.\\.\\.|…)', lambda x: '@' * len(x.group(1)), input_text)
        input_text = re.sub('[.;!?]', self.SENTENCE_DELIMITER, input_text)

        # preserve [s], [n] [er] etc.
        input_text = re.sub(r'\[([a-zA-Z]{1,3})]', '\u2191\\g<1>\u2191', input_text)

        input_text = re.sub(rf'[^\w_@{self.SENTENCE_DELIMITER}\u2191 ]', ' ', input_text)
        input_text = re.sub(r'\d', ' ', input_text)

        input_text = re.sub(r'\u2191([a-zA-Z]{1,3})\u2191', '[\\g<1>]', input_text)

        return input_text.lower()

    def __clean_word(self, input_word: str) -> str:
        input_word = input_word.replace('ß', 'ss')
        input_word = input_word.replace('ä', 'ae')
        input_word = input_word.replace('ö', 'oe')
        input_word = input_word.replace('ü', 'ue')
        input_word = input_word.replace('ey', 'ei')
        input_word = input_word.replace('[', '')
        input_word = input_word.replace(']', '')
        return input_word

    def __remove_special_characters(self, input_string: str) -> str:
        input_string = re.sub(r'[^\w@ ]|[\u03B1\u03B2]', '', input_string)

        # TODO: _ ist bei \w dabei, ist das ein Problem?
        if re.search(r'\w', input_string):
            input_string = re.sub('@', '', input_string)

        return input_string

    def __make_min_length_match_starting_positions(self, text: Text) -> (Dict[str, List[int]], MinHashLSH):
        """
        Takes a source text and returns a tuple consisting of a map and a list of hashes. The map maps strings to their
        starting positions in the text.
        :param text: The source text
        :return: A tuple consisting of a map of strings and their starting positions and a list of hashes of the strings
        in the map.
        """

        min_length_match_starting_positions: Dict[str, List[int]] = {}
        hashes: MinHashLSH = MinHashLSH(threshold=self.lsh_threshold, num_perm=self.HASH_PERM)

        text_begin_pos: int = text.tk_start_pos
        text_end_pos: int = text.tk_end_pos

        for position in range(text_begin_pos, text_end_pos - self.initial_match_length + 1):
            minimal_match_string: str = ''

            for token in self.tokens[position: position + self.initial_match_length]:
                minimal_match_string += token.text

            minimal_match_string = self.__remove_special_characters(minimal_match_string)
            minimal_match_character_set = set(minimal_match_string)
            minimal_match_hash = MinHash(num_perm=self.HASH_PERM)

            for char in minimal_match_character_set:
                minimal_match_hash.update(char.encode('utf8'))

            if minimal_match_string in min_length_match_starting_positions:
                min_length_match_starting_positions[minimal_match_string].append(position)
            else:
                hashes.insert(minimal_match_string, minimal_match_hash, False)
                min_length_match_starting_positions[minimal_match_string] = [position]

        return min_length_match_starting_positions, hashes

    def __print_matches(self, matches, literature_content, scientific_content):  # pragma: no cover

        result = ''

        for match in matches:
            similarity_literature = match.source_match_span
            similarity_scientific = match.target_match_span

            content = literature_content[
                      similarity_literature.character_start:similarity_literature.character_end]
            result += f'\n\n{similarity_literature.character_start}\t{similarity_literature.character_end}' \
                      f'\t{content}'

            content = scientific_content[
                      similarity_scientific.character_start:similarity_scientific.character_end]
            result += f'\n{similarity_scientific.character_start}\t{similarity_scientific.character_end}' \
                      f'\t{content}'

        print(result)
