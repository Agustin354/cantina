import logging
import json
from models.ficha_movimiento import crear_movimiento
from repositories.ficha_repo import guardar_movimiento, total_fichas_emitidas, total_fichas_usadas

logger = logging.getLogger(__name__)

VALOR_FICHA = 1000


def emitir_fichas(denominacion, cantidad):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a cero")
    if denominacion not in [1000, 5000, 10000, 15000, 20000]:
        raise ValueError("Denominación no válida")

    monto_guaranies = denominacion * cantidad
    cantidad_fichas = monto_guaranies // VALOR_FICHA
    observacion = f"Emisión: {cantidad}x {denominacion:,} Gs."
    movimiento = crear_movimiento("emision", monto_guaranies, observacion)
    mov_id = guardar_movimiento(movimiento)

    logger.info(json.dumps({
        "event": "fichas_emitidas",
        "denominacion": denominacion,
        "cantidad_billetes": cantidad,
        "monto_guaranies": monto_guaranies,
        "cantidad_fichas": cantidad_fichas,
    }))

    return {
        "id": mov_id,
        "monto_guaranies": monto_guaranies,
        "cantidad_fichas": cantidad_fichas,
    }


def registrar_uso_fichas(total_fichas, observacion="Venta de productos"):
    monto_guaranies = total_fichas * VALOR_FICHA
    movimiento = crear_movimiento("uso", monto_guaranies, observacion)
    return guardar_movimiento(movimiento)


def saldo_fichas_disponibles():
    emitidas = total_fichas_emitidas()
    usadas = total_fichas_usadas()
    return emitidas - usadas
