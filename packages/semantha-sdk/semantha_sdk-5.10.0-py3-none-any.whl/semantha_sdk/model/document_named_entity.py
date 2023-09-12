
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class DocumentNamedEntity(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: Optional[str] = None
    text: Optional[str] = None

DocumentNamedEntitySchema = class_schema(DocumentNamedEntity, base_schema=SemanthaSchema)
