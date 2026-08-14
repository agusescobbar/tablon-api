from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./tablon.db"

# check_same_thread=False es necesario porque SQLite + FastAPI
# pueden usar la conexión desde distintos threads de request.
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
