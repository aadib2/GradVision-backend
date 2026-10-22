from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.models import Application as ApplicationModel, Program as ProgramModel, Task as TaskModel
from app.schemas.applications import ApplicationUpdate

def get_user_applications(
    db: Session,
    user_id: int,
) -> list[ApplicationModel]:
    return list(
        db.execute(
            select(ApplicationModel).where(
                ApplicationModel.user_id == user_id
            )
        ).scalars()
    )


def create_application(
    db: Session,
    user_id: int,
    program_id: int,
) -> ApplicationModel | None:
    program = db.get(ProgramModel, program_id)

    if program is None:
        return None

    application = ApplicationModel(
        user_id=user_id,
        program_id=program_id,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def update_application(
    db: Session,
    application_id: int,
    user_id: int,
    application_data: ApplicationUpdate,
) -> ApplicationModel | None:
    application = db.execute(
        select(ApplicationModel).where(
            ApplicationModel.application_id == application_id,
            ApplicationModel.user_id == user_id,
        )
    ).scalar_one_or_none()

    if application is None:
        return None

    for field, value in application_data.model_dump(
        exclude_unset=True
    ).items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application


def delete_application(
    db: Session,
    application_id: int,
    user_id: int,
) -> bool:
    application = db.execute(
        select(ApplicationModel).where(
            ApplicationModel.application_id == application_id,
            ApplicationModel.user_id == user_id,
        )
    ).scalar_one_or_none()

    if application is None:
        return False

    db.delete(application)
    db.commit()

    return True