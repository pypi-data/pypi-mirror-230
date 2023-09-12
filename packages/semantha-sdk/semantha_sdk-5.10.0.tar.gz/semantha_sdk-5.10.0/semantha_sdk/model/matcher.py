
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class Matcher(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    type: Optional[str] = None
    value: Optional[str] = None

MatcherSchema = class_schema(Matcher, base_schema=SemanthaSchema)
