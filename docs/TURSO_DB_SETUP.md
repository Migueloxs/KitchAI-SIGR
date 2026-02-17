# Configuración de Turso DB

Este proyecto utiliza Turso DB (LibSQL) como base de datos, siguiendo la arquitectura hexagonal.

## 📦 Estructura

```
src/
└── shared/
    └── infrastructure/
        ├── config/
        │   └── settings.py          # Configuración de variables de entorno
        └── database/
            └── turso_connection.py   # Conexión a Turso DB
```

## 🔧 Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
TURSO_DATABASE_URL=libsql://kitchai-des-arroyo.aws-us-east-2.turso.io
TURSO_AUTH_TOKEN=tu_token_de_autenticacion
ENVIRONMENT=development
```

### 2. Instalación de Dependencias

```bash
uv sync
```

## 🚀 Uso

### Conexión Básica

La conexión a Turso se inicializa automáticamente al importar el módulo:

```python
from src.shared.infrastructure.database.turso_connection import get_turso_client

# Obtener el cliente de Turso
client = get_turso_client()

# Ejecutar una consulta
result = client.execute("SELECT * FROM users")
```

### Uso en Repositorios (Arquitectura Hexagonal)

#### 1. Definir el Repositorio en el Dominio

```python
# src/modules/User/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.modules.User.domain.entities.user import User

class UserRepository(ABC):
    """Interfaz del repositorio de usuarios (Puerto)."""
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass
```

#### 2. Implementar el Repositorio en la Infraestructura

```python
# src/modules/User/infrastructure/user_repository_impl.py
from typing import List, Optional
from src.modules.User.domain.repositories.user_repository import UserRepository
from src.modules.User.domain.entities.user import User
from src.shared.infrastructure.database.turso_connection import get_turso_client

class TursoUserRepository(UserRepository):
    """Implementación del repositorio usando Turso DB (Adaptador)."""
    
    def __init__(self):
        self.client = get_turso_client()
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Buscar usuario por ID."""
        result = self.client.execute(
            "SELECT * FROM users WHERE id = ?",
            [user_id]
        )
        
        if result.rows:
            row = result.rows[0]
            return User(
                id=row["id"],
                name=row["name"],
                email=row["email"]
            )
        return None
    
    def find_all(self) -> List[User]:
        """Obtener todos los usuarios."""
        result = self.client.execute("SELECT * FROM users")
        
        users = []
        for row in result.rows:
            users.append(User(
                id=row["id"],
                name=row["name"],
                email=row["email"]
            ))
        return users
    
    def save(self, user: User) -> User:
        """Guardar o actualizar usuario."""
        if user.id:
            # Actualizar
            self.client.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                [user.name, user.email, user.id]
            )
        else:
            # Insertar
            result = self.client.execute(
                "INSERT INTO users (name, email) VALUES (?, ?) RETURNING id",
                [user.name, user.email]
            )
            user.id = result.rows[0]["id"]
        
        return user
    
    def delete(self, user_id: int) -> bool:
        """Eliminar usuario."""
        self.client.execute(
            "DELETE FROM users WHERE id = ?",
            [user_id]
        )
        return True
```

#### 3. Usar en los Casos de Uso

```python
# src/modules/User/application/usecases/get_user_by_id.py
from typing import Optional
from src.modules.User.domain.entities.user import User
from src.modules.User.domain.repositories.user_repository import UserRepository

class GetUserById:
    """Caso de uso: Obtener usuario por ID."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self, user_id: int) -> Optional[User]:
        """Ejecutar el caso de uso."""
        return self.user_repository.find_by_id(user_id)
```

#### 4. Configurar en FastAPI

```python
# main.py
from fastapi import FastAPI, Depends
from src.modules.User.infrastructure.user_repository_impl import TursoUserRepository
from src.modules.User.application.usecases.get_user_by_id import GetUserById

app = FastAPI(title="KitchAI")

# Dependency Injection
def get_user_repository() -> TursoUserRepository:
    return TursoUserRepository()

def get_user_by_id_usecase(
    repo: TursoUserRepository = Depends(get_user_repository)
) -> GetUserById:
    return GetUserById(repo)

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    usecase: GetUserById = Depends(get_user_by_id_usecase)
):
    user = usecase.execute(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
```

## 🔍 Endpoints de Prueba

### Health Check

Verifica que la aplicación y la conexión a la base de datos estén funcionando:

```
GET http://localhost:8000/health
```

Respuesta exitosa:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "KitchAI está funcionando correctamente"
}
```

## 📚 Arquitectura Hexagonal

La implementación sigue los principios de la arquitectura hexagonal:

1. **Dominio**: Contiene las entidades y las interfaces (puertos) de los repositorios
2. **Aplicación**: Contiene los casos de uso que orquestan la lógica de negocio
3. **Infraestructura**: Contiene las implementaciones (adaptadores) como el repositorio de Turso

### Beneficios

- ✅ Independencia de la base de datos
- ✅ Fácil de testear (mock de repositorios)
- ✅ Cambio de base de datos sin afectar la lógica de negocio
- ✅ Código limpio y mantenible

## 🔒 Seguridad

- ⚠️ El archivo `.env` está en `.gitignore` y no debe subirse al repositorio
- ✅ Usa `.env.example` como plantilla para otros desarrolladores
- 🔐 Las credenciales de Turso deben manejarse de forma segura

## 🛠️ Comandos Útiles

```bash
# Iniciar el servidor
uv run uvicorn main:app --reload

# Instalar dependencias
uv sync

# Actualizar dependencias
uv lock
```

## 📖 Recursos

- [Turso Documentation](https://docs.turso.tech/)
- [LibSQL Client Python](https://github.com/libsql/libsql-client-py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
