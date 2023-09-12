
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class SemiSuperVisedDocument(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    document_id: Optional[str] = None
    topic_id: Optional[int] = None

SemiSuperVisedDocumentSchema = class_schema(SemiSuperVisedDocument, base_schema=SemanthaSchema)
