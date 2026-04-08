import os
import logging
import json
from flask import Blueprint, request, session, redirect, render_template, jsonify, send_file
from services.estadisticas_service import calcular_stats
from services.excel_service import generar_excel
from config import REPORTS_DIR_PRODUCCION, EXTERNAL_PREFIX

logger = logging.getLogger(__name__)

reportes_bp = Blueprint("reportes", __name__)


def _requiere_produccion():
    if session.get("role") != "produccion":
        url = EXTERNAL_PREFIX + "/" if EXTERNAL_PREFIX else "/"
        return redirect(url)
    return None


@reportes_bp.route("/produccion")
def produccion():
    redir = _requiere_produccion()
    if redir:
        return redir
    logout_url = EXTERNAL_PREFIX + "/logout" if EXTERNAL_PREFIX else "/logout"
    return render_template("produccion.html",
                           usuario=session.get("usuario", "Producción"),
                           logout_url=logout_url,
                           base_url=EXTERNAL_PREFIX)


@reportes_bp.route("/api/stats")
def api_stats():
    redir = _requiere_produccion()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        stats = calcular_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(json.dumps({"event": "error_stats", "detalle": str(e)}))
        return jsonify({"error": "No se pudieron cargar las estadísticas"}), 500


@reportes_bp.route("/api/reportes")
def api_listar_reportes():
    redir = _requiere_produccion()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        os.makedirs(REPORTS_DIR_PRODUCCION, exist_ok=True)
        archivos = sorted(
            [f for f in os.listdir(REPORTS_DIR_PRODUCCION) if f.endswith(".xlsx")],
            reverse=True,
        )
        return jsonify(archivos)
    except Exception as e:
        logger.error(json.dumps({"event": "error_listar_reportes", "detalle": str(e)}))
        return jsonify({"error": "No se pudieron listar los reportes"}), 500


@reportes_bp.route("/api/reportes/download/<nombre>")
def api_descargar(nombre):
    redir = _requiere_produccion()
    if redir:
        return jsonify({"error": "No autorizado"}), 401

    # Evitar path traversal
    nombre_limpio = os.path.basename(nombre)
    if not nombre_limpio.endswith(".xlsx"):
        return jsonify({"error": "Archivo no válido"}), 400

    ruta = os.path.join(REPORTS_DIR_PRODUCCION, nombre_limpio)
    if not os.path.exists(ruta):
        return jsonify({"error": "Archivo no encontrado"}), 404

    return send_file(ruta, as_attachment=True, download_name=nombre_limpio)


@reportes_bp.route("/api/reportes/generar", methods=["POST"])
def api_generar_reporte():
    redir = _requiere_produccion()
    if redir:
        return jsonify({"error": "No autorizado"}), 401
    try:
        nombre = generar_excel()
        return jsonify({"ok": True, "nombre": nombre})
    except Exception as e:
        logger.error(json.dumps({"event": "error_generar_reporte", "detalle": str(e)}))
        return jsonify({"error": "No se pudo generar el reporte. Intente de nuevo"}), 500
