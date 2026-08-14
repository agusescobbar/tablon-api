import uuid
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .config import ADMIN_KEY, SESSION_COOKIE_MAX_AGE_SECONDS, SESSION_COOKIE_NAME
from .database import create_db_and_tables, get_session
from .models import Message
from .schemas import MessageCreate, MessagePublic, MessageUpdate

app = FastAPI(
    title="Tablón de Anuncios",
    description="API CRUD para publicar y moderar mensajes cortos de forma anónima.",
    version="1.0.0",
)

# El frontend (Vite) corre en otro puerto, así que necesita CORS habilitado.
# allow_credentials=True es obligatorio para que la cookie de sesión viaje
# entre front y back; por eso NO se puede usar allow_origins=["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


def get_or_set_session_id(request: Request, response: Response) -> str:
    """Lee el id de sesión de la cookie, o crea uno nuevo si no existe."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        )
    return session_id


def require_admin(x_admin_key: Optional[str] = Header(default=None)) -> None:
    """Dependencia de autorización simple basada en un header 'X-Admin-Key'."""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de administrador inválida o ausente.",
        )


@app.post(
    "/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Publicar un mensaje",
)
def create_message(
    payload: MessageCreate,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> Message:
    session_id = get_or_set_session_id(request, response)

    existing = session.exec(
        select(Message).where(Message.session_id == session_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Ya publicaste un mensaje. Solo se permite un mensaje por sesión.",
        )

    message = Message(content=payload.content, session_id=session_id)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@app.get(
    "/messages",
    response_model=List[MessagePublic],
    summary="Listar mensajes",
)
def list_messages(
    session: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
) -> List[Message]:
    statement = (
        select(Message)
        .order_by(Message.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return session.exec(statement).all()


@app.get(
    "/messages/{message_id}",
    response_model=MessagePublic,
    summary="Obtener un mensaje puntual",
)
def get_message(message_id: int, session: Session = Depends(get_session)) -> Message:
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")
    return message


@app.patch(
    "/messages/{message_id}",
    response_model=MessagePublic,
    summary="Editar un mensaje (solo admin)",
)
def update_message(
    message_id: int,
    payload: MessageUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> Message:
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")

    # Extraemos solo los datos que enviaron explícitamente en el JSON
    message_data = payload.model_dump(exclude_unset=True)

    for key, value in message_data.items():
        setattr(message, key, value)

    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@app.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un mensaje (solo admin)",
)
def delete_message(
    message_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
) -> None:
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado.")
    session.delete(message)
    session.commit()


@app.get("/health")
def health_check():
    return {"status": "ok"}