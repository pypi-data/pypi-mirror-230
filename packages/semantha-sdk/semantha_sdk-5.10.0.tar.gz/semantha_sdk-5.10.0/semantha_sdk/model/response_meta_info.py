
from dataclasses import dataclass

from marshmallow_dataclass import class_schema

from semantha_sdk.model.semantha_entity import SemanthaModelEntity, SemanthaSchema

from semantha_sdk.model.meta_info_page import MetaInfoPage
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


@dataclass(frozen=True)
class ResponseMetaInfo(SemanthaModelEntity):
    """ author semantha, this is a generated class do not change manually! """
    info: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None
    page: Optional[MetaInfoPage] = None

ResponseMetaInfoSchema = class_schema(ResponseMetaInfo, base_schema=SemanthaSchema)
