import logging
import json
from config import VALOR_FICHA, PRECIO_MULTIPLO, calcular_rango
from models.producto import crear_producto
from repositories.producto_repo import (
    listar_activos, listar_todos, obtener_por_id, actualizar_stock,
    buscar_por_nombre, insertar_producto, actualizar_precio as repo_actualizar_precio,
    desactivar_producto, activar_producto as repo_activar_producto,
)

logger = logging.getLogger(__name__)

CATEGORIAS_VALIDAS = {"salado", "dulce", "bebida", "general"}


# ═══════════════════════════════════════════════════════════════
# <<OBTENER PRODUCTOS ACTIVOS>>
# Retorna lista de productos disponibles para la venta
# ═══════════════════════════════════════════════════════════════
def obtener_productos() -> list:
    return listar_activos()


# ═══════════════════════════════════════════════════════════════
# <<OBTENER TODOS LOS PRODUCTOS>>
# Para el panel de gestión (incluye inactivos)
# ═══════════════════════════════════════════════════════════════
def obtener_todos_productos() -> list:
    return listar_todos()


# ═══════════════════════════════════════════════════════════════
# <<AGREGAR PRODUCTO>>
# Valida datos y persiste un nuevo producto en la BD
# ───────────────────────────────────────────────────────────────
# <<PARAMS>>
#   data: dict — {nombre, precio_guaranies, stock, categoria}
#
# <<RETURNS>>
#   str — ID del documento insertado
#
# <<ERRORES>>
#   ValueError — nombre vacío, precio inválido, nombre duplicado
#
# <<KAIZEN>>
#   Soporte para precios no múltiplos de 1000 con redondeo automático
# ═══════════════════════════════════════════════════════════════
def agregar_producto(data: dict) -> str:
    nombre = data.get("nombre", "").strip()
    if not nombre:
        raise ValueError("El nombre del producto es obligatorio")

    precio_gs = int(data.get("precio_guaranies", 0))
    if precio_gs <= 0:
        raise ValueError("El precio debe ser mayor a 0")
    if precio_gs % PRECIO_MULTIPLO != 0:
        raise ValueError(f"El precio debe ser múltiplo de {PRECIO_MULTIPLO} Gs.")

    categoria = data.get("categoria", "general")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError(f"Categoría inválida. Use: {', '.join(CATEGORIAS_VALIDAS)}")

    if buscar_por_nombre(nombre):
        raise ValueError(f"Ya existe un producto con el nombre '{nombre}'")

    stock = max(0, int(data.get("stock", 0)))
    doc   = crear_producto(nombre, precio_gs, stock, categoria)
    pid   = insertar_producto(doc)

    logger.info(json.dumps({
        "event":    "producto_agregado",
        "id":       pid,
        "nombre":   nombre,
        "precio_gs": precio_gs,
    }))
    return pid


# ═══════════════════════════════════════════════════════════════
# <<ACTUALIZAR PRECIO DE PRODUCTO>>
# Cambia precio, recalcula rango y guarda auditoría
# ───────────────────────────────────────────────────────────────
# <<PARAMS>>
#   producto_id    : str — ObjectId como string
#   nuevo_precio_gs: int — nuevo precio en Guaraníes
#   usuario        : str — nombre del operador (para auditoría)
# ═══════════════════════════════════════════════════════════════
def actualizar_precio_producto(producto_id: str, nuevo_precio_gs: int,
                                usuario: str = "Ventas") -> None:
    nuevo_precio_gs = int(nuevo_precio_gs)
    if nuevo_precio_gs <= 0:
        raise ValueError("El precio debe ser mayor a 0")
    if nuevo_precio_gs % PRECIO_MULTIPLO != 0:
        raise ValueError(f"El precio debe ser múltiplo de {PRECIO_MULTIPLO} Gs.")

    nuevo_precio_fichas = nuevo_precio_gs // VALOR_FICHA
    nuevo_rango         = calcular_rango(nuevo_precio_gs)
    repo_actualizar_precio(producto_id, nuevo_precio_fichas, nuevo_precio_gs, nuevo_rango, usuario)


# ═══════════════════════════════════════════════════════════════
# <<DESACTIVAR PRODUCTO>>
# Marca el producto como inactivo (baja lógica)
# ═══════════════════════════════════════════════════════════════
def dar_baja_producto(producto_id: str) -> None:
    prod = obtener_por_id(producto_id)
    if not prod:
        raise ValueError("Producto no encontrado")
    desactivar_producto(producto_id)


# ═══════════════════════════════════════════════════════════════
# <<ACTIVAR PRODUCTO>>
# Reactiva un producto que estaba en baja lógica
# ═══════════════════════════════════════════════════════════════
def reactivar_producto(producto_id: str) -> None:
    prod = obtener_por_id(producto_id)
    if not prod:
        raise ValueError("Producto no encontrado")
    repo_activar_producto(producto_id)


# ═══════════════════════════════════════════════════════════════
# <<VERIFICAR Y DESCONTAR STOCK>>
# Valida stock de todos los items antes de descontar ninguno
# (two-phase commit: verificar todo primero, luego descontar)
# ═══════════════════════════════════════════════════════════════
def verificar_y_descontar_stock(items: list) -> None:
    for item in items:
        producto = obtener_por_id(item["producto_id"])
        if not producto:
            raise ValueError("Producto no encontrado")
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
            "event":       "stock_descontado",
            "producto_id": item["producto_id"],
            "nombre":      item.get("nombre", ""),
            "cantidad":    item["cantidad"],
        }))
