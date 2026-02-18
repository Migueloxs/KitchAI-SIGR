"""
Servicio de dominio PasswordService.
Maneja el hashing y verificación de contraseñas usando bcrypt.
"""
import bcrypt


class PasswordService:
    """
    Servicio para manejar el hashing y verificación de contraseñas.
    Utiliza bcrypt para garantizar seguridad en el almacenamiento.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generar un hash seguro de una contraseña.
        Utiliza bcrypt con un factor de trabajo de 12 (recomendado).
        
        Args:
            password: Contraseña en texto plano
        
        Returns:
            Hash de la contraseña en formato string
        
        Example:
            >>> hashed = PasswordService.hash_password("MiPassword123!")
            >>> print(hashed)  # $2b$12$...
        """
        # Convertir la contraseña a bytes
        password_bytes = password.encode('utf-8')
        
        # Generar el salt y crear el hash
        # El factor de trabajo 12 es un balance entre seguridad y rendimiento
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Retornar como string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verificar si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano a verificar
            hashed_password: Hash almacenado en la base de datos
        
        Returns:
            True si la contraseña es correcta, False en caso contrario
        
        Example:
            >>> hashed = PasswordService.hash_password("MiPassword123!")
            >>> PasswordService.verify_password("MiPassword123!", hashed)
            True
            >>> PasswordService.verify_password("OtraPassword", hashed)
            False
        """
        try:
            # Convertir ambos a bytes
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            # Verificar la contraseña
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            # Si hay algún error en la verificación, retornar False
            print(f"Error al verificar contraseña: {str(e)}")
            return False
