
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class Distance(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    top: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    right: Optional[float] = None

DistanceSchema = class_schema(Distance, base_schema=SemanthaSchema)
