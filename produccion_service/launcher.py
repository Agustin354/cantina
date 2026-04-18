import os
import sys
import threading
import time
import webbrowser
import tkinter as tk
from datetime import datetime
from pathlib import Path

# ── PyInstaller: apuntar al directorio extraído ────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, 'app'))

# ── Directorio de reportes en Documentos del usuario ──────────────────────────
_reports_base = Path.home() / 'Documents' / 'TiaPerla' / 'reports'
(_reports_base / 'ventas').mkdir(parents=True, exist_ok=True)
(_reports_base / 'produccion').mkdir(parents=True, exist_ok=True)

# ── Credenciales (embebidas en el build por GitHub Actions) ───────────────────
os.environ.setdefault('MONGODB_URI',           'PLACEHOLDER_MONGODB_URI')
os.environ.setdefault('MONGODB_DB',            'quiosco')
os.environ.setdefault('SECRET_KEY',            'tia_perla_secret_key_2024')
os.environ['PORT']                   = '5001'
os.environ['EXTERNAL_PREFIX']        = ''
os.environ['CORS_ORIGINS']           = ''
os.environ['REPORTS_DIR_VENTAS']     = str(_reports_base / 'ventas')
os.environ['REPORTS_DIR_PRODUCCION'] = str(_reports_base / 'produccion')

PORT = 5001


def _run_flask():
    from app import app
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)


def _open_browser():
    time.sleep(2)
    webbrowser.open(f'http://localhost:{PORT}')


def _auto_close():
    while True:
        if datetime.now().hour >= 18:
            os.kill(os.getpid(), 9)
        time.sleep(30)


threading.Thread(target=_run_flask,    daemon=True).start()
threading.Thread(target=_open_browser, daemon=True).start()
threading.Thread(target=_auto_close,   daemon=True).start()

# ── Ventana principal ─────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Tía Perla – Producción")
root.geometry("320x170")
root.resizable(False, False)
root.configure(bg='#2c3e50')

tk.Label(root, text="Sistema de Producción",
         font=('Arial', 14, 'bold'), bg='#2c3e50', fg='white').pack(pady=(20, 4))
tk.Label(root, text="✓ Iniciado correctamente  |  Cierra a las 18:00",
         bg='#2c3e50', fg='#2ecc71', font=('Arial', 9)).pack(pady=2)

tk.Button(root, text="Abrir en navegador",
          command=lambda: webbrowser.open(f'http://localhost:{PORT}'),
          bg='#3498db', fg='white', padx=10, pady=5, bd=0,
          font=('Arial', 10)).pack(pady=(14, 4))
tk.Button(root, text="Cerrar sistema",
          command=lambda: sys.exit(0),
          bg='#e74c3c', fg='white', padx=10, pady=5, bd=0,
          font=('Arial', 10)).pack(pady=4)

root.mainloop()
