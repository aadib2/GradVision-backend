from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.universities import (
    get_professors,
    search_universities,
)
from app.schemas.universities import (
    ProfessorRead,
    UniversitySummary,
)
from app.crud.universities import (
    get_professors,
    search_universities,
)

from app.crud.programs import search_programs as search_programs_crud
from app.models.models import DegreeType
from app.schemas.programs import ProgramSearchResult

router = APIRouter(prefix="/search", tags=["Search"])

@router.get(
    "/universities",
    response_model=list[UniversitySummary],
)
def search_universities_endpoint(
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return search_universities(
        db=db,
        location=location,
        search=search,
        program_fields=program_fields,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/professors",
    response_model=list[ProfessorRead],
)
def get_professors_endpoint(
    university_id: int,
    db: Session = Depends(get_db),
):
    return get_professors(
        db=db,
        university_id=university_id,
    )

@router.get(
    "/programs",
    response_model=list[ProgramSearchResult],
)
def search_programs_endpoint(
    search: str | None = None,
    location: str | None = None,
    degree_type: list[DegreeType] | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return search_programs_crud(
        db=db,
        search=search,
        location=location,
        degree_type=degree_type,
        limit=limit,
        offset=offset,
    )