"""Program and calendar event schemas."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import DegreeType


class ProgramIdRequest(BaseModel):
    program_id: int

class SavedProgram(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    program_id: int
    user_id: int
    saved_at: date

class CalendarEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    program_id: int
    label: str
    event_type: str
    event_date: date


class ProgramSummary(BaseModel):
    """Short card view used on the Explore page and saved-programs list."""
    model_config = ConfigDict(from_attributes=True)

    program_id: int
    program_name: str
    degree_type: DegreeType
    university_name: str
    program_start: Optional[int] = None
    program_end: Optional[int] = None


class Program(BaseModel):
    """Full program detail."""
    model_config = ConfigDict(from_attributes=True)

    program_id: int
    university_id: int
    program_name: str
    degree_type: DegreeType
    field: Optional[str] = None
    funding_available: bool = False
    events: list[CalendarEvent] = Field(default_factory=list)
    application_requirements: list[str] = Field(default_factory=list)
    application_link: Optional[str] = None
    program_start: Optional[int] = None
    program_end: Optional[int] = None
    program_content: list[str] = Field(default_factory=list)
    price: Optional[int] = None


class ProgramSearchResultUniversity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    university_id: int
    university_name: str
    location: Optional[str] = None


class ProgramSearchResult(BaseModel):
    """Row shape for /api/search — build this in the repository layer from a
    join across Program + University (+ a MIN(Event.event_date) subquery for
    next_deadline); it doesn't map 1:1 from a bare Program row."""

    program_id: int
    program_name: str
    degree_type: DegreeType
    field: Optional[str] = None
    price: Optional[int] = None
    funding_available: bool = False
    university: ProgramSearchResultUniversity
    next_deadline: Optional[date] = None
