from datetime import datetime


def crear_reporte_meta(nombre_archivo, tipo="completo"):
    return {
        "nombre": nombre_archivo,
        "tipo": tipo,
        "generado_en": datetime.utcnow(),
    }
