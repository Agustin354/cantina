from datetime import datetime


def crear_venta(items, total_fichas, forma_pago="fichas"):
    now = datetime.utcnow()
    return {
        "fecha": now.strftime("%Y-%m-%d"),
        "items": items,
        "total_fichas": total_fichas,
        "forma_pago": forma_pago,
        "timestamp": now,
    }
