from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.routes import users as users_routes
from app.routes import programs
from app.routes import papers
from app.routes import auth as auth_routes
from app.routes import applications as applications_routes
from app.routes import task as tasks_routes
from app.routes import search as search_routes
from app.core.database import Base, engine
from app.core.exceptions import http_exception_handler, validation_exception_handler
from app.models import models  # noqa: F401 — register ORM tables with Base.metadata


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Authorization",
        "Content-Language",
        "Content-Type",
        "Origin",
        "X-Requested-With",
    ],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users_routes.router, prefix="/api")
programs.register(app) # add endpoints relating to programs/universities
papers.register(app) # add endpoints relating to papers

app.include_router(auth_routes.router, prefix="/api")
app.include_router(applications_routes.router, prefix="/api")
app.include_router(tasks_routes.router, prefix="/api")
app.include_router(search_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}
