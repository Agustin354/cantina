import logging
import json
from flask import Blueprint, request, session, jsonify, redirect
from services.ficha_service import emitir_fichas
from config import DENOMINACIONES

logger = logging.getLogger(__name__)

fichas_bp = Blueprint("fichas", __name__)


def _requiere_ventas():
    if session.get("role") != "ventas":
        return redirect("/")
    return None


@fichas_bp.route("/api/denominaciones")
def api_denominaciones():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    return jsonify(DENOMINACIONES)


@fichas_bp.route("/api/emitir", methods=["POST"])
def api_emitir():
    redir = _requiere_ventas()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}
    emisiones = data.get("emisiones", [])

    if not emisiones:
        return jsonify({"error": "No se especificaron emisiones"}), 400

    total_fichas = 0
    total_guaranies = 0
    resultados = []

    for em in emisiones:
        try:
            denominacion = int(em.get("denominacion", 0))
            cantidad     = int(em.get("cantidad", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Datos de emisión inválidos"}), 400

        if cantidad <= 0:
            continue

        try:
            resultado = emitir_fichas(denominacion, cantidad)
            total_fichas    += resultado["cantidad_fichas"]
            total_guaranies += resultado["monto_guaranies"]
            resultados.append(resultado)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(json.dumps({"event": "error_emision", "detalle": str(e)}))
            return jsonify({"error": "No se pudieron emitir las fichas. Intente de nuevo"}), 500

    if not resultados:
        return jsonify({"error": "No se ingresó ninguna cantidad válida"}), 400

    logger.info(json.dumps({
        "event": "emision_confirmada",
        "total_fichas": total_fichas,
        "total_guaranies": total_guaranies,
        "operaciones": len(resultados),
    }))

    return jsonify({
        "ok": True,
        "total_fichas": total_fichas,
        "total_guaranies": total_guaranies,
        "resultados": resultados,
    })
