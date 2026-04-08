from datetime import datetime

VALOR_FICHA = 1000


def crear_movimiento(tipo, monto_guaranies, observacion=""):
    now = datetime.utcnow()
    return {
        "fecha": now.strftime("%Y-%m-%d"),
        "tipo": tipo,
        "monto_guaranies": monto_guaranies,
        "cantidad_fichas": monto_guaranies // VALOR_FICHA,
        "valor_ficha": VALOR_FICHA,
        "observacion": observacion,
        "timestamp": now,
    }
