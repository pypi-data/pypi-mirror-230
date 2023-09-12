
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.extractor import Extractor
from semantha_sdk.model.extractor_attribute import ExtractorAttribute
from semantha_sdk.model.table import Table
from typing import List
from typing import Optional


@dataclass(frozen=True)
class ExtractorClass(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    class_id: str
    id: Optional[str] = None
    matcher: Optional[List[Extractor]] = None
    metadata: Optional[str] = None
    attributes: Optional[List[ExtractorAttribute]] = None
    tables: Optional[List[Table]] = None
    document_type: Optional[str] = None
    split_document_extractor: Optional[str] = None

ExtractorClassSchema = class_schema(ExtractorClass, base_schema=SemanthaSchema)
