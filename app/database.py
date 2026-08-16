import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if TURSO_URL and TURSO_TOKEN:
    # El auth_token va en connect_args, NO como query param en la URL
    DATABASE_URL = f"sqlite+{TURSO_URL}?secure=true"
    connect_args = {"auth_token": TURSO_TOKEN}
else:
    # Base de datos local para desarrollo
    DATABASE_URL = "sqlite:///./tablon.db"
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session