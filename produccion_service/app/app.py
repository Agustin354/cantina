import logging
import json
import sys
from flask import Flask
from config import SECRET_KEY, EXTERNAL_PREFIX

# ─── Logging en formato JSON ───────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger(__name__)

# ─── App Flask ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates")
app.secret_key = SECRET_KEY

# Cookie con nombre y path distintos para no conflictuar con ventas_service
app.config["SESSION_COOKIE_NAME"]     = "produccion_session"
app.config["SESSION_COOKIE_PATH"]     = EXTERNAL_PREFIX + "/" if EXTERNAL_PREFIX else "/"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ─── Blueprints ────────────────────────────────────────────────────────────────
from routes.auth_routes     import auth_bp
from routes.reportes_routes import reportes_bp

app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)

# ─── Manejo global de errores ──────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    from flask import redirect
    url = EXTERNAL_PREFIX + "/" if EXTERNAL_PREFIX else "/"
    return redirect(url)


@app.errorhandler(500)
def server_error(e):
    from flask import jsonify
    logger.error(json.dumps({"event": "error_servidor", "detalle": str(e)}))
    return jsonify({"error": "No hay conexión con el servidor. Intente de nuevo"}), 500


if __name__ == "__main__":
    from config import PORT
    app.run(host="0.0.0.0", port=PORT, debug=False)
