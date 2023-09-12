
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class SimpleProperty(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    value: str
    property_id: str

SimplePropertySchema = class_schema(SimpleProperty, base_schema=SemanthaSchema)
