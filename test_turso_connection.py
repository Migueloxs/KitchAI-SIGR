"""
Script de ejemplo para probar la conexión a Turso DB.
Este script crea una tabla de ejemplo y realiza operaciones básicas.
"""
from src.shared.infrastructure.database.turso_connection import get_turso_client


def main():
    """Función principal para probar la conexión."""
    print("🔌 Conectando a Turso DB...\n")
    
    try:
        # Obtener el cliente
        client = get_turso_client()
        
        # 1. Crear tabla de ejemplo (si no existe)
        print("📋 Creando tabla 'users_example'...")
        client.execute("""
            CREATE TABLE IF NOT EXISTS users_example (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla creada o ya existe\n")
        
        # 2. Insertar datos de ejemplo
        print("➕ Insertando usuarios de ejemplo...")
        users_to_insert = [
            ("Juan Pérez", "juan@example.com"),
            ("María García", "maria@example.com"),
            ("Carlos López", "carlos@example.com")
        ]
        
        for name, email in users_to_insert:
            try:
                client.execute(
                    "INSERT INTO users_example (name, email) VALUES (?, ?)",
                    [name, email]
                )
                print(f"  ✓ Usuario agregado: {name}")
            except Exception as e:
                # Si el usuario ya existe (email único), ignorar
                if "UNIQUE constraint" in str(e):
                    print(f"  ⚠️  Usuario ya existe: {name}")
                else:
                    raise
        
        print()
        
        # 3. Consultar todos los usuarios
        print("🔍 Consultando todos los usuarios...")
        result = client.execute("SELECT * FROM users_example")
        
        print(f"\n📊 Total de usuarios: {len(result.rows)}\n")
        print("ID | Nombre          | Email")
        print("-" * 50)
        for row in result.rows:
            print(f"{row['id']:<3}| {row['name']:<16}| {row['email']}")
        
        print("\n" + "=" * 50)
        
        # 4. Buscar un usuario específico
        print("\n🔎 Buscando usuario con ID = 1...")
        result = client.execute(
            "SELECT * FROM users_example WHERE id = ?",
            [1]
        )
        
        if result.rows:
            user = result.rows[0]
            print(f"✅ Usuario encontrado:")
            print(f"   Nombre: {user['name']}")
            print(f"   Email: {user['email']}")
            print(f"   Creado: {user['created_at']}")
        else:
            print("❌ Usuario no encontrado")
        
        print("\n✨ ¡Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
