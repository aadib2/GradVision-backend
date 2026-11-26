from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload
from datetime import date

from app.crud.user import get_user_by_id as get_user
from app.models.models import Program, SavedProgram

from app.models.models import DegreeType, Program, University
from app.schemas.programs import (
    ProgramSearchProfessor,
    ProgramSearchResult,
    ProgramSearchResultUniversity,
)

def get_program(db: Session, program_id: int) -> Program | None:
    """Return one program with its events loaded, or None if it doesn't exist.

    Returns the ORM object (like crud/user.py does); the route validates it into
    the `Program` schema. `events` is eager-loaded so that works after the query,
    and the route decides whether None means a 404.
    """
    query = (
        select(Program)
        .options(selectinload(Program.events))
        .where(Program.program_id == program_id)
    )
    return db.execute(query).scalar_one_or_none()



def remove_program(db:Session, program_id: int, user_id: int):
    user = get_user(db, user_id)
    program = get_program(db, program_id)

    if program and user:
        saved_program = db.query(SavedProgram).filter(SavedProgram.user_id == user_id, SavedProgram.program_id == program_id).first()
        if saved_program:
            db.delete(saved_program)
            db.commit()
            user.saved_programs.remove(saved_program)
            return saved_program
    return []
        

def get_saved_programs(db:Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    return user.saved_programs

def get_program_by_id(db: Session, program_id: int) -> Program | None:
    return get_program(db, program_id)

def search_programs(
    db: Session,
    search: str | None = None,
    location: str | None = None,
    degree_type: list[DegreeType] | None = None,
    limit: int = 50,
    offset: int = 0,
):
    statement = (
        select(Program)
        .join(Program.university)
        .options(
            selectinload(Program.events),
            selectinload(Program.university)
            .selectinload(University.professors),
        )
    )

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Program.program_name.ilike(search_pattern),
                Program.field.ilike(search_pattern),
                University.university_name.ilike(search_pattern),
            )
        )

    if location:
        location_filters = [
            University.location.ilike(f"%{value}%")
            for value in location
        ]

        statement = statement.where(or_(*location_filters))

    if degree_type:
        statement = statement.where(
            Program.degree_type.in_(degree_type)
        )
        
    statement = (
        statement
        .order_by(University.university_name, Program.program_name)
        .offset(offset)
        .limit(limit)
    )

    programs = list(db.execute(statement).scalars().all())
    results: list[ProgramSearchResult] = []

    for program in programs:
        university = program.university

        professors = [
            ProgramSearchProfessor.model_validate(professor)
            for professor in university.professors
        ]

        search_text = " ".join(
            [
                program.program_name or "",
                program.field or "",
                *(program.program_content or []),
                *[
                    interest
                    for professor in university.professors
                    for interest in (professor.research_interests or [])
                ],
            ]
        ).lower()

        search_terms = (
            search.lower().split()
            if search
            else []
        )

        matching_terms = sum(
            term in search_text
            for term in search_terms
        )

        match_score = (
            round((matching_terms / len(search_terms)) * 100)
            if search_terms
            else 0
        )

        future_events = [
            event.event_date
            for event in program.events
            if event.event_date >= date.today()
        ]

        next_deadline = min(future_events) if future_events else None

        results.append(
            ProgramSearchResult(
                program_id=program.program_id,
                program_name=program.program_name,
                degree_type=program.degree_type,
                field=program.field,
                price=program.price,
                funding_available=program.funding_available,
                program_start=program.program_start,
                program_end=program.program_end,
                match_score=match_score,
                next_deadline=next_deadline,
                university=ProgramSearchResultUniversity(
                    university_id=university.university_id,
                    university_name=university.university_name,
                    location=university.location,
                ),
                professors=professors,
            )
        )

    return results