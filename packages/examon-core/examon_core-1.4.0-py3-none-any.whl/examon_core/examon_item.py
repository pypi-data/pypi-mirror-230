from .examon_in_memory_db import ExamonInMemoryDatabase
from .models.question_factory import QuestionFactory


def examon_item(internal_id=None, choices=None,
                tags=None, hints=None, repository=None,
                generated_choices=None, param1=None):
    def inner_function(function):
        processed_question = QuestionFactory.build(
            function=function, choice_list=choices,
            tags=tags, hints=hints, internal_id=internal_id,
            version=1, repository=repository,
            generated_choices=generated_choices,
            param1=param1, metrics=True)
        ExamonInMemoryDatabase.add(processed_question)
        return function

    return inner_function
