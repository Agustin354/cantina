# 🏪 Sistema Quiosco TÍA PERLA

Sistema de control de fichas y ventas para quiosco escolar en Paraguay.

## Acceso rápido

| Panel | URL | Usuario | Contraseña |
|-------|-----|---------|------------|
| Ventas | http://localhost/ | Ventas | Ventas |
| Producción | http://localhost/produccion | Producción | Producción |

## Iniciar el sistema

```bash
docker-compose up --build
```

Luego abrir el navegador en **http://localhost**

## Detener el sistema

```bash
docker-compose down
```

## Estructura

- **ventas_service** (puerto 5000): Emisión de fichas y registro de ventas
- **produccion_service** (puerto 5001): Dashboard, estadísticas y reportes Excel
- **nginx** (puerto 80): Puerta de entrada unificada

## Modelo de negocio

```
DINERO REAL (Gs.) → FICHAS (1 ficha = 1000 Gs.) → PRODUCTOS (precio en fichas)

SALDO_FICHAS    = FICHAS_EMITIDAS - FICHAS_USADAS
SALDO_GUARANIES = SALDO_FICHAS × 1000
```

## Reportes Excel

Los reportes se generan en `/reports/ventas/` y `/reports/produccion/` con 3 hojas:
1. **RESUMEN FINANCIERO** — balance general
2. **MOVIMIENTOS DE FICHAS** — historial de emisiones y usos
3. **VENTAS POR PRODUCTO** — consolidado de productos vendidos
