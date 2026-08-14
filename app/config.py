import os
from dotenv import load_dotenv

# Carga las variables del archivo .env al entorno de Python
load_dotenv()

# Ahora sí busca ADMIN_KEY en .env; si no la encuentra usa "faustirey" por defecto
ADMIN_KEY = os.getenv("ADMIN_KEY", "faustirey")

SESSION_COOKIE_NAME = "board_session"
SESSION_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365 # 1 año