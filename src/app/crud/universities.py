from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.models import DegreeType, Professor, Program, University
from app.schemas.universities import UniversitySummary


def list_universities(
    db: Session,
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[UniversitySummary]:
    """List universities for GET /api/universities/ (public, no user needed).

    - location / search: case-insensitive "contains" match on location / name.
    - program_fields: keep universities with at least one program whose `field`
      is any of these values (exact match).
    - Results are ordered by name (then id, so pagination is stable).
    """


    # these are not columns so they need to be calculated via scalar subqueries
    program_count = (
        select(func.count(Program.program_id))
        .where(Program.university_id == University.university_id)
        .correlate(University)
        .scalar_subquery()
    )
    professor_count = (
        select(func.count(Professor.professor_id))
        .where(Professor.university_id == University.university_id)
        .correlate(University)
        .scalar_subquery()
    )

    stmt = select(
        University.university_id,
        University.university_name,
        University.location,
        program_count.label("program_count"),
        professor_count.label("professor_count"),
    )

    if location:
        stmt = stmt.where(University.location.ilike(f"%{location}%"))
    if search:
        stmt = stmt.where(University.university_name.ilike(f"%{search}%"))
    if program_fields:
        # match any universities that have at least one program who's field is one of the program fields provided
        stmt = stmt.where(University.programs.any(Program.field.in_(program_fields)))

    stmt = stmt.order_by(University.university_name, University.university_id)
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    rows = db.execute(stmt).mappings().all()
    return [UniversitySummary(**row) for row in rows]


def search_universities(
    db: Session,
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[UniversitySummary]:
    """Search universities for GET /api/search/universities (same filters as the list)."""
    return list_universities(db, location, search, program_fields, limit, offset)


def get_professors(db: Session, university_id: int) -> list[Professor]:
    """All professors at one university, ordered by name."""
    return list(
        db.execute(
            select(Professor)
            .where(Professor.university_id == university_id)
            .order_by(Professor.name, Professor.professor_id)
        ).scalars()
    )


def get_programs_from_university(
    db: Session,
    university_id: int,
    field: str | None = None,
    degree_type: DegreeType | None = None,
) -> list[Program]:
    """Programs at one university, optionally filtered by field and degree type."""
    stmt = select(Program).where(Program.university_id == university_id)
    if field:
        stmt = stmt.where(Program.field == field)
    if degree_type:
        stmt = stmt.where(Program.degree_type == degree_type)
    return list(db.execute(stmt.order_by(Program.program_name, Program.program_id)).scalars())
