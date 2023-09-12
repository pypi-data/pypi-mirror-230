
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class AttributeOverview(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    datatype: Optional[str] = None

AttributeOverviewSchema = class_schema(AttributeOverview, base_schema=SemanthaSchema)
