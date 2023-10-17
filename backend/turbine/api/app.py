from .auth import get_user
from logging import getLogger
import logging
from .routers import tasks, pipelines, misc
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from turbine.database import db, User, Task, Pipeline
from peewee import IntegrityError
from contextlib import asynccontextmanager
from fastapi import Request, HTTPException


logger = getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        db.connect()
        db.create_tables([User, Task, Pipeline])
        User.create(api_key="b4f9137a-81bc-4acf-ae4e-ee33bef63dec")
    except IntegrityError:
        pass

    yield
    db.close()


app = FastAPI(
    dependencies=[Depends(get_user)],
    lifespan=lifespan,
)


@app.middleware("http")
async def db_middleware(request: Request, call_next):
    try:
        if db.is_closed():
            db.connect()
    except Exception as e:
        logger.error(f"Error while connecting to database: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    response = await call_next(request)

    try:
        if not db.is_closed():
            db.close()
    except Exception as e:
        logger.error(f"Error while closing database: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://console.useturbine.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(pipelines.router)
app.include_router(misc.router)
