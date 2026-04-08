import logging
import json
from repositories.producto_repo import listar_activos, obtener_por_id, actualizar_stock

logger = logging.getLogger(__name__)


def obtener_productos():
    return listar_activos()


def verificar_y_descontar_stock(items):
    """Valida stock de todos los items antes de descontar ninguno."""
    for item in items:
        producto = obtener_por_id(item["producto_id"])
        if not producto:
            raise ValueError(f"Producto no encontrado")
        if not producto.get("activo", False):
            raise ValueError(f"El producto '{producto['nombre']}' no está disponible")
        if producto["stock"] < item["cantidad"]:
            raise ValueError(
                f"Stock insuficiente para '{producto['nombre']}'. "
                f"Disponible: {producto['stock']}, solicitado: {item['cantidad']}"
            )

    for item in items:
        actualizar_stock(item["producto_id"], item["cantidad"])
        logger.info(json.dumps({
            "event": "stock_descontado",
            "producto_id": item["producto_id"],
            "nombre": item.get("nombre", ""),
            "cantidad": item["cantidad"],
        }))
