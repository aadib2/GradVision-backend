from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.crud.user import get_user_by_id as get_user
from app.models.models import Program, SavedProgram


def get_program(db: Session, program_id: int) -> Program | None:
    """Return one program with its events loaded, or None if it doesn't exist.

    Returns the ORM object (like crud/user.py does); the route validates it into
    the `Program` schema. `events` is eager-loaded so that works after the query,
    and the route decides whether None means a 404.
    """
    query = (
        select(Program)
        .options(selectinload(Program.events))
        .where(Program.program_id == program_id)
    )
    return db.execute(query).scalar_one_or_none()



def remove_program(db:Session, program_id: int, user_id: int):
    user = get_user(db, user_id)
    program = get_program(db, program_id)

    if program and user:
        saved_program = db.query(SavedProgram).filter(SavedProgram.user_id == user_id, SavedProgram.program_id == program_id).first()
        if saved_program:
            db.delete(saved_program)
            db.commit()
            user.saved_programs.remove(saved_program)
            return saved_program
    return []
        

def get_saved_programs(db:Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    return user.saved_programs

def get_program_by_id(db: Session, program_id: int) -> Program | None:
    return get_program(db, program_id)