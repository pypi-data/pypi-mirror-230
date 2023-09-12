
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class Name(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str

NameSchema = class_schema(Name, base_schema=SemanthaSchema)
