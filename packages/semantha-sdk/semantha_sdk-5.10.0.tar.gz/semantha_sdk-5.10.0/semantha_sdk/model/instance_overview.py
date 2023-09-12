
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class InstanceOverview(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    class_name: Optional[str] = None
    class_id: Optional[str] = None

InstanceOverviewSchema = class_schema(InstanceOverview, base_schema=SemanthaSchema)
