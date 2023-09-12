
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class Regex(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    regex: str
    id: Optional[str] = None

RegexSchema = class_schema(Regex, base_schema=SemanthaSchema)
