import logging
import json
from datetime import datetime
from bson import ObjectId
from database import get_db

logger = logging.getLogger(__name__)


def listar_activos() -> list:
    db = get_db()
    productos = list(db.productos.find({"activo": True}).sort("nombre", 1))
    for p in productos:
        p["_id"] = str(p["_id"])
    return productos


def listar_todos() -> list:
    """Incluye inactivos — solo para el panel de gestión."""
    db = get_db()
    productos = list(db.productos.find({}).sort("nombre", 1))
    for p in productos:
        p["_id"] = str(p["_id"])
    return productos


def obtener_por_id(producto_id: str) -> dict | None:
    db = get_db()
    try:
        p = db.productos.find_one({"_id": ObjectId(producto_id)})
    except Exception:
        return None
    if p:
        p["_id"] = str(p["_id"])
    return p


def buscar_por_nombre(nombre: str) -> dict | None:
    """Búsqueda insensible a mayúsculas para validar nombre único."""
    db = get_db()
    return db.productos.find_one({"nombre": {"$regex": f"^{nombre}$", "$options": "i"}})


def insertar_producto(doc: dict) -> str:
    db = get_db()
    result = db.productos.insert_one(doc)
    logger.info(json.dumps({
        "event":    "producto_insertado",
        "id":       str(result.inserted_id),
        "nombre":   doc.get("nombre", ""),
    }))
    return str(result.inserted_id)


def actualizar_precio(producto_id: str, nuevo_precio: int, nuevo_precio_gs: int,
                      nuevo_rango: str, usuario: str = "sistema") -> None:
    # ┌─────────────────────────────────────────────────────────────────┐
    # │ [SECCIÓN]  audit_precio                                         │
    # │ [PROPÓSITO] Registrar historial antes de actualizar             │
    # │ [INPUT]    producto_id, precios nuevos, usuario                 │
    # │ [OUTPUT]   Documento actualizado + entrada en historial_precios  │
    # └─────────────────────────────────────────────────────────────────┘
    db = get_db()
    prod = db.productos.find_one({"_id": ObjectId(producto_id)})
    if not prod:
        return

    entrada_hist = {
        "fecha":              datetime.utcnow(),
        "precio_anterior":    prod.get("precio", 0),
        "precio_nuevo":       nuevo_precio,
        "precio_anterior_gs": prod.get("precio_guaranies", 0),
        "precio_nuevo_gs":    nuevo_precio_gs,
        "modificado_por":     usuario,
    }

    db.productos.update_one(
        {"_id": ObjectId(producto_id)},
        {
            "$set": {
                "precio":             nuevo_precio,
                "precio_guaranies":   nuevo_precio_gs,
                "rango":              nuevo_rango,
                "fecha_modificacion": datetime.utcnow(),
            },
            "$push": {"historial_precios": entrada_hist},
        }
    )
    logger.info(json.dumps({
        "event":         "precio_actualizado",
        "producto_id":   producto_id,
        "precio_ant_gs": entrada_hist["precio_anterior_gs"],
        "precio_nuevo_gs": nuevo_precio_gs,
        "usuario":       usuario,
    }))


def desactivar_producto(producto_id: str) -> None:
    db = get_db()
    db.productos.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": {"activo": False, "fecha_baja": datetime.utcnow()}}
    )
    logger.info(json.dumps({"event": "producto_desactivado", "producto_id": producto_id}))


def activar_producto(producto_id: str) -> None:
    db = get_db()
    db.productos.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": {"activo": True, "fecha_activacion": datetime.utcnow()}}
    )
    logger.info(json.dumps({"event": "producto_activado", "producto_id": producto_id}))


def actualizar_stock(producto_id: str, cantidad: int) -> None:
    db = get_db()
    db.productos.update_one(
        {"_id": ObjectId(producto_id)},
        {"$inc": {"stock": -cantidad}},
    )
