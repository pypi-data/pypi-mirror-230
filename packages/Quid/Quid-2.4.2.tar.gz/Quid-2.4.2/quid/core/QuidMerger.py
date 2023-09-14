from typing import List
from quid.core.InternalMatch import InternalMatch
from quid.core.InternalMatchSpan import InternalMatchSpan
import re

from quid.core.Text import Text
from quid.core.Token import Token


# noinspection PyMethodMayBeStatic
class QuidMerger:
    tokens: List[Token]

    SENTENCE_DELIMITER = '\u2190'
    SENTENCE_DELIMITER_START_REGEX: str = f'^[{SENTENCE_DELIMITER}]'
    SENTENCE_DELIMITER_END_REGEX: str = f'[{SENTENCE_DELIMITER}]$'

    def __init__(self, min_match_length: int,
                 max_merge_distance: int,
                 max_merge_ellipse_distance: int,
                 keep_ambiguous_matches: bool):
        """
        :param min_match_length: The minimum number of tokens of a match
        :param max_merge_distance: The maximum distance in tokens between to matches considered for merging
        :param max_merge_ellipse_distance: The maximum distance in tokens between two matches considered for merging
        where the target text contains an ellipses between the matches
        :param keep_ambiguous_matches: If False, for a match with multiple matched segments in the source text,
        multiple matches will be returned. Otherwise, only the first match will be returned.
        """

        self.min_match_length = min_match_length
        self.max_merge_distance = max_merge_distance
        self.max_merge_ellipse_distance = max_merge_ellipse_distance
        self.texts = []
        self.tokens = []
        self.keep_ambiguous_matches = keep_ambiguous_matches

    def compare(self, matches: List[InternalMatch], tokens: List[Token], texts: List[Text]) -> List[InternalMatch]:
        self.tokens = tokens
        self.texts = texts
        matches.sort(key=lambda x: x.target_match_span.character_start, reverse=False)

        # self.__print_matches(matches, source_text, target_text)

        cleaned_matches: List[InternalMatch] = self.__merge_neighbouring_matches(matches)
        cleaned_matches = self.__remove_matches_with_overlapping_target_match_spans(cleaned_matches)
        cleaned_matches = self.__remove_too_short_matches(cleaned_matches)
        self.__remove_boundary_overshoot(cleaned_matches)
        # After removing boundary overshoot, we can end up with matches which are shorter than the threshold
        cleaned_matches = self.__remove_too_short_matches(cleaned_matches)
        return cleaned_matches

    def __remove_matches_with_overlapping_target_match_spans(self, matches: List[InternalMatch]):
        """
        Removes matches which overlap in the target texts. When keep_ambiguous_matches is true, then matches are only
        removed if they also overlap in the source text.
        :param matches: The input list of matches.
        :return: The remaining matches.
        """
        if len(matches) == 0:
            return []

        result: List[InternalMatch] = []

        if not self.keep_ambiguous_matches:
            match_position: int = 1
            current_match = matches[0]

            while match_position < len(matches):
                next_match = matches[match_position]

                current_target_match_span = current_match.target_match_span
                next_target_match_span = next_match.target_match_span

                current_end_pos = current_target_match_span.character_end
                next_start_pos = next_target_match_span.character_start

                if next_start_pos >= current_end_pos:
                    result.append(current_match)
                    current_match = next_match
                else:
                    current_token_length = current_target_match_span.token_length
                    next_token_length = next_target_match_span.token_length

                    if current_token_length < next_token_length:
                        current_match = next_match

                match_position += 1

            result.append(current_match)
        else:
            for current_match_pos, current_match in enumerate(matches):
                found_conflict = False
                for next_match_pos in range(current_match_pos, len(matches)):
                    next_match = matches[next_match_pos]

                    current_target_match_span = current_match.target_match_span
                    next_target_match_span = next_match.target_match_span

                    current_end_pos = current_target_match_span.character_end
                    next_start_pos = next_target_match_span.character_start

                    if next_start_pos < current_end_pos:
                        source_current_start_pos = current_match.source_match_span.character_start
                        source_current_end_pos = current_match.source_match_span.character_end
                        source_next_start_pos = next_match.source_match_span.character_end
                        source_next_end_pos = next_match.source_match_span.character_end

                        overlap_start = max(source_current_start_pos, source_next_start_pos)
                        overlap_end = min(source_current_end_pos, source_next_end_pos)
                        overlap_length = overlap_end - overlap_start

                        if overlap_length > 0:
                            current_token_length = current_target_match_span.token_length
                            next_token_length = next_target_match_span.token_length

                            if current_token_length < next_token_length:
                                found_conflict = True
                                break
                    else:
                        break

                if not found_conflict:
                    result.append(current_match)

        return result

    def __merge_neighbouring_matches(self, matches: List[InternalMatch]):
        """
        Merges matches which are closer together than the defined threshold.
        :param matches: The input list of matches.
        :return: The new list of matches.
        """

        remaining_matches = matches
        result = []

        while len(remaining_matches) > 0:
            current_match = remaining_matches[0]
            positions_to_delete = [0]

            for i in range(1, len(remaining_matches)):
                next_match = remaining_matches[i]

                current_source_sim = current_match.source_match_span
                next_source_sim = next_match.source_match_span
                current_target_sim = current_match.target_match_span
                next_target_sim = next_match.target_match_span

                current_source_start = current_source_sim.token_start_pos
                current_target_start = current_target_sim.token_start_pos
                next_source_start = next_source_sim.token_start_pos
                next_target_start = next_target_sim.token_start_pos
                current_source_end = current_source_sim.token_start_pos + current_source_sim.token_length
                current_target_end = current_target_sim.token_start_pos + current_target_sim.token_length
                next_source_end = next_source_sim.token_start_pos + next_source_sim.token_length
                next_target_end = next_target_sim.token_start_pos + next_target_sim.token_length

                if ((0 <= next_target_start - current_target_end <= self.max_merge_distance
                     and 0 <= next_source_start - current_source_end <= self.max_merge_distance)
                        or (next_target_start - current_target_end == 1
                            and self.tokens[next_target_start - 1].text.startswith('@')
                            and current_source_start < next_source_start
                            and next_source_start - current_source_end <= self.max_merge_ellipse_distance)
                        or (next_target_end > current_target_end > next_target_start > current_target_start
                            and next_source_end > current_source_end > next_source_start > current_source_start)):

                    source_match_span = InternalMatchSpan(current_source_sim.token_start_pos,
                                                          next_source_sim.token_start_pos +
                                                          next_source_sim.token_length -
                                                          current_source_sim.token_start_pos,
                                                          current_source_sim.character_start,
                                                          next_source_sim.character_end)

                    target_match_span = InternalMatchSpan(current_target_sim.token_start_pos,
                                                          next_target_sim.token_start_pos +
                                                          next_target_sim.token_length -
                                                          current_target_sim.token_start_pos,
                                                          current_target_sim.character_start,
                                                          next_target_sim.character_end)
                    current_match = InternalMatch(source_match_span, target_match_span)

                    positions_to_delete.append(i)
                elif 0 <= next_target_start - current_target_end > self.max_merge_distance:
                    break

            for position in reversed(positions_to_delete):
                del remaining_matches[position]

            result.append(current_match)

        return result

    def __remove_too_short_matches(self, matches: List[InternalMatch]):
        """
        Removes matches which are shorter than a threshold.
        :param matches: The list of matches to check.
        :return: The remaining matches.
        """
        result: List[InternalMatch] = []

        for match in matches:
            if (match.target_match_span.token_length >= self.min_match_length and
                    match.source_match_span.token_length >= self.min_match_length):
                result.append(match)
            elif (match.target_match_span.token_length >= self.min_match_length - 1 and
                    self.tokens[match.target_match_span.token_start_pos].text.startswith('@')):
                result.append(match)
            elif (match.target_match_span.token_length >= self.min_match_length - 1 and
                  match.target_match_span.token_start_pos - 1 >= self.texts[0].tk_end_pos and
                  (self.tokens[match.target_match_span.token_start_pos].text.startswith('@') or
                   self.tokens[match.target_match_span.token_start_pos - 1].text.startswith('@'))):
                result.append(match)
            else:
                pass

        return result

    def __remove_boundary_overshoot(self, matches: List[InternalMatch]):
        """
        Remove tokens after sentence delimiters if they're likely to have matched by accident. Does not return anything
        but modifies the matches in place.
        :param matches: The list of matches to check.
        """
        for match in matches:
            current_source_match_span = match.source_match_span
            current_target_match_span = match.target_match_span

            found = False
            if current_source_match_span.token_length > 3:
                source_token_end_pos = current_source_match_span.token_start_pos + \
                                       current_source_match_span.token_length
                source_token_text = self.tokens[source_token_end_pos - 1].text

                target_token_end_pos = (current_target_match_span.token_start_pos +
                                        current_target_match_span.token_length)

                target_token_text = self.tokens[target_token_end_pos - 1].text

                if (re.search(self.SENTENCE_DELIMITER_START_REGEX, source_token_text) or
                        re.search(self.SENTENCE_DELIMITER_END_REGEX, source_token_text) or
                        re.search(self.SENTENCE_DELIMITER_START_REGEX, target_token_text) or
                        re.search(self.SENTENCE_DELIMITER_END_REGEX, target_token_text)):
                    continue

                for i in range(2, 4):
                    source_token = self.tokens[source_token_end_pos - i]
                    source_token_text = source_token.text

                    if (re.search(self.SENTENCE_DELIMITER_START_REGEX, source_token_text) or
                            re.search(self.SENTENCE_DELIMITER_END_REGEX, source_token_text)):

                        for j in range(2, 4):
                            target_token = self.tokens[target_token_end_pos - j]
                            target_token_text = target_token.text

                            if target_token_text in source_token_text:
                                found = True

                                current_source_match_span.token_length -= i
                                current_target_match_span.token_length -= j

                                current_source_match_span.character_end = self.tokens[
                                    source_token_end_pos - i].end_pos
                                current_target_match_span.character_end = self.tokens[
                                    target_token_end_pos - j].end_pos
                                break

                        if found:
                            break

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
