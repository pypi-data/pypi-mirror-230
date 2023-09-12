
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.rect import Rect
from typing import Optional


@dataclass(frozen=True)
class Range(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    rect: Optional[Rect] = None
    page: Optional[int] = None

RangeSchema = class_schema(Range, base_schema=SemanthaSchema)
