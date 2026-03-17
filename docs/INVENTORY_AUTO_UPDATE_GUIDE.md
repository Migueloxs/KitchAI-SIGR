# Actualizacion Automatica del Inventario tras Pedidos

## Objetivo

Cuando un pedido se confirma (transicion `pending` -> `preparing`), el sistema debe:

- Descontar automaticamente el stock de los articulos involucrados.
- Crear alertas internas si el stock queda en minimo o por debajo.
- Reflejar los cambios de forma inmediata para todos los paneles.

## Criterios de Aceptacion Cubiertos

- CA1: Descuento automatico de cantidades al confirmarse un pedido.
- CA2: Disparo de alerta interna cuando el stock queda en o bajo el minimo.
- CA3: Actualizacion inmediata al persistirse en Turso DB y disponibilidad via endpoints.

## Flujo Tecnico

1. El pedido cambia de estado con `PUT /api/orders/{order_id}/status` y `new_status=preparing`.
2. `OrderService` invoca `InventoryOrderSyncService`.
3. Se valida stock disponible para todos los items del pedido.
4. Se descuentan cantidades por cada item (`menu_item_id` del pedido debe coincidir con `id` en `inventory_items`).
5. Si `current_quantity <= minimum_stock`, se crea alerta en `inventory_alerts`.
6. Se registra procesamiento idempotente del pedido en `order_inventory_updates`.

## Endpoints Relacionados

- `PUT /api/orders/{order_id}/status` (confirmacion operativa del pedido)
- `GET /api/inventory/{item_id}` (verificar stock actualizado)
- `GET /api/inventory/alerts` (consultar alertas internas activas)

## Migracion de Base de Datos

Se agrega la migracion:

- `002_inventory_order_auto_update.sql`

Tablas nuevas:

- `order_inventory_updates`: evita descuentos duplicados por pedido.
- `inventory_alerts`: almacena alertas internas de bajo stock.

## Prueba

Con API levantada:

```bash
python test_inventory_auto_update.py
```
