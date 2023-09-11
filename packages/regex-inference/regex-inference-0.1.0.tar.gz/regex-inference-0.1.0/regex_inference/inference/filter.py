import re
from typing import List


class Filter:
    @staticmethod
    def match(regex: str, patterns: List[str]) -> List[str]:
        try:
            re_com = re.compile(regex)
        except BaseException as e:
            print('syntax error in result_regex:', regex)
            raise e
        result = list(
            filter(
                lambda x: re_com.fullmatch(x) is not None,
                patterns))
        return result

    @staticmethod
    def mismatch(
            regex: str, patterns: List[str]) -> List[str]:
        try:
            re_com = re.compile(regex)
        except BaseException as e:
            print('syntax error in result_regex:', regex)
            raise e
        result = list(filter(lambda x: re_com.fullmatch(x) is None, patterns))
        return result
