
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class AnswerReference(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    name: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[str] = None

AnswerReferenceSchema = class_schema(AnswerReference, base_schema=SemanthaSchema)
