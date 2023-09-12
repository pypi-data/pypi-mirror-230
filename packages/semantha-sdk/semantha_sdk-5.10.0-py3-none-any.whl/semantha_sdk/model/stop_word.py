
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class StopWord(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    word: str
    id: Optional[str] = None
    standard: Optional[bool] = None

StopWordSchema = class_schema(StopWord, base_schema=SemanthaSchema)
