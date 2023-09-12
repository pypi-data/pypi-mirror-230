
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.tag_docs import TagDocs
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Statistic(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    library_size: Optional[int] = None
    size: Optional[int] = None
    number_of_sentences: Optional[int] = None
    docs_per_tag: Optional[List[TagDocs]] = None

StatisticSchema = class_schema(Statistic, base_schema=SemanthaSchema)
