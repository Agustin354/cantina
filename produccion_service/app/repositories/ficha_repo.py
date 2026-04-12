from database import get_db


def _stringify_ids(docs: list) -> list:
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs


def _sum_fichas(match: dict, field: str = "cantidad_fichas") -> int:
    """Suma `field` en fichas_movimientos con el filtro dado."""
    db = get_db()
    result = list(db.fichas_movimientos.aggregate([
        {"$match": match},
        {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
    ]))
    return result[0]["total"] if result else 0


def _periodo_match(tipo: str, fecha_inicio: str, fecha_fin: str) -> dict:
    return {"tipo": tipo, "fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}


def todos_los_movimientos() -> list:
    db = get_db()
    return _stringify_ids(list(db.fichas_movimientos.find().sort("timestamp", -1)))


def movimientos_del_periodo(fecha_inicio: str, fecha_fin: str) -> list:
    db = get_db()
    return _stringify_ids(list(db.fichas_movimientos.find(
        {"fecha": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    ).sort("timestamp", -1)))


def total_fichas_emitidas() -> int:
    return _sum_fichas({"tipo": "emision"})


def fichas_emitidas_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    return _sum_fichas(_periodo_match("emision", fecha_inicio, fecha_fin))


def total_fichas_usadas() -> int:
    return _sum_fichas({"tipo": "uso"})


def fichas_usadas_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    return _sum_fichas(_periodo_match("uso", fecha_inicio, fecha_fin))


def total_ingresado_guaranies() -> int:
    return _sum_fichas({"tipo": "emision"}, "monto_guaranies")


def ingresado_periodo(fecha_inicio: str, fecha_fin: str) -> int:
    return _sum_fichas(_periodo_match("emision", fecha_inicio, fecha_fin), "monto_guaranies")
