
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Any
from typing import List
from typing import Optional


@dataclass(frozen=True)
class PlotlyChart(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    data: Optional[List[Any]] = None
    layout: Optional[Any] = None

PlotlyChartSchema = class_schema(PlotlyChart, base_schema=SemanthaSchema)
