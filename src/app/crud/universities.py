from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_id as get_user
from app.models.models import Professor, Program, University
from app.schemas.universities import ProfessorRead, UniversitySummary
from app.schemas.programs import ProgramSummary


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


# def search_universities(db:Session, user_id: int, location: str = None, degree_type: str = None):
#     user = get_user(db, user_id)
#     if not user:
#         return []

#     programs = db.query(Program).filter(Program.degree_type == degree_type, Program.field == user.program_interests).all()
#     universities = db.query(University).filter(University.location == location, University.programs == programs).all()
#     return universities

# def get_professors(db:Session, university_id: int, user_id: int):
#     user = get_user(db, user_id)
#     if not user:
#         return []
#     return db.query(ProfessorRead).filter(ProfessorRead.university_id == university_id, ProfessorRead.research_interests == user.research_interests).all()

# def get_programs_from_university(db:Session, university_id: int, field: str = None, degree_type: str = None):
#     query = db.query(ProgramSummary).filter(ProgramSummary.university_id == university_id)
#     if field:
#         query = query.filter(ProgramSummary.field == field)
#     if degree_type:
#         query = query.filter(ProgramSummary.degree_type == degree_type)
#     return query.all()
