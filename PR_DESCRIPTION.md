# Pull Request: Sistema de Autenticación Completo

## 📋 Descripción

Implementación completa del sistema de autenticación para KitchAI siguiendo todos los criterios de aceptación y mejores prácticas profesionales.

## ✨ Características Implementadas

### Módulo de Autenticación
- ✅ Endpoint `POST /api/auth/register` - Registro de usuarios
- ✅ Endpoint `POST /api/auth/login` - Inicio de sesión con JWT
- ✅ Sistema de roles: admin, employee, waiter
- ✅ Validaciones robustas de entrada
- ✅ Documentación automática con Swagger/OpenAPI

### Seguridad
- ✅ **CA1**: Endpoint de registro con todos los campos requeridos
- ✅ **CA2**: Contraseñas hasheadas con bcrypt (factor 12) - NUNCA en texto plano
- ✅ **CA3**: Bloqueo automático tras 5 intentos fallidos (15 min) - Error 429
- ✅ **CA4**: API completamente documentada en `/docs` y `/redoc`

### Validaciones de Contraseña
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial

### Protección contra Ataques
- ✅ Brute Force Protection (bloqueo tras 5 intentos)
- ✅ Rate Limiting con código 429
- ✅ Auditoría de intentos de login (tabla `login_attempts`)
- ✅ Validación estricta con Pydantic

## 🏗️ Arquitectura

Implementada con **Domain-Driven Design (DDD)** y **Clean Architecture**:

```
src/modules/User/
├── domain/              # Lógica de negocio pura
│   ├── entities/        # User, Role
│   ├── value_objects/   # Email, Password
│   └── services/        # PasswordService, AuthService
├── application/         # Casos de uso
│   ├── usecases/       # RegisterUser, LoginUser
│   └── dto/            # DTOs para API
└── infrastructure/      # Detalles técnicos
    ├── repositories/   # UserRepository, RoleRepository, LoginAttemptRepository
    └── api/            # auth_router (FastAPI endpoints)
```

## 📁 Archivos Principales

### Nuevos Archivos Creados
- `src/modules/User/domain/entities/user.py` - Entidad User con lógica de negocio
- `src/modules/User/domain/entities/role.py` - Entidad Role
- `src/modules/User/domain/value_objects/email.py` - Validación de email
- `src/modules/User/domain/value_objects/password.py` - Validación de contraseña
- `src/modules/User/domain/services/password_service.py` - Hash con bcrypt
- `src/modules/User/domain/services/auth_service.py` - Generación de JWT
- `src/modules/User/application/usecases/register_user.py` - Caso de uso: Registro
- `src/modules/User/application/usecases/login_user.py` - Caso de uso: Login
- `src/modules/User/application/dto/` - DTOs (RegisterRequest, LoginRequest, UserResponse, AuthResponse)
- `src/modules/User/infrastructure/repositories/` - Repositorios (User, Role, LoginAttempt)
- `src/modules/User/infrastructure/api/auth_router.py` - Endpoints FastAPI
- `docs/API_AUTH_GUIDE.md` - Guía completa de uso de la API
- `docs/README_AUTH.md` - README del sistema
- `IMPLEMENTATION_SUMMARY.md` - Resumen de implementación
- `test_auth_simple.ps1` - Script de pruebas automatizado

### Archivos Modificados
- `main.py` - Configuración de FastAPI con Swagger mejorado
- `src/shared/infrastructure/config/settings.py` - Configuración JWT
- `pyproject.toml` - Nuevas dependencias (bcrypt, pyjwt)
- `.env.example` - Variables de entorno actualizadas

## 🧪 Testing

### Pruebas Automatizadas
```powershell
.\test_auth_simple.ps1
```

**Resultados:**
```
✅ [TEST 1] Servidor verificado
✅ [TEST 2] Usuario registrado exitosamente
✅ [TEST 3] Login exitoso con JWT
✅ [TEST 4] Bloqueo en intento 5 (Error 429)
✅ [TEST 5] Validación de email duplicado
```

### Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Cambios Estadísticos

- **Archivos nuevos**: 30+
- **Líneas de código**: 2000+
- **Cobertura de CAs**: 100%
- **Principios aplicados**: SOLID, DDD, Clean Architecture

## 🔐 Variables de Entorno Requeridas

```env
# Añadir al archivo .env
JWT_SECRET_KEY=tu-clave-secreta-de-al-menos-32-caracteres
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

## ✅ Criterios de Aceptación

- [x] **CA1**: Endpoint POST /api/auth/register implementado y funcionando
- [x] **CA2**: Contraseñas hasheadas con bcrypt (NUNCA en texto plano)
- [x] **CA3**: Bloqueo tras 5 intentos fallidos con código 429
- [x] **CA4**: API completamente documentada con Swagger/OpenAPI

## 🚀 Cómo Probar

1. **Instalar dependencias**:
   ```bash
   uv sync
   ```

2. **Configurar .env**:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

3. **Iniciar servidor**:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn main:app --reload
   ```

4. **Ejecutar pruebas**:
   ```powershell
   .\test_auth_simple.ps1
   ```

5. **Acceder a documentación**:
   - http://localhost:8000/docs

## 📝 Notas Adicionales

- Todo el código está comentado en español siguiendo estándares profesionales
- Se aplicaron principios SOLID y Clean Architecture
- El sistema es completamente escalable y fácil de mantener
- Incluye manejo robusto de errores y validaciones exhaustivas
- Sistema de auditoría implementado para seguridad

## 🎯 Impacto

Este PR introduce el sistema de autenticación completo que permite:
- Registro seguro de usuarios (admin, employee, waiter)
- Login con JWT para autenticación en toda la API
- Protección contra ataques de fuerza bruta
- Base sólida para el desarrollo de los demás módulos del sistema

---

**Tipo de cambio**: ⭐ Feature (Nueva funcionalidad)  
**Prioridad**: 🔴 Alta  
**Breaking changes**: ❌ No

cc: @Migueloxs
