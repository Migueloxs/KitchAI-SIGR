from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from src.shared.infrastructure.database.turso_connection import turso_db

app = FastAPI(title="KitchAI")


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


@app.get("/health", response_class=JSONResponse)
def health_check():
    """Endpoint para verificar el estado de la aplicación y la conexión a la base de datos."""
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
