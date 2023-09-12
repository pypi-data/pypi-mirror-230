
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.matcher import Matcher
from semantha_sdk.model.range import Range
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Extractor(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    type: Optional[str] = None
    value: Optional[str] = None
    combination_type: Optional[str] = None
    range: Optional[Range] = None
    start: Optional[Matcher] = None
    end: Optional[Matcher] = None
    in_between_extractor: Optional[List["Extractor"]] = None

ExtractorSchema = class_schema(Extractor, base_schema=SemanthaSchema)
