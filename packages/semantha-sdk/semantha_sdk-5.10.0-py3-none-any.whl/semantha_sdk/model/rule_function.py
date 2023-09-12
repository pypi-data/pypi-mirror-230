
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class RuleFunction(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    min_arg_length: Optional[int] = None
    max_arg_length: Optional[int] = None
    type: Optional[str] = None

RuleFunctionSchema = class_schema(RuleFunction, base_schema=SemanthaSchema)
