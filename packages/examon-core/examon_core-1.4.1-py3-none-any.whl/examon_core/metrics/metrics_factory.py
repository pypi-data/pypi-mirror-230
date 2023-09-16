import logging
import ast
from radon.raw import analyze
from radon.metrics import h_visit

from .code_analysis_visitor import CodeAnalysisVisitor
from ..models.code_metrics import CodeMetrics


class CalcDifficultyDefaultStrategy:

    def __init__(self, metrics):
        self.metrics = metrics

    def calc_difficulty(self):
        value = self.metrics.difficulty
        if value == 0:
            return "Easy"
        elif 0 < value <= 1:
            return "Medium"
        elif 1 < value < 3:
            return "Hard"
        elif value >= 3:
            return 'Very Hard'


class CodeMetricsFactory:
    @staticmethod
    def build(code_as_string):
        if code_as_string == '' or code_as_string is None:
            raise Exception('Cannot use empty string')
        cm = CodeMetrics()
        raw = analyze(code_as_string)
        visit_data = h_visit(code_as_string)

        cm.difficulty = round(visit_data.total.difficulty, 2)
        cm.no_of_functions = len(visit_data.functions)
        cm.loc = raw.loc
        cm.lloc = raw.lloc
        cm.sloc = raw.sloc
        cm.categorised_difficulty = CalcDifficultyDefaultStrategy(cm).calc_difficulty()

        tree = ast.parse(code_as_string)
        m = CodeAnalysisVisitor()
        m.visit(tree)

        cm.imports = list(m.modules)
        cm.calls = list(m.calls)
        cm.extra = list(m.counts)
        logging.debug(f'CodeMetricsFactory.build: {cm}')

        return cm
