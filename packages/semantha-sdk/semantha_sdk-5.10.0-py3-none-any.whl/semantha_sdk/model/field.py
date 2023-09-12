
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class Field(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: str
    type: str

FieldSchema = class_schema(Field, base_schema=SemanthaSchema)
