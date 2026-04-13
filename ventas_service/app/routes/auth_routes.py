import os
import logging
import json
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from config import USUARIOS

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if session.get("role") == "ventas":
        return redirect("/ventas")
    produccion_url = os.getenv("PRODUCCION_URL", "/produccion")
    return render_template("login.html", produccion_url=produccion_url)


@auth_bp.route("/login/ventas", methods=["POST"])
def login_ventas():
    data = request.get_json(silent=True) or {}
    usuario = data.get("usuario", "").strip()
    password = data.get("password", "").strip()

    user_data = USUARIOS.get(usuario)
    if user_data and user_data["password"] == password and user_data["role"] == "ventas":
        session["usuario"] = usuario
        session["role"] = "ventas"
        logger.info(json.dumps({"event": "login_exitoso", "usuario": usuario, "role": "ventas"}))
        return jsonify({"ok": True, "redirect": "/ventas"})

    logger.warning(json.dumps({"event": "login_fallido", "usuario": usuario}))
    return jsonify({"ok": False, "error": "Usuario o contraseña incorrectos"}), 401


@auth_bp.route("/login/produccion", methods=["POST"])
def login_produccion():
    """
    Verifica credenciales de Producción desde el formulario unificado.
    Si son válidas, redirige al panel de producción para que ese
    servicio establezca su propia sesión.
    """
    data = request.get_json(silent=True) or {}
    usuario = data.get("usuario", "").strip()
    password = data.get("password", "").strip()

    user_data = USUARIOS.get(usuario)
    if user_data and user_data["password"] == password and user_data["role"] == "produccion":
        logger.info(json.dumps({"event": "login_produccion_desde_ventas", "usuario": usuario}))
        return jsonify({"ok": True, "redirect": "/produccion/login/produccion", "forward": True,
                        "usuario": usuario, "password": password})

    logger.warning(json.dumps({"event": "login_produccion_fallido", "usuario": usuario}))
    return jsonify({"ok": False, "error": "Usuario o contraseña incorrectos"}), 401


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
