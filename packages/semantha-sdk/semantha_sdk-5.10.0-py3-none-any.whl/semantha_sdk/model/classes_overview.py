
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import List
from typing import Optional


@dataclass(frozen=True)
class ClassesOverview(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    attributes: Optional[List["ClassesOverview"]] = None
    object_property_id: Optional[str] = None

ClassesOverviewSchema = class_schema(ClassesOverview, base_schema=SemanthaSchema)
