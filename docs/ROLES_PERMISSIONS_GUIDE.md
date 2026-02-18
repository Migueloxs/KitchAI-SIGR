# Gestión de Roles y Permisos

## 📋 Descripción

El sistema de KitchAI implementa un modelo completo de gestión de roles y permisos que cumple con los criterios de aceptación:

- **CA1**: Tabla `roles` con 3 roles predefinidos (admin, employee, waiter)
- **CA2**: Tabla `role_permissions` que vincula roles con permisos
- **CA3**: Asignación automática del rol 'waiter' por defecto al crear usuarios

## 🎯 Roles del Sistema

### 1. **Admin** (Administrador)
- **ID**: `uuid-role-admin`
- **Descripción**: Acceso total al sistema
- **Permisos**:
  - `manage_users`: Gestionar usuarios
  - `manage_inventory`: Gestionar inventario
  - `view_reports`: Ver reportes
  - `manage_orders`: Gestionar pedidos
  - `view_tables`: Ver mesas

### 2. **Employee** (Empleado)
- **ID**: `uuid-role-employee`
- **Descripción**: Gestión de inventario y reportes
- **Permisos**:
  - `manage_inventory`: Gestionar inventario
  - `view_reports`: Ver reportes

### 3. **Waiter** (Mesero)
- **ID**: `uuid-role-waiter`
- **Descripción**: Gestión de pedidos y mesas
- **Permisos**:
  - `manage_orders`: Gestionar pedidos
  - `view_tables`: Ver mesas
  - **ROL POR DEFECTO**: Se asigna automáticamente a nuevos usuarios

---

## 📡 Endpoints de Roles y Permisos

### 1. Listar Todos los Roles

**GET** `/api/roles/`

Obtiene la lista de todos los roles definidos en el sistema.

#### Response (200 OK)
```json
[
  {
    "id": "uuid-role-admin",
    "name": "admin",
    "description": "Administrador con acceso total",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "uuid-role-employee",
    "name": "employee",
    "description": "Empleado con acceso a inventario y reportes",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "uuid-role-waiter",
    "name": "waiter",
    "description": "Mesero con acceso a pedidos y mesas",
    "created_at": "2026-02-17T10:30:00"
  }
]
```

#### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/roles/"
```

---

### 2. Listar Todos los Permisos

**GET** `/api/roles/permissions/`

Obtiene la lista de todos los permisos disponibles en el sistema.

#### Response (200 OK)
```json
[
  {
    "id": "perm-1",
    "name": "manage_users",
    "description": "Gestionar usuarios",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "perm-2",
    "name": "manage_inventory",
    "description": "Gestionar inventario",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "perm-3",
    "name": "view_reports",
    "description": "Ver reportes",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "perm-4",
    "name": "manage_orders",
    "description": "Gestionar pedidos",
    "created_at": "2026-02-17T10:30:00"
  },
  {
    "id": "perm-5",
    "name": "view_tables",
    "description": "Ver mesas",
    "created_at": "2026-02-17T10:30:00"
  }
]
```

#### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/roles/permissions/"
```

---

### 3. Obtener Permisos de un Rol

**GET** `/api/roles/{role_id}/permissions`

Obtiene todos los permisos asociados a un rol específico.

#### Parámetros
- `role_id` (path): ID del rol (p.ej., `uuid-role-admin`)

#### Response (200 OK)
```json
{
  "id": "uuid-role-admin",
  "name": "admin",
  "description": "Administrador con acceso total",
  "permissions": [
    {
      "id": "perm-1",
      "name": "manage_users",
      "description": "Gestionar usuarios",
      "created_at": "2026-02-17T10:30:00"
    },
    {
      "id": "perm-2",
      "name": "manage_inventory",
      "description": "Gestionar inventario",
      "created_at": "2026-02-17T10:30:00"
    },
    {
      "id": "perm-3",
      "name": "view_reports",
      "description": "Ver reportes",
      "created_at": "2026-02-17T10:30:00"
    },
    {
      "id": "perm-4",
      "name": "manage_orders",
      "description": "Gestionar pedidos",
      "created_at": "2026-02-17T10:30:00"
    },
    {
      "id": "perm-5",
      "name": "view_tables",
      "description": "Ver mesas",
      "created_at": "2026-02-17T10:30:00"
    }
  ]
}
```

#### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/roles/uuid-role-admin/permissions"
```

---

### 4. Cambiar el Rol de un Usuario

**PUT** `/api/roles/users/{user_id}/role`

Asigna un nuevo rol a un usuario existente.

#### Parámetros
- `user_id` (path): ID del usuario

#### Request Body
```json
{
  "role": "admin"
}
```

#### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+18295551234",
  "role_id": "uuid-role-admin",
  "created_at": "2026-02-17T10:30:00"
}
```

#### Errores Posibles
- **404 Not Found**: El usuario no existe
- **400 Bad Request**: El rol especificado no existe o es inválido

#### Ejemplo cURL
```bash
curl -X PUT "http://localhost:8000/api/roles/users/{user_id}/role" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'
```

#### Ejemplo PowerShell
```powershell
$body = @{
    role = "admin"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/roles/users/{user_id}/role" `
    -Method Put `
    -ContentType "application/json" `
    -Body $body
```

---

## 🔄 Flujo de Asignación de Roles

### 1. **Registro de Usuario (sin especificar rol)**
```bash
POST /api/auth/register
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+1829555-1234",
  "password": "SecurePass123!"
  // rol omitido → se asigna 'waiter' automáticamente
}
```
**Resultado**: Usuario creado con rol `waiter` (uuid-role-waiter)

### 2. **Cambiar el Rol de un Usuario Existente**
```bash
PUT /api/roles/users/{user_id}/role
{
  "role": "admin"
}
```
**Resultado**: Usuario actualizado con nuevo rol `admin` (uuid-role-admin)

---

## 📊 Modelo de Datos

### Tabla: roles
```sql
CREATE TABLE roles (
    id TEXT PRIMARY KEY,           -- UUID
    name TEXT NOT NULL UNIQUE,     -- admin, employee, waiter
    description TEXT,              -- Descripción del rol
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: permissions
```sql
CREATE TABLE permissions (
    id TEXT PRIMARY KEY,           -- UUID
    name TEXT NOT NULL UNIQUE,     -- manage_users, manage_inventory, etc.
    description TEXT,              -- Descripción del permiso
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: role_permissions
```sql
CREATE TABLE role_permissions (
    id TEXT PRIMARY KEY,           -- UUID
    role_id TEXT NOT NULL,         -- Referencia a roles
    permission_id TEXT NOT NULL,   -- Referencia a permissions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)  -- No duplicados
);
```

---

## ✅ Criterios de Aceptación

### CA1: Tabla de Roles con Límite de Tres Roles ✅
```
✅ Tabla 'roles' existe
✅ Rol 'admin' registrado (administrador con acceso total)
✅ Rol 'employee' registrado (acceso a inventario y reportes)
✅ Rol 'waiter' registrado (acceso a pedidos y mesas)
```

### CA2: Tabla Relacional role_permissions ✅
```
✅ Tabla 'role_permissions' existe
✅ Vinculación admin → todos los permisos
✅ Vinculación employee → manage_inventory, view_reports
✅ Vinculación waiter → manage_orders, view_tables
```

### CA3: Asignación Automática de 'waiter' ✅
```
✅ Si no se especifica 'role' al registrar: rol = 'waiter'
✅ El campo 'role' es OPCIONAL en POST /api/auth/register
✅ Pydantic asigna 'waiter' como valor por defecto
```

---

## 🚀 Testing

### Prueba: Registrar sin especificar rol

```powershell
$body = @{
    name = "Test User"
    email = "test@kitchai.com"
    phone = "+18299991234"
    password = "TestPass123!"
    # role OMITIDO
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Verificar que role_id contiene 'waiter'
$response.role_id  # Debería ser: uuid-role-waiter
```

### Prueba: Cambiar el rol de un usuario

```powershell
$body = @{
    role = "admin"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/roles/users/{user_id}/role" `
    -Method Put `
    -ContentType "application/json" `
    -Body $body

# Verificar que el rol fue actualizado
$response.role_id  # Debería ser: uuid-role-admin
```

---

## 🔐 Seguridad

- Solo administradores pueden cambiar roles (futuras implementaciones)
- Los permisos se validan contra la tabla `role_permissions`
- Auditoría de cambios de rol (futuro)
- Validación estricta de entrada

---

## 📚 Referencias

- [API de Autenticación](API_AUTH_GUIDE.md)
- [Setup de Base de Datos](TURSO_DB_SETUP.md)
- [README Principal](README_AUTH.md)
