from datetime import datetime
from config import VALOR_FICHA


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
