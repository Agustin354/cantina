import logging
import json
from datetime import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING
from config import MONGODB_URI, MONGODB_DB, PRODUCTOS_INICIALES, DENOMINACIONES_INICIALES

logger = logging.getLogger(__name__)

_client = None
_db     = None


def get_db():
    global _client, _db
    if _db is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
            _client.server_info()
            _db = _client[MONGODB_DB]
            _init_indexes(_db)
            _init_data(_db)
            logger.info(json.dumps({"event": "db_conectada", "base": MONGODB_DB}))
        except Exception as e:
            logger.error(json.dumps({"event": "error_db", "detalle": str(e)}))
            raise
    return _db


def _init_indexes(db):
    # ┌─────────────────────────────────────────────────────────────────┐
    # │ [SECCIÓN]  indexes                                              │
    # │ [PROPÓSITO] Crear índices para consultas frecuentes             │
    # │ [INPUT]    db (conexión activa)                                 │
    # │ [OUTPUT]   Índices creados en Atlas (idempotente)               │
    # └─────────────────────────────────────────────────────────────────┘
    db.ventas_productos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("tipo", ASCENDING)])
    db.productos.create_index([("nombre", ASCENDING)], unique=True, sparse=True)
    db.productos.create_index([("categoria", ASCENDING)])
    db.productos.create_index([("rango", ASCENDING)])
    db.fichas_denominaciones.create_index([("valor_gs", ASCENDING)], unique=True)


def _init_data(db):
    # ┌─────────────────────────────────────────────────────────────────┐
    # │ [SECCIÓN]  seed_productos (smart sync)                          │
    # │ [PROPÓSITO] Sincronizar productos con la lista oficial:         │
    # │   1. Eliminar productos que ya no están en PRODUCTOS_INICIALES  │
    # │      (placeholders viejos de sesiones anteriores)               │
    # │   2. Insertar productos que faltan (preserva stock existente)   │
    # │ [INPUT]    PRODUCTOS_INICIALES de config.py                     │
    # │ [OUTPUT]   Colección productos sincronizada con lista oficial   │
    # └─────────────────────────────────────────────────────────────────┘
    nombres_oficiales = [p["nombre"] for p in PRODUCTOS_INICIALES]

    # Paso 1: eliminar documentos que no están en la lista oficial
    resultado_baja = db.productos.delete_many(
        {"nombre": {"$nin": nombres_oficiales}}
    )
    if resultado_baja.deleted_count > 0:
        logger.info(json.dumps({
            "event":    "productos_obsoletos_eliminados",
            "cantidad": resultado_baja.deleted_count,
        }))

    # Paso 2: insertar solo los productos que no existen aún
    nombres_existentes = {
        p["nombre"] for p in db.productos.find({}, {"nombre": 1})
    }
    now      = datetime.utcnow()
    nuevos   = []
    for p in PRODUCTOS_INICIALES:
        if p["nombre"] not in nombres_existentes:
            prod = dict(p)
            prod["fecha_creacion"]    = now
            prod["historial_precios"] = []
            nuevos.append(prod)
    if nuevos:
        db.productos.insert_many(nuevos)
        logger.info(json.dumps({
            "event":    "productos_nuevos_insertados",
            "cantidad": len(nuevos),
            "nombres":  [p["nombre"] for p in nuevos],
        }))

    # ┌─────────────────────────────────────────────────────────────────┐
    # │ [SECCIÓN]  seed_denominaciones                                  │
    # │ [PROPÓSITO] Insertar denominaciones de fichas si no existen     │
    # │ [INPUT]    DENOMINACIONES_INICIALES de config.py                │
    # │ [OUTPUT]   Colección fichas_denominaciones con 5 documentos     │
    # └─────────────────────────────────────────────────────────────────┘
    if db.fichas_denominaciones.count_documents({}) == 0:
        now = datetime.utcnow()
        denoms = []
        for d in DENOMINACIONES_INICIALES:
            doc = dict(d)
            doc["fecha_creacion"] = now
            denoms.append(doc)
        db.fichas_denominaciones.insert_many(denoms)
        logger.info(json.dumps({
            "event":    "denominaciones_iniciales_cargadas",
            "cantidad": len(denoms),
        }))
