"""User profile routes (sign up and My Vision profile CRUD)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import programs as programs_crud
from app.crud import saved_programs as saved_programs_crud
from app.crud import user as user_crud
from app.models.models import User as UserModel
from app.schemas.common import SuccessResponse, UserCreateResponse
from app.schemas.programs import ProgramIdRequest, ProgramSummary
from app.schemas.users import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def _ensure_self(current_user: UserModel, user_id: int) -> None:
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this profile",
        )


def _get_user_or_404(db: Session, user_id: int) -> UserModel:
    user = user_crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get(
    "/{id}/saved-programs/",
    response_model=list[ProgramSummary],
    tags=["Saved Programs"],
)
def list_saved_programs(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> list[ProgramSummary]:
    _ensure_self(current_user, id)
    _get_user_or_404(db, id)
    programs = saved_programs_crud.list_saved_programs(db, id)
    return [ProgramSummary.model_validate(program) for program in programs]


@router.post(
    "/{id}/saved-programs/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Saved Programs"],
)
def save_program(
    id: int,
    body: ProgramIdRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SuccessResponse:
    _ensure_self(current_user, id)
    _get_user_or_404(db, id)
    if programs_crud.get_program(db, body.program_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    if saved_programs_crud.get_saved_program(db, id, body.program_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program is already saved",
        )
    saved_programs_crud.save_program(db, id, body.program_id)
    return SuccessResponse()
 

@router.delete(
    "/{id}/saved-programs/{program_id}",
    response_model=SuccessResponse,
    tags=["Saved Programs"],
)
def unsave_program(
    id: int,
    program_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SuccessResponse:
    _ensure_self(current_user, id)
    _get_user_or_404(db, id)
    saved = saved_programs_crud.get_saved_program(db, id, program_id)
    if saved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved program not found",
        )
    saved_programs_crud.delete_saved_program(db, saved)
    return SuccessResponse()
  
@router.post("", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserCreateResponse:
    if user_crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    user = user_crud.create_user(db, user_in)
    return UserCreateResponse(user=User.model_validate(user))


@router.get("/{id}", response_model=User)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> User:
    _ensure_self(current_user, id)
    user = user_crud.get_user_by_id(db, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return User.model_validate(user)


@router.patch("/{id}", response_model=SuccessResponse)
def update_user(
    id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SuccessResponse:
    _ensure_self(current_user, id)
    user = user_crud.get_user_by_id(db, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user_in.email is not None and user_in.email != user.email:
        existing = user_crud.get_user_by_email(db, user_in.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )
    user_crud.update_user(db, user, user_in)
    return SuccessResponse()
  
  
@router.delete("/{id}", response_model=SuccessResponse)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> SuccessResponse:
    _ensure_self(current_user, id)
    user = user_crud.get_user_by_id(db, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user_crud.delete_user(db, user)
    return SuccessResponse()
