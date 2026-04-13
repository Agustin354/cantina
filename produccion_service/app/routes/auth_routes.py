import logging
import json
from flask import Blueprint, request, session, redirect, render_template, jsonify
from config import USUARIOS, EXTERNAL_PREFIX, EXTERNAL_URL

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _dashboard_url():
    base = EXTERNAL_URL if EXTERNAL_URL else EXTERNAL_PREFIX
    return base + "/produccion"


def _login_url():
    return EXTERNAL_PREFIX + "/" if EXTERNAL_PREFIX else "/"


@auth_bp.route("/")
def index():
    if session.get("role") == "produccion":
        return redirect(_dashboard_url())
    login_url = EXTERNAL_PREFIX + "/login/produccion" if EXTERNAL_PREFIX else "/login/produccion"
    ventas_url = "/"
    return render_template("login.html", login_url=login_url, ventas_url=ventas_url)


@auth_bp.route("/login/produccion", methods=["POST"])
def login_produccion():
    data     = request.get_json(silent=True) or {}
    usuario  = data.get("usuario", "").strip()
    password = data.get("password", "").strip()

    user_data = USUARIOS.get(usuario)
    if user_data and user_data["password"] == password and user_data["role"] == "produccion":
        session["usuario"] = usuario
        session["role"]    = "produccion"
        logger.info(json.dumps({"event": "login_exitoso", "usuario": usuario}))
        return jsonify({"ok": True, "redirect": _dashboard_url()})

    logger.warning(json.dumps({"event": "login_fallido", "usuario": usuario}))
    return jsonify({"ok": False, "error": "Usuario o contraseña incorrectos"}), 401


@auth_bp.route("/logout")
def logout():
    session.clear()
    # Redirige siempre al login principal (ventas)
    return redirect("/" if not EXTERNAL_PREFIX else EXTERNAL_PREFIX.replace("/produccion", "/") or "/")
