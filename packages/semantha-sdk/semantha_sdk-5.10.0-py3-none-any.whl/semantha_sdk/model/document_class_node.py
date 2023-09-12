
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.custom_field import CustomField
from typing import List
from typing import Optional


@dataclass(frozen=True)
class DocumentClassNode(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Optional[str] = None
    documents_count: Optional[int] = None
    custom_fields: Optional[List[CustomField]] = None

DocumentClassNodeSchema = class_schema(DocumentClassNode, base_schema=SemanthaSchema)
