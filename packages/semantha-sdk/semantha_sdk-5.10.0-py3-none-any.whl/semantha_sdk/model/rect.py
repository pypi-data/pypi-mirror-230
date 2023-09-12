
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class Rect(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    x: float
    y: float
    width: float
    height: float
    page: int

RectSchema = class_schema(Rect, base_schema=SemanthaSchema)
