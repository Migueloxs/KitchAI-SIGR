# Shifts Management API Guide

**User Story**: Gestión de Horarios y Turnos de Trabajo (Work Schedule and Shift Management)

**Implementation**: Complete REST API for shift management with calendar view

## Overview

The Shifts Management API provides comprehensive capabilities for managing employee work schedules and shifts in the restaurant. All endpoints follow the hexagonal architecture pattern and integrate with Turso database.

### Requirements

- **CA1**: Define weekly shifts (entry/exit times) and assign to one or multiple employees
- **CA2**: Prevent overlapping shifts on the same day for an employee
- **CA3**: Show assigned shifts in a shared calendar accessible to affected employees

---

## Authentication & Authorization

All endpoints require JWT authentication.

### Role-Based Access

- **Admin**: Full access to all shift management features
- **Supervisor**: Can create, assign, and manage shifts
- **Employee**: Can view their own calendar and other team calendars

---

## API Endpoints

### 1. Shift Management (CA1)

#### Create Shift

**Endpoint**: `POST /api/shifts/shifts/`

**Description**: Define a new shift pattern for a specific day of the week

**Request**:
```json
{
  "name": "Mañana",
  "day_of_week": 0,
  "start_time": "08:00",
  "end_time": "16:00"
}
```

**Query Parameters**:
- `name` (string, required): Shift name (e.g., "Mañana", "Tarde", "Noche")
- `day_of_week` (integer, required): 0=Monday through 6=Sunday
- `start_time` (string, required): Start time in HH:MM format
- `end_time` (string, required): End time in HH:MM format

**Response** (201 Created):
```json
{
  "id": "shift-uuid",
  "name": "Mañana",
  "day_of_week": 0,
  "day_name": "Lunes",
  "start_time": "08:00",
  "end_time": "16:00",
  "is_active": true,
  "created_at": "2026-03-26T12:00:00",
  "updated_at": "2026-03-26T12:00:00"
}
```

**Required Role**: Admin or Supervisor

---

#### Get All Shifts

**Endpoint**: `GET /api/shifts/shifts/`

**Query Parameters**:
- `active_only` (boolean, default: true): Filter only active shifts

**Response** (200 OK): List of ShiftResponseDTO

---

#### Get Shifts by Day

**Endpoint**: `GET /api/shifts/shifts/day/{day_of_week}`

**Path Parameters**:
- `day_of_week` (integer): 0=Monday, 6=Sunday

**Response** (200 OK): List of shifts for that day

---

#### Update Shift

**Endpoint**: `PUT /api/shifts/shifts/{shift_id}`

**Request**:
```json
{
  "name": "Mañana Actualizada",
  "start_time": "07:00",
  "end_time": "15:00",
  "is_active": true
}
```

**Response** (200 OK): Updated ShiftResponseDTO

**Required Role**: Admin or Supervisor

---

#### Delete Shift

**Endpoint**: `DELETE /api/shifts/shifts/{shift_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Turno eliminado correctamente"
}
```

**Required Role**: Admin

---

### 2. Shift Assignments (CA1, CA2)

#### Assign Shift to Employee

**Endpoint**: `POST /api/shifts/assignments/`

**Description**: Assign a shift to an employee (CA1)

**Request**:
```json
{
  "shift_id": "shift-uuid",
  "employee_id": "employee-uuid",
  "start_date": "2026-03-26",
  "end_date": "2026-06-26",
  "notes": "Temporal arrangement until new hire"
}
```

**Query Parameters**:
- `shift_id` (string, required): UUID of the shift
- `employee_id` (string, required): UUID of the employee
- `start_date` (date, required): Start date in YYYY-MM-DD format
- `end_date` (date, optional): End date (NULL for indefinite)
- `notes` (string, optional): Additional notes

**Response** (201 Created):
```json
{
  "id": "assignment-uuid",
  "shift_id": "shift-uuid",
  "shift_name": "Mañana",
  "day_of_week": 0,
  "day_name": "Lunes",
  "start_time": "08:00",
  "end_time": "16:00",
  "employee_id": "employee-uuid",
  "employee_name": "Juan García",
  "email": "juan@restaurant.com",
  "start_date": "2026-03-26",
  "end_date": "2026-06-26",
  "notes": "Temporal arrangement until new hire",
  "is_active": true,
  "created_at": "2026-03-26T12:00:00",
  "updated_at": "2026-03-26T12:00:00"
}
```

**CA2 Validation**: Automatically checks for overlapping shifts

**Error Response** (400 Bad Request) - If conflicts:
```json
{
  "detail": "El empleado ya tiene turnos asignados en esa fecha: Tarde (14:00-22:00). No pueden solaparse."
}
```

**Required Role**: Admin or Supervisor

---

#### Bulk Assign Shift

**Endpoint**: `POST /api/shifts/assignments/bulk/`

**Description**: Assign the same shift to multiple employees (CA1)

**Request**:
```json
{
  "shift_id": "shift-uuid",
  "employee_ids": ["emp-1", "emp-2", "emp-3"],
  "start_date": "2026-03-26",
  "end_date": "2026-06-26",
  "notes": "Group assignment"
}
```

**Response** (201 Created):
```json
{
  "successful": 3,
  "failed": 0,
  "errors": [],
  "assigned_shifts": [
    { ...ShiftAssignmentResponseDTO... }
  ]
}
```

**CA2 Validation**: Each employee is validated individually

**Required Role**: Admin or Supervisor

---

#### Get Employee Assignments

**Endpoint**: `GET /api/shifts/assignments/employee/{employee_id}`

**Path Parameters**:
- `employee_id` (string): UUID of the employee

**Response** (200 OK): List of ShiftAssignmentResponseDTO

---

#### Update Assignment

**Endpoint**: `PUT /api/shifts/assignments/{assignment_id}`

**Description**: Modify an assignment (extend or end it)

**Request**:
```json
{
  "end_date": "2026-05-26",
  "notes": "Extended due to new hire delay"
}
```

**Response** (200 OK): Updated ShiftAssignmentResponseDTO

**Required Role**: Admin or Supervisor

---

#### Delete Assignment

**Endpoint**: `DELETE /api/shifts/assignments/{assignment_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Asignación de turno eliminada"
}
```

**Required Role**: Admin or Supervisor

---

### 3. Calendar View (CA3)

#### Get Employee Calendar

**Endpoint**: `GET /api/shifts/calendar/employee/{employee_id}`

**Description**: CA3 - Get employee's weekly calendar showing all assigned shifts

**Path Parameters**:
- `employee_id` (string): UUID of the employee

**Query Parameters**:
- `week_start` (string, optional): Week start date in YYYY-MM-DD format (defaults to current week)

**Response** (200 OK):
```json
{
  "employee_id": "employee-uuid",
  "employee_name": "Juan García",
  "week_start": "2026-03-23",
  "week_end": "2026-03-29",
  "schedule": {
    "Lunes": [
      {
        "employee_id": "employee-uuid",
        "employee_name": "Juan García",
        "email": "juan@restaurant.com",
        "shift_id": "shift-uuid",
        "shift_name": "Mañana",
        "day_of_week": 0,
        "day_name": "Lunes",
        "start_time": "08:00",
        "end_time": "16:00",
        "start_date": "2026-03-26",
        "end_date": null,
        "notes": null,
        "is_active": true,
        "created_at": "2026-03-26T12:00:00",
        "updated_at": "2026-03-26T12:00:00"
      }
    ],
    "Martes": [],
    "Miércoles": [
      { ...shift details... }
    ],
    "Jueves": [],
    "Viernes": [
      { ...shift details... }
    ],
    "Sábado": [],
    "Domingo": []
  }
}
```

**Accessible to**: All employees (can view own calendar) and supervisors/admins (can view any employee's calendar)

---

#### Get Team Calendar

**Endpoint**: `GET /api/shifts/calendar/team/`

**Description**: CA3 - Get calendars for multiple employees

**Query Parameters**:
- `employee_ids` (string, required): Comma-separated list of employee UUIDs
- `week_start` (string, optional): Week start date in YYYY-MM-DD format

**Response** (200 OK): List of WeeklyCalendarDTO

**Required Role**: Admin or Supervisor

---

### 4. Conflict Detection (CA2)

#### Check for Overlapping Shifts

**Endpoint**: `GET /api/shifts/conflicts/check/`

**Description**: CA2 - Verify if an employee has conflicting shifts on a specific date

**Query Parameters**:
- `employee_id` (string, required): UUID of the employee
- `target_date` (string, required): Date in YYYY-MM-DD format

**Response if Conflicts** (200 OK):
```json
{
  "employee_id": "employee-uuid",
  "employee_name": "Juan García",
  "date": "2026-03-26",
  "conflicts": [
    {
      "shift_id": "shift-1",
      "name": "Mañana",
      "time": "08:00-16:00"
    },
    {
      "shift_id": "shift-2",
      "name": "Tarde",
      "time": "14:00-22:00"
    }
  ],
  "message": "El empleado tiene 2 turnos solapados el 2026-03-26"
}
```

**Response if No Conflicts** (200 OK):
```json
{
  "message": "Sin conflictos de turnos"
}
```

**Required Role**: Admin or Supervisor

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message describing what's wrong with the request"
}
```

### 403 Forbidden
```json
{
  "detail": "Se requiere ser Administrador o Supervisor para gestionar turnos"
}
```

### 404 Not Found
```json
{
  "detail": "Turno con ID {id} no encontrado"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error creando turno: {error_details}"
}
```

---

## Data Models

### Shift Entity

```python
{
  "id": "uuid",
  "name": "string",
  "day_of_week": 0-6,
  "day_name": "string",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "is_active": boolean,
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### ShiftAssignment Entity

```python
{
  "id": "uuid",
  "shift_id": "uuid",
  "employee_id": "uuid",
  "shift_name": "string",
  "day_of_week": 0-6,
  "day_name": "string",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "employee_name": "string",
  "email": "string",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD or null",
  "notes": "string or null",
  "is_active": boolean,
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

---

## Validations & Business Rules

### CA1: Shift Assignment Rules
- Each shift must have unique name per day of week
- Shifts must have valid start and end times (HH:MM format)
- Shifts can be assigned to one or multiple employees
- Assignments can have start and end dates

### CA2: Overlap Prevention
- An employee cannot have multiple shifts on the same day
- Automatic validation when assigning shifts
- Returns detailed conflict information if overlaps detected
- Validation applies to entire date range of assignment

### CA3: Calendar Features
- Calendar shows all active assignments for selected week
- Displays employee name, shift details, and timing
- Can view single employee or team calendar
- Accessible to employees and supervisors

---

## Example Workflows

### Workflow 1: Define and Assign Morning Shift

```bash
# 1. Create morning shift
curl -X POST "http://localhost:8001/api/shifts/shifts/" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mañana",
    "day_of_week": 0,
    "start_time": "08:00",
    "end_time": "16:00"
  }'

# 2. Assign to employee
curl -X POST "http://localhost:8001/api/shifts/assignments/" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "shift_id": "shift-uuid-from-step1",
    "employee_id": "employee-uuid",
    "start_date": "2026-04-01",
    "end_date": null
  }'

# 3. View employee calendar
curl -X GET "http://localhost:8001/api/shifts/calendar/employee/employee-uuid" \
  -H "Authorization: Bearer {TOKEN}"
```

### Workflow 2: Bulk Assign to Team

```bash
curl -X POST "http://localhost:8001/api/shifts/assignments/bulk/" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "shift_id": "shift-uuid",
    "employee_ids": ["emp-1", "emp-2", "emp-3", "emp-4"],
    "start_date": "2026-04-01",
    "notes": "Monday morning shift crew"
  }'
```

### Workflow 3: Check for Conflicts

```bash
curl -X GET "http://localhost:8001/api/shifts/conflicts/check/?employee_id=emp-1&target_date=2026-03-26" \
  -H "Authorization: Bearer {TOKEN}"
```

---

## Database Schema

### shifts table
```sql
CREATE TABLE shifts (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  day_of_week INTEGER NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  is_active BOOLEAN DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

### shift_assignments table
```sql
CREATE TABLE shift_assignments (
  id TEXT PRIMARY KEY,
  shift_id TEXT NOT NULL,
  employee_id TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (shift_id) REFERENCES shifts (id),
  FOREIGN KEY (employee_id) REFERENCES users (id)
);
```

### active_shift_assignments view
Shows currently active assignments filtered by date ranges

---

## Architecture

### Hexagonal Architecture Implementation

**Domain Layer**:
- `Shift` entity with overlap detection logic
- `ShiftAssignment` entity with activity tracking

**Application Layer**:
- `ShiftsService` with business logic
- DTOs for all request/response types

**Infrastructure Layer**:
- `ShiftsRepository` for database operations
- `shifts_router` for REST endpoints

---

## Testing

All functionality is tested with:
- Unit tests for domain entities
- Integration tests for database operations
- API endpoint testing via Swagger UI

Run tests:
```bash
pytest test_shifts_module.py -v
```

---

## Support

For issues or questions about the Shifts API, refer to:
- This API Guide
- Domain entity docstrings
- Service method documentation
- Main README.md

---

**Implementation Date**: March 26, 2026
**Status**: Production Ready
