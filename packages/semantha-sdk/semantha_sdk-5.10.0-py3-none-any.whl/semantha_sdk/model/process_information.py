
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.version import Version
from typing import Optional


@dataclass(frozen=True)
class ProcessInformation(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    created: Optional[str] = None
    edited: Optional[str] = None
    version: Optional[Version] = None

ProcessInformationSchema = class_schema(ProcessInformation, base_schema=SemanthaSchema)
