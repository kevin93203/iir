from pydantic import BaseModel
from enum import Enum
from typing import List

class Data (BaseModel):
    filenames: list[str]
    documents: list[str]
    inverted_index: dict[str, list[tuple[int,int]]]
    titles: list[str]
    inverted_index_titles: dict[str, list[tuple[int,int]]]

class QueryOperator(str, Enum):
    OR = "or"
    AND = "and"

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    totalPages: int
    current_page: int
    pageSize: int
    query: str | None = None
    query_keywords: list[str] | None = None