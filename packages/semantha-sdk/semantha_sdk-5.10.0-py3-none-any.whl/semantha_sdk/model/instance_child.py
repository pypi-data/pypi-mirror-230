
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class InstanceChild(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    relation_id: str
    class_id: str
    id: Optional[str] = None
    class_name: Optional[str] = None

InstanceChildSchema = class_schema(InstanceChild, base_schema=SemanthaSchema)
