
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.field import Field
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Argument(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    value: Optional[str] = None
    fields: Optional[List[Field]] = None
    condition: Optional["ConditionValue"] = None

from semantha_sdk.model.condition_value import ConditionValue
ArgumentSchema = class_schema(Argument, base_schema=SemanthaSchema)
