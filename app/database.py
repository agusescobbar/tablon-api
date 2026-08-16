import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# DEBUG temporal - borrar después de confirmar
print(f"[DEBUG] TURSO_URL presente: {bool(TURSO_URL)} -> {TURSO_URL}")
print(f"[DEBUG] TURSO_TOKEN presente: {bool(TURSO_TOKEN)}, longitud: {len(TURSO_TOKEN) if TURSO_TOKEN else 0}")

if TURSO_URL and TURSO_TOKEN:
    # Formato oficial para Turso con sqlalchemy-libsql:
    # sqlite+libsql://<host>?authToken=<token>&secure=true
    DATABASE_URL = f"sqlite+{TURSO_URL}?authToken={TURSO_TOKEN}&secure=true"
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