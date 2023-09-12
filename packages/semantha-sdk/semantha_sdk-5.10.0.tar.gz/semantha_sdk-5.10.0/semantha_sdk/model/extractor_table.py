
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.column import Column
from semantha_sdk.model.extractor_class_overview import ExtractorClassOverview
from typing import List
from typing import Optional


@dataclass(frozen=True)
class ExtractorTable(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    class_id: str
    type: str
    id: Optional[str] = None
    columns: Optional[List[Column]] = None
    end_names: Optional[List[str]] = None
    start_before: Optional[List[str]] = None
    end_after: Optional[List[str]] = None
    used_classes: Optional[List[ExtractorClassOverview]] = None
    column_names: Optional[List[str]] = None

ExtractorTableSchema = class_schema(ExtractorTable, base_schema=SemanthaSchema)
