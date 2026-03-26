# Guía de Finanzas - KitchAI SIGR

## Descripción General

El módulo de Finanzas implementa un sistema automático de cálculo de ingresos, egresos y ganancias para el restaurante. Integra datos de ventas registradas con un control detallado de gastos operativos para proporcionar reportes financieros en tiempo real.

## Características Principales

### CA1: Cálculo Automático de Ingresos
El sistema calcula automáticamente los ingresos totales sumando todas las ventas registradas en un período específico.

**Cálculo:**
```
Ingresos Totales = Σ(monto_final de todas las ventas en el período)
```

**Endpoints:**
- `GET /api/finances/income/daily/?date=YYYY-MM-DD` - Ingresos del día
- `GET /api/finances/income/period/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Ingresos del período

**Ejemplo de Respuesta:**
```json
{
  "date": "2024-01-15",
  "total_income": 2500.50
}
```

### CA2: Cálculo Automático de Ganancias
El sistema resta automáticamente los egresos registrados para obtener la ganancia neta.

**Cálculo:**
```
Ganancia Neta = Ingresos - Egresos
Margen de Ganancia (%) = (Ganancia Neta / Ingresos) × 100
```

**Endpoints:**
- `GET /api/finances/profit/daily/?date=YYYY-MM-DD` - Ganancia del día
- `GET /api/finances/profit/period/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Ganancia del período

**Ejemplo de Respuesta:**
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "total_income": 75000.00,
  "total_expenses": 45000.00,
  "net_profit": 30000.00,
  "profit_margin_percent": 40.0
}
```

### CA3: Reportes en Tiempo Real
Los resultados se actualizan en tiempo real y están disponibles a través de una API con tres niveles de detalle.

**Reportes Disponibles:**

#### 1. Reporte Diario (DailyFinancialDTO)
```
GET /api/finances/report/daily/?date=YYYY-MM-DD
```

**Campos:**
- `date`: Fecha del reporte
- `total_income`: Ingresos totales del día
- `total_expenses`: Gastos totales del día
- `net_profit`: Ganancia neta del día
- `transaction_count`: Número total de transacciones (ventas + gastos)

**Ejemplo:**
```json
{
  "date": "2024-01-15",
  "total_income": 2500.50,
  "total_expenses": 1200.00,
  "net_profit": 1300.50,
  "transaction_count": 15
}
```

#### 2. Reporte de Período (PeriodFinancialDTO)
```
GET /api/finances/report/period/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Campos:**
- `period_start` y `period_end`: Rango de fechas
- `total_income`, `total_expenses`, `net_profit`: Totales agregados
- `profit_margin_percent`: Margen de ganancia del período
- `daily_average_income`, `daily_average_expense`, `daily_average_profit`: Promedios diarios
- `transaction_count`: Total de transacciones en el período

**Ejemplo:**
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "total_income": 75000.00,
  "total_expenses": 45000.00,
  "net_profit": 30000.00,
  "profit_margin_percent": 40.0,
  "daily_average_income": 2419.35,
  "daily_average_expense": 1451.61,
  "daily_average_profit": 967.74,
  "transaction_count": 485
}
```

#### 3. Reporte Detallado (FinancialReportDTO)
```
GET /api/finances/report/comprehensive/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Campos:**
- Todos los campos del reporte de período
- `daily_summaries`: Array con resumen diario de cada día en el período
- `expenses_by_category`: Desglose de gastos por categoría con porcentajes
- `top_expense_category`: Categoría de gasto con mayor impacto

**Ejemplo:**
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-03",
  "total_income": 7500.00,
  "total_expenses": 3600.00,
  "net_profit": 3900.00,
  "profit_margin_percent": 52.0,
  "daily_average_income": 2500.00,
  "daily_average_expense": 1200.00,
  "daily_average_profit": 1300.00,
  "transaction_count": 45,
  "daily_summaries": [
    {
      "date": "2024-01-01",
      "total_income": 2500.00,
      "total_expenses": 1200.00,
      "net_profit": 1300.00,
      "transaction_count": 15
    },
    {
      "date": "2024-01-02",
      "total_income": 2500.00,
      "total_expenses": 1200.00,
      "net_profit": 1300.00,
      "transaction_count": 15
    },
    {
      "date": "2024-01-03",
      "total_income": 2500.00,
      "total_expenses": 1200.00,
      "net_profit": 1300.00,
      "transaction_count": 15
    }
  ],
  "expenses_by_category": [
    {
      "category_name": "Inventario",
      "total_amount": 1500.00,
      "percentage": 41.67,
      "count": 8
    },
    {
      "category_name": "Servicios",
      "total_amount": 800.00,
      "percentage": 22.22,
      "count": 4
    },
    {
      "category_name": "Mantenimiento",
      "total_amount": 500.00,
      "percentage": 13.89,
      "count": 3
    },
    {
      "category_name": "Suministros",
      "total_amount": 300.00,
      "percentage": 8.33,
      "count": 2
    },
    {
      "category_name": "Otros",
      "total_amount": 500.00,
      "percentage": 13.89,
      "count": 3
    }
  ],
  "top_expense_category": "Inventario"
}
```

## Gestión de Gastos

### Crear Gasto
```
POST /api/finances/expenses/
```

**Parámetros (JSON):**
```json
{
  "category": "Inventario",
  "description": "Compra de ingredientes frescos",
  "amount": 500.00,
  "vendor": "Distribuidor ABC",
  "notes": "Entrega para semana del 15-21 de enero",
  "expense_date": "2024-01-15"
}
```

**Categorías Disponibles:**
- `Inventario` - Compras de ingredientes
- `Servicios` - Servicios externos (internet, telefonía, etc.)
- `Mantenimiento` - Reparaciones y mantenimiento
- `Suministros` - Equipos y suministros operativos
- `Nómina` - Salarios y beneficios de empleados
- `Marketing` - Publicidad y promociones
- `Transporte` - Logística y transporte
- `Otros` - Gastos diversos

### Listar Gastos
```
GET /api/finances/expenses/
```

**Respuesta:**
Array de gastos con todos sus detalles.

### Obtener Gasto Específico
```
GET /api/finances/expenses/{expense_id}
```

**Respuesta:**
```json
{
  "id": "uuid-12345",
  "category": "Inventario",
  "description": "Compra de ingredientes frescos",
  "amount": 500.00,
  "vendor": "Distribuidor ABC",
  "notes": "Entrega para semana del 15-21 de enero",
  "expense_date": "2024-01-15",
  "registered_at": "2024-01-15T10:30:00",
  "registered_by": "uuid-admin-123"
}
```

## Arquitectura del Módulo

```
src/modules/Finances/
├── domain/
│   ├── entities/
│   │   └── expense.py          # Modelos de dominio
│   └── repositories/
│       └── finances_repository_interface.py  # Contrato
├── application/
│   ├── dto/
│   │   └── finance_response.py  # DTOs de respuesta
│   └── usecases/
│       └── finances_usecases.py # Lógica de negocio
└── infrastructure/
    ├── repositories/
    │   └── finances_repository.py  # Implementación Turso
    └── api/
        └── finances_router.py      # Endpoints
```

## Integración con Otros Módulos

### Integración con Módulo de Ventas
El módulo de Finanzas se integra automáticamente con el módulo de Ventas:
- **Ingresos**: Se obtienen desde la tabla `sales` sumando `final_amount`
- **Período**: Se consultan ventas dentro del rango de fechas especificado
- **Cálculo**: Totalmente automático, sin intervención manual

### Requisitos Previos
- ✅ Tabla `sales` con campo `final_amount`
- ✅ Campo `sale_date` en formato ISO (YYYY-MM-DD)
- ✅ Módulo de Ventas debe estar operativo

## Base de Datos

### Migración: 006_create_expenses_table.sql

Crea dos tablas:

#### Tabla: expenses
```sql
CREATE TABLE expenses (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    vendor TEXT,
    notes TEXT,
    expense_date DATE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    registered_by TEXT NOT NULL,
    FOREIGN KEY (registered_by) REFERENCES users(id),
    FOREIGN KEY (category) REFERENCES expense_categories(name)
)
```

Índices:
- `idx_expenses_date` en `expense_date`
- `idx_expenses_category` en `category`
- `idx_expenses_registered_at` en `registered_at`

#### Tabla: expense_categories
```sql
CREATE TABLE expense_categories (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Categorías Pre-cargadas:**
1. Inventario
2. Servicios
3. Mantenimiento
4. Suministros
5. Nómina
6. Marketing
7. Transporte
8. Otros

## Seguridad y Permisos

### Niveles de Acceso

**Administrador (admin):**
- ✅ Crear gastos
- ✅ Listar gastos
- ✅ Ver gasto específico
- ✅ Generar reporte diario
- ✅ Generar reporte de período
- ✅ Generar reporte detallado (completo)

**Empleado (employee):**
- ✅ Ver reporte diario
- ✅ Ver reporte de período
- ✅ Ver categorías de gasto
- ❌ Crear gastos
- ❌ Ver detalles de gastos

**Mesero (waiter):**
- ❌ Acceso restringido

### Autenticación
Todo endpoint requiere un token JWT válido en el header:
```
Authorization: Bearer {token_jwt}
```

## Ejemplos de Uso

### Obtener Ingresos Totales del Mes
```bash
curl -X GET "http://localhost:8000/api/finances/income/period/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {token}"
```

**Respuesta:**
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "total_income": 75000.00
}
```

### Obtener Ganancia Neta del Mes con Margen
```bash
curl -X GET "http://localhost:8000/api/finances/profit/period/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {token}"
```

**Respuesta:**
```json
{
  "period_start": "2024-01-01",
  "period_end": "2024-01-31",
  "total_income": 75000.00,
  "total_expenses": 45000.00,
  "net_profit": 30000.00,
  "profit_margin_percent": 40.0
}
```

### Obtener Reporte Detallado con Desglose por Categoría
```bash
curl -X GET "http://localhost:8000/api/finances/report/comprehensive/?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {token}"
```

**Respuesta**: Incluye desglose diario y por categoría de gastos

### Registrar un Gasto
```bash
curl -X POST "http://localhost:8000/api/finances/expenses/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Inventario",
    "description": "Compra de ingredientes frescos",
    "amount": 500.00,
    "vendor": "Distribuidor ABC",
    "notes": "Entrega para semana del 15-21 de enero",
    "expense_date": "2024-01-15"
  }'
```

## Consideraciones de Rendimiento

1. **Índices de Base de Datos**: Se han creado índices en `expense_date`, `category` y `registered_at` para optimizar queries de período y categoría

2. **Cálculos en Memoria**: Para períodos largos, los gráficos de desglose se calculan en la aplicación, no en la BD

3. **Querys Eficientes**: Todas las operaciones usan filtros de fecha a nivel de BD para minimizar datos transferidos

4. **Caché Potencial**: Los reportes pueden ser cacheados por el frontend si no se actualizan muy frecuentemente

## Resolución de Problemas

### Error: "Total de ingresos es 0"
- Verificar que existan ventas registradas en el rango de fechas
- Confirmar que las ventas tienen `final_amount > 0`
- Verificar que el campo `sale_date` está en formato correcto

### Error: "Gasto no encontrado"
- Verificar que el `expense_id` es correcto
- Confirmar que el gasto existe en la base de datos
- Verificar permisos del usuario

### Error: "Permiso denegado"
- Solo administradores pueden crear y listar gastos
- Empleados solo pueden ver reportes
- Verificar token JWT vigente

## Hoja de Ruta Futura

- [ ] Presupuestos por categoría
- [ ] Alertas de gastos que exceden presupuesto
- [ ] Proyecciones de ganancia basadas en tendencias
- [ ] Exportación de reportes a PDF/Excel
- [ ] Análisis de tendencias mensuales y anuales
