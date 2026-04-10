import logging
import json
from bson import ObjectId
from database import get_db

logger = logging.getLogger(__name__)


def listar_activas() -> list:
    db = get_db()
    docs = list(db.fichas_denominaciones.find({"activo": True}).sort("valor_gs", 1))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


def buscar_por_valor(valor_gs: int) -> dict | None:
    db = get_db()
    return db.fichas_denominaciones.find_one({"valor_gs": valor_gs, "activo": True})


def insertar_denominacion(doc: dict) -> str:
    db = get_db()
    result = db.fichas_denominaciones.insert_one(doc)
    logger.info(json.dumps({
        "event":    "denominacion_insertada",
        "id":       str(result.inserted_id),
        "valor_gs": doc.get("valor_gs", 0),
        "nombre":   doc.get("nombre", ""),
    }))
    return str(result.inserted_id)
