import logging
import json
import sys
from datetime import date, timedelta
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from config import SECRET_KEY, EXTERNAL_PREFIX, CORS_ORIGINS

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

# CORS: permite fetch cross-origin desde ventas_service (Railway)
if CORS_ORIGINS:
    CORS(app, origins=CORS_ORIGINS.split(","), supports_credentials=True)

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


# ─── Scheduler de reportes automáticos ────────────────────────────────────────
def _generar_reporte_auto(tipo: str):
    try:
        from services.excel_service import generar_excel
        hoy = date.today()
        if tipo == "semanal":
            # Corre el viernes a las 18:00 → reporta la semana actual (lun–vie)
            viernes = hoy                             # hoy ES el viernes
            lunes   = viernes - timedelta(days=4)     # lunes de esta semana
            fi, ff  = lunes.strftime("%Y-%m-%d"), viernes.strftime("%Y-%m-%d")
        else:  # mensual
            # Corre el día 1 a las 00:10 → reporta el mes anterior
            ultimo  = hoy - timedelta(days=1)
            primero = ultimo.replace(day=1)
            fi, ff  = primero.strftime("%Y-%m-%d"), ultimo.strftime("%Y-%m-%d")
        nombre = generar_excel(tipo=tipo, fecha_inicio=fi, fecha_fin=ff)
        logger.info(json.dumps({
            "event":   f"reporte_auto_{tipo}",
            "nombre":  nombre,
            "periodo": f"{fi}/{ff}",
        }))
    except Exception as e:
        logger.error(json.dumps({"event": f"error_reporte_auto_{tipo}", "detalle": str(e)}))

_tz = pytz.timezone("America/Asuncion")
_scheduler = BackgroundScheduler(timezone=_tz)
# Semanal: todos los lunes a las 00:05
_scheduler.add_job(_generar_reporte_auto, "cron", args=["semanal"],
                   day_of_week="fri", hour=18, minute=0,
                   id="reporte_semanal", replace_existing=True)
# Mensual: el día 1 de cada mes a las 00:10
_scheduler.add_job(_generar_reporte_auto, "cron", args=["mensual"],
                   day=1, hour=0, minute=10,
                   id="reporte_mensual", replace_existing=True)
try:
    _scheduler.start()
    logger.info(json.dumps({"event": "scheduler_iniciado"}))
except Exception as e:
    logger.error(json.dumps({"event": "error_scheduler", "detalle": str(e)}))


if __name__ == "__main__":
    from config import PORT
    app.run(host="0.0.0.0", port=PORT, debug=False)
