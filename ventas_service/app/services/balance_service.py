from repositories.ficha_repo import total_fichas_emitidas, total_fichas_usadas
from config import VALOR_FICHA


def calcular_balance():
    emitidas = total_fichas_emitidas()
    usadas = total_fichas_usadas()
    saldo_fichas = emitidas - usadas
    saldo_guaranies = saldo_fichas * VALOR_FICHA
    total_ingresado = emitidas * VALOR_FICHA
    total_gastado = usadas * VALOR_FICHA

    return {
        "fichas_emitidas": emitidas,
        "fichas_usadas": usadas,
        "saldo_fichas": saldo_fichas,
        "saldo_guaranies": saldo_guaranies,
        "total_ingresado_guaranies": total_ingresado,
        "total_gastado_guaranies": total_gastado,
    }
