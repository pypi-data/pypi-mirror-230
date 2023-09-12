
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class ExtractionReference(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    similarity: Optional[float] = None
    used: Optional[bool] = None

ExtractionReferenceSchema = class_schema(ExtractionReference, base_schema=SemanthaSchema)
