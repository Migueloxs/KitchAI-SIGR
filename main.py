from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from src.shared.infrastructure.database.turso_connection import turso_db
from src.modules.User.infrastructure.api.auth_router import router as auth_router
from src.modules.User.infrastructure.api.roles_router import router as roles_router
from src.modules.Order.infrastructure.api.order_router import order_router

# Configuración de la aplicación con metadata para Swagger/OpenAPI
app = FastAPI(
    title="KitchAI - Sistema de Gestión Integral para Restaurantes",
    description="""
    ## KitchAI SIGR (Sistema Integral de Gestión de Restaurantes)
    
    API REST para la gestión completa de un restaurante, incluyendo:
    
    * **Autenticación y Usuarios**: Registro, login y gestión de usuarios con diferentes roles
    * **Gestión de Inventario**: Control de productos y existencias
    * **Gestión de Pedidos**: Administración de órdenes y comandas
    * **Gestión de Mesas**: Control de mesas y asignaciones
    * **Reportes**: Generación de informes y estadísticas
    
    ### Autenticación
    
    La API utiliza JWT (JSON Web Tokens) para autenticación. Para acceder a endpoints protegidos:
    
    1. Registra un usuario con `POST /api/auth/register`
    2. Inicia sesión con `POST /api/auth/login` para obtener un token
    3. Incluye el token en el header: `Authorization: Bearer {token}`
    
    ### Roles de Usuario
    
    - **admin**: Acceso total al sistema
    - **employee**: Gestión de inventario y reportes
    - **waiter**: Gestión de pedidos y mesas
    
    ### Seguridad
    
    - ✅ Contraseñas hasheadas con bcrypt
    - ✅ Tokens JWT con expiración configurable
    - ✅ Bloqueo automático tras 5 intentos fallidos (15 minutos)
    - ✅ Registro de auditoría de intentos de login
    """,
    version="1.0.0",
    contact={
        "name": "Equipo KitchAI",
        "email": "soporte@kitchai.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_tags=[
        {
            "name": "Autenticación",
            "description": "Operaciones de registro, login y gestión de sesiones"
        },
        {
            "name": "Roles y Permisos",
            "description": "Gestión de roles, permisos y asignación de roles a usuarios"
        },
        {
            "name": "Salud",
            "description": "Endpoints para verificar el estado del sistema"
        }
    ]
)

# Incluir routers de módulos
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(order_router)


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    print("🚀 Iniciando KitchAI...")
    # La conexión ya se inicializa automáticamente con el import
    # Asegurar que los roles básicos existan en la base de datos.
    try:
        # el método execute de turso_db permite SQL directa
        turso_db.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # insertar roles con INSERT OR IGNORE para no duplicar
        defaults = [
            ('uuid-role-admin', 'admin', 'Administrador con acceso total'),
            ('uuid-role-employee', 'employee', 'Empleado con acceso a inventario y reportes'),
            ('uuid-role-waiter', 'waiter', 'Mesero con acceso a pedidos y mesas')
        ]
        for rid, name, desc in defaults:
            turso_db.execute(
                "INSERT OR IGNORE INTO roles (id, name, description) VALUES (?, ?, ?)",
                [rid, name, desc]
            )
        print("✅ Roles por defecto verificados/creados")

        # Asegurarse de que existan las tablas de permisos y relaciones
        turso_db.execute(
            """
            CREATE TABLE IF NOT EXISTS permissions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        turso_db.execute(
            """
            CREATE TABLE IF NOT EXISTS role_permissions (
                id TEXT PRIMARY KEY,
                role_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(role_id, permission_id)
            )
            """
        )

        # Cargar permisos básicos si faltan
        perm_defaults = [
            ('perm-1', 'manage_users', 'Gestionar usuarios'),
            ('perm-2', 'manage_inventory', 'Gestionar inventario'),
            ('perm-3', 'view_reports', 'Ver reportes'),
            ('perm-4', 'manage_orders', 'Gestionar pedidos'),
            ('perm-5', 'view_tables', 'Ver mesas')
        ]
        for pid, pname, pdesc in perm_defaults:
            turso_db.execute(
                "INSERT OR IGNORE INTO permissions (id, name, description) VALUES (?, ?, ?)",
                [pid, pname, pdesc]
            )
        print("✅ Permisos por defecto verificados/creados")

        # relaciones por defecto entre roles y permisos
        rp_defaults = [
            ('rp-1', 'uuid-role-admin', 'perm-1'),
            ('rp-2', 'uuid-role-admin', 'perm-2'),
            ('rp-3', 'uuid-role-admin', 'perm-3'),
            ('rp-4', 'uuid-role-admin', 'perm-4'),
            ('rp-5', 'uuid-role-admin', 'perm-5'),
            ('rp-6', 'uuid-role-employee', 'perm-2'),
            ('rp-7', 'uuid-role-employee', 'perm-3'),
            ('rp-8', 'uuid-role-waiter', 'perm-4'),
            ('rp-9', 'uuid-role-waiter', 'perm-5')
        ]
        for rid, roleid, permid in rp_defaults:
            turso_db.execute(
                "INSERT OR IGNORE INTO role_permissions (id, role_id, permission_id) VALUES (?, ?, ?)",
                [rid, roleid, permid]
            )
        print("✅ Asociaciones rol-permiso creadas")
    except Exception as e:
        print(f"⚠️  Error al inicializar roles: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación."""
    print("👋 Cerrando KitchAI...")
    turso_db.close()


@app.get("/", response_class=HTMLResponse)
def kitchai():
    return """
    <html>
        <head>
            <title>KitchAI</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #1e1e2f, #2b5876);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .box {
                    text-align: center;
                    padding: 40px;
                    border-radius: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    box-shadow: 0 0 20px rgba(0,0,0,0.4);
                }
                h1 {
                    font-size: 3em;
                }
                p {
                    font-size: 1.2em;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>KitchAI</h1>
                <p>La forma inteligente de gestionar tu restaurante.</p>
                <p>Powered by FastAPI</p>
            </div>
        </body>
    </html>
    """


@app.get("/health", response_class=JSONResponse, tags=["Salud"])
def health_check():
    """
    Endpoint de health check para verificar el estado del sistema.
    
    Verifica:
    - Estado de la aplicación
    - Conexión a la base de datos Turso
    
    Returns:
        Estado del sistema y sus componentes
    """
    try:
        # Verificar conexión a la base de datos
        result = turso_db.execute("SELECT 1 as health_check")
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "KitchAI está funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
