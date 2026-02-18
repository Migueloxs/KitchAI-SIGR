"""
Servicio de dominio AuthService.
Maneja la lógica de autenticación y generación de tokens JWT.
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict


class AuthService:
    """
    Servicio para manejar la autenticación y tokens JWT.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Inicializar el servicio de autenticación.
        
        Args:
            secret_key: Clave secreta para firmar los tokens JWT
            algorithm: Algoritmo de encriptación (por defecto HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, user_id: str, email: str, role_id: str, 
                       expires_in_minutes: int = 60) -> str:
        """
        Generar un token JWT para un usuario autenticado.
        
        Args:
            user_id: ID del usuario
            email: Email del usuario
            role_id: ID del rol del usuario
            expires_in_minutes: Tiempo de expiración en minutos (por defecto 60)
        
        Returns:
            Token JWT como string
        """
        # Calcular fecha de expiración
        expiration = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        # Payload del token
        payload = {
            "user_id": user_id,
            "email": email,
            "role_id": role_id,
            "exp": expiration,
            "iat": datetime.utcnow()  # Issued at (emitido en)
        }
        
        # Generar y retornar el token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verificar y decodificar un token JWT.
        
        Args:
            token: Token JWT a verificar
        
        Returns:
            Payload del token si es válido, None si no lo es
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
    
    def refresh_token(self, old_token: str, expires_in_minutes: int = 60) -> Optional[str]:
        """
        Renovar un token JWT existente.
        
        Args:
            old_token: Token JWT anterior
            expires_in_minutes: Tiempo de expiración del nuevo token
        
        Returns:
            Nuevo token JWT si el anterior era válido, None en caso contrario
        """
        # Verificar el token anterior
        payload = self.verify_token(old_token)
        
        if payload is None:
            return None
        
        # Generar un nuevo token con los mismos datos
        return self.generate_token(
            user_id=payload["user_id"],
            email=payload["email"],
            role_id=payload["role_id"],
            expires_in_minutes=expires_in_minutes
        )
