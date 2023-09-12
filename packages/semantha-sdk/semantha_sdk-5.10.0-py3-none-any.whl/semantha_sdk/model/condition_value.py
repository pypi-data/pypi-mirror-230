
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import List
from typing import Optional


@dataclass(frozen=True)
class ConditionValue(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    function: Optional[str] = None
    arguments: Optional[List["Argument"]] = None

from semantha_sdk.model.argument import Argument
ConditionValueSchema = class_schema(ConditionValue, base_schema=SemanthaSchema)
