from pydantic import BaseModel
from typing import List, Optional


class ColumnSchema(BaseModel):
    column_name: str
    data_type: str
    is_primary_key: bool
    not_null: bool


class ColumnProfile(BaseModel):
    column_name: str
    null_count: int
    unique_count: int
    sample_value: Optional[str]


class TableDocumentation(BaseModel):
    table_name: str
    schema: List[ColumnSchema]
    preview: List[dict]
    profile: List[ColumnProfile]


class DatabaseDocumentation(BaseModel):
    database_summary: dict
