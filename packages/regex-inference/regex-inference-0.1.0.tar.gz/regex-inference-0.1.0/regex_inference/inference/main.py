from typing import List
from threading import Thread
from .engine import Engine
from ..evaluator import Evaluator


class Inference:
    def __init__(self, *args, **kwargs):
        if 'n_thread' in kwargs:
            self._n_thread = kwargs['n_thread']
            del kwargs['n_thread']
        else:
            self._n_thread = 30
        self._engine = Engine(*args, **kwargs)

    def run(self, train_patterns: List[str],
            val_patterns: List[str] = []) -> str:
        if val_patterns:
            regex_list = self.get_regex_sequence(train_patterns, val_patterns)
        else:
            regex_list = self.get_regex_sequence(
                train_patterns, train_patterns)
        return Engine.merge_regex_sequence(regex_list)

    def get_regex_sequence(
            self, train_patterns: List[str], val_patterns: List[str]) -> List[str]:
        class GetThread(Thread):
            def __init__(self, engine):
                Thread.__init__(self)
                self.value = None
                self._engine = engine

            def run(self):
                regex_list = self._engine.get_regex_sequence(train_patterns)
                _, _, f1 = Evaluator.evaluate_regex_list(
                    regex_list, val_patterns)
                self.value = (f1, regex_list)
        threads = []
        for _ in range(self._n_thread):
            thread = GetThread(self._engine)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        results = [thread.value for thread in threads]
        result = sorted(results, key=lambda x: x[0], reverse=True)[0][1]
        return result
