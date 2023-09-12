
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.answer_reference import AnswerReference
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Answer(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    answer: Optional[str] = None
    references: Optional[List[AnswerReference]] = None

AnswerSchema = class_schema(Answer, base_schema=SemanthaSchema)
