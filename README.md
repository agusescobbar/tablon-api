# Tablón de Anuncios — API

API CRUD en FastAPI para un tablón de mensajes cortos (máx. 140 caracteres), con un mensaje por sesión de navegador y borrado exclusivo para el admin.

## Cómo funciona

- **Sesión**: al primer `POST /messages` de un visitante, la API le asigna una cookie `board_session` (UUID, `httponly`). Esa cookie identifica a la sesión en los próximos requests.
- **Un mensaje por sesión**: se valida dos veces — antes de insertar (devuelve `429`) y a nivel de base de datos (`session_id` es `UNIQUE`), así que no hay forma de esquivarlo aunque haya una condición de carrera.
- **Admin**: el borrado exige un header `X-Admin-Key` que coincida con la variable de entorno `ADMIN_KEY`. Sin ese header, o con uno incorrecto, la API responde `403`.

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configurar la clave de admin

```bash
export ADMIN_KEY="una-clave-larga-y-secreta"   # en Windows: set ADMIN_KEY=...
```

Si no la definís, se usa un valor por defecto (`changeme-admin-key`) — **no lo dejes así en producción**.

## Levantar el servidor

```bash
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`, con documentación interactiva en `http://127.0.0.1:8000/docs`.

## Endpoints

| Método | Ruta               | Descripción                          | Auth requerida |
|--------|--------------------|---------------------------------------|-----------------|
| POST   | `/messages`         | Publica un mensaje (1 por sesión)     | —                |
| GET    | `/messages`         | Lista mensajes (`limit`, `offset`)    | —                |
| GET    | `/messages/{id}`    | Obtiene un mensaje puntual            | —                |
| DELETE | `/messages/{id}`    | Elimina un mensaje                    | Header `X-Admin-Key` |

## Ejemplos con curl

Publicar un mensaje (guardando la cookie de sesión en `cookies.txt`):

```bash
curl -c cookies.txt -X POST http://127.0.0.1:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Hola tablón!"}'
```

Intentar publicar un segundo mensaje con la misma sesión (debería dar `429`):

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "Otro mensaje"}'
```

Listar mensajes:

```bash
curl http://127.0.0.1:8000/messages
```

Borrar un mensaje como admin:

```bash
curl -X DELETE http://127.0.0.1:8000/messages/1 \
  -H "X-Admin-Key: una-clave-larga-y-secreta"
```

## Notas para producción

- La base es SQLite (`tablon.db`) por simplicidad; para producción real conviene Postgres, cambiando solo `DATABASE_URL` en `app/database.py`.
- El límite "un mensaje por sesión" depende de la cookie: si el usuario borra cookies o usa otro navegador, puede volver a publicar. Si necesitás algo más estricto (por IP, por cuenta, etc.), decime y lo sumamos.
- La autenticación de admin es intencionalmente simple (una clave compartida). Para un panel de administración real con varios admins, convendría reemplazarla por JWT o sesiones autenticadas.
