from datetime import datetime


def crear_producto(nombre, precio, stock, categoria="general"):
    return {
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
    }
