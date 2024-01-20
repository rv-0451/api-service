from pydantic import BaseModel
from typing import Dict
from pydantic import constr


QUERY_REGEX = r"^(?:name|metadata)(?:\.[a-zA-Z0-9-]+)*=[a-zA-Z0-9-]+$"


class Data(BaseModel):
    """
    Basic data model,
    it has name and metadata
    """
    name: str
    metadata: Dict


class DataQuery(BaseModel):
    """
    Model for query validation
    """
    query: constr(pattern=QUERY_REGEX)
