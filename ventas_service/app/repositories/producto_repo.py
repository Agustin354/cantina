from bson import ObjectId
from database import get_db


def listar_activos():
    db = get_db()
    productos = list(db.productos.find({"activo": True}))
    for p in productos:
        p["_id"] = str(p["_id"])
    return productos


def obtener_por_id(producto_id):
    db = get_db()
    try:
        p = db.productos.find_one({"_id": ObjectId(producto_id)})
    except Exception:
        return None
    if p:
        p["_id"] = str(p["_id"])
    return p


def actualizar_stock(producto_id, cantidad):
    db = get_db()
    db.productos.update_one(
        {"_id": ObjectId(producto_id)},
        {"$inc": {"stock": -cantidad}},
    )
