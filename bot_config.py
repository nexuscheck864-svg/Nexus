
import os
import json
import random
from datetime import datetime, timedelta

# Configuración de DNI/RENIEC (simulado)
class DNIGenerator:
    @staticmethod
    def generate_dni_info():
        """Genera información de DNI simulada"""
        first_names = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'José', 'Rosa']
        last_names = ['García', 'González', 'Rodríguez', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez']
        
        dni = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        return {
            'dni': dni,
            'nombres': f"{random.choice(first_names)} {random.choice(first_names)}",
            'apellidos': f"{random.choice(last_names)} {random.choice(last_names)}",
            'fecha_nacimiento': f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(1970, 2005)}",
            'estado_civil': random.choice(['SOLTERO', 'CASADO', 'DIVORCIADO', 'VIUDO']),
            'ubigeo': f"{random.randint(10, 25):02d}{random.randint(1, 9):02d}{random.randint(1, 15):02d}"
        }

# Configuración de pasarelas de pago
PAYMENT_GATEWAYS = {
    'stripe': {
        'name': 'Stripe',
        'url': 'https://stripe.com',
        'fees': '2.9% + $0.30',
        'countries': 'Global',
        'status': '🟢 Activo'
    },
    'paypal': {
        'name': 'PayPal',
        'url': 'https://paypal.com',
        'fees': '3.4% + $0.30',
        'countries': 'Global',
        'status': '🟢 Activo'
    },
    'square': {
        'name': 'Square',
        'url': 'https://squareup.com',
        'fees': '2.6% + $0.10',
        'countries': 'US, CA, AU, JP',
        'status': '🟢 Activo'
    }
}

# Sistema de claves premium
PREMIUM_KEYS = {
    'ULTRA2024': {'days': 30, 'used': False},
    'PREMIUM365': {'days': 365, 'used': False},
    'GOLD90': {'days': 90, 'used': False}
}

class KeyManager:
    @staticmethod
    def validate_key(key_code: str) -> dict:
        """Valida una clave premium"""
        if key_code in PREMIUM_KEYS and not PREMIUM_KEYS[key_code]['used']:
            return {
                'valid': True,
                'days': PREMIUM_KEYS[key_code]['days']
            }
        return {'valid': False}
    
    @staticmethod
    def use_key(key_code: str):
        """Marca una clave como usada"""
        if key_code in PREMIUM_KEYS:
            PREMIUM_KEYS[key_code]['used'] = True

# Logs y estadísticas
class BotLogger:
    @staticmethod
    def log_command(user_id: str, command: str, success: bool = True):
        """Registra uso de comandos"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'command': command,
            'success': success
        }
        
        try:
            with open('bot_logs.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
    
    @staticmethod
    def get_stats():
        """Obtiene estadísticas del bot"""
        try:
            stats = {
                'total_commands': 0,
                'successful_commands': 0,
                'most_used_command': '',
                'active_users_today': set()
            }
            
            today = datetime.now().date()
            command_count = {}
            
            with open('bot_logs.json', 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        log_date = datetime.fromisoformat(log['timestamp']).date()
                        
                        stats['total_commands'] += 1
                        if log['success']:
                            stats['successful_commands'] += 1
                        
                        command = log['command']
                        command_count[command] = command_count.get(command, 0) + 1
                        
                        if log_date == today:
                            stats['active_users_today'].add(log['user_id'])
                    except:
                        continue
            
            if command_count:
                stats['most_used_command'] = max(command_count, key=command_count.get)
            
            stats['active_users_today'] = len(stats['active_users_today'])
            return stats
        except:
            return {
                'total_commands': 0,
                'successful_commands': 0,
                'most_used_command': 'N/A',
                'active_users_today': 0
            }
