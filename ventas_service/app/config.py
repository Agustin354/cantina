import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB  = os.getenv("MONGODB_DB", "quiosco")
SECRET_KEY  = os.getenv("SECRET_KEY", "tia_perla_secret_key_2024")
PORT        = int(os.getenv("PORT", 5000))

# ═══════════════════════════════════════════════════════════════
# <<CONFIGURACIÓN DE FICHAS>>
# 1 ficha = VALOR_FICHA guaraníes
# DENOMINACIONES: valores en Gs. disponibles para emitir
# ═══════════════════════════════════════════════════════════════
VALOR_FICHA   = 500          # 1 ficha = 500 Guaraníes
DENOMINACIONES = [1000, 5000, 10000, 15000, 20000]
PRECIO_MINIMO_GS = 500       # precio mínimo válido
PRECIO_MULTIPLO  = 500       # todo precio debe ser múltiplo de este valor

# ── Rangos de precio (en Guaraníes) ──────────────────────────
RANGO_ECONOMICO_MAX = 2000   # < 3000 Gs.
RANGO_ESTANDAR_MAX  = 4000   # 3000 – 4000 Gs.
# premium: > 4000 Gs.


def calcular_rango(precio_guaranies: int) -> str:
    if precio_guaranies < 3000:
        return "economico"
    if precio_guaranies <= 4000:
        return "estandar"
    return "premium"


USUARIOS = {
    "Ventas":     {"password": "Ventas",     "role": "ventas"},
    "Producción": {"password": "Producción", "role": "produccion"},
}

# ═══════════════════════════════════════════════════════════════
# <<DENOMINACIONES INICIALES DE FICHAS>>
# Se insertan en la colección fichas_denominaciones si está vacía.
# color: código HEX para visualización en el panel.
# ═══════════════════════════════════════════════════════════════
DENOMINACIONES_INICIALES = [
    {"nombre": "Ficha 1",  "valor_gs":  1000, "color": "#95A5A6", "activo": True},
    {"nombre": "Ficha 5",  "valor_gs":  5000, "color": "#27AE60", "activo": True},
    {"nombre": "Ficha 10", "valor_gs": 10000, "color": "#2980B9", "activo": True},
    {"nombre": "Ficha 15", "valor_gs": 15000, "color": "#8E44AD", "activo": True},
    {"nombre": "Ficha 20", "valor_gs": 20000, "color": "#E67E22", "activo": True},
]

# ═══════════════════════════════════════════════════════════════
# <<PRODUCTOS INICIALES>>
# precio       = cantidad de fichas (precio_guaranies // VALOR_FICHA)
# precio_guaranies = valor real en Gs.
# rango        = "economico" | "estandar" | "premium"
# categoria    = "salado" | "dulce" | "bebida"
#
# NOTA: se insertan solo si la colección `productos` está vacía.
# Si ya existen productos anteriores (placeholder) en Atlas,
# vaciar la colección antes de iniciar el servicio.
# ═══════════════════════════════════════════════════════════════
PRODUCTOS_INICIALES = [
    # ── Salados / Comedor ────────────────────────────────────
    # precio = precio_guaranies // VALOR_FICHA (500 Gs)
    # ── Lista 1: Salados ─────────────────────────────────────
    {
        "nombre": "Chipa",
        "precio": 4,  "precio_guaranies": 2000,
        "stock": 50,  "categoria": "salado", "rango": "economico", "activo": True,
    },
    {
        "nombre": "Sandwich Verdura",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 30,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Sandwich Milanesa Carne",
        "precio": 12, "precio_guaranies": 6000,
        "stock": 20,  "categoria": "salado", "rango": "premium",   "activo": True,
    },
    {
        "nombre": "Sandwich Milanesa Pollo",
        "precio": 12, "precio_guaranies": 6000,
        "stock": 20,  "categoria": "salado", "rango": "premium",   "activo": True,
    },
    {
        "nombre": "Bauru Primavera",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 30,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Empanada Carne",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 50,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Empanada JyQ",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 50,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Empanada Pollo",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 50,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Mixto JyQ",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 30,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Arrolladito JyQ",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 30,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Arrolladito Pachao",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 30,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Pizza",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 20,  "categoria": "salado", "rango": "estandar",  "activo": True,
    },
    # ── Lista 2: Dulces ──────────────────────────────────────
    {
        "nombre": "Mix Frutas",
        "precio": 14, "precio_guaranies": 7000,
        "stock": 15,  "categoria": "dulce",  "rango": "premium",   "activo": True,
    },
    {
        "nombre": "Sandía en Trozos",
        "precio": 10, "precio_guaranies": 5000,
        "stock": 15,  "categoria": "dulce",  "rango": "premium",   "activo": True,
    },
    {
        "nombre": "Ensalada de Frutas",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 20,  "categoria": "dulce",  "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Marmolada",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 20,  "categoria": "dulce",  "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Torta de Banana",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 20,  "categoria": "dulce",  "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Villarboa Huevo",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 20,  "categoria": "dulce",  "rango": "estandar",  "activo": True,
    },
    # ── Lista 2: Bebidas ─────────────────────────────────────
    {
        "nombre": "Jugo Natural",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 30,  "categoria": "bebida", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Café Negro",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 40,  "categoria": "bebida", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Café c/ Leche",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 40,  "categoria": "bebida", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Cocido Negro",
        "precio": 6,  "precio_guaranies": 3000,
        "stock": 40,  "categoria": "bebida", "rango": "estandar",  "activo": True,
    },
    {
        "nombre": "Cocido c/ Leche",
        "precio": 8,  "precio_guaranies": 4000,
        "stock": 40,  "categoria": "bebida", "rango": "estandar",  "activo": True,
    },
]
