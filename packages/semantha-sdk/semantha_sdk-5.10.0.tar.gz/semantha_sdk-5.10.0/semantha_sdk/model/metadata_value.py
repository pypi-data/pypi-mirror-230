
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema



@dataclass(frozen=True)
class MetadataValue(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: str
    value: str

MetadataValueSchema = class_schema(MetadataValue, base_schema=SemanthaSchema)
