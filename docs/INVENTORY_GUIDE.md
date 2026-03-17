# Gestion Basica de Inventario

Este modulo implementa CRUD de articulos de inventario siguiendo arquitectura hexagonal.

## Alcance

- Crear articulos de inventario.
- Consultar un articulo o listar todos.
- Editar articulos existentes.
- Eliminar articulos existentes.
- Persistir cambios en Turso DB.

## Endpoints

Base path: `/api/inventory`

- `POST /` crea articulo.
- `GET /` lista articulos.
- `GET /alerts` lista alertas internas activas (no resueltas).
- `GET /alerts/dashboard` lista el dashboard completo de alertas.
- `PUT /alerts/{alert_id}/view` marca una alerta como vista.
- `PUT /alerts/{alert_id}/resolve` marca una alerta como resuelta.
- `POST /alerts/daily-check` ejecuta manualmente la verificacion diaria de stock minimo.
- `GET /{item_id}` obtiene un articulo por ID.
- `PUT /{item_id}` actualiza un articulo.
- `DELETE /{item_id}` elimina un articulo.

## Seguridad

Todos los endpoints requieren JWT (`Authorization: Bearer <token>`) y rol `admin` (`role_id = uuid-role-admin`).

## Modelo de Datos

Tabla: `inventory_items`

Campos:
- `id` (TEXT, PK)
- `name` (TEXT, UNIQUE, NOT NULL)
- `category` (TEXT, NOT NULL)
- `current_quantity` (REAL, NOT NULL, >= 0)
- `minimum_stock` (REAL, NOT NULL, >= 0)
- `unit` (TEXT, NOT NULL)
- `created_at` (TEXT, NOT NULL)
- `updated_at` (TEXT, NOT NULL)

## Migraciones

Se agrego migracion versionada:

- `001_create_inventory_items.sql`
- `002_inventory_order_auto_update.sql`
- `004_inventory_alerts_dashboard_and_daily_checks.sql`

El runner se ejecuta automaticamente en startup y registra versiones aplicadas en `schema_migrations`.

## Actualizacion Automatica tras Pedidos

Cuando un pedido pasa de `pending` a `preparing`:

- El sistema descuenta automaticamente del inventario cada item del pedido.
- El descuento se hace de forma idempotente por pedido (no descuenta dos veces).
- Si un articulo queda en stock minimo o por debajo, se registra una alerta interna en `inventory_alerts`.
- Las alertas se consultan con `GET /api/inventory/alerts`.

## Alertas de Stock Minimo y Notificaciones

Se agrega una verificacion diaria automatica (scheduler interno) que:

- Revisa todos los articulos en `current_quantity <= minimum_stock`.
- Crea alertas internas tipo `DAILY_MIN_STOCK` en `inventory_alerts`.
- Evita duplicar alertas para el mismo articulo en el mismo dia (`check_date`).

Nuevos estados de alerta:

- `is_viewed`: indica si el administrador ya reviso la alerta.
- `is_resolved`: indica si la alerta ya fue atendida.
- `viewed_at`: fecha de marcado como vista.
- `resolved_at`: fecha de marcado como resuelta.
- `check_date`: dia logico de la verificacion diaria.

## Prueba Rapida

Con el servidor arriba:

```bash
python test_inventory_crud.py
```
