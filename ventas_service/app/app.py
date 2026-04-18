import logging
import json
import sys
import os
from flask import Flask
from config import SECRET_KEY

_template_folder = (
    os.path.join(sys._MEIPASS, 'app', 'templates')
    if getattr(sys, 'frozen', False)
    else 'templates'
)

# ─── Logging en formato JSON ───────────────────────────────────────────────────
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(message)s',
)
logger = logging.getLogger(__name__)

# ─── App Flask ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=_template_folder)
app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_NAME"] = "ventas_session"
app.config["SESSION_COOKIE_PATH"] = "/"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ─── Blueprints ────────────────────────────────────────────────────────────────
from routes.auth_routes   import auth_bp
from routes.ventas_routes import ventas_bp
from routes.fichas_routes import fichas_bp

app.register_blueprint(auth_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(fichas_bp)

# ─── Manejo global de errores ──────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    from flask import redirect
    return redirect("/")


@app.errorhandler(500)
def server_error(e):
    from flask import jsonify
    logger.error(json.dumps({"event": "error_servidor", "detalle": str(e)}))
    return jsonify({"error": "No hay conexión con el servidor. Intente de nuevo"}), 500


if __name__ == "__main__":
    from config import PORT
    app.run(host="0.0.0.0", port=PORT, debug=False)
