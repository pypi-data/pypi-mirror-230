
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class TagDocs(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    tag: Optional[str] = None
    count: Optional[int] = None

TagDocsSchema = class_schema(TagDocs, base_schema=SemanthaSchema)
