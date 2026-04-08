from datetime import datetime
from database import get_db


def guardar_venta(venta):
    db = get_db()
    result = db.ventas_productos.insert_one(venta)
    return str(result.inserted_id)


def ventas_del_dia(fecha=None):
    db = get_db()
    if fecha is None:
        fecha = datetime.utcnow().strftime("%Y-%m-%d")
    ventas = list(db.ventas_productos.find({"fecha": fecha}).sort("timestamp", -1))
    for v in ventas:
        v["_id"] = str(v["_id"])
    return ventas
