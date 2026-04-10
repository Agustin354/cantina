import logging
import json
from flask import Blueprint, request, session, redirect, render_template, jsonify
from config import VALOR_FICHA, PRECIO_MULTIPLO
from services.producto_service import (
    obtener_productos, obtener_todos_productos,
    verificar_y_descontar_stock,
    agregar_producto, actualizar_precio_producto,
    dar_baja_producto, reactivar_producto,
)
from services.ficha_service import saldo_fichas_disponibles, registrar_uso_fichas
from services.balance_service import calcular_balance
from models.venta import crear_venta
from models.ficha_denominacion import crear_denominacion
from repositories.venta_repo import guardar_venta
from repositories.denominacion_repo import listar_activas, buscar_por_valor, insertar_denominacion

logger = logging.getLogger(__name__)

ventas_bp = Blueprint("ventas", __name__)


def _requiere_ventas():
    if session.get("role") != "ventas":
        return redirect("/")
    return None


# ═══════════════════════════════════════════════════════════════
# VISTAS
# ═══════════════════════════════════════════════════════════════

@ventas_bp.route("/ventas")
def ventas():
    redir = _requiere_ventas()
    if redir:
        return redir
    return render_template("ventas.html", usuario=session.get("usuario", "Ventas"))


# ═══════════════════════════════════════════════════════════════
# API — PRODUCTOS (lectura + gestión)
# ═══════════════════════════════════════════════════════════════

@ventas_bp.route("/api/productos", methods=["GET"])
def api_productos():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        return jsonify(obtener_productos())
    except Exception as e:
        logger.error(json.dumps({"event": "error_api_productos", "detalle": str(e)}))
        return jsonify({"error": "No se pudieron cargar los productos"}), 500


@ventas_bp.route("/api/productos/todos", methods=["GET"])
def api_productos_todos():
    """Para el panel de gestión — incluye inactivos."""
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        return jsonify(obtener_todos_productos())
    except Exception as e:
        logger.error(json.dumps({"event": "error_api_productos_todos", "detalle": str(e)}))
        return jsonify({"error": "Error al cargar productos"}), 500


@ventas_bp.route("/api/productos", methods=["POST"])
def api_agregar_producto():
    """
    BOTÓN A — Agregar Producto
    Body JSON: {nombre, precio_guaranies, stock, categoria}
    """
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}
    try:
        pid = agregar_producto(data)
        return jsonify({"ok": True, "id": pid}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(json.dumps({"event": "error_agregar_producto", "detalle": str(e)}))
        return jsonify({"error": "No se pudo agregar el producto"}), 500


@ventas_bp.route("/api/productos/<producto_id>/precio", methods=["PUT"])
def api_actualizar_precio(producto_id):
    """
    BOTÓN B — Modificar precio de producto existente
    Body JSON: {precio_guaranies}
    """
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data       = request.get_json(silent=True) or {}
    precio_gs  = data.get("precio_guaranies")
    if precio_gs is None:
        return jsonify({"error": "Falta precio_guaranies"}), 400

    try:
        actualizar_precio_producto(producto_id, precio_gs, session.get("usuario", "Ventas"))
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(json.dumps({"event": "error_actualizar_precio", "detalle": str(e)}))
        return jsonify({"error": "No se pudo actualizar el precio"}), 500


@ventas_bp.route("/api/productos/<producto_id>/baja", methods=["PUT"])
def api_baja_producto(producto_id):
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        dar_baja_producto(producto_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(json.dumps({"event": "error_baja_producto", "detalle": str(e)}))
        return jsonify({"error": "No se pudo desactivar el producto"}), 500


@ventas_bp.route("/api/productos/<producto_id>/activar", methods=["PUT"])
def api_activar_producto(producto_id):
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        reactivar_producto(producto_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(json.dumps({"event": "error_activar_producto", "detalle": str(e)}))
        return jsonify({"error": "No se pudo activar el producto"}), 500


# ═══════════════════════════════════════════════════════════════
# API — DENOMINACIONES DE FICHAS
# ═══════════════════════════════════════════════════════════════

@ventas_bp.route("/api/denominaciones", methods=["GET"])
def api_denominaciones():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        return jsonify(listar_activas())
    except Exception as e:
        logger.error(json.dumps({"event": "error_denominaciones", "detalle": str(e)}))
        return jsonify({"error": "Error al cargar denominaciones"}), 500


@ventas_bp.route("/api/denominaciones", methods=["POST"])
def api_agregar_denominacion():
    """
    BOTÓN B — Crear nueva denominación de ficha
    Body JSON: {nombre, valor_gs, color}
    """
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data     = request.get_json(silent=True) or {}
    nombre   = data.get("nombre", "").strip()
    valor_gs = int(data.get("valor_gs", 0))
    color    = data.get("color", "#27AE60")

    if not nombre:
        return jsonify({"error": "El nombre de la denominación es obligatorio"}), 400
    if valor_gs <= 0 or valor_gs % PRECIO_MULTIPLO != 0:
        return jsonify({"error": f"El valor debe ser positivo y múltiplo de {PRECIO_MULTIPLO} Gs."}), 400
    if buscar_por_valor(valor_gs):
        return jsonify({"error": f"Ya existe una denominación de {valor_gs} Gs."}), 400

    try:
        doc = crear_denominacion(nombre, valor_gs, color)
        did = insertar_denominacion(doc)
        return jsonify({"ok": True, "id": did}), 201
    except Exception as e:
        logger.error(json.dumps({"event": "error_agregar_denominacion", "detalle": str(e)}))
        return jsonify({"error": "No se pudo crear la denominación"}), 500


# ═══════════════════════════════════════════════════════════════
# API — VENTAS
# ═══════════════════════════════════════════════════════════════

@ventas_bp.route("/api/venta", methods=["POST"])
def api_venta():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data     = request.get_json(silent=True) or {}
    items_raw = data.get("items", [])

    if not items_raw:
        return jsonify({"error": "El carrito está vacío"}), 400

    items        = []
    total_fichas = 0
    for item in items_raw:
        producto_id = item.get("producto_id", "")
        nombre      = item.get("nombre", "")
        cantidad    = int(item.get("cantidad", 0))
        precio      = int(item.get("precio_fichas", 0))
        if cantidad <= 0 or precio <= 0 or not producto_id:
            return jsonify({"error": "Datos de producto inválidos"}), 400
        subtotal      = precio * cantidad
        total_fichas += subtotal
        items.append({
            "producto_id":      producto_id,
            "nombre":           nombre,
            "cantidad":         cantidad,
            "precio_fichas":    precio,
            "subtotal_fichas":  subtotal,
        })

    saldo = saldo_fichas_disponibles()
    if saldo < total_fichas:
        return jsonify({
            "error": f"Fichas insuficientes. Disponibles: {saldo}, necesarias: {total_fichas}"
        }), 400

    try:
        verificar_y_descontar_stock(items)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(json.dumps({"event": "error_stock", "detalle": str(e)}))
        return jsonify({"error": "Error al verificar stock. Intente de nuevo"}), 500

    try:
        registrar_uso_fichas(total_fichas, f"Venta: {len(items)} producto(s)")
        venta    = crear_venta(items, total_fichas)
        venta_id = guardar_venta(venta)
        logger.info(json.dumps({
            "event":        "venta_realizada",
            "venta_id":     venta_id,
            "total_fichas": total_fichas,
            "items":        len(items),
        }))
        return jsonify({
            "ok":              True,
            "venta_id":        venta_id,
            "total_fichas":    total_fichas,
            "total_guaranies": total_fichas * VALOR_FICHA,
        })
    except Exception as e:
        logger.error(json.dumps({"event": "error_guardar_venta", "detalle": str(e)}))
        return jsonify({"error": "No se pudo registrar la venta. Intente de nuevo"}), 500


# ═══════════════════════════════════════════════════════════════
# API — BALANCE
# ═══════════════════════════════════════════════════════════════

@ventas_bp.route("/api/balance")
def api_balance():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        return jsonify(calcular_balance())
    except Exception as e:
        logger.error(json.dumps({"event": "error_balance", "detalle": str(e)}))
        return jsonify({"error": "No se pudo calcular el balance"}), 500
