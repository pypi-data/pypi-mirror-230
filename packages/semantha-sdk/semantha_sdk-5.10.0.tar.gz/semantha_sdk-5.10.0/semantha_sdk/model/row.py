
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.table_cell import TableCell
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Row(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    cells: Optional[List[TableCell]] = None

RowSchema = class_schema(Row, base_schema=SemanthaSchema)
