
import re
import html
from typing import Any, Dict, List

class InputValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'subprocess',
            r'os\.system',
            r'\.\./',
            r'file://',
            r'ftp://',
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
        ]
        
        self.sql_injection_patterns = [
            r"'.*?(\sor\s|\sand\s).*?'",
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*\s+set',
        ]
    
    def sanitize_input(self, text: str) -> str:
        """Sanitizar entrada de texto"""
        if not isinstance(text, str):
            return str(text)
        
        # Escapar HTML
        text = html.escape(text)
        
        # Remover caracteres de control peligrosos
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Limitar longitud
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        return text
    
    def validate_command_input(self, text: str) -> Dict[str, Any]:
        """Validar entrada de comandos"""
        result = {
            'is_safe': True,
            'warnings': [],
            'sanitized_text': self.sanitize_input(text)
        }
        
        text_lower = text.lower()
        
        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                result['is_safe'] = False
                result['warnings'].append(f"Patrón peligroso detectado: {pattern}")
        
        # Verificar inyección SQL
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                result['is_safe'] = False
                result['warnings'].append(f"Posible inyección SQL: {pattern}")
        
        # Verificar caracteres sospechosos
        if len(re.findall(r'[^\x20-\x7E]', text)) > len(text) * 0.3:
            result['warnings'].append("Alto contenido de caracteres no ASCII")
        
        return result
    
    def validate_file_input(self, filename: str) -> bool:
        """Validar nombres de archivo"""
        dangerous_patterns = [
            r'\.\.',
            r'^/',
            r'\\',
            r'[<>:"|?*]',
            r'^\.',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, filename):
                return False
        
        return True
    
    def validate_user_id(self, user_id: str) -> bool:
        """Validar formato de ID de usuario"""
        if not isinstance(user_id, str):
            return False
        
        # Solo números, longitud razonable
        return re.match(r'^\d{1,20}$', user_id) is not None
    
    def validate_chat_id(self, chat_id: str) -> bool:
        """Validar formato de ID de chat"""
        if not isinstance(chat_id, str):
            return False
        
        # Puede ser negativo para grupos
        return re.match(r'^-?\d{1,20}$', chat_id) is not None
