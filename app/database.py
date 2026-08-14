import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Cargar las variables del archivo .env si estamos en local
load_dotenv()

# Intentar obtener credenciales de Turso
TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

if TURSO_URL and TURSO_TOKEN:
    # Si existen variables de Turso (por ejemplo, en Render o en tu .env local)
    clean_url = TURSO_URL.replace("libsql://", "").replace("https://", "")
    DATABASE_URL = f"sqlite+libsql://{clean_url}?authToken={TURSO_TOKEN}&secure=true"
    connect_args = {}
else:
    # Si no hay credenciales de Turso, usamos la base SQLite local como siempre
    DATABASE_URL = "sqlite:///./tablon.db"
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session