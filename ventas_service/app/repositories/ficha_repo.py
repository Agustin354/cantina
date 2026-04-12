from database import get_db


def _sum_fichas(match: dict, field: str = "cantidad_fichas") -> int:
    """Suma `field` en fichas_movimientos con el filtro dado."""
    db = get_db()
    result = list(db.fichas_movimientos.aggregate([
        {"$match": match},
        {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
    ]))
    return result[0]["total"] if result else 0


def guardar_movimiento(movimiento):
    db = get_db()
    result = db.fichas_movimientos.insert_one(movimiento)
    return str(result.inserted_id)


def total_fichas_emitidas() -> int:
    return _sum_fichas({"tipo": "emision"})


def total_fichas_usadas() -> int:
    return _sum_fichas({"tipo": "uso"})
