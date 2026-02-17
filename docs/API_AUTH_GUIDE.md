# API de Autenticación - Guía de Uso

## 🚀 Estado del Servidor

El servidor está ejecutándose en: **http://localhost:8000**

## 📚 Documentación Interactiva

FastAPI proporciona documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Endpoints de Autenticación

### 1. Registro de Usuario

**POST** `/api/auth/register`

Registra un nuevo usuario en el sistema.

#### Request Body

```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+1829555-1234",
  "password": "SecurePass123!",
  "role": "waiter"
}
```

#### Validaciones

- **Email**: Debe ser único en el sistema
- **Password**: 
  - Mínimo 8 caracteres
  - Al menos una letra mayúscula
  - Al menos una letra minúscula
  - Al menos un número
  - Al menos un carácter especial (!@#$%^&*(),.?":{}|<>)
- **Role**: Debe ser uno de: `admin`, `employee`, `waiter`

#### Response (201 Created)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+18295551234",
  "role_id": "uuid-role-waiter",
  "created_at": "2026-02-17T10:30:00"
}
```

#### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "phone": "+1829555-1234",
    "password": "SecurePass123!",
    "role": "waiter"
  }'
```

#### Ejemplo PowerShell

```powershell
$body = @{
    name = "Juan Pérez"
    email = "juan.perez@example.com"
    phone = "+1829555-1234"
    password = "SecurePass123!"
    role = "waiter"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

---

### 2. Inicio de Sesión (Login)

**POST** `/api/auth/login`

Autentica un usuario y retorna un token JWT.

#### Request Body

```json
{
  "email": "juan.perez@example.com",
  "password": "SecurePass123!"
}
```

#### Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJqdWFuLnBlcmV6QGV4YW1wbGUuY29tIiwicm9sZV9pZCI6InV1aWQtcm9sZS13YWl0ZXIiLCJleHAiOjE3MDk0NjAwMDAsImlhdCI6MTcwOTQ1NjQwMH0.XXX",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "phone": "+18295551234",
    "role_id": "uuid-role-waiter",
    "created_at": "2026-02-17T10:30:00"
  }
}
```

#### Ejemplo cURL

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@example.com",
    "password": "SecurePass123!"
  }'
```

#### Ejemplo PowerShell

```powershell
$body = @{
    email = "juan.perez@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

# Guardar el token para usarlo en futuras peticiones
$token = $response.access_token
```

---

## 🔒 Seguridad Implementada

### CA1: Endpoint de Registro ✅
- ✅ POST /api/auth/register implementado
- ✅ Acepta: nombre, email, teléfono, contraseña, rol
- ✅ Retorna código 201 con datos del usuario
- ✅ NO incluye la contraseña en la respuesta

### CA2: Hash Seguro de Contraseñas ✅
- ✅ Contraseñas hasheadas con **bcrypt** (factor 12)
- ✅ NUNCA se almacenan en texto plano
- ✅ Validación de fortaleza de contraseña

### CA3: Bloqueo por Intentos Fallidos ✅
- ✅ Contador de intentos fallidos
- ✅ Bloqueo automático tras **5 intentos fallidos**
- ✅ Duración del bloqueo: **15 minutos**
- ✅ Retorna código **429 (Too Many Requests)** cuando está bloqueado
- ✅ Registro de auditoría en tabla `login_attempts`

### CA4: Documentación de API ✅
- ✅ Documentación con **Swagger/OpenAPI**
- ✅ Ejemplos de requests y responses
- ✅ Descripciones detalladas de cada endpoint
- ✅ Validaciones documentadas

---

## 🎯 Usando el Token JWT

Una vez que obtengas el token al hacer login, debes incluirlo en el header `Authorization` de tus futuras peticiones:

```
Authorization: Bearer {tu_token_jwt}
```

### Ejemplo con cURL

```bash
curl -X GET "http://localhost:8000/api/protected-endpoint" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ejemplo con PowerShell

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/protected-endpoint" `
    -Method Get `
    -Headers $headers
```

---

## 🧪 Probando el Sistema

### Flujo Completo de Prueba

1. **Registrar un usuario**:
```powershell
$registerBody = @{
    name = "María García"
    email = "maria.garcia@test.com"
    phone = "+18095551234"
    password = "TestPass123!"
    role = "admin"
} | ConvertTo-Json

$user = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method Post -ContentType "application/json" -Body $registerBody

Write-Host "Usuario registrado: $($user.email)"
```

2. **Hacer login**:
```powershell
$loginBody = @{
    email = "maria.garcia@test.com"
    password = "TestPass123!"
} | ConvertTo-Json

$auth = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method Post -ContentType "application/json" -Body $loginBody

$token = $auth.access_token
Write-Host "Token obtenido: $($token.Substring(0, 20))..."
Write-Host "Usuario autenticado: $($auth.user.name)"
```

3. **Probar bloqueo por intentos fallidos**:
```powershell
# Intentar login 5 veces con contraseña incorrecta
1..5 | ForEach-Object {
    $failBody = @{
        email = "maria.garcia@test.com"
        password = "ContraseñaIncorrecta"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
            -Method Post -ContentType "application/json" -Body $failBody
    } catch {
        Write-Host "Intento $($_) fallido: $($_.Exception.Message)"
    }
}
```

---

## 📋 Roles Disponibles

Los siguientes roles están precargados en la base de datos:

| Rol | ID | Descripción | Permisos |
|-----|-----|-------------|----------|
| **admin** | uuid-role-admin | Administrador con acceso total | Gestionar usuarios, inventario, reportes, pedidos, mesas |
| **employee** | uuid-role-employee | Empleado con acceso a inventario y reportes | Gestionar inventario, ver reportes |
| **waiter** | uuid-role-waiter | Mesero con acceso a pedidos y mesas | Gestionar pedidos, ver mesas |

---

## ⚙️ Variables de Entorno

Asegúrate de configurar las siguientes variables en tu archivo `.env`:

```env
# Database
TURSO_DATABASE_URL=libsql://...
TURSO_AUTH_TOKEN=...

# Application
ENVIRONMENT=development

# JWT Configuration
JWT_SECRET_KEY=tu-clave-secreta-muy-segura-de-al-menos-32-caracteres
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

**⚠️ Importante**: 
- En producción, `JWT_SECRET_KEY` es **obligatorio**
- Usa una clave segura de al menos 32 caracteres
- Nunca expongas tu `JWT_SECRET_KEY` en el código fuente

---

## 🏗️ Arquitectura Implementada

El sistema está construido siguiendo **Domain-Driven Design (DDD)** y **Clean Architecture**:

```
src/modules/User/
├── domain/                 # Capa de dominio (lógica de negocio)
│   ├── entities/          # User, Role
│   ├── value_objects/     # Email, Password
│   └── services/          # PasswordService, AuthService
│
├── application/           # Capa de aplicación (casos de uso)
│   ├── usecases/         # RegisterUser, LoginUser
│   └── dto/              # RegisterRequest, LoginRequest, UserResponse, AuthResponse
│
└── infrastructure/        # Capa de infraestructura (detalles técnicos)
    ├── repositories/     # UserRepository, RoleRepository, LoginAttemptRepository
    └── api/              # auth_router (endpoints FastAPI)
```

---

## ✨ Características Implementadas

- ✅ Registro de usuarios con validaciones robustas
- ✅ Login con JWT (JSON Web Tokens)
- ✅ Hash de contraseñas con bcrypt
- ✅ Bloqueo automático tras 5 intentos fallidos (15 minutos)
- ✅ Registro de auditoría de intentos de login
- ✅ Validación de fortaleza de contraseñas
- ✅ Validación de emails
- ✅ Sistema de roles (admin, employee, waiter)
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Arquitectura limpia y escalable (DDD)
- ✅ Comentarios descriptivos en español
- ✅ Manejo profesional de errores

---

## 📱 Acceder a la Documentación

Una vez que el servidor esté ejecutándose, visita:

- **Swagger UI (recomendado)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Desde ahí podrás:
- Ver todos los endpoints disponibles
- Probar las peticiones directamente desde el navegador
- Ver ejemplos de requests y responses
- Ver los esquemas de datos (DTOs)

---

¡El sistema de autenticación está completamente implementado y listo para usar! 🎉
