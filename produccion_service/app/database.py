import logging
import json
from pymongo import MongoClient, DESCENDING, ASCENDING
from config import MONGODB_URI, MONGODB_DB

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
            _ensure_indexes(_db)
            logger.info(json.dumps({"event": "db_conectada", "base": MONGODB_DB}))
        except Exception as e:
            logger.error(json.dumps({"event": "error_db", "detalle": str(e)}))
            raise
    return _db


def _ensure_indexes(db):
    db.ventas_productos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("fecha", DESCENDING)])
    db.fichas_movimientos.create_index([("tipo", ASCENDING)])
