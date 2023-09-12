
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.document_cluster import DocumentCluster
from semantha_sdk.model.plotly_chart import PlotlyChart
from typing import Dict
from typing import List
from typing import Optional


@dataclass(frozen=True)
class ClusteringResponse(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    clusters: Optional[List[DocumentCluster]] = None
    plotly: Optional[Dict[str, PlotlyChart]] = None

ClusteringResponseSchema = class_schema(ClusteringResponse, base_schema=SemanthaSchema)
