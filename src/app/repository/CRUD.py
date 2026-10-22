"""holding in case we are missing any of the operations in the crud folder

from sqlalchemy.orm import Session
from models import User, Professor, University, Program, SavedProgram, CalendarEvent
from schemas import UserCreate, UserUpdate 
from schemas import ProfessorRead, UniversitySummary, University
from schemas import ProgramSummary, Program, Application
from schemas import ProfessorRead, Paper
from schemas import CalendarEvent

def create_user(db:Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db:Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db:Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db:Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def search_universities(db:Session, user_id: int, location: str = None, program_type: str = None):
    user = get_user(db, user_id)
    if not user:
        return []

    programs = db.query(Program).filter(Program.program_type == program_type, Program.field == user.program_interests).all()
    universities = db.query(University).filter(University.location == location, University.programs == programs).all()
    return universities

def get_professors(db:Session, university_id: int, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    return db.query(ProfessorRead).filter(ProfessorRead.university_id == university_id, ProfessorRead.research_interests == user.research_interests).all()

def get_programs_from_university(db:Session, university_id: int, field: str = None, degree_type: str = None):
    query = db.query(ProgramSummary).filter(ProgramSummary.university_id == university_id)
    if field:
        query = query.filter(ProgramSummary.field == field)
    if degree_type:
        query = query.filter(ProgramSummary.degree_type == degree_type)
    return query.all()

def get_program(db:Session, program_id: int):
    return db.query(ProgramSummary).filter(ProgramSummary.program_id == program_id).first()

def save_program(db:Session, program_id: int, user_id: int):
    user = get_user(db, user_id)
    program = get_program(db, program_id)
    
#     if program and user:
#         saved_program = SavedProgram(user_id=user_id, program_id=program_id)
#         db.add(saved_program)
#         db.commit()
#         db.refresh(saved_program)
#         user.saved_programs.append(saved_program)
#         return saved_program
#     return []

# def remove_program(db:Session, program_id: int, user_id: int):
#     user = get_user(db, user_id)
#     program = get_program(db, program_id)

#     if program and user:
#         saved_program = db.query(SavedProgram).filter(SavedProgram.user_id == user_id, SavedProgram.program_id == program_id).first()
#         if saved_program:
#             db.delete(saved_program)
#             db.commit()
#             user.saved_programs.remove(saved_program)
#             return saved_program
#     return []
        

# def get_saved_programs(db:Session, user_id: int):
#     user = get_user(db, user_id)
#     if not user:
#         return []
    
#     return user.saved_programs

# def get_due_dates(db:Session, user_id: int):
#     # Implement the logic to retrieve due dates for a user's saved programs
#     # This is a placeholder implementation; you should replace it with your actual retrieval logic
#     due_dates = []  # Replace with actual query to get due dates for the user's saved programs
#     return due_dates

# def get_papers(db:Session, professor_id: int):
#     papers = db.query(Paper).filter(Paper.professor_ids.contains([professor_id])).all()
#     return papers

# def auth_login(db:Session, username: str, password: str):
#     # Implement the logic to authenticate a user
#     # This is a placeholder implementation; you should replace it with your actual authentication logic
#     user = db.query(User).filter(User.username == username, User.password == password).first()
#     return user

# def auth_logout(db:Session, user_id: int):
#     # Implement the logic to log out a user
#     # This is a placeholder implementation; you should replace it with your actual logout logic
#     pass

# def auth_refresh(db:Session, user_id: int):
#     # Implement the logic to refresh authentication for a user
#     # This is a placeholder implementation; you should replace it with your actual refresh logic
#     pass

# def get_applications(db:Session, user_id: int):
#     user = get_user(db, user_id)
#     if not user:
#         return []
#     applications = user.applications
#     return applications

# def update_application(db:Session, application_id: int, user_id: int, application_data):
#     # Implement the logic to update an application for a user
#     # This is a placeholder implementation; you should replace it with your actual update logic
#     application = db.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
#     if application:
#         for key, value in application_data.items():
#             setattr(application, key, value)
#         db.commit()
#         db.refresh(application)
#     return application

# def get_tasks(db:Session, user_id: int):
#     # Implement the logic to retrieve tasks for a user
#     # This is a placeholder implementation; you should replace it with your actual retrieval logic
#     tasks = []  # Replace with actual query to get tasks for the user
#     return tasks

# def add_task(db:Session, user_id: int, task_data):
#     # Implement the logic to add a task for a user
#     # This is a placeholder implementation; you should replace it with your actual add logic
#     new_task = Task(**task_data, user_id=user_id)
#     db.add(new_task)
#     db.commit()
#     db.refresh(new_task)
#     return new_task

# def update_task(db:Session, task_id: int, user_id: int, task_data):
#     # Implement the logic to update a task for a user
#     # This is a placeholder implementation; you should replace it with your actual update logic
#     task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
#     if task:
#         for key, value in task_data.items():
#             setattr(task, key, value)
#         db.commit()
#         db.refresh(task)
#     return task

# def remove_task(db:Session, task_id: int, user_id: int):
#     # Implement the logic to remove a task for a user
#     # This is a placeholder implementation; you should replace it with your actual remove logic
#     task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
#     if task:
#         db.delete(task)
#         db.commit()
#     return task

