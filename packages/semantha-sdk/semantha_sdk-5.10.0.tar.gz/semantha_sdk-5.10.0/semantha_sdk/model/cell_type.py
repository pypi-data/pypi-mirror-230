
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class CellType(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: str
    name: str
    color: str

CellTypeSchema = class_schema(CellType, base_schema=SemanthaSchema)
