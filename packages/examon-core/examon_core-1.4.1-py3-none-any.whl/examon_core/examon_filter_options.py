from dataclasses import dataclass


@dataclass
class ExamonFilterOptions:
    tags_any: list = None
    difficulty_category: str = None
    tags_all: list = None
    max_questions: int = None
