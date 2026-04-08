from database import get_db


def guardar_movimiento(movimiento):
    db = get_db()
    result = db.fichas_movimientos.insert_one(movimiento)
    return str(result.inserted_id)


def total_fichas_emitidas():
    db = get_db()
    pipeline = [
        {"$match": {"tipo": "emision"}},
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
