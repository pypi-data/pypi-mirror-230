
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.label import Label
from typing import List
from typing import Optional


@dataclass(frozen=True)
class DataProperty(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    functional: Optional[bool] = None
    labels: Optional[List[Label]] = None

DataPropertySchema = class_schema(DataProperty, base_schema=SemanthaSchema)
