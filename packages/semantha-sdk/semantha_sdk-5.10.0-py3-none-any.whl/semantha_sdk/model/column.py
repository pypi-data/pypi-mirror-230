
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import List
from typing import Optional


@dataclass(frozen=True)
class Column(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    property_id: str
    possible_names: Optional[List[str]] = None

ColumnSchema = class_schema(Column, base_schema=SemanthaSchema)
