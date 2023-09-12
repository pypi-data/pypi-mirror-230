
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.source_document import SourceDocument
from typing import Optional


@dataclass(frozen=True)
class ClusteredDocument(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    source_document: Optional[SourceDocument] = None
    probability: Optional[float] = None

ClusteredDocumentSchema = class_schema(ClusteredDocument, base_schema=SemanthaSchema)
