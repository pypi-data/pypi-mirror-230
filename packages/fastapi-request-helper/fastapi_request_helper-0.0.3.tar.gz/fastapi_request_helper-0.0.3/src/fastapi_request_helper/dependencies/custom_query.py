from typing import Any, Optional

from fastapi import Query
from pydantic.fields import Undefined


def custom_query(default: Any = Undefined, alias: Optional[str] = None):
    return Query(alias=alias, default=default)
