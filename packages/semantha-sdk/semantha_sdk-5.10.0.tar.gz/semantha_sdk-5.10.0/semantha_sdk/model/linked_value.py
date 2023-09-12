
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class LinkedValue(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    value: Optional[str] = None
    linked_value: Optional[str] = None

LinkedValueSchema = class_schema(LinkedValue, base_schema=SemanthaSchema)
