"""Paper schemas."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Paper(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int
    title: str
    authors: list[str] = Field(default_factory=list)
    professor_ids: list[int] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    publication_date: Optional[date] = None
    external_id_openalex: Optional[str] = None
    link: Optional[str] = None
