import logging
import json
from datetime import datetime
from pymongo import MongoClient, DESCENDING, ASCENDING
from config import MONGODB_URI, MONGODB_DB, PRODUCTOS_INICIALES

logger = logging.getLogger(__name__)

_client = None
_db = None


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
    db.ventas_productos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("tipo", ASCENDING)])


def _init_data(db):
    if db.productos.count_documents({}) == 0:
        productos = []
        for p in PRODUCTOS_INICIALES:
            prod = dict(p)
            prod["fecha_creacion"] = datetime.utcnow()
            productos.append(prod)
        db.productos.insert_many(productos)
        logger.info(json.dumps({"event": "productos_iniciales_cargados", "cantidad": len(productos)}))
