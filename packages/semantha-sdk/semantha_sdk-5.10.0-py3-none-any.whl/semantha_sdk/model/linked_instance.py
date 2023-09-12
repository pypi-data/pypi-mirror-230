
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.linked_value import LinkedValue
from typing import List
from typing import Optional


@dataclass(frozen=True)
class LinkedInstance(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    instance_id: Optional[str] = None
    linked_values: Optional[List[LinkedValue]] = None

LinkedInstanceSchema = class_schema(LinkedInstance, base_schema=SemanthaSchema)
