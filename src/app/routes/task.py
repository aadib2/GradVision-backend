from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import tasks as task_crud
from app.models.models import Task as TaskModel, User as UserModel
from app.schemas.applications import (
    Task as TaskSchema,
    TaskCreate,
    TaskCreateResponse,
    TaskUpdate,
)
from app.schemas.common import SuccessResponse
from app.schemas.programs import CalendarEvent

router = APIRouter(tags=["Tasks and Calendar"])


def ensure_self(current_user: UserModel, user_id: int) -> None:
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access these tasks",
        )


def _get_owned_task(db: Session, task_id: int, current_user: UserModel) -> TaskModel:
    task = task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if task.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task",
        )
    return task


@router.get(
    "/users/{user_id}/calendar/",
    response_model=list[CalendarEvent],
)
def get_user_calendar(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return task_crud.get_user_calendar(db, user_id)


@router.get(
    "/users/{user_id}/tasks/",
    response_model=list[TaskSchema],
)
def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return task_crud.get_user_tasks(db, user_id)


@router.post(
    "/users/{user_id}/tasks/",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    user_id: int,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_self(current_user, user_id)

    task = task_crud.create_task(db, user_id, task_in)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return TaskCreateResponse(task=TaskSchema.model_validate(task))


@router.patch(
    "/tasks/{task_id}",
    response_model=SuccessResponse,
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    task_crud.update_task(db, task, task_in)
    return SuccessResponse()


@router.delete(
    "/tasks/{task_id}",
    response_model=SuccessResponse,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    task_crud.delete_task(db, task)
    return SuccessResponse()
