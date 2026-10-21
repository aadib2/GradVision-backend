from sqlalchemy import select
from sqlalchemy.orm import Session

from models import (
    User,
    Professor,
    University,
    Program,
    SavedProgram,
    CalendarEvent,
)

from schemas import (
    UserCreate,
    UserUpdate,
    ProfessorRead,
    UniversitySummary,
    University,
    ProgramSummary,
    Program,
    Application,
    Paper,
    CalendarEvent,
)


def create_user(db: Session, user: UserCreate) -> User | None:
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    return db.execute(statement).scalar_one_or_none()


def update_user(db: Session, user_id: int, user: UserUpdate) -> User | None:
    db_user = get_user(db, user_id)

    if db_user:
        for key, value in user.dict().items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)

    return db_user


def delete_user(db: Session, user_id: int) -> User | None:
    db_user = get_user(db, user_id)

    if db_user:
        db.delete(db_user)
        db.commit()

    return db_user


def search_universities(db: Session, user_id: int, location: str = None, program_type: str = None) -> list[University] | None:
    user = get_user(db, user_id)

    if not user:
        return []

    program_statement = select(Program).where(
        Program.program_type == program_type,
        Program.field == user.program_interests,
    )
    programs = db.execute(program_statement).scalars().all()

    university_statement = select(University).where(
        University.location == location,
        University.programs == programs,
    )
    universities = db.execute(university_statement).scalars().all()

    return universities


def get_professors(db: Session, university_id: int, user_id: int) -> list[ProfessorRead] | None:
    user = get_user(db, user_id)

    if not user:
        return []

    statement = select(ProfessorRead).where(
        ProfessorRead.university_id == university_id,
        ProfessorRead.research_interests.overlap(user.research_interests)
    )

    return db.execute(statement).scalars().all()


def get_programs_from_university(db: Session, university_id: int, field: str = None, degree_type: str = None) -> list[ProgramSummary] | None:
    conditions = [
        ProgramSummary.university_id == university_id
    ]

    if field:
        conditions.append(ProgramSummary.field == field)

    if degree_type:
        conditions.append(ProgramSummary.degree_type == degree_type)

    statement = select(ProgramSummary).where(*conditions)

    return db.execute(statement).scalars().all()


def get_program(db: Session, program_id: int) -> ProgramSummary | None:
    statement = select(ProgramSummary).where(
        ProgramSummary.program_id == program_id
    )

    return db.execute(statement).scalars().first()


def save_program(db: Session, program_id: int, user_id: int) -> SavedProgram | None:
    user = get_user(db, user_id)
    program = get_program(db, program_id)

    if program and user:
        saved_program = SavedProgram(
            user_id=user_id,
            program_id=program_id,
        )

        db.add(saved_program)
        db.commit()
        db.refresh(saved_program)

        user.saved_programs.append(saved_program)

        return saved_program

    return []


def remove_program(db: Session, program_id: int, user_id: int) -> SavedProgram | None:
    user = get_user(db, user_id)
    program = get_program(db, program_id)

    if program and user:
        statement = select(SavedProgram).where(
            SavedProgram.user_id == user_id,
            SavedProgram.program_id == program_id,
        )

        saved_program = db.execute(statement).scalars().first()

        if saved_program:
            db.delete(saved_program)
            db.commit()

            user.saved_programs.remove(saved_program)

            return saved_program

    return []


def get_saved_programs(db: Session, user_id: int) -> list[ProgramSummary] | None:
    user = get_user(db, user_id)

    if not user:
        return []

    return user.saved_programs


def get_due_dates(db: Session, user_id: int): #need to implement still
    user = get_user(db, user_id)

    return []


def get_papers(db: Session, professor_id: int) -> list[Paper] | None:
    statement = select(Paper).where(
        Paper.professor_ids.contains([professor_id])
    )

    return db.execute(statement).scalars().all()


def auth_login(db: Session, username: str, password: str) -> User | None:
    # Implement the logic to authenticate a user
    # This is a placeholder implementation; you should replace it with your actual authentication logic
    statement = select(User).where(
        User.username == username,
        User.password == password,
    )

    return db.execute(statement).scalars().first()


def auth_logout(db: Session, user_id: int):
    # Implement the logic to log out a user
    # This is a placeholder implementation; you should replace it with your actual logout logic
    pass


def auth_refresh(db: Session, user_id: int):
    # Implement the logic to refresh authentication for a user
    # This is a placeholder implementation; you should replace it with your actual refresh logic
    pass


def get_applications(db: Session, user_id: int) -> list[Application] | None:
    user = get_user(db, user_id)

    if not user:
        return []

    applications = user.applications

    return applications


def update_application(
    db: Session,
    application_id: int,
    user_id: int,
    application_data,
):
    # Implement the logic to update an application for a user
    # This is a placeholder implementation; you should replace it with your actual update logic
    statement = select(Application).where(
        Application.id == application_id,
        Application.user_id == user_id,
    )

    application = db.execute(statement).scalars().first()

    if application:
        for key, value in application_data.items():
            setattr(application, key, value)

        db.commit()
        db.refresh(application)

    return application


def get_tasks(db: Session, user_id: int):
    # Implement the logic to retrieve tasks for a user
    # This is a placeholder implementation; you should replace it with your actual retrieval logic
    tasks = []

    return tasks


def add_task(db: Session, user_id: int, task_data):
    # Implement the logic to add a task for a user
    # This is a placeholder implementation; you should replace it with your actual add logic
    new_task = Task(**task_data, user_id=user_id)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    task_data,
):
    # Implement the logic to update a task for a user
    # This is a placeholder implementation; you should replace it with your actual update logic
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
    )

    task = db.execute(statement).scalars().first()

    if task:
        for key, value in task_data.items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)

    return task


def remove_task(db: Session, task_id: int, user_id: int):
    # Implement the logic to remove a task for a user
    # This is a placeholder implementation; you should replace it with your actual remove logic
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
    )

    task = db.execute(statement).scalars().first()

    if task:
        db.delete(task)
        db.commit()

    return task