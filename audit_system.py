
import json
import hashlib
from datetime import datetime
from typing import Dict, Any
import logging

class AuditSystem:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler('audit.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_action(self, user_id: str, action: str, details: Dict[str, Any], 
                   ip_address: str = None, success: bool = True):
        """Registrar acción en el sistema de auditoría"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': ip_address,
            'success': success,
            'hash': self._generate_hash(user_id, action, details)
        }
        
        self.logger.info(json.dumps(audit_record))
        return audit_record
    
    def _generate_hash(self, user_id: str, action: str, details: Dict[str, Any]) -> str:
        """Generar hash para integridad del registro"""
        data = f"{user_id}{action}{json.dumps(details, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def get_user_activity(self, user_id: str, days: int = 7) -> list:
        """Obtener actividad de usuario"""
        try:
            activities = []
            with open('audit.log', 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.split(' - ', 1)[1])
                        if record['user_id'] == user_id:
                            activities.append(record)
                    except:
                        continue
            return activities[-50:]  # Últimas 50 actividades
        except:
            return []
    
    def detect_suspicious_activity(self, user_id: str) -> Dict[str, Any]:
        """Detectar actividad sospechosa"""
        activities = self.get_user_activity(user_id, 1)  # Último día
        
        alerts = {
            'rapid_commands': False,
            'failed_auths': 0,
            'unusual_patterns': False,
            'risk_level': 'low'
        }
        
        if len(activities) > 100:  # Más de 100 comandos en un día
            alerts['rapid_commands'] = True
            alerts['risk_level'] = 'medium'
        
        failed_auths = sum(1 for a in activities if not a['success'])
        alerts['failed_auths'] = failed_auths
        
        if failed_auths > 10:
            alerts['risk_level'] = 'high'
        
        return alerts
