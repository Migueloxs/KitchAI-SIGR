from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from src.shared.infrastructure.database.turso_connection import turso_db
from src.modules.User.infrastructure.api.auth_router import router as auth_router

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
            "name": "Salud",
            "description": "Endpoints para verificar el estado del sistema"
        }
    ]
)

# Incluir routers de módulos
app.include_router(auth_router)


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    print("🚀 Iniciando KitchAI...")
    # La conexión ya se inicializa automáticamente con el import


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
