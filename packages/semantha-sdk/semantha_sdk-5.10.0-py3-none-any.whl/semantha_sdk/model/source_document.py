
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class SourceDocument(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    paragraph_id: Optional[str] = None

SourceDocumentSchema = class_schema(SourceDocument, base_schema=SemanthaSchema)
