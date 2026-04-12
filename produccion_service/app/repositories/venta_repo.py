from datetime import datetime
from database import get_db
from config import VALOR_FICHA


def _stringify_ids(docs: list) -> list:
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs


def _pipeline_ventas_por_producto(match: dict = None, limite: int = None) -> list:
    """Construye el pipeline de agregación para ventas por producto."""
    pipeline = []
    if match:
        pipeline.append({"$match": match})
    pipeline += [
        {"$unwind": "$items"},
        {"$group": {
            "_id":            "$items.nombre",
            "total_cantidad": {"$sum": "$items.cantidad"},
            "total_fichas":   {"$sum": "$items.subtotal_fichas"},
        }},
        {"$sort": {"total_cantidad": -1}},
    ]
    if limite:
        pipeline.append({"$limit": limite})
    return pipeline


def ventas_del_dia(fecha=None) -> list:
    db = get_db()
    if fecha is None:
        fecha = datetime.utcnow().strftime("%Y-%m-%d")
    return _stringify_ids(list(
        db.ventas_productos.find({"fecha": fecha}).sort("timestamp", -1)
    ))


def todas_las_ventas() -> list:
    db = get_db()
    return _stringify_ids(list(db.ventas_productos.find().sort("timestamp", -1)))


def top_productos(limite=5) -> list:
    db = get_db()
    return list(db.ventas_productos.aggregate(
        _pipeline_ventas_por_producto(limite=limite)
    ))


def ventas_por_producto() -> list:
    db = get_db()
    return list(db.ventas_productos.aggregate(_pipeline_ventas_por_producto()))


def total_ventas_guaranies() -> int:
    db = get_db()
    result = list(db.ventas_productos.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_fichas"}}},
    ]))
    return (result[0]["total"] if result else 0) * VALOR_FICHA


def ventas_por_producto_periodo(fecha_inicio: str, fecha_fin: str) -> list:
    db = get_db()
    match = {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    return list(db.ventas_productos.aggregate(_pipeline_ventas_por_producto(match=match)))


def ventas_guaranies_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    db = get_db()
    result = list(db.ventas_productos.aggregate([
        {"$match": {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_fichas"}}},
    ]))
    return (result[0]["total"] if result else 0) * VALOR_FICHA
