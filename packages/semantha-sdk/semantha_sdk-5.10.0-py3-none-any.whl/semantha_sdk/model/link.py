
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class Link(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    document_name: Optional[str] = None
    paragraph_id: Optional[str] = None

LinkSchema = class_schema(Link, base_schema=SemanthaSchema)
