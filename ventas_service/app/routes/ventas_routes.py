import logging
import json
from flask import Blueprint, request, session, redirect, render_template, jsonify
from services.producto_service import obtener_productos, verificar_y_descontar_stock
from services.ficha_service import saldo_fichas_disponibles, registrar_uso_fichas
from services.balance_service import calcular_balance
from models.venta import crear_venta
from repositories.venta_repo import guardar_venta

logger = logging.getLogger(__name__)

ventas_bp = Blueprint("ventas", __name__)


def _requiere_ventas():
    if session.get("role") != "ventas":
        return redirect("/")
    return None


@ventas_bp.route("/ventas")
def ventas():
    redir = _requiere_ventas()
    if redir:
        return redir
    return render_template("ventas.html", usuario=session.get("usuario", "Ventas"))


@ventas_bp.route("/api/productos")
def api_productos():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        productos = obtener_productos()
        return jsonify(productos)
    except Exception as e:
        logger.error(json.dumps({"event": "error_api_productos", "detalle": str(e)}))
        return jsonify({"error": "No se pudieron cargar los productos"}), 500


@ventas_bp.route("/api/venta", methods=["POST"])
def api_venta():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}
    items_raw = data.get("items", [])

    if not items_raw:
        return jsonify({"error": "El carrito está vacío"}), 400

    items = []
    total_fichas = 0
    for item in items_raw:
        producto_id = item.get("producto_id", "")
        nombre      = item.get("nombre", "")
        cantidad    = int(item.get("cantidad", 0))
        precio      = int(item.get("precio_fichas", 0))
        if cantidad <= 0 or precio <= 0 or not producto_id:
            return jsonify({"error": "Datos de producto inválidos"}), 400
        subtotal = precio * cantidad
        total_fichas += subtotal
        items.append({
            "producto_id": producto_id,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_fichas": precio,
            "subtotal_fichas": subtotal,
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
        venta = crear_venta(items, total_fichas)
        venta_id = guardar_venta(venta)
        logger.info(json.dumps({
            "event": "venta_realizada",
            "venta_id": venta_id,
            "total_fichas": total_fichas,
            "items": len(items),
        }))
        return jsonify({
            "ok": True,
            "venta_id": venta_id,
            "total_fichas": total_fichas,
            "total_guaranies": total_fichas * 1000,
        })
    except Exception as e:
        logger.error(json.dumps({"event": "error_guardar_venta", "detalle": str(e)}))
        return jsonify({"error": "No se pudo registrar la venta. Intente de nuevo"}), 500


@ventas_bp.route("/api/balance")
def api_balance():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        balance = calcular_balance()
        return jsonify(balance)
    except Exception as e:
        logger.error(json.dumps({"event": "error_balance", "detalle": str(e)}))
        return jsonify({"error": "No se pudo calcular el balance"}), 500
