
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.link import Link
from semantha_sdk.model.rect import Rect
from semantha_sdk.model.reference import Reference
from semantha_sdk.model.sentence import Sentence
from typing import Dict
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Paragraph(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    text: Optional[str] = None
    type: Optional[str] = None
    id: Optional[str] = None
    document_name: Optional[str] = None
    sentences: Optional[List[Sentence]] = None
    references: Optional[List[Reference]] = None
    context: Optional[Dict[str, str]] = None
    areas: Optional[List[Rect]] = None
    links: Optional[List[Link]] = None
    comment: Optional[str] = None
    verified: Optional[bool] = None
    data_url_image: Optional[str] = None
    references_safe: Optional[List[Reference]] = None

ParagraphSchema = class_schema(Paragraph, base_schema=SemanthaSchema)
