from datetime import datetime
from database import get_db
from config import VALOR_FICHA


def ventas_del_dia(fecha=None):
    db = get_db()
    if fecha is None:
        fecha = datetime.utcnow().strftime("%Y-%m-%d")
    ventas = list(db.ventas_productos.find({"fecha": fecha}).sort("timestamp", -1))
    for v in ventas:
        v["_id"] = str(v["_id"])
    return ventas


def todas_las_ventas():
    db = get_db()
    ventas = list(db.ventas_productos.find().sort("timestamp", -1))
    for v in ventas:
        v["_id"] = str(v["_id"])
    return ventas


def top_productos(limite=5):
    db = get_db()
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id":            "$items.nombre",
            "total_cantidad": {"$sum": "$items.cantidad"},
            "total_fichas":   {"$sum": "$items.subtotal_fichas"},
        }},
        {"$sort": {"total_cantidad": -1}},
        {"$limit": limite},
    ]
    return list(db.ventas_productos.aggregate(pipeline))


def ventas_por_producto():
    db = get_db()
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id":            "$items.nombre",
            "total_cantidad": {"$sum": "$items.cantidad"},
            "total_fichas":   {"$sum": "$items.subtotal_fichas"},
        }},
        {"$sort": {"total_cantidad": -1}},
    ]
    return list(db.ventas_productos.aggregate(pipeline))


def total_ventas_guaranies():
    db = get_db()
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total_fichas"}}},
    ]
    result = list(db.ventas_productos.aggregate(pipeline))
    return (result[0]["total"] if result else 0) * VALOR_FICHA


def ventas_por_producto_periodo(fecha_inicio: str, fecha_fin: str) -> list:
    db = get_db()
    pipeline = [
        {"$match": {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id":            "$items.nombre",
            "total_cantidad": {"$sum": "$items.cantidad"},
            "total_fichas":   {"$sum": "$items.subtotal_fichas"},
        }},
        {"$sort": {"total_cantidad": -1}},
    ]
    return list(db.ventas_productos.aggregate(pipeline))


def ventas_guaranies_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    db = get_db()
    pipeline = [
        {"$match": {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_fichas"}}},
    ]
    result = list(db.ventas_productos.aggregate(pipeline))
    return (result[0]["total"] if result else 0) * VALOR_FICHA
