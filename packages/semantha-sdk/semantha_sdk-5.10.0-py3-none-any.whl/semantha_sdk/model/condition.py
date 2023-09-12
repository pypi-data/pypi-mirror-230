
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.condition_value import ConditionValue
from typing import Optional


@dataclass(frozen=True)
class Condition(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    left: Optional[ConditionValue] = None
    operator: Optional[str] = None
    right: Optional[ConditionValue] = None
    condition_string: Optional[str] = None

ConditionSchema = class_schema(Condition, base_schema=SemanthaSchema)
