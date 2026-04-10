import os
import logging
import json
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter
from repositories.ficha_repo import (
    todos_los_movimientos, total_fichas_emitidas,
    total_fichas_usadas, total_ingresado_guaranies
)
from repositories.venta_repo import ventas_por_producto, total_ventas_guaranies
from config import REPORTS_DIR_VENTAS, REPORTS_DIR_PRODUCCION, VALOR_FICHA

logger = logging.getLogger(__name__)
COLOR_HEADER = "366092"
COLOR_TOTAL  = "E8F5E9"
COLOR_WHITE  = "FFFFFF"


# ── Helpers de estilo ──────────────────────────────────────────────────────────

def _header_fill():
    return PatternFill("solid", fgColor=COLOR_HEADER)

def _total_fill():
    return PatternFill("solid", fgColor=COLOR_TOTAL)

def _thin_border():
    s = Side(style="thin")
    return Border(left=s, right=s, top=s, bottom=s)

def _estilo_header(cell):
    cell.fill      = _header_fill()
    cell.font      = Font(color=COLOR_WHITE, bold=True, size=11)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border    = _thin_border()

def _estilo_total(cell, bold=True):
    cell.fill   = _total_fill()
    cell.font   = Font(bold=bold)
    cell.border = _thin_border()

def _estilo_celda(cell):
    cell.border    = _thin_border()
    cell.alignment = Alignment(vertical="center")

def _fmt_moneda(cell):
    cell.number_format = "#,##0"

def _autofit(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 50)


# ── Hoja 1: Resumen Financiero ─────────────────────────────────────────────────

def _hoja_resumen(wb):
    ws = wb.create_sheet("RESUMEN FINANCIERO")
    ws.sheet_view.showGridLines = False

    emitidas  = total_fichas_emitidas()
    usadas    = total_fichas_usadas()
    saldo_fic = emitidas - usadas
    saldo_gs  = saldo_fic * VALOR_FICHA
    ingresado = total_ingresado_guaranies()
    gastado   = total_ventas_guaranies()
    diferencia = ingresado - gastado
    consistente = abs(diferencia) < 1

    titulo_fill = PatternFill("solid", fgColor="1A1A2E")
    ws["A1"] = "CANTINA — RESUMEN FINANCIERO"
    ws["A1"].fill      = PatternFill("solid", fgColor="1A1A2E")
    ws["A1"].font      = Font(color=COLOR_WHITE, bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells("A1:C1")
    ws.row_dimensions[1].height = 32

    ws["A2"] = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws["A2"].font = Font(italic=True, color="666666")
    ws.merge_cells("A2:C2")
    ws.row_dimensions[2].height = 20

    filas = [
        ("CONCEPTO", "VALOR", "UNIDAD"),
        None,
        ("Total Ingresado (dinero en caja)", ingresado, "Gs."),
        ("Total Gastado (fichas usadas)",    gastado,   "Gs."),
        ("Diferencia en caja",               diferencia,"Gs."),
        None,
        ("Total Fichas Emitidas",  emitidas,  "fichas"),
        ("Total Fichas Usadas",    usadas,    "fichas"),
        ("Saldo de Fichas",        saldo_fic, "fichas"),
        ("Saldo en Guaraníes",     saldo_gs,  "Gs."),
        None,
        ("Estado", "🟢 CONSISTENTE" if consistente else "🔴 HAY DIFERENCIA", ""),
    ]

    for i, fila in enumerate(filas, start=4):
        ws.row_dimensions[i].height = 22
        if fila is None:
            continue
        a, b, c = fila
        ws.cell(i, 1, a)
        ws.cell(i, 2, b)
        ws.cell(i, 3, c)

        if i == 4:  # encabezado
            for col in range(1, 4):
                _estilo_header(ws.cell(i, col))
        elif fila[0] in ("Diferencia en caja", "Saldo en Guaraníes", "Estado"):
            for col in range(1, 4):
                _estilo_total(ws.cell(i, col))
            if fila[0] in ("Diferencia en caja", "Saldo en Guaraníes"):
                _fmt_moneda(ws.cell(i, 2))
        else:
            for col in range(1, 4):
                _estilo_celda(ws.cell(i, col))
            if fila[2] == "Gs.":
                _fmt_moneda(ws.cell(i, 2))

    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 12


# ── Hoja 2: Movimientos de Fichas ──────────────────────────────────────────────

def _hoja_movimientos(wb):
    ws = wb.create_sheet("MOVIMIENTOS DE FICHAS")
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[1].height = 24

    headers = ["Fecha", "Tipo", "Monto (Gs.)", "Cantidad Fichas", "Observación"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(1, col, h)
        _estilo_header(cell)

    movimientos = todos_los_movimientos()
    for fila, m in enumerate(movimientos, start=2):
        fecha = m.get("fecha", "")
        tipo  = m.get("tipo", "").capitalize()
        monto = m.get("monto_guaranies", 0)
        cant  = m.get("cantidad_fichas", 0)
        obs   = m.get("observacion", "")

        ws.cell(fila, 1, fecha)
        ws.cell(fila, 2, tipo)
        ws.cell(fila, 3, monto)
        ws.cell(fila, 4, cant)
        ws.cell(fila, 5, obs)

        for col in range(1, 6):
            _estilo_celda(ws.cell(fila, col))
        _fmt_moneda(ws.cell(fila, 3))

    # Fila de totales
    if movimientos:
        tf = len(movimientos) + 2
        ws.cell(tf, 1, "TOTALES").font = Font(bold=True)
        ws.cell(tf, 3, sum(m.get("monto_guaranies", 0) for m in movimientos))
        ws.cell(tf, 4, sum(m.get("cantidad_fichas", 0) for m in movimientos))
        for col in range(1, 6):
            _estilo_total(ws.cell(tf, col))
        _fmt_moneda(ws.cell(tf, 3))

    _autofit(ws)


# ── Hoja 3: Ventas por Producto ────────────────────────────────────────────────

def _hoja_ventas_producto(wb):
    ws = wb.create_sheet("VENTAS POR PRODUCTO")
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[1].height = 24

    headers = ["Producto", "Cantidad", "Total Fichas", "Total Guaraníes"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(1, col, h)
        _estilo_header(cell)

    ventas = ventas_por_producto()
    for fila, v in enumerate(ventas, start=2):
        nombre  = v.get("_id", "")
        cant    = v.get("total_cantidad", 0)
        fichas  = v.get("total_fichas", 0)
        guarani = fichas * VALOR_FICHA

        ws.cell(fila, 1, nombre)
        ws.cell(fila, 2, cant)
        ws.cell(fila, 3, fichas)
        ws.cell(fila, 4, guarani)

        for col in range(1, 5):
            _estilo_celda(ws.cell(fila, col))
        _fmt_moneda(ws.cell(fila, 4))

    if ventas:
        tf = len(ventas) + 2
        ws.cell(tf, 1, "TOTALES")
        ws.cell(tf, 2, sum(v.get("total_cantidad", 0) for v in ventas))
        total_fic = sum(v.get("total_fichas", 0) for v in ventas)
        ws.cell(tf, 3, total_fic)
        ws.cell(tf, 4, total_fic * VALOR_FICHA)
        for col in range(1, 5):
            _estilo_total(ws.cell(tf, col))
        _fmt_moneda(ws.cell(tf, 4))

    _autofit(ws)


# ── Función principal ──────────────────────────────────────────────────────────

def generar_excel():
    os.makedirs(REPORTS_DIR_VENTAS,     exist_ok=True)
    os.makedirs(REPORTS_DIR_PRODUCCION, exist_ok=True)

    timestamp   = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    nombre      = f"reporte_{timestamp}.xlsx"

    wb = Workbook()
    wb.remove(wb.active)  # eliminar hoja por defecto

    _hoja_resumen(wb)
    _hoja_movimientos(wb)
    _hoja_ventas_producto(wb)

    ruta_ventas     = os.path.join(REPORTS_DIR_VENTAS,     nombre)
    ruta_produccion = os.path.join(REPORTS_DIR_PRODUCCION, nombre)

    wb.save(ruta_ventas)
    wb.save(ruta_produccion)

    logger.info(json.dumps({"event": "reporte_generado", "nombre": nombre}))
    return nombre
