
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.settings import Settings
from typing import Optional


@dataclass(frozen=True)
class Domain(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    id: Optional[str] = None
    name: Optional[str] = None
    base_url: Optional[str] = None
    settings: Optional[Settings] = None

DomainSchema = class_schema(Domain, base_schema=SemanthaSchema)
