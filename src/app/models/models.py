"""
SQLAlchemy ORM models for GradVision, matching gradvision-openapi.yaml

Cascade policy:
  - User-owned rows (PastEducation, Application, Task, SavedPrograms) cascade-delete
    with their User, via ondelete="CASCADE" + passive_deletes=True on the FK and
    cascade="all, delete-orphan" on the parent relationship. Deleting a user should
    clean up everything that belongs only to them.
  - Catalog rows (Program, Professor under a University; Event under a Program;
    the ProfessorPapers join) default to RESTRICT (no ondelete clause). You don't
    want deleting a University to silently wipe out Programs/Professors that may
    still be referenced elsewhere (e.g. a user's Application). If you want
    catalog-side cascades later, add ondelete="CASCADE" to those FKs deliberately.

Join tables (SavedPrograms, ProfessorPapers) are modeled as association *objects*
(full mapped classes with their own composite PK), not bare secondary tables, so
you can add columns to them later (SavedPrograms already has saved_at) and query
them directly without going through the parent/child relationship.
"""

from __future__ import annotations

import enum
from datetime import datetime, date

from sqlalchemy import (
    String, Text, Integer, Boolean, Date, DateTime, ForeignKey, JSON, Enum, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy

from app.core.database import Base


# ---------------------------------------------------------------------------
# enums
# ---------------------------------------------------------------------------

class DegreeType(str, enum.Enum):
    masters = "Masters"
    phd = "PhD"
    combined = "Combined"


class ApplicationStatus(str, enum.Enum):
    not_started = "not started"
    in_progress = "in progress"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"


# ---------------------------------------------------------------------------
# User + the things that belong only to a user
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    research_interests: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    career_goals: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    program_interests: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    personal_statement: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # user-owned -> cascade delete
    past_education: Mapped[list["PastEducation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    saved_programs: Mapped[list["SavedProgram"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class PastEducation(Base):
    """One prior school for a user. Note: university_name is plain text rather than FK to Universities table
    since a school is not guaranteed to be stored there."""

    __tablename__ = "past_education"

    education_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )

    university_name: Mapped[str] = mapped_column(String(255))
    major: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str] = mapped_column(String(50))
    year_started: Mapped[int] = mapped_column(Integer)
    year_ended: Mapped[int] = mapped_column(Integer)
    currently_attending: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="past_education")


# ---------------------------------------------------------------------------
# catalog: universities, programs, events, professors, papers
# ---------------------------------------------------------------------------

class University(Base):
    __tablename__ = "universities"

    university_id: Mapped[int] = mapped_column(primary_key=True)
    university_name: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # catalog data -> no cascade; restrict by default (no ondelete clause)
    programs: Mapped[list["Program"]] = relationship(back_populates="university")
    professors: Mapped[list["Professor"]] = relationship(back_populates="university")


class Program(Base):
    __tablename__ = "programs"

    program_id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.university_id"))

    program_name: Mapped[str] = mapped_column(String(255))
    degree_type: Mapped[DegreeType] = mapped_column(Enum(DegreeType))
    field: Mapped[str | None] = mapped_column(String(255), nullable=True)
    funding_available: Mapped[bool] = mapped_column(Boolean, default=False)
    application_requirements: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    application_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    program_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program_content: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    price: Mapped[int | None] = mapped_column(Integer, nullable=True)

    university: Mapped["University"] = relationship(back_populates="programs")
    university_name: AssociationProxy[str] = association_proxy("university", "university_name")
    events: Mapped[list["Event"]] = relationship(back_populates="program")

    # reverse side of user-owned join tables -> fine to cascade from here too,
    # but the delete is driven from the User/Application side in practice
    saved_by: Mapped[list["SavedProgram"]] = relationship(back_populates="program")
    applications: Mapped[list["Application"]] = relationship(back_populates="program")


class Event(Base):
    """Calendar Event Table"""

    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.program_id"))

    label: Mapped[str] = mapped_column(String(255))
    event_type: Mapped[str] = mapped_column(String(100))
    event_date: Mapped[date] = mapped_column(Date)

    program: Mapped["Program"] = relationship(back_populates="events")


class Professor(Base):
    __tablename__ = "professors"

    professor_id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.university_id"))

    name: Mapped[str] = mapped_column(String(255))
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    research_interests: Mapped[list[str] | None] = mapped_column(JSON, default=list)

    university: Mapped["University"] = relationship(back_populates="professors")
    papers: Mapped[list["ProfessorPaper"]] = relationship(back_populates="professor")


class Paper(Base):
    __tablename__ = "papers"

    paper_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    topics: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    external_id_openalex: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    professors: Mapped[list["ProfessorPaper"]] = relationship(back_populates="paper")
    professor_ids: AssociationProxy[list[int]] = association_proxy("professors", "professor_id")


class ProfessorPaper(Base):
    """Association object for the Professor <-> Paper many-to-many."""

    __tablename__ = "professor_papers"
    professor_id: Mapped[int] = mapped_column(
        ForeignKey("professors.professor_id"), primary_key=True
    )
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.paper_id"), primary_key=True
    )

    professor: Mapped["Professor"] = relationship(back_populates="papers")
    paper: Mapped["Paper"] = relationship(back_populates="professors")


# ---------------------------------------------------------------------------
# user activity: saved programs, applications, tasks
# ---------------------------------------------------------------------------

class SavedProgram(Base):
    """Association object for the User <-> Program many-to-many (bookmarks)."""

    __tablename__ = "saved_programs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.program_id"), primary_key=True
    )
    saved_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="saved_programs")
    program: Mapped["Program"] = relationship(back_populates="saved_by")


class Application(Base):
    __tablename__ = "applications"

    application_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.program_id"))

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.not_started
    )
    transcripts_done: Mapped[bool] = mapped_column(Boolean, default=False)
    recommendations_done: Mapped[bool] = mapped_column(Boolean, default=False)
    statement_done: Mapped[bool] = mapped_column(Boolean, default=False)
    test_scores_done: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # link to the personal statement for this application, kept in an external doc
    statement_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")
    program: Mapped["Program"] = relationship(back_populates="applications")
    program_name: AssociationProxy[str] = association_proxy("program", "program_name")

    @property
    def university_name(self) -> str:
        # two hops (Application -> Program -> University), so a plain property
        return self.program.university.university_name

    # user-owned-through-application -> cascade with the application
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", passive_deletes=True
    )
 

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    # optional: a task doesn't have to belong to an application
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.application_id", ondelete="CASCADE"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(500))
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="tasks")
    application: Mapped["Application | None"] = relationship(back_populates="tasks")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
