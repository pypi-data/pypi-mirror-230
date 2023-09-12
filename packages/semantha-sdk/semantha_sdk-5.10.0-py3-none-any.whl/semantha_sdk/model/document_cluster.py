
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.clustered_document import ClusteredDocument
from typing import List
from typing import Optional


@dataclass(frozen=True)
class DocumentCluster(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[int] = None
    count: Optional[int] = None
    label: Optional[str] = None
    content: Optional[List[ClusteredDocument]] = None
    representive_docs: Optional[List[str]] = None

DocumentClusterSchema = class_schema(DocumentCluster, base_schema=SemanthaSchema)
