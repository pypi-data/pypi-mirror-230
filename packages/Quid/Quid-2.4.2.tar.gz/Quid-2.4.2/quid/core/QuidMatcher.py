from typing import List, Dict, Optional
from quid.core.InternalMatch import InternalMatch
from quid.core.BestMatch import BestMatch
from quid.core.InternalMatchSpan import InternalMatchSpan
from quid.core.Text import Text
import re
from quid.core.Token import Token
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from datasketch import MinHash, MinHashLSH


# noinspection PyMethodMayBeStatic
class QuidMatcher:
    tokens: List[Token]
    texts: List[Text]
    forward_references: Dict[int, List[int]]
    # Value relevant for fuzzy matching
    HASH_PERM: int = 128

    def __init__(self, initial_match_length: int,
                 look_back_limit: int,
                 look_ahead_limit: int,
                 min_levenshtein_similarity: float,
                 lsh_threshold: float):
        """
        :param initial_match_length: The length of initial matches
        :param look_back_limit: The maximum number of tokens to skip when extending a match backwards
        :param look_ahead_limit: The maximum number of tokens to skip when extending a match forwards
        where the target text contains an ellipses between the matches
        multiple matches will be returned. Otherwise, only the first match will be returned.
        :param min_levenshtein_similarity: The threshold for the minimal levenshtein similarity between tokens (and the
        initial n-grams) to be accepted as a match
        """

        self.initial_match_length = initial_match_length
        self.look_back_limit = look_back_limit
        self.look_ahead_limit = look_ahead_limit
        self.forward_references = {}
        self.texts = []
        self.tokens = []
        self.min_levenshtein_similarity = min_levenshtein_similarity
        self.lsh_threshold = lsh_threshold

    def compare(self, source_text: Text, target_text: Text, tokens: List[Token],
                cached_min_length_match_positions: Dict[str, List[int]],
                cached_hashes: MinHashLSH) -> List[InternalMatch]:
        """
        Compare the two input texts and return a list of matching sequences.
        :param source_text: A source text
        :param target_text: A target text
        :param cached_min_length_match_positions: A map of strings to their starting positions in the source text
        :param cached_hashes: A MinHashLSH object
        :return: A list of found matches
        :param tokens:
        """

        self.texts = [source_text, target_text]
        self.tokens = tokens
        self.forward_references = {}

        min_length_match_positions = cached_min_length_match_positions
        hashes = cached_hashes

        self.__make_forward_references(self.texts[1], min_length_match_positions, hashes)
        matches: List[InternalMatch] = self.__get_similarities(self.texts[0], self.texts[1])

        return matches

    def __remove_special_characters(self, input_string: str) -> str:
        input_string = re.sub(r'[^\w@ ]|[\u03B1\u03B2]', '', input_string)

        # TODO: _ ist bei \w dabei, ist das ein Problem?
        if re.search(r'\w', input_string):
            input_string = re.sub('@', '', input_string)

        return input_string

    def __make_forward_references(self, text: Text, min_length_match_starting_positions: Dict[str, List[int]],
                                  hashes: MinHashLSH):
        """
        Takes a target text, a mapping of strings to the position in the source text where a string starts
        and a list of hashes.
        It then tries to find matching strings in the target texts and creates a mapping of the starting positions in
        the source text to a list of starting positions in the target text.
        :param text: The target text
        :param min_length_match_starting_positions: A map of strings to positions where the string is a combination of
        x tokens.
        mapped to the position in the text where the string starts.
        :param hashes: The hashes of the minimal length strings.
        :return: A mapping of starting positions in the source text to a list of starting positions in the target text.
        """

        text_begin_pos: int = text.tk_start_pos
        text_end_pos: int = text.tk_end_pos

        for token_pos in range(text_begin_pos, text_end_pos - self.initial_match_length + 1):
            minimal_match_string: str = ''

            for token in self.tokens[token_pos: token_pos + self.initial_match_length]:
                minimal_match_string += self.__remove_special_characters(token.text)

            minimal_match_character_set = set(minimal_match_string)
            minimal_match_hash = MinHash(num_perm=self.HASH_PERM)

            for char in minimal_match_character_set:
                minimal_match_hash.update(char.encode('utf8'))

            possible_matches = hashes.query(minimal_match_hash)

            closest_match = self.__get_closest_match(possible_matches, minimal_match_string)
            if closest_match:
                for match_starting_position in min_length_match_starting_positions[closest_match]:
                    if match_starting_position in self.forward_references:
                        self.forward_references[match_starting_position].append(token_pos)
                    else:
                        self.forward_references[match_starting_position] = [token_pos]

    def __get_similarities(self, source_text: Text, target_text: Text) -> List[InternalMatch]:
        """
        Takes a source text and a target text and tries to find matching sequences.
        :param source_text: The source text
        :param target_text: The target text
        :return: A list of matches.
        """

        target_position_to_source_positions_map = {}

        for source_token_position, target_token_positions in self.forward_references.items():
            for target_token_position in target_token_positions:
                if target_token_position in target_position_to_source_positions_map:
                    target_position_to_source_positions_map[target_token_position].append(source_token_position)
                else:
                    target_position_to_source_positions_map[target_token_position] = [source_token_position]

        source_token_start_pos = source_text.tk_start_pos
        source_token_end_pos = source_text.tk_end_pos
        matches: List[InternalMatch] = []

        while source_token_start_pos + self.initial_match_length <= source_token_end_pos:
            best_match: Optional[BestMatch] = self.__get_best_match(source_text, target_text,
                                                                    source_token_start_pos)

            if best_match and best_match.source_length > 0:
                source_character_start_pos = self.tokens[best_match.source_token_start].start_pos
                source_character_end_pos = self.tokens[
                    best_match.source_token_start + best_match.source_length - 1].end_pos
                target_character_start_pos = self.tokens[best_match.target_token_start].start_pos
                target_character_end_pos = self.tokens[
                    best_match.target_token_start + best_match.target_length - 1].end_pos

                source_match_span = InternalMatchSpan(best_match.source_token_start, best_match.source_length,
                                                      source_character_start_pos, source_character_end_pos)
                target_match_span = InternalMatchSpan(best_match.target_token_start, best_match.target_length,
                                                      target_character_start_pos, target_character_end_pos)

                matches.append(InternalMatch(source_match_span, target_match_span))

                best_match_token_start_pos = best_match.target_token_start
                best_match_token_end_pos = best_match.target_token_start + best_match.target_length

                best_match_source_token_start_pos = best_match.source_token_start
                best_match_source_token_end_pos = best_match.source_token_start + best_match.source_length

                for target_token_pos in range(best_match_token_start_pos + 1, best_match_token_end_pos):
                    if target_token_pos in target_position_to_source_positions_map:
                        for source_token_position in target_position_to_source_positions_map[target_token_pos]:
                            if best_match_source_token_start_pos < source_token_position < best_match_source_token_end_pos:
                                if target_token_pos in self.forward_references[source_token_position]:
                                    self.forward_references[source_token_position].remove(target_token_pos)
            else:
                if source_token_start_pos not in self.forward_references.keys() or len(
                        self.forward_references[source_token_start_pos]) == 0:
                    source_token_start_pos += 1

        return matches

    def __get_best_match(self, source_text: Text, target_text: Text, source_token_start_pos: int) \
            -> Optional[BestMatch]:
        """
        Find the next best match starting from the given position.
        :param source_text: The source text
        :param target_text: The target text
        :param source_token_start_pos: The position from which to start looking
        :return: The best match or None if no match was found
        """

        target_token_start_pos = self.__get_next_target_token_position(source_token_start_pos)

        if target_token_start_pos == -1:
            return None

        best_match = None
        offset_source = 0
        offset_target = 0

        min_match_length = self.initial_match_length

        # find possibly better start point
        new_source_token_start = source_token_start_pos
        new_target_token_start = target_token_start_pos
        source_extra_length = 0
        target_extra_length = 0

        if self.tokens[new_target_token_start - 1].text.startswith('@'):
            for i in range(1, min(self.look_back_limit, new_source_token_start)):
                if self.__fuzzy_match(self.tokens[new_source_token_start - i].text,
                                      self.tokens[new_target_token_start - 2].text):
                    new_source_token_start -= i
                    new_target_token_start -= 2
                    source_extra_length += i
                    target_extra_length += 2

                    for j in range(1, min(self.initial_match_length - 1, new_source_token_start + 1)):
                        if self.__fuzzy_match(self.tokens[new_source_token_start - j].text,
                                              self.tokens[new_target_token_start - j].text):
                            new_source_token_start -= 1
                            new_target_token_start -= 1
                            source_extra_length += 1
                            target_extra_length += 1

                    break

        new_match_length = min_match_length
        source_token_pos = source_token_start_pos + min_match_length
        target_token_pos = target_token_start_pos + min_match_length

        has_skipped = False

        while source_token_pos < source_text.tk_end_pos and target_text.tk_end_pos > target_token_pos:

            # skip from 1 to n tokens in source text. N can be defined by the user.
            if self.tokens[target_token_pos].text.startswith('@'):
                found = False

                for i in range(1, self.look_ahead_limit + 1):
                    if (target_token_pos + 1 < len(self.tokens) and source_token_pos + i < source_text.tk_end_pos and
                            self.__fuzzy_match(self.tokens[source_token_pos + i].text,
                                               self.tokens[target_token_pos + 1].text)):
                        source_token_pos += i
                        target_token_pos += 1
                        new_match_length += i
                        offset_target += i - 1
                        found = True
                        break

                if not found:
                    break

            # do tokens at aligned positions match
            if self.__fuzzy_match(self.tokens[source_token_pos].text, self.tokens[target_token_pos].text):
                source_token_pos += 1
                target_token_pos += 1
                new_match_length += 1
            # combine two tokens in source text
            elif (source_token_pos + 1 < source_text.tk_end_pos and
                  self.__fuzzy_match(self.tokens[source_token_pos].text + self.tokens[source_token_pos + 1].text,
                                     self.tokens[target_token_pos].text)):
                source_token_pos += 2
                target_token_pos += 1
                new_match_length += 2
                offset_target += 1
            # combine two tokens in target text
            elif (target_token_pos + 1 < len(self.tokens) and
                  self.__fuzzy_match(self.tokens[source_token_pos].text,
                                     self.tokens[target_token_pos].text +
                                     self.tokens[target_token_pos + 1].text)):
                source_token_pos += 1
                target_token_pos += 2
                new_match_length += 2
                offset_source += 1
            elif not has_skipped:
                found = False

                # skip one token in the source text
                if (source_token_pos + 1 < source_text.tk_end_pos and
                        self.__fuzzy_match(self.tokens[source_token_pos + 1].text, self.tokens[target_token_pos].text)):
                    source_token_pos += 2
                    target_token_pos += 1
                    new_match_length += 2
                    offset_target += 1
                    found = True
                    has_skipped = True

                if not found:
                    # skip one token in the target text
                    if (target_token_pos + 1 < len(self.tokens) and
                            self.__fuzzy_match(self.tokens[source_token_pos].text,
                                               self.tokens[target_token_pos + 1].text)):
                        source_token_pos += 1
                        target_token_pos += 2
                        new_match_length += 2
                        offset_source += 1
                        found = True
                        has_skipped = True

                if not found:
                    break
            else:
                break

        if new_match_length >= self.initial_match_length:
            best_match_token_pos = target_token_start_pos
            best_match = BestMatch(source_token_start_pos - source_extra_length,
                                   best_match_token_pos - target_extra_length,
                                   new_match_length - offset_source + source_extra_length,
                                   new_match_length - offset_target + target_extra_length)

        return best_match

    def __get_next_target_token_position(self, current_source_token_position: int) -> int:
        """
        Takes a source token position and gets the next target token position if possible.
        :param current_source_token_position: A source token position
        :return: The next target token position or -1 if no position could be found.
        """

        for source_token_position, target_token_positions in self.forward_references.items():
            if current_source_token_position == source_token_position and len(target_token_positions) > 0:
                next_token_position = target_token_positions[0]
                del target_token_positions[0]
                return next_token_position

        return -1

    def __fuzzy_match(self, input1: str, input2: str) -> bool:
        input1 = self.__remove_special_characters(input1)
        input2 = self.__remove_special_characters(input2)

        input1_length = len(input1)
        input2_length = len(input2)

        if min(input1_length, input2_length) < 2:
            return input1 == input2

        ratio = Levenshtein.normalized_similarity(input1, input2)
        return ratio >= self.min_levenshtein_similarity

    def __get_closest_match(self, candidates: List[str], word: str) -> Optional[str]:
        if not candidates or len(candidates) == 0:
            return None

        candidates = [self.__remove_special_characters(element) for element in candidates]
        word = self.__remove_special_characters(word)

        if word in candidates:
            return word

        best_candidate = process.extractOne(word, candidates, scorer=Levenshtein.normalized_similarity,
                                            score_cutoff=self.min_levenshtein_similarity)

        if best_candidate:
            return best_candidate[0]

        return None

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
