# Gestión de Nómina Básica - Guía Completa

## Descripción General

El módulo de **Gestión de Nómina Básica** (Payroll Management) proporciona las APIs necesarias para calcular e intermediar datos de nómina de empleados. Está diseñado para integrarse con sistemas de nómina externos y proporciona información detallada de horas trabajadas, ausencias y cálculos de salarios.

### Características Principales

1. **Cálculo de Horas Trabajadas (CA1)**
   - Diferencia entre horas normales y horas extras
   - Seguimiento de retrasos y ausencias
   - Integración con datos de asistencia

2. **Gestión de Ausencias (CA2)**
   - Registro de ausencias justificadas (vacaciones, incapacidades, etc.)
   - Registro de ausencias injustificadas (inasistencias)
   - Marcado de ausencias como pagadas o no pagadas

3. **Exportación de Datos (CA3)**
   - Formato JSON consumible por sistemas de nómina externos
   - Reportes con sumas totales y resúmenes
   - Datos de aprobación y estado de pago

---

## Conceptos Clave

### Períodos de Nómina

Un período de nómina define el rango de fechas para el cual se calcula la nómina. Puede ser:

- **WEEKLY**: Períodos semanales
- **BIWEEKLY**: Períodos quincenales
- **MONTHLY**: Períodos mensuales
- **CUSTOM**: Períodos personalizados

Ejemplo:
```json
{
  "id": "period-2026-03",
  "name": "2026-03 (March 2026)",
  "period_type": "MONTHLY",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31"
}
```

### Horas Trabajadas

Las horas trabajadas se calculan en base a los registros de entrada/salida del empleado:

- **Normal Hours**: Horas dentro de la jornada estándar (ej: 8 horas/día)
- **Overtime Hours**: Horas más allá de la jornada estándar
- **Lateness**: Minutos totales de retrasos y cantidad de veces que llegó tarde

```json
{
  "employee_id": "emp-123",
  "normal_hours": 160.0,
  "overtime_hours": 12.5,
  "total_hours": 172.5,
  "times_late": 5,
  "minutes_late": 145
}
```

### Ausencias

Las ausencias pueden ser:

- **JUSTIFIED**: Vacaciones, incapacidades médicas, permisos autorizados
= **UNJUSTIFIED**: Inasistencias no justificadas

Y pueden ser:

- **Paid**: Se pagan como días de trabajo
- **Unpaid**: Se descuentan del salario

---

## Endpoints de API

### 1. Gestión de Períodos de Nómina

#### Crear Período de Nómina

```http
POST /api/payroll/periods
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "2026-03 (March 2026)",
  "period_type": "MONTHLY",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "is_active": true
}
```

**Respuesta (201 Created):**
```json
{
  "id": "period-2026-03",
  "name": "2026-03 (March 2026)",
  "period_type": "MONTHLY",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "is_active": true,
  "created_at": "2026-02-28T10:00:00",
  "updated_at": "2026-02-28T10:00:00"
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

---

#### Obtener Períodos Activos

```http
GET /api/payroll/periods/active
Authorization: Bearer {token}
```

**Respuesta (200 OK):**
```json
[
  {
    "id": "period-2026-03",
    "name": "2026-03 (March 2026)",
    "period_type": "MONTHLY",
    "start_date": "2026-03-01",
    "end_date": "2026-03-31",
    "is_active": true,
    "created_at": "2026-02-28T10:00:00",
    "updated_at": "2026-02-28T10:00:00"
  }
]
```

---

### 2. Cálculo de Horas Trabajadas (CA1)

#### Calcular Horas Trabajadas

```http
POST /api/payroll/worked-hours
Authorization: Bearer {token}
Content-Type: application/json

{
  "employee_id": "emp-123",
  "payroll_period_id": "period-2026-03"
}
```

**Respuesta (200 OK):**
```json
{
  "id": "wh-456",
  "employee_id": "emp-123",
  "employee_name": "Juan García",
  "email": "juan@kitchai.com",
  "payroll_period": "2026-03 (March 2026)",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "normal_hours": 160.0,
  "overtime_hours": 12.5,
  "total_hours": 172.5,
  "minutes_late": 145,
  "times_late": 5,
  "days_present": 22
}
```

**Permisos Requeridos:** HR_MANAGER, SUPERVISOR, o datos propios

**Notas:**
- Las horas se calculan automáticamente desde los registros de asistencia
- Las horas extra se identifican comparando contra la duración esperada del turno
- Se incluye un resumen de retrasos

---

### 3. Gestión de Ausencias (CA2)

#### Obtener Ausencias

```http
POST /api/payroll/absences
Authorization: Bearer {token}
Content-Type: application/json

{
  "employee_id": "emp-123",
  "payroll_period_id": "period-2026-03"
}
```

**Respuesta (200 OK):**
```json
{
  "employee_id": "emp-123",
  "employee_name": "Juan García",
  "email": "juan@kitchai.com",
  "payroll_period": "2026-03 (March 2026)",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "justified_absences": 2,
  "unjustified_absences": 1,
  "total_absences": 3,
  "paid_absences": 2
}
```

**Permisos Requeridos:** HR_MANAGER, SUPERVISOR, o datos propios

---

#### Registrar Ausencia

```http
POST /api/payroll/absences/record
Authorization: Bearer {token}
Content-Type: application/json

{
  "employee_id": "emp-123",
  "absence_date": "2026-03-05",
  "absence_type": "JUSTIFIED",
  "reason": "Medical leave",
  "description": "Doctor appointment",
  "is_paid": true
}
```

**Respuesta (201 Created):**
```json
{
  "id": "abs-789",
  "employee_id": "emp-123",
  "absence_date": "2026-03-05",
  "absence_type": "JUSTIFIED",
  "reason": "Medical leave",
  "created_at": "2026-03-05T09:00:00"
}
```

**Permisos Requeridos:** HR_MANAGER, SUPERVISOR, ADMIN

---

### 4. Detracciones

#### Agregar Detracción

```http
POST /api/payroll/deductions
Authorization: Bearer {token}
Content-Type: application/json

{
  "employee_id": "emp-123",
  "payroll_period_id": "period-2026-03",
  "deduction_type": "DISCOUNT",
  "amount": 100.00,
  "reason": "Disciplinary action",
  "description": "Breakage of equipment"
}
```

**Respuesta (201 Created):**
```json
{
  "id": "ded-101",
  "employee_id": "emp-123",
  "amount": 100.00,
  "reason": "Disciplinary action",
  "created_at": "2026-03-10T14:30:00"
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

**Tipos de Detracciones:**
- **ABSENCE**: Detracción por inasistencia
- **DISCOUNT**: Descuento disciplinario
- **OTHER**: Otras detracciones

---

### 5. Cálculo de Nómina

#### Calcular Nómina

```http
POST /api/payroll/calculate
Authorization: Bearer {token}
Content-Type: application/json

{
  "employee_id": "emp-123",
  "payroll_period_id": "period-2026-03",
  "hourly_rate": 15.50,
  "overtime_multiplier": 1.5,
  "include_deductions": true
}
```

**Respuesta (200 OK):**
```json
{
  "id": "calc-111",
  "employee_id": "emp-123",
  "employee_name": "Juan García",
  "payroll_period_id": "period-2026-03",
  "payroll_period": "2026-03 (March 2026)",
  "normal_hours": 160.0,
  "overtime_hours": 12.5,
  "hourly_rate": 15.50,
  "overtime_multiplier": 1.5,
  "base_salary": 2480.00,
  "overtime_salary": 291.88,
  "gross_salary": 2771.88,
  "total_deductions": 150.00,
  "net_salary": 2621.88,
  "status": "CALCULATED",
  "calculated_at": "2026-03-31T18:00:00"
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

**Cálculos Realizados:**
```
base_salary = normal_hours * hourly_rate
overtime_salary = overtime_hours * hourly_rate * overtime_multiplier
gross_salary = base_salary + overtime_salary
net_salary = gross_salary - total_deductions
```

---

### 6. Reportes y Exportación (CA3)

#### Generar Reporte de Nómina

```http
POST /api/payroll/report
Authorization: Bearer {token}
Content-Type: application/json

{
  "payroll_period_id": "period-2026-03",
  "include_deductions": true,
  "format_type": "JSON"
}
```

**Respuesta (200 OK):**
```json
{
  "payroll_period_id": "period-2026-03",
  "payroll_period": "2026-03 (March 2026)",
  "period_start": "2026-03-01",
  "period_end": "2026-03-31",
  "generated_at": "2026-03-31T18:30:00",
  "company_name": "KitchAI SIGR",
  "currency": "USD",
  "records": [
    {
      "employee_id": "emp-123",
      "employee_name": "Juan García",
      "email": "juan@kitchai.com",
      "normal_hours": 160.0,
      "overtime_hours": 12.5,
      "hourly_rate": 15.50,
      "overtime_multiplier": 1.5,
      "base_salary": 2480.00,
      "overtime_salary": 291.88,
      "gross_salary": 2771.88,
      "total_deductions": 150.00,
      "net_salary": 2621.88,
      "status": "APPROVED",
      "paid": false
    }
  ],
  "summary": {
    "total_employees": 1,
    "total_gross_salary": 2771.88,
    "total_deductions": 150.00,
    "total_net_salary": 2621.88,
    "total_normal_hours": 160.0,
    "total_overtime_hours": 12.5,
    "employees_paid": 0,
    "employees_pending": 1
  }
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

---

#### Exportar como JSON

```http
POST /api/payroll/export/json
Authorization: Bearer {token}
Content-Type: application/json

{
  "payroll_period_id": "period-2026-03",
  "include_deductions": true,
  "format_type": "JSON"
}
```

**Respuesta (200 OK):**
```json
{
  "export_id": "exp-aBC123",
  "export_date": "2026-03-31T18:35:00",
  "export_format": "JSON",
  "payroll_report": { /* ... payroll report data ... */ },
  "export_method": "API"
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

**Casos de Uso:**
- Exportar datos a sistemas de nómina externos (ADP, SAP, etc.)
- Integración con software de contabilidad
- Auditoría y reportes financieros

---

### 7. Flujo de Aprobación y Pago

#### Aprobar Nómina

```http
POST /api/payroll/approve
Authorization: Bearer {token}
Content-Type: application/json

{
  "payroll_id": "calc-111"
}
```

**Respuesta (200 OK):**
```json
{
  "id": "calc-111",
  "status": "APPROVED",
  "approved_by": "user-789",
  "approved_at": "2026-03-31T19:00:00",
  // ... other fields ...
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN

---

#### Marcar como Pagado

```http
POST /api/payroll/pay
Authorization: Bearer {token}
Content-Type: application/json

{
  "payroll_id": "calc-111"
}
```

**Respuesta (200 OK):**
```json
{
  "id": "calc-111",
  "status": "PAID",
  "paid_at": "2026-03-31T20:00:00",
  // ... other fields ...
}
```

**Permisos Requeridos:** HR_MANAGER, ADMIN, ACCOUNTING

**Flujo de Estados:**
```
DRAFT → CALCULATED → APPROVED → PAID
```

---

## Flujo de Trabajo Completo

### Ejemplo: Procesar Nómina de Marzo 2026

#### Paso 1: Crear Período de Nómina
```bash
curl -X POST http://localhost:8000/api/payroll/periods \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2026-03 (March 2026)",
    "period_type": "MONTHLY",
    "start_date": "2026-03-01",
    "end_date": "2026-03-31",
    "is_active": true
  }'
```

#### Paso 2: Calcular Horas para Cada Empleado
```bash
curl -X POST http://localhost:8000/api/payroll/worked-hours \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "payroll_period_id": "period-2026-03"
  }'
```

#### Paso 3: Revisar Ausencias
```bash
curl -X POST http://localhost:8000/api/payroll/absences \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "payroll_period_id": "period-2026-03"
  }'
```

#### Paso 4: Agregar Detracciones si Aplica
```bash
curl -X POST http://localhost:8000/api/payroll/deductions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "payroll_period_id": "period-2026-03",
    "deduction_type": "OTHER",
    "amount": 50.00,
    "reason": "Uniform cost"
  }'
```

#### Paso 5: Calcular Nómina
```bash
curl -X POST http://localhost:8000/api/payroll/calculate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "emp-123",
    "payroll_period_id": "period-2026-03",
    "hourly_rate": 15.50,
    "overtime_multiplier": 1.5,
    "include_deductions": true
  }'
```

#### Paso 6: Generar Reporte
```bash
curl -X POST http://localhost:8000/api/payroll/report \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "payroll_period_id": "period-2026-03",
    "include_deductions": true,
    "format_type": "JSON"
  }'
```

#### Paso 7: Aprobar Nóminas
```bash
curl -X POST http://localhost:8000/api/payroll/approve \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "payroll_id": "calc-111"
  }'
```

#### Paso 8: Marcar como Pagado
```bash
curl -X POST http://localhost:8000/api/payroll/pay \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "payroll_id": "calc-111"
  }'
```

---

## Integración con Asistencia

El módulo de Nómina se integra con el módulo de Asistencia para obtener:

- **Registros de Entrada/Salida**: Para calcular horas trabajadas
- **Alertas de Asistencia**: Para identificar ausencias automáticas
- **Información de Retrasos**: Minutos y veces tarde

Asegúrate de que el módulo de Asistencia esté:
1. ✅ Correctamente configurado
2. ✅ Recibiendo check-ins y check-outs
3. ✅ Generando alertas de asistencia

---

## Consideraciones de Seguridad

1. **Autenticación**: Todos los endpoints requieren token JWT válido
2. **Autorización**: Solo HR_MANAGER, SUPERVISOR, y ADMIN pueden acceder
3. **Privacidad**: Los empleados solo pueden ver sus propios datos
4. **Auditoría**: Las aprobaciones y pagos se registran con timestamps y usuario
5. **Validación**: Todos los datos se validan antes de guardar

---

## Troubleshooting

### Error: "Payroll period not found"
- Asegúrate de crear el período de nómina primero
- Verifica que el `payroll_period_id` sea correcto

### Error: "No work hours found"
- El empleado debe tener registros de asistencia en el período
- Verifica que los registros de check-in/check-out estén disponibles

### Error: "Cannot access other employee's hours"
- Solo HR_MANAGER, SUPERVISOR, o ADMIN pueden ver datos de todos
- Los empleados solo pueden ver sus propios datos

### Error: "Unauthorized" (401)
- Verifica que el token JWT sea válido
- Asegúrate de incluir `Authorization: Bearer {token}` en el header

### Error: "Forbidden" (403)
- Tu rol no tiene permiso para esta operación
- Contacta a tu administrador para solicitar permisos

---

## Soporte

Para reportar problemas o solicitar funcionalidades adicionales:
- Email: soporte@kitchai.com
- GitHub: [repositorio del proyecto]
