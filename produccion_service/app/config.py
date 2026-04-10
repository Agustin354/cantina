import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB  = os.getenv("MONGODB_DB", "quiosco")
SECRET_KEY  = os.getenv("SECRET_KEY", "tia_perla_secret_key_2024")
PORT        = int(os.getenv("PORT", 5001))
VALOR_FICHA = 500   # 1 ficha = 500 Guaraníes

# Prefijo externo cuando se sirve detrás de NGINX (ej. /produccion)
# Vacío para acceso directo en el puerto 5001
EXTERNAL_PREFIX = os.getenv("EXTERNAL_PREFIX", "")

USUARIOS = {
    "Producción": {"password": "Producción", "role": "produccion"},
}

REPORTS_DIR_VENTAS     = "/reports/ventas"
REPORTS_DIR_PRODUCCION = "/reports/produccion"
