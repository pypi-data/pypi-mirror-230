
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.paragraph import Paragraph
from typing import List
from typing import Optional


@dataclass(frozen=True)
class PageContent(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    paragraphs: Optional[List[Paragraph]] = None

PageContentSchema = class_schema(PageContent, base_schema=SemanthaSchema)
