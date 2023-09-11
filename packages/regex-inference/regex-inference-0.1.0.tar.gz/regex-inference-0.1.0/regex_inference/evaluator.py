from typing import List, Tuple
from .inference import Filter
from .inference import Engine


class Evaluator:
    @staticmethod
    def evaluate_regex_list(
            regex_list: List[str], patterns: List[str]) -> Tuple[float, float, float]:
        """
        Args:
            - regex_list: regex to be evaluated
            - patterns: patterns to be matched by the regex_list
        Returns:
            - precision: describe how well each regex in the regex list describe the patterns
            - recall: describe how well the entire regex list match the patterns
            - f1: combined score for precision and recall
        """

        recall = Evaluator.recall(regex_list, patterns)
        precision = Evaluator.precision(regex_list, patterns)
        f1 = 2. / (1. / precision + 1. / recall)
        return precision, recall, f1

    @staticmethod
    def precision(regex_list: List[str], patterns: List[str]) -> float:
        divided_patterns = Engine._divide_patterns(regex_list, patterns)
        precisions = []
        for i in range(len(divided_patterns)):
            negative_patterns = Evaluator._collect_negative_patterns(
                i, divided_patterns)
            precision = Evaluator.regex_precision(
                regex_list[i], divided_patterns[i], negative_patterns)
            precisions.append(precision)
        precision = sum(precisions) / len(precisions)
        return precision

    @staticmethod
    def recall(regex_list: List[str], patterns: List[str]) -> float:
        """
        Recall evaluate how well the regex capture the patterns presented.

        Args:
            - regex: whole regex consists of multiple sub-regex
            - patterns: the patterns in the future or not presented but should be captured by the regex.
        """
        regex = Engine.merge_regex_sequence(regex_list)
        return len(Filter.match(regex, patterns)) / len(patterns)

    @staticmethod
    def _collect_negative_patterns(
            target_regex_index: int, divided_patterns: List[List[str]]) -> List[str]:
        negative_patterns = []
        for not_i in [j for j in range(
                len(divided_patterns)) if j != target_regex_index]:
            negative_patterns.extend(divided_patterns[not_i])
        return negative_patterns

    @staticmethod
    def regex_precision(
            sub_regex: str, positive_patterns: List[str], negative_patterns: List[str]) -> float:
        """
        Precision evaluate how precise or explainable is the regex on the target patterns.

        Because my goal is that each sub-regex should exactly match its target patterns,
        the positive patterns and negative patterns for the sub-regex is defined as follows:

        * positive_patterns: pattern presented previously and matched by the sub-regex
        * negative_patterns: pattern not hosted by the sub-regex.
        """
        if positive_patterns:
            return len(Filter.match(sub_regex, positive_patterns)) / \
                len(Filter.match(sub_regex,
                                 positive_patterns + negative_patterns))
        else:
            return 0.0
