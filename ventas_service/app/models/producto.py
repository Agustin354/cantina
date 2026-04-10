from datetime import datetime
from config import VALOR_FICHA, calcular_rango


def crear_producto(nombre: str, precio_guaranies: int, stock: int, categoria: str = "general") -> dict:
    """
    # ═══════════════════════════════════════════════════════════════
    # <<CREAR DOCUMENTO PRODUCTO>>
    # Construye el dict a insertar en la colección `productos`
    # ───────────────────────────────────────────────────────────────
    # <<PARAMS>>
    #   nombre          : str  — nombre del producto (requerido)
    #   precio_guaranies: int  — precio en Gs., múltiplo de VALOR_FICHA
    #   stock           : int  — unidades iniciales (>= 0)
    #   categoria       : str  — "salado" | "dulce" | "bebida" | "general"
    #
    # <<RETURNS>>
    #   dict — documento listo para insert_one()
    #
    # <<KAIZEN>>
    #   Agregar campo `imagen_url` para mostrar foto en el panel
    # ═══════════════════════════════════════════════════════════════
    """
    precio_fichas = precio_guaranies // VALOR_FICHA
    return {
        "nombre":           nombre,
        "precio":           precio_fichas,
        "precio_guaranies": precio_guaranies,
        "stock":            max(0, stock),
        "categoria":        categoria,
        "rango":            calcular_rango(precio_guaranies),
        "activo":           True,
        "fecha_creacion":   datetime.utcnow(),
        "historial_precios": [],
    }
