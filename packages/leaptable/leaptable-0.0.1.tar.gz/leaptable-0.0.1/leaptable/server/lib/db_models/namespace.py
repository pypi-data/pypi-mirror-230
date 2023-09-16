#!/usr/bin/env python

__authors__ = ["Peter W. Njenga"]
__copyright__ = "Copyright © 2023 Leaptable, Inc."

# Standard Libraries

# External Libraries
from datetime import datetime

from enum import Enum

import json
from pydantic import BaseModel, Field, BeforeValidator

# Internal Libraries
from typing import Optional, Dict, List, Any, Annotated

from pydantic.types import UUID, Json
from uuid6 import uuid7
from validators import uuid

from leaptable.server.lib.db_connection import Database

def transform_str_to_json(v: dict | None) -> dict:
    if v:
        if isinstance(v, str):
            v = json.loads(v)
        elif isinstance(v, list):
            print(type(v[0]))
            v = [json.loads(i) for i in v]

    return v

ParsedDict = Annotated[dict, BeforeValidator(transform_str_to_json)]

class PROCESSING_STATUS(str, Enum):
    QUEUED = 'QUEUED'
    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'
    ERROR = 'ERROR'

class Namespace(BaseModel):
    id_: UUID = Field(alias="_id", default_factory=uuid7)
    cr_: datetime = Field(alias="_cr", default_factory=datetime.utcnow)
    up_: datetime = Field(alias="_up", default_factory=datetime.utcnow)
    slug: str
    name: str
    api_key: str | None = None
    trace_db: Optional[Database] = None
    trace_db_params: ParsedDict | None = {}
    data_db: Optional[Database] = None
    data_db_params: Optional[ParsedDict] = {}
    redis_params: Optional[Dict[str, str]] = {}
    redis_conn: Optional[Database] = None


class Job(BaseModel):
    id_: UUID = Field(alias="_id", default_factory=uuid7)
    cr_: datetime = Field(alias="_cr", default_factory=datetime.utcnow)
    up_: datetime = Field(alias="_up", default_factory=datetime.utcnow)
    prompt: Any | None = None
    prompt_format_version: str
    initiator_id: UUID
    initiator_type: str = None
    engine_vs: str = "v0.0.1"
    read_cache: bool
    write_cache: bool
    table_name: str
    input_params: Any | None = None
    output_params: Any | None = None
