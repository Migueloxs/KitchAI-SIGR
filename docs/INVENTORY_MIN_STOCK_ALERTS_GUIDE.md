# Alertas de Stock Minimo y Notificaciones Internas

## Objetivo

Implementar monitoreo diario de inventario para detectar articulos en stock minimo y permitir al administrador gestionar alertas desde un dashboard.

## Criterios de Aceptacion Implementados

- CA1: Verificacion diaria de stock (`current_quantity <= minimum_stock`) y creacion de notificacion interna.
- CA2: Dashboard de alertas para consulta operativa.
- CA3: Marcado de alertas como `vistas` y `resueltas`.

## Flujo

1. En startup, FastAPI inicia un scheduler interno que ejecuta una revision diaria.
2. La revision diaria crea alertas `DAILY_MIN_STOCK` por item y por fecha (`check_date`).
3. El dashboard expone alertas activas e historicas para administradores.
4. El administrador puede marcar alertas como vistas o resueltas.

## Endpoints

Base path: `/api/inventory`

- `GET /alerts`: lista solo alertas activas (`is_resolved = false`).
- `GET /alerts/dashboard`: lista todas las alertas (historicas y activas).
- `PUT /alerts/{alert_id}/view`: marca alerta como vista (`is_viewed = true`).
- `PUT /alerts/{alert_id}/resolve`: marca alerta como resuelta (`is_resolved = true`).
- `POST /alerts/daily-check`: ejecuta revision diaria manual.

## Migracion Turso

Archivo:

- `src/shared/infrastructure/database/migrations/versions/004_inventory_alerts_dashboard_and_daily_checks.sql`

Cambios:

- `ALTER TABLE inventory_alerts ADD COLUMN is_viewed INTEGER NOT NULL DEFAULT 0`
- `ALTER TABLE inventory_alerts ADD COLUMN check_date TEXT`
- `ALTER TABLE inventory_alerts ADD COLUMN viewed_at TEXT`
- Nuevos indices para dashboard y filtro diario.

## Prueba Recomendada

Con API levantada:

```bash
python test_inventory_min_stock_alerts.py
```

El test valida:

- Creacion de item en stock minimo.
- Ejecucion de verificacion diaria.
- Presencia en dashboard.
- Marcado de alerta como vista y resuelta.
- Ausencia de alerta resuelta en endpoint de activas.
