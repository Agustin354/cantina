from datetime import datetime


def crear_denominacion(nombre: str, valor_gs: int, color: str = "#27AE60") -> dict:
    """
    # ═══════════════════════════════════════════════════════════════
    # <<CREAR DOCUMENTO DENOMINACIÓN DE FICHA>>
    # Construye el dict para la colección `fichas_denominaciones`
    # ───────────────────────────────────────────────────────────────
    # <<PARAMS>>
    #   nombre  : str — nombre descriptivo (ej: "Ficha 5")
    #   valor_gs: int — valor en Guaraníes (> 0, múltiplo de 1000)
    #   color   : str — código HEX para mostrar en el panel (#RRGGBB)
    #
    # <<RETURNS>>
    #   dict — documento listo para insert_one()
    #
    # <<ERRORES>>
    #   No valida aquí — la validación ocurre en denominacion_service
    #
    # <<KAIZEN>>
    #   Agregar campo `icono` para representación visual por tipo
    # ═══════════════════════════════════════════════════════════════
    """
    return {
        "nombre":         nombre,
        "valor_gs":       valor_gs,
        "color":          color,
        "activo":         True,
        "fecha_creacion": datetime.utcnow(),
    }
