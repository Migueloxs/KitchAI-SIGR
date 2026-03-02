# 🍴 KitchAI - Sistema Integral de Gestión de Restaurantes (SIGR)

Sistema completo de gestión para restaurantes con autenticación segura, gestión de usuarios, inventario, pedidos y más.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API](#-api)
- [Arquitectura](#-arquitectura)
- [Criterios de Aceptación](#-criterios-de-aceptación)
- [Testing](#-testing)

## ✨ Características

### Módulo de Autenticación ✅

- ✅ **Registro de usuarios** con validaciones robustas
- ✅ **Login seguro** con JWT (JSON Web Tokens)
- ✅ **Hash de contraseñas** con bcrypt (factor 12)
- ✅ **Bloqueo automático** tras 5 intentos fallidos (15 minutos)
- ✅ **Registro de auditoría** de intentos de login
- ✅ **Sistema de roles**: admin, employee, waiter
- ✅ **Validación de fortaleza** de contraseñas
- ✅ **Documentación automática** con Swagger/OpenAPI

### Seguridad Implementada 🔒

- **CA1**: Endpoint POST `/api/auth/register` con todos los campos requeridos
- **CA2**: Contraseñas hasheadas con bcrypt (NUNCA en texto plano)
- **CA3**: Bloqueo tras 5 intentos fallidos, retorna error 429
- **CA4**: API completamente documentada en `/docs` con ejemplos

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Python 3.13+** - Lenguaje de programación
- **Turso DB (LibSQL)** - Base de datos SQLite distribuida
- **bcrypt** - Hash seguro de contraseñas
- **PyJWT** - JSON Web Tokens
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI
- **uv** - Gestor de paquetes ultra-rápido

## 📦 Instalación

### Requisitos Previos

- Python 3.13 o superior
- uv (gestor de paquetes)
- Cuenta en Turso DB

### Pasos de Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repo>
cd KitchAI-SIGR
```

2. **Instalar dependencias**:
```bash
uv sync
```

3. **Configurar variables de entorno**:

Crea un archivo `.env` en la raíz del proyecto:

```env
# Database
TURSO_DATABASE_URL=libsql://tu-base-de-datos.turso.io
TURSO_AUTH_TOKEN=tu-token-de-autenticacion

# Application
ENVIRONMENT=development

# JWT Configuration
JWT_SECRET_KEY=tu-clave-secreta-muy-segura-de-al-menos-32-caracteres
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

4. **Crear las tablas de la base de datos**:

Ejecuta el script SQL ubicado en `docs/TURSO_DB_SETUP.md` en tu base de datos Turso.

## 🚀 Uso

### Iniciar el Servidor

#### Opción 1: Con uv (recomendado en producción)
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Opción 2: Con Python del virtual environment
```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Opción 3: Modo desarrollo con hot-reload
```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

El servidor estará disponible en: **http://localhost:8000**

### Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API

### Endpoints de Autenticación

#### POST `/api/auth/register`

Registra un nuevo usuario en el sistema. Si no se incluye el campo `role`, el
usuario recibirá automáticamente el rol **waiter** por defecto.

**Request Body**:
```json
{
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+1829555-1234",
  "password": "SecurePass123!"
  # "role" es opcional; si se omite se utiliza "waiter"
}
```

**Response (201)**:
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

#### POST `/api/auth/login`

Autentica un usuario y retorna un token JWT.

**Request Body**:
```json
{
  "email": "juan.perez@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

**Ver documentación completa**: [API_AUTH_GUIDE.md](docs/API_AUTH_GUIDE.md)

## 🏗️ Arquitectura

El proyecto sigue **Domain-Driven Design (DDD)** y **Clean Architecture**:

```
src/
├── modules/
│   └── User/
│       ├── domain/              # Capa de Dominio (Lógica de Negocio)
│       │   ├── entities/        # User, Role
│       │   ├── value_objects/   # Email, Password
│       │   └── services/        # PasswordService, AuthService
│       │
│       ├── application/         # Capa de Aplicación (Casos de Uso)
│       │   ├── usecases/       # RegisterUser, LoginUser
│       │   └── dto/            # DTOs (Request/Response)
│       │
│       └── infrastructure/      # Capa de Infraestructura
│           ├── repositories/   # Acceso a datos
│           └── api/            # Endpoints HTTP
│
└── shared/
    └── infrastructure/
        ├── config/             # Configuración global
        └── database/           # Conexión a BD
```

### Capas de la Arquitectura

1. **Dominio**: Entidades, Value Objects, Servicios de Dominio
   - Lógica de negocio pura
   - Sin dependencias externas
   - Reglas de validación

2. **Aplicación**: Casos de Uso, DTOs
   - Orquesta la lógica de dominio
   - Define contratos de entrada/salida
   - Coordina repositorios y servicios

3. **Infraestructura**: Repositorios, APIs, Configuración
   - Implementaciones concretas
   - Acceso a base de datos
   - Endpoints HTTP

### Principios Aplicados

- ✅ **SOLID**: Principios de diseño orientado a objetos
- ✅ **DDD**: Domain-Driven Design
- ✅ **Clean Architecture**: Separación de capas
- ✅ **Repository Pattern**: Abstracción de acceso a datos
- ✅ **Dependency Injection**: Desacoplamiento de componentes

## ✅ Criterios de Aceptación

### CA1: Endpoint de Registro ✅

```
✅ Existe POST /api/auth/register
✅ Acepta: name, email, phone, password, role
✅ Retorna código 201
✅ Retorna datos del usuario (SIN contraseña)
```

### CA2: Hash Seguro de Contraseñas ✅

```
✅ Contraseñas hasheadas con bcrypt (factor 12)
✅ NUNCA almacenadas en texto plano
✅ Verificación segura con bcrypt.checkpw
```

### CA3: Bloqueo por Intentos Fallidos ✅

```
✅ Contador de intentos fallidos
✅ Bloqueo tras 5 intentos consecutivos
✅ Duración del bloqueo: 15 minutos
✅ Retorna código 429 (Too Many Requests)
✅ Registro de auditoría de intentos
```

### CA4: Documentación de API ✅

```
✅ Swagger UI en /docs
✅ ReDoc en /redoc
✅ Ejemplos de requests y responses
✅ Descripciones detalladas
✅ Esquemas de validación documentados
```

## 🧪 Testing

### Prueba Manual con Script

Ejecuta el script de prueba automatizado:

```powershell
.\test_auth_api.ps1
```

Este script probará:
- ✅ Registro de usuario
- ✅ Login exitoso
- ✅ Bloqueo por intentos fallidos
- ✅ Validación de email duplicado
- ✅ Validación de contraseña débil

### Prueba Manual con cURL

#### Registrar Usuario
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+18299991234",
    "password": "TestPass123!",
    "role": "waiter"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Prueba con Swagger UI

1. Abre http://localhost:8000/docs
2. Expande el endpoint deseado
3. Haz clic en "Try it out"
4. Ingresa los datos de ejemplo
5. Haz clic en "Execute"

## 📊 Base de Datos

### Tablas Implementadas

- **users**: Usuarios del sistema
- **roles**: Roles (admin, employee, waiter)
- **permissions**: Permisos del sistema
- **role_permissions**: Relación roles-permisos
- **login_attempts**: Auditoría de intentos de login
- **jwt_blacklist**: Tokens revocados

### Diagrama de Relaciones

```
users ─────┐
           │
           ├─── roles ─── role_permissions ─── permissions
           │
           └─── login_attempts
```

## 🔐 Seguridad

### Autenticación

- JWT (JSON Web Tokens) con expiración configurable
- Tokens firmados con HS256
- Incluye información del usuario y rol

### Contraseñas

- Hash con bcrypt (factor 12)
- Validación de fortaleza:
  - Mínimo 8 caracteres
  - Mayúsculas, minúsculas, números, caracteres especiales

### Protección contra Ataques

- ✅ Bloqueo tras intentos fallidos (Brute Force Protection)
- ✅ Auditoría de intentos de login
- ✅ Tokens con expiración
- ✅ Validación de datos de entrada (Pydantic)

## 📝 Variables de Entorno

| Variable | Descripción | Requerida | Default |
|----------|-------------|-----------|---------|
| `TURSO_DATABASE_URL` | URL de conexión a Turso DB | ✅ Sí | - |
| `TURSO_AUTH_TOKEN` | Token de autenticación de Turso | ✅ Sí | - |
| `ENVIRONMENT` | Entorno (development/production) | ❌ No | development |
| `JWT_SECRET_KEY` | Clave secreta para JWT | ⚠️ Producción | (temporal en dev) |
| `JWT_ALGORITHM` | Algoritmo de firma JWT | ❌ No | HS256 |
| `JWT_EXPIRATION_MINUTES` | Tiempo de expiración del token | ❌ No | 60 |

## 📚 Documentación Adicional

- [Guía de API de Autenticación](docs/API_AUTH_GUIDE.md)
- [Setup de Base de Datos Turso](docs/TURSO_DB_SETUP.md)

## 🤝 Contribución

Este proyecto fue desarrollado siguiendo las mejores prácticas de desarrollo de software:

- ✅ Código limpio y documentado
- ✅ Arquitectura escalable
- ✅ Comentarios descriptivos en español
- ✅ Manejo profesional de errores
- ✅ Validaciones robustas
- ✅ Seguridad como prioridad

## 📄 Licencia

MIT License

---

**Desarrollado con ❤️ por el equipo de KitchAI**
