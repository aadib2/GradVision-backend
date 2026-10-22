from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import applications as application_crud
from app.models.models import User as UserModel
from app.schemas.applications import (
    Application as ApplicationSchema,
    ApplicationCreateResponse,
    ApplicationUpdate,
)
from app.schemas.common import SuccessResponse
from app.schemas.programs import ProgramIdRequest

router = APIRouter(tags=["Applications"])


def ensure_current_user(
    user_id: int,
    current_user: UserModel,
) -> None:
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own applications",
        )


@router.get(
    "/users/{user_id}/applications/",
    response_model=list[ApplicationSchema],
)
def get_user_applications(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_current_user(user_id, current_user)

    return application_crud.get_user_applications(
        db=db,
        user_id=current_user.user_id,
    )


@router.post(
    "/users/{user_id}/applications/",
    response_model=ApplicationCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    user_id: int,
    application_in: ProgramIdRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_current_user(user_id, current_user)

    application = application_crud.create_application(
        db=db,
        user_id=current_user.user_id,
        program_id=application_in.program_id,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    return {
        "success": True,
        "application": ApplicationSchema.model_validate(application),
    }


@router.patch(
    "/applications/{application_id}",
    response_model=SuccessResponse,
)
def update_application(
    application_id: int,
    application_in: ApplicationUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    application = application_crud.update_application(
        db=db,
        application_id=application_id,
        user_id=current_user.user_id,
        application_data=application_in,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return {
        "success": True,
        "message": "Application updated successfully",
        "data": ApplicationSchema.model_validate(application),
    }


@router.delete(
    "/applications/{application_id}",
    response_model=SuccessResponse,
)
def delete_application(
    application_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = application_crud.delete_application(
        db=db,
        application_id=application_id,
        user_id=current_user.user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return {
        "success": True,
        "message": "Application deleted successfully",
        "data": None,
    }