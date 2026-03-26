# Guía de Ventas y Reportes - KitchAI SIGR

## Descripción General

El módulo de **Ventas** implementa el registro automático de transacciones financieras cuando un pedido se marca como completado. Este sistema cumple con los siguientes criterios de aceptación:

- **CA1**: Cada pedido marcado como "pagado" o "entregado" se registra automáticamente como una venta con fecha, monto y productos
- **CA2**: Cada venta incluye el método de pago y el ID del empleado (mesero) que generó la orden
- **CA3**: Las ventas se almacenan en Turso (LibSQL) y son accesibles para reportes

## Arquitectura

El módulo sigue el patrón **hexagonal** con tres capas:

### 1. Domain (Dominio)

**Ubicación**: `src/modules/Sales/domain/`

Define la lógica y modelos de negocio sin dependencias externas.

```
domain/
├── entities/
│   └── sale.py              # Modelos: Sale, SaleItem
└── repositories/
    └── sales_repository_interface.py  # Contrato del repositorio
```

**Entidades principales**:

```python
class Sale(BaseModel):
    id: str                          # UUID único
    order_id: str                    # FK: pedido original
    order_number: str                # ORD-XXXX-XXXX (referencia)
    customer_name: str               # Nombre del cliente
    waiter_id: str                   # ID del mesero (CA2)
    payment_method: str              # CASH, CARD, etc. (CA2)
    total_amount: float              # Monto sin tax/descuento
    tax_amount: float                # Impuesto (18%)
    discount_amount: float           # Descuentos aplicados
    final_amount: float              # Total a pagar
    items_count: int                 # Cantidad de productos
    sale_date: str                   # YYYY-MM-DD (CA1)
    registered_at: datetime          # Timestamp de registro
    items: List[SaleItem]            # Detalles de productos (CA1)

class SaleItem(BaseModel):
    id: str
    sale_id: str
    menu_item_id: str
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
```

### 2. Application (Aplicación)

**Ubicación**: `src/modules/Sales/application/`

Contiene la lógica de casos de uso y transferencia de datos.

```
application/
├── dto/
│   └── sale_response.py           # Modelos de respuesta
└── usecases/
    └── sales_usecases.py          # SalesService
```

**SalesService**: Orquesta la creación y consulta de ventas.

```python
class SalesService:
    def register_sale_from_order(order: Order) -> Sale
        """Convierte un pedido completado en venta"""
        
    def get_all_sales() -> List[SaleResponseDTO]
        """Retorna todas las ventas"""
    
    def get_sales_by_date_range(start: str, end: str) -> List[SaleResponseDTO]
        """Filtra ventas por rango de fechas"""
    
    def get_sales_by_waiter(waiter_id: str) -> List[SaleResponseDTO]
        """Obtiene ventas de un mesero específico"""
    
    def get_daily_report(date: str) -> dict
        """Reporte diario: total ventas, ingresos, impuestos"""
    
    def get_period_report(start: str, end: str) -> SalesReportDTO
        """Reporte de período con breakdowns"""
```

### 3. Infrastructure (Infraestructura)

**Ubicación**: `src/modules/Sales/infrastructure/`

Implementa integraciones con la base de datos y API REST.

```
infrastructure/
├── repositories/
│   └── sales_repository.py        # Implementación Turso
└── api/
    └── sales_router.py            # Endpoints REST
```

**SalesRepository**: Maneja persistencia en Turso.

- `create()`: Inserta venta + items con transacciones
- `get_by_id()`, `get_by_order_id()`: Consultas por ID
- `get_by_date_range()`, `get_by_waiter()`: Filtrado
- `get_summary_by_date()`, `get_summary_by_waiter()`: Agregación para reportes
- `exists_for_order()`: Previene duplicados

## Flujo Automático de Registro

### Paso 1: Creación de Orden

```
[Mesero] crea pedido con PUT /api/orders/
```

El pedido comienza en estado `PENDING` y transita por:
- `PENDING` → `PREPARING` (se descuenta inventario)
- `PREPARING` → `READY`
- `READY` → `SERVED` (dine_in) o `DELIVERED` (takeout/delivery)

### Paso 2: Completación Automática de Venta

Cuando el orden transita a `SERVED` o `DELIVERED`:

```python
# En OrderService.update_order_status()
if new_status in [OrderStatus.SERVED, OrderStatus.DELIVERED]:
    self.sales_service.register_sale_from_order(saved_order)
```

### Paso 3: Verificación Database

**La venta se crea en tablas Turso**:

```sql
-- sales: Registro de transacciones
CREATE TABLE sales (
    id TEXT PRIMARY KEY,
    order_id TEXT UNIQUE,
    order_number TEXT,
    customer_name TEXT,
    waiter_id TEXT,
    payment_method TEXT,          -- CA2
    total_amount REAL,
    tax_amount REAL,
    discount_amount REAL,
    final_amount REAL,
    items_count INTEGER,
    sale_date TEXT,               -- CA1
    registered_at TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- sale_items: Detalles de productos vendidos
CREATE TABLE sale_items (
    id TEXT PRIMARY KEY,
    sale_id TEXT,
    menu_item_id TEXT,
    menu_item_name TEXT,          -- CA1: Nom. producto
    quantity INTEGER,             -- CA1: Cantidad
    unit_price REAL,              -- CA1: Precio
    subtotal REAL,                -- CA1: Monto
    FOREIGN KEY (sale_id) REFERENCES sales(id)
);
```

## Endpoints REST

### Listar Ventas

```http
GET /api/sales/

Authorization: Bearer {admin_token}
```

**Respuesta (200)**:
```json
[
  {
    "id": "sale-uuid",
    "order_id": "order-uuid",
    "order_number": "ORD-2025-12345678",
    "customer_name": "Juan Pérez",
    "waiter_id": "waiter-uuid",
    "payment_method": "CARD",
    "final_amount": 414.50,
    "sale_date": "2025-03-26",
    "items": [
      {
        "menu_item_name": "Hamburguesa",
        "quantity": 2,
        "unit_price": 150.00,
        "subtotal": 300.00
      }
    ]
  }
]
```

### Obtener Venta por ID

```http
GET /api/sales/{sale_id}

Authorization: Bearer {admin_token}
```

### Ventas por Rango de Fechas

```http
GET /api/sales/by-date-range/?start_date=2025-03-20&end_date=2025-03-26

Authorization: Bearer {admin_token}
```

### Ventas por Mesero

```http
GET /api/sales/by-waiter/{waiter_id}

Authorization: Bearer {admin_token}
```

### Reporte Diario

```http
GET /api/sales/report/daily/?date=2025-03-26

Authorization: Bearer {employee_token}
```

**Respuesta**:
```json
{
  "date": "2025-03-26",
  "total_sales": 12,
  "total_revenue": 5240.50,
  "total_tax": 943.29,
  "total_discount": 0.00,
  "by_waiter": [
    {
      "waiter_id": "waiter-1",
      "sales_count": 5,
      "revenue": 2100.00
    }
  ]
}
```

### Reporte de Período

```http
GET /api/sales/report/period/?start_date=2025-03-20&end_date=2025-03-26

Authorization: Bearer {employee_token}
```

**Respuesta**:
```json
{
  "period": {
    "start": "2025-03-20",
    "end": "2025-03-26"
  },
  "total_sales": 95,
  "total_revenue": 42850.75,
  "total_tax": 7713.14,
  "by_waiter": [
    {
      "waiter_id": "waiter-uuid",
      "name": "Carlos López",
      "sales_count": 23,
      "revenue": 10250.00
    }
  ],
  "by_payment_method": [
    {
      "method": "CASH",
      "count": 45,
      "amount": 19500.00
    },
    {
      "method": "CARD",
      "count": 50,
      "amount": 23350.75
    }
  ]
}
```

## Autorización

| Endpoint | Admin | Employee | Waiter | Descripción |
|---------|-------|----------|--------|-------------|
| GET /sales/ | ✅ | ❌ | ❌ | Listar todas las ventas |
| GET /sales/{id} | ✅ | ❌ | ❌ | Ver venta específica |
| GET /sales/by-waiter/{id} | ✅ | ❌ | ❌ | Ventas de mesero |
| GET /sales/report/daily | ✅ | ✅ | ❌ | Reporte diario |
| GET /sales/report/period | ✅ | ✅ | ❌ | Reporte de período |

## Migraciones

La base de datos se actualiza automáticamente con:

**Archivo**: `src/shared/infrastructure/database/migrations/005_create_sales_table.sql`

Se ejecuta automáticamente al iniciar la aplicación via `run_migrations()`.

## Pruebas

### Ejecutar Suite Completa

```bash
pytest test_sales_autoregistration.py -v
```

### Criterios de Aceptación

| CA | Test | Validación |
|----|------|-----------|
| CA1 | `test_ca1_auto_register_sale_with_order_info` | Venta contiene fecha, monto y productos |
| CA2 | `test_ca2_sales_include_payment_and_employee` | Venta tiene método de pago e ID mesero |
| CA3 | `test_ca3_sales_reports_from_turso` | Ventas accesibles en reportes |

### Ejecución Local

```bash
# 1. Iniciar servidor
python main.py

# 2. En otra terminal
pytest test_sales_autoregistration.py -v -s

# 3. Ver reportes en Swagger
# http://localhost:8000/docs
```

## Tratamiento de Errores

### Duplicación Prevención

Si se intenta registrar una venta para un order_id que ya existe:
- **Validación**: `UNIQUE(order_id)` en tabla sales
- **Código**: `SalesRepository.exists_for_order()` verifica antes de insertar
- **Respuesta**: Si existe, se omite silenciosamente (no falla la transición)

### Fallo de Registro

Si `register_sale_from_order()` falla:
```python
try:
    self.sales_service.register_sale_from_order(saved_order)
except Exception as e:
    print(f"Error al registrar venta: {e}")
    # La orden sigue completada aunque la venta falle
```

## Integración con OrderService

El registro automático se dispara desde [src/modules/Order/application/usecases/order_usecases.py](../src/modules/Order/application/usecases/order_usecases.py):

```python
class OrderService:
    def __init__(self):
        self.sales_service = SalesService()  # ← Importa
    
    def update_order_status(...):
        # ... actualizar estado ...
        
        # Registrar venta automáticamente
        if new_status in [OrderStatus.SERVED, OrderStatus.DELIVERED]:
            self.sales_service.register_sale_from_order(saved_order)
```

## Estructura de Carpetas

```
src/modules/Sales/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── sale.py
│   └── repositories/
│       ├── __init__.py
│       └── sales_repository_interface.py
├── application/
│   ├── __init__.py
│   ├── dto/
│   │   ├── __init__.py
│   │   └── sale_response.py
│   └── usecases/
│       ├── __init__.py
│       └── sales_usecases.py
└── infrastructure/
    ├── __init__.py
    ├── repositories/
    │   ├── __init__.py
    │   └── sales_repository.py
    └── api/
        ├── __init__.py
        └── sales_router.py
```

## Notas de Desarrollo

### Transacciones

Cuando se crea una venta:
```python
# Se inserta en dos tablas con UUID único
def create(sale: Sale) -> Sale:
    # Insertar sale
    self.db.execute("INSERT INTO sales ...")
    # Insertar sale_items
    for item in sale.items:
        self.db.execute("INSERT INTO sale_items ...")
```

### Performance

Las queries están optimizadas con índices:
- `idx_sales_order_id`: Búsqueda por pedido
- `idx_sales_date`: Reportes por fecha
- `idx_sales_waiter`: Reportes por mesero
- `idx_sales_registered_at`: Ordenamiento temporal

### Próximas Mejoras

- [ ] Integración con sistema de contabilidad externa
- [ ] Exportación a archivos (CSV, PDF)
- [ ] Webhook para notificaciones de ventas
- [ ] Validación de consistencia de montos

## Contacto y Soporte

Para reportar problemas o sugerencias sobre el módulo de Ventas:

- Email: soporte@kitchai.com
- Issue Tracker: [GitHub Issues]

## Versión

- **Versión Actual**: 1.0.0
- **Última Actualización**: 2025-03-26
- **Estado**: Producción
