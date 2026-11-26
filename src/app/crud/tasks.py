from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    Application as ApplicationModel,
    Event as EventModel,
    SavedProgram as SavedProgramModel,
    Task as TaskModel,
)
from app.schemas.applications import TaskCreate, TaskUpdate


def get_user_tasks(db: Session, user_id: int) -> list[TaskModel]:
    return list(
        db.execute(
            select(TaskModel)
            .where(TaskModel.user_id == user_id)
            .order_by(TaskModel.due_date.is_(None), TaskModel.due_date, TaskModel.task_id)
        ).scalars()
    )


def get_task(db: Session, task_id: int) -> TaskModel | None:
    return db.get(TaskModel, task_id)


def create_task(db: Session, user_id: int, task_in: TaskCreate) -> TaskModel | None:
    """Create a task; returns None if application_id isn't one of the user's applications."""
    if task_in.application_id is not None:
        application = db.get(ApplicationModel, task_in.application_id)
        if application is None or application.user_id != user_id:
            return None

    task = TaskModel(user_id=user_id, **task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: TaskModel, task_in: TaskUpdate) -> TaskModel:
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: TaskModel) -> None:
    db.delete(task)
    db.commit()


def get_user_calendar(db: Session, user_id: int) -> list[EventModel]:
    """Events for every program the user has applied to or saved."""
    applied = select(ApplicationModel.program_id).where(ApplicationModel.user_id == user_id)
    saved = select(SavedProgramModel.program_id).where(SavedProgramModel.user_id == user_id)
    return list(
        db.execute(
            select(EventModel)
            .where(EventModel.program_id.in_(applied.union(saved)))
            .order_by(EventModel.event_date, EventModel.event_id)
        ).scalars()
    )
