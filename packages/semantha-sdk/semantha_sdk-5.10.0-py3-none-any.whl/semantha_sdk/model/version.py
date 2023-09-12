
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from typing import Optional


@dataclass(frozen=True)
class Version(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    tt: Optional[str] = None
    customer: Optional[str] = None

VersionSchema = class_schema(Version, base_schema=SemanthaSchema)
