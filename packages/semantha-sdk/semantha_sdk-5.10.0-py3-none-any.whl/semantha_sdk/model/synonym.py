
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import List
from typing import Optional


@dataclass(frozen=True)
class Synonym(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    word: Optional[str] = None
    regex: Optional[str] = None
    synonym: Optional[str] = None
    tags: Optional[List[str]] = None

SynonymSchema = class_schema(Synonym, base_schema=SemanthaSchema)
