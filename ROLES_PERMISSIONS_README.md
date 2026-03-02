# KitchAI - Gestión de Roles y Permisos 📋

## 🎯 Quick Start

Este documento guía a través de la implementación completa de **Gestión de Roles y Permisos** para KitchAI-SIGR.

### Estado: ✅ COMPLETADO

---

## 📖 Documentación Disponible

### 1. **IMPLEMENTATION_SUMMARY.md** ⭐ [COMIENZA AQUÍ]
   - Resumen ejecutivo de cambios
   - Archivos creados y modificados
   - Criterios de aceptación cumplidos
   - [Lee esto primero para entender qué se hizo]

### 2. **ROLES_PERMISSIONS_GUIDE.md** [REFERENCIA TÉCNICA]
   - Detalles de cada endpoint
   - Ejemplos de cURL y PowerShell
   - Estructura de datos (ER)
   - Flujos de trabajo paso a paso
   - [Consulta esto para trabajar con los endpoints]

### 3. **API_AUTH_GUIDE.md** [AUTENTICACIÓN]
   - Endpoints de login/registro
   - Cómo omitir el campo 'role' para obtener 'waiter' por defecto
   - [Necesario para entender el flujo completo]

### 4. **README_AUTH.md**
   - Información general del módulo de autenticación
   - Arquitectura del proyecto
   - [Contexto del proyecto general]

---

## 🚀 Para Iniciar el Servidor

```bash
# Activar virtual environment
.venv\Scripts\Activate.ps1

# Instalar dependencias (si es necesario)
pip install -e .

# Iniciar servidor
python -m uvicorn main:app --reload

# El servidor estará en: http://localhost:8000
```

---

## 🧪 Para Ejecutar Pruebas

### Test Completo de Roles y Permisos
```powershell
# En otra terminal PowerShell:
.\test_roles_permissions.ps1
```

**Prueba:**
- [x] Lista de roles
- [x] Lista de permisos
- [x] Permisos por rol
- [x] Registrar sin rol (obtiene 'waiter')
- [x] Cambiar rol de usuario

### Tests de Autenticación
```powershell
.\test_auth_api.ps1        # Test completo
.\test_auth_simple.ps1     # Test simple
```

---

## 📋 Criterios de Aceptación

### CA1: Tabla Roles ✅
```
✅ Tabla 'roles' con 3 roles:
   - admin (administrador)
   - employee (empleado)
   - waiter (mesero)
```

### CA2: Tabla role_permissions ✅
```
✅ Tabla 'role_permissions' vincula roles y permisos
✅ Cada rol tiene permisos específicos asignados
```

### CA3: Rol por Defecto ✅
```
✅ Al registrar usuario sin especificar 'role'
✅ Se asigna automáticamente 'waiter'
✅ El campo 'role' es OPCIONAL en POST /api/auth/register
```

---

## 💻 Endpoints Principales

### Autenticación & Usuarios

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/register` | POST | Registrar usuario (role opcional, default: waiter) |
| `/api/auth/login` | POST | Iniciar sesión |

### Roles & Permisos

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/roles/` | GET | Listar todos los roles |
| `/api/roles/permissions/` | GET | Listar todos los permisos |
| `/api/roles/{role_id}/permissions` | GET | Obtener permisos de un rol |
| `/api/roles/users/{user_id}/role` | PUT | Cambiar rol de un usuario |

---

## 📝 Ejemplo: Flujo Completo

### Paso 1: Registrar Usuario sin Rol
```bash
POST /api/auth/register

{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "phone": "+18299991234",
  "password": "SecurePass123!"
  # role OMITIDO → obtiene 'waiter'
}

Response: role_id = uuid-role-waiter
```

### Paso 2: Cambiar Rol a Admin
```bash
PUT /api/roles/users/{user_id}/role

{
  "role": "admin"
}

Response: role_id = uuid-role-admin
```

### Paso 3: Ver Permisos del Nuevo Rol
```bash
GET /api/roles/uuid-role-admin/permissions

Response: [manage_users, manage_inventory, view_reports, manage_orders, view_tables]
```

---

## 🗂️ Estructura de Archivos Principales

```
src/modules/User/
├── domain/entities/
│   ├── permission.py  ← NUEVO
│   ├── role.py
│   └── user.py
├── application/
│   ├── usecases/
│   │   ├── update_user_role.py  ← NUEVO
│   │   ├── register_user.py     (modificado)
│   │   └── login_user.py
│   └── dto/
│       ├── change_role_request.py      ← NUEVO
│       ├── permission_response.py      ← NUEVO
│       ├── register_request.py         (modificado)
│       ├── user_response.py
│       └── auth_response.py
├── infrastructure/
│   ├── repositories/
│   │   ├── permission_repository.py    ← NUEVO
│   │   ├── user_repository.py
│   │   └── role_repository.py
│   └── api/
│       ├── roles_router.py             ← NUEVO
│       └── auth_router.py              (modificado)

docs/
├── ROLES_PERMISSIONS_GUIDE.md          ← NUEVO
├── API_AUTH_GUIDE.md                   (modificado)
├── README_AUTH.md
└── TURSO_DB_SETUP.md

test_roles_permissions.ps1              ← NUEVO (test script)
```

---

## 🔍 Verificación Rápida

### Check 1: ¿Están las tablas creadas?
```bash
# Al iniciar el servidor, en los logs debe aparecer:
# ✅ Roles por defecto verificados/creados
# ✅ Permisos por defecto verificados/creados
# ✅ Asociaciones rol-permiso creadas
```

### Check 2: ¿Puedo listar roles?
```bash
curl http://localhost:8000/api/roles/
# Debe retornar 3 roles
```

### Check 3: ¿Se asigna rol por defecto?
```powershell
# Registra sin rol y verifica que role_id = uuid-role-waiter
```

---

## 🛠️ Troubleshooting

### Problema: "Error al conectar a la BD"
**Solución:** Verificar que la BD Turso esté funcionando y las credenciales en `.env` sean correctas.

### Problema: "Tabla roles no existe"
**Solución:** Reiniciar el servidor. La tabla se crea automáticamente en `startup_event()`.

### Problema: "Rol no encontrado"
**Solución:** Asegúrate de usar exactamente: `admin`, `employee`, o `waiter` (minúsculas).

---

## 📞 Información de Contacto

- **Equipo**: KitchAI Backend Dev
- **Fecha**: Febrero 17, 2026
- **Estado**: ✅ Completado y Testeado
- **Documentación**: Completa

---

## 🎓 Aprendizajes Clave

1. **Pydantic y Valores por Defecto**: El campo `role` en `RegisterRequest` usa `Field('waiter')` para asignar automáticamente el valor.

2. **Inicialización en Startup**: Los roles y permisos se crean en `main.py::startup_event()` para garantizar consistencia.

3. **Tabla Relacional**: `role_permissions` mantiene la relación M:N entre roles y permisos sin duplicados.

4. **DTOs Específicos**: Se usaron `ChangeRoleRequest` y `RolePermissionsResponse` para cada caso de uso específico.

---

## 📖 Referencias Externas

- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Turso DB: https://turso.tech/
- SQLite: https://www.sqlite.org/

---

**Última actualización: 17-02-2026**
**Status: ✅ PRODUCTION READY**
