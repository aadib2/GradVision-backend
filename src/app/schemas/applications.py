"""Application and task (dashboard) schemas."""

from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.models import ApplicationStatus
from app.schemas.base import PartialUpdate

# matches the String(2048) column on Application.statement_url
MAX_STATEMENT_URL_LENGTH = 2048


class Application(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: int
    user_id: int
    program_id: int
    program_name: str
    university_name: str
    status: ApplicationStatus = ApplicationStatus.not_started
    transcripts_done: bool = False
    recommendations_done: bool = False
    statement_done: bool = False
    test_scores_done: bool = False
    notes: Optional[str] = None
    statement_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationUpdate(PartialUpdate):
    non_nullable = frozenset(
        {
            "status",
            "transcripts_done",
            "recommendations_done",
            "statement_done",
            "test_scores_done",
        }
    )

    status: Optional[ApplicationStatus] = None
    transcripts_done: Optional[bool] = None
    recommendations_done: Optional[bool] = None
    statement_done: Optional[bool] = None
    test_scores_done: Optional[bool] = None
    notes: Optional[str] = None
    # nullable, so null clears the link; an empty string is rejected
    statement_url: Optional[str] = None

    @field_validator("statement_url")
    @classmethod
    def _validate_statement_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("statement_url cannot be empty; send null to remove it")
        if len(value) > MAX_STATEMENT_URL_LENGTH:
            raise ValueError(
                f"statement_url must be at most {MAX_STATEMENT_URL_LENGTH} characters"
            )
        try:
            parsed = urlparse(value)
        except ValueError:
            raise ValueError("statement_url must be a valid http or https URL")
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("statement_url must be a valid http or https URL")
        return value


class TaskCreate(BaseModel):
    title: str
    due_date: Optional[datetime] = None
    application_id: Optional[int] = None


class TaskUpdate(PartialUpdate):
    non_nullable = frozenset({"title", "completed"})

    title: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    user_id: int
    application_id: Optional[int] = None
    title: str
    due_date: Optional[datetime] = None
    completed: bool = False

class ApplicationCreateResponse(BaseModel):
    success: bool = True
    application: Application

class TaskCreateResponse(BaseModel):
    success: bool = True
    task: Task