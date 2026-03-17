# KitchAI - Sistema Inteligente de Gestión de Restaurantes

Sistema de gestión de restaurantes con backend en FastAPI y frontend en Next.js.

## 🚀 Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **Turso DB**: Base de datos SQLite distribuida (LibSQL)
- **Next.js**: Frontend web con App Router
- **TypeScript**: Tipado estático para el frontend
- **Python 3.13+**
- **UV**: Gestor de paquetes rápido para Python
- **pnpm**: Gestor de paquetes del frontend

## 📁 Estructura del Proyecto

```
KitchAI-SIGR/
├── frontend/                      # Landing page y frontend web en Next.js
│   ├── app/                       # Rutas y paginas
│   ├── components/                # Componentes reutilizables
│   ├── public/                    # Assets estaticos
│   └── package.json               # Dependencias del frontend
├── src/
│   ├── modules/                    # Módulos de dominio
│   │   └── User/                   # Módulo de usuarios
│   │       ├── domain/             # Entidades y reglas de negocio
│   │       ├── application/        # Casos de uso
│   │       └── infrastructure/     # Implementaciones (BD, APIs)
│   └── shared/                     # Código compartido
│       └── infrastructure/
│           ├── config/             # Configuración
│           │   └── settings.py
│           └── database/           # Conexión a BD
│               └── turso_connection.py
├── main.py                         # Punto de entrada de la aplicación
├── .env                            # Variables de entorno (no se sube a git)
├── .env.example                    # Plantilla de variables de entorno
└── pyproject.toml                  # Dependencias del proyecto
```

## Frontend

Para ejecutar la landing page:

```bash
cd frontend
pnpm install
pnpm dev
```

La aplicacion queda disponible en `http://localhost:3000`.

## ⚙️ Configuración

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd KitchAI-SIGR
git checkout develop
```

### 2. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales de Turso:

```env
TURSO_DATABASE_URL=https://your-database.turso.io
TURSO_AUTH_TOKEN=your_actual_token_here
ENVIRONMENT=development
```

### 3. Instalar dependencias

```bash
uv sync
```

### 4. Ejecutar el servidor

```bash
uv run uvicorn main:app --reload
```

O directamente con Python:

```bash
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

La aplicación estará disponible en: http://localhost:8000

## 🔍 Endpoints Disponibles

- `GET /` - Página de bienvenida
- `GET /health` - Verificar estado de la aplicación y base de datos
- `GET /docs` - Documentación interactiva (Swagger)
- `POST /api/inventory/` - Crear artículo de inventario (admin)
- `GET /api/inventory/` - Listar artículos de inventario (admin)
- `GET /api/inventory/alerts` - Listar alertas internas activas (admin)
- `GET /api/inventory/alerts/dashboard` - Dashboard de alertas de inventario (admin)
- `PUT /api/inventory/alerts/{alert_id}/view` - Marcar alerta como vista (admin)
- `PUT /api/inventory/alerts/{alert_id}/resolve` - Marcar alerta como resuelta (admin)
- `POST /api/inventory/alerts/daily-check` - Ejecutar chequeo diario manual de stock mínimo (admin)
- `GET /api/inventory/{item_id}` - Obtener artículo por ID (admin)
- `PUT /api/inventory/{item_id}` - Actualizar artículo (admin)
- `DELETE /api/inventory/{item_id}` - Eliminar artículo (admin)

## 🏗️ Arquitectura Hexagonal

El proyecto sigue los principios de la arquitectura hexagonal (puertos y adaptadores):

### Capas:

1. **Dominio**: Lógica de negocio pura (entidades, interfaces de repositorios)
2. **Aplicación**: Casos de uso que orquestan la lógica
3. **Infraestructura**: Implementaciones concretas (BD, APIs externas, etc.)

### Beneficios:

- ✅ Independencia de frameworks y bases de datos
- ✅ Testeable (fácil crear mocks)
- ✅ Mantenible y escalable
- ✅ Cambios de tecnología sin afectar lógica de negocio

## 📚 Documentación Adicional

- [Configuración de Turso DB](docs/TURSO_DB_SETUP.md) - Guía completa de uso de Turso
- [Gestión de Inventario](docs/INVENTORY_GUIDE.md) - CRUD de inventario, seguridad y migraciones
- [Auto-actualización de inventario tras pedidos](docs/INVENTORY_AUTO_UPDATE_GUIDE.md) - Descuentos automáticos y alertas internas
- [Alertas de stock mínimo y notificaciones](docs/INVENTORY_MIN_STOCK_ALERTS_GUIDE.md) - Dashboard y gestión de alertas vistas/resueltas

## 🧪 Pruebas

Para probar la conexión a Turso DB:

```bash
.\.venv\Scripts\python.exe test_turso_connection.py
```

Para probar CRUD de inventario:

```bash
.\.venv\Scripts\python.exe test_inventory_crud.py
```

Para probar actualización automática tras confirmar pedidos:

```bash
.\.venv\Scripts\python.exe test_inventory_auto_update.py
```

Para probar alertas de stock mínimo, dashboard y estados de alerta:

```bash
.\.venv\Scripts\python.exe test_inventory_min_stock_alerts.py
```

## 🔒 Seguridad

- **NO** subas el archivo `.env` al repositorio
- Las credenciales deben manejarse de forma segura
- Usa `.env.example` solo como plantilla

## 📝 Notas

- Este proyecto usa Python 3.13+
- La base de datos es Turso DB (fork de SQLite)
- Se usa `uv` como gestor de paquetes por su velocidad

## 👥 Equipo

Proyecto Final - ITLA

## 📄 Licencia

[Especificar licencia]
