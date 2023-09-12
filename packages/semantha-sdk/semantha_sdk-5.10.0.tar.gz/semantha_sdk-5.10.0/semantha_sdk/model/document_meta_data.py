
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class DocumentMetaData(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    file_name: Optional[str] = None
    document_type: Optional[str] = None

DocumentMetaDataSchema = class_schema(DocumentMetaData, base_schema=SemanthaSchema)
