
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class FileReference(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    file_id: Optional[str] = None
    name: Optional[str] = None
    page_number: Optional[int] = None

FileReferenceSchema = class_schema(FileReference, base_schema=SemanthaSchema)
