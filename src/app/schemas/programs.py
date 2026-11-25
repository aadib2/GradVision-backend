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


class ProgramSearchProfessor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    professor_id: int
    name: str
    department: Optional[str] = None
    research_interests: list[str] = Field(default_factory=list)


class ProgramSearchResult(BaseModel):
    program_id: int
    program_name: str
    degree_type: DegreeType
    field: Optional[str] = None
    price: Optional[int] = None
    funding_available: bool = False
    program_start: Optional[int] = None
    program_end: Optional[int] = None
    match_score: int = 0
    next_deadline: Optional[date] = None

    university: ProgramSearchResultUniversity
    professors: list[ProgramSearchProfessor] = Field(default_factory=list)