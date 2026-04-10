from repositories.venta_repo import ventas_del_dia, top_productos, total_ventas_guaranies
from repositories.ficha_repo import (
    total_fichas_emitidas, total_fichas_usadas, total_ingresado_guaranies
)
from config import VALOR_FICHA


def calcular_stats():
    emitidas        = total_fichas_emitidas()
    usadas          = total_fichas_usadas()
    saldo_fichas    = emitidas - usadas
    saldo_guaranies = saldo_fichas * VALOR_FICHA
    ingresado       = total_ingresado_guaranies()
    gastado_gs      = total_ventas_guaranies()
    diferencia      = ingresado - gastado_gs
    consistente     = abs(diferencia) < 1  # tolerancia de 1 Gs.

    ventas_hoy    = ventas_del_dia()
    top_prods     = top_productos(5)
    cant_ventas   = len(ventas_hoy)
    total_fichas_dia = sum(v.get("total_fichas", 0) for v in ventas_hoy)

    return {
        "fichas_emitidas":        emitidas,
        "fichas_usadas":          usadas,
        "saldo_fichas":           saldo_fichas,
        "saldo_guaranies":        saldo_guaranies,
        "total_ingresado":        ingresado,
        "total_gastado":          gastado_gs,
        "diferencia":             diferencia,
        "consistente":            consistente,
        "ventas_hoy_cantidad":    cant_ventas,
        "ventas_hoy_fichas":      total_fichas_dia,
        "ventas_hoy_guaranies":   total_fichas_dia * VALOR_FICHA,
        "top_productos":          top_prods,
        "ventas_del_dia":         ventas_hoy,
    }
