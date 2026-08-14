import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if TURSO_URL and TURSO_TOKEN:
    # Formato oficial y directo para Turso con libsql
    clean_url = TURSO_URL.replace("libsql://", "https://")
    DATABASE_URL = f"sqlite+{clean_url}?authToken={TURSO_TOKEN}&secure=true"
    connect_args = {}
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