
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.attribute import Attribute
from semantha_sdk.model.label import Label
from semantha_sdk.model.metadata_value import MetadataValue
from typing import List
from typing import Optional


@dataclass(frozen=True)
class Clazz(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    name: str
    id: Optional[str] = None
    read_only: Optional[bool] = None
    functional: Optional[bool] = None
    labels: Optional[List[Label]] = None
    metadata: Optional[List[MetadataValue]] = None
    comment: Optional[str] = None
    attributes: Optional[List[Attribute]] = None

ClazzSchema = class_schema(Clazz, base_schema=SemanthaSchema)
