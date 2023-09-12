
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.clustering_response import ClusteringResponse
from semantha_sdk.model.response_meta_info import ResponseMetaInfo
from typing import Optional


@dataclass(frozen=True)
class SmartClusterResponseContainer(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    meta: Optional[ResponseMetaInfo] = None
    data: Optional[ClusteringResponse] = None

SmartClusterResponseContainerSchema = class_schema(SmartClusterResponseContainer, base_schema=SemanthaSchema)
