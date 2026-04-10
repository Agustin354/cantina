from database import get_db


def todos_los_movimientos():
    db = get_db()
    movs = list(db.fichas_movimientos.find().sort("timestamp", -1))
    for m in movs:
        m["_id"] = str(m["_id"])
    return movs


def movimientos_del_periodo(fecha_inicio: str, fecha_fin: str) -> list:
    db = get_db()
    movs = list(db.fichas_movimientos.find(
        {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    ).sort("timestamp", -1))
    for m in movs:
        m["_id"] = str(m["_id"])
    return movs


def total_fichas_emitidas():
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "emision"}},
        {"$group": {"_id": None, "total": {"$sum": "$cantidad_fichas"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0


def fichas_emitidas_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "emision", "fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$group": {"_id": None, "total": {"$sum": "$cantidad_fichas"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0


def total_fichas_usadas():
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "uso"}},
        {"$group": {"_id": None, "total": {"$sum": "$cantidad_fichas"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0


def fichas_usadas_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "uso", "fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$group": {"_id": None, "total": {"$sum": "$cantidad_fichas"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0


def total_ingresado_guaranies():
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "emision"}},
        {"$group": {"_id": None, "total": {"$sum": "$monto_guaranies"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0


def ingresado_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "emision", "fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
        {"$group": {"_id": None, "total": {"$sum": "$monto_guaranies"}}},
    ]
    result = list(db.fichas_movimientos.aggregate(pipeline))
    return result[0]["total"] if result else 0
