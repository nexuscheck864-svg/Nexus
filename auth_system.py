
import hashlib
import hmac
import time
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

class TokenAuthSystem:
    def __init__(self):
        self.session_tokens: Dict[str, dict] = {}
        self.auth_attempts: Dict[str, list] = {}
        self.secret_key = secrets.token_hex(32)
    
    def generate_session_token(self, user_id: str, permissions: list) -> str:
        """Generar token de sesión con permisos específicos"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=2)
        
        self.session_tokens[token] = {
            'user_id': user_id,
            'permissions': permissions,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        return token
    
    def verify_token(self, token: str, required_permission: str) -> tuple[bool, str]:
        """Verificar token y permisos"""
        if token not in self.session_tokens:
            return False, "Token inválido"
        
        session = self.session_tokens[token]
        
        if datetime.now() > session['expires_at']:
            del self.session_tokens[token]
            return False, "Token expirado"
        
        if required_permission not in session['permissions']:
            return False, "Permisos insuficientes"
        
        return True, session['user_id']
    
    def rate_limit_check(self, user_id: str, max_attempts: int = 5) -> bool:
        """Control de rate limiting para autenticación"""
        now = time.time()
        
        if user_id not in self.auth_attempts:
            self.auth_attempts[user_id] = []
        
        # Limpiar intentos antiguos (últimos 15 minutos)
        self.auth_attempts[user_id] = [
            attempt for attempt in self.auth_attempts[user_id]
            if now - attempt < 900
        ]
        
        if len(self.auth_attempts[user_id]) >= max_attempts:
            return False
        
        self.auth_attempts[user_id].append(now)
        return True
    
    def revoke_token(self, token: str):
        """Revocar token específico"""
        if token in self.session_tokens:
            del self.session_tokens[token]
    
    def cleanup_expired_tokens(self):
        """Limpiar tokens expirados"""
        now = datetime.now()
        expired_tokens = [
            token for token, session in self.session_tokens.items()
            if now > session['expires_at']
        ]
        for token in expired_tokens:
            del self.session_tokens[token]
