from fastapi import APIRouter, Depends
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


router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/universities",
    response_model=list[UniversitySummary],
)
def search_universities_endpoint(
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
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