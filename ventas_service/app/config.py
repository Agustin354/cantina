import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "quiosco")
SECRET_KEY = os.getenv("SECRET_KEY", "tia_perla_secret_key_2024")
PORT = int(os.getenv("PORT", 5000))

DENOMINACIONES = [1000, 5000, 10000, 15000, 20000]
VALOR_FICHA = 1000

USUARIOS = {
    "Ventas": {"password": "Ventas", "role": "ventas"},
    "Producción": {"password": "Producción", "role": "produccion"},
}

PRODUCTOS_INICIALES = [
    {"nombre": "Coca Cola 500ml", "precio": 5,  "stock": 100, "categoria": "bebidas",  "activo": True},
    {"nombre": "Hamburguesa",      "precio": 13, "stock": 50,  "categoria": "comidas",  "activo": True},
    {"nombre": "Empanada de Carne","precio": 3,  "stock": 200, "categoria": "comidas",  "activo": True},
    {"nombre": "Empanada de Jamón","precio": 3,  "stock": 150, "categoria": "comidas",  "activo": True},
    {"nombre": "Empanada de Pollo","precio": 3,  "stock": 150, "categoria": "comidas",  "activo": True},
    {"nombre": "Papas Fritas",     "precio": 4,  "stock": 80,  "categoria": "comidas",  "activo": True},
    {"nombre": "Agua 500ml",       "precio": 3,  "stock": 120, "categoria": "bebidas",  "activo": True},
    {"nombre": "Lapicera",         "precio": 2,  "stock": 300, "categoria": "utiles",   "activo": True},
    {"nombre": "Cuaderno",         "precio": 15, "stock": 50,  "categoria": "utiles",   "activo": True},
]
