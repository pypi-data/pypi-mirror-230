
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.row import Row
from typing import List
from typing import Optional


@dataclass(frozen=True)
class DocumentTable(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    rows: Optional[List[Row]] = None

DocumentTableSchema = class_schema(DocumentTable, base_schema=SemanthaSchema)
