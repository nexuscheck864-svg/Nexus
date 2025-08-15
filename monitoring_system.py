
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import json

class SecurityMonitor:
    def __init__(self, bot_instance, db_instance):
        self.bot = bot_instance
        self.db = db_instance
        self.alerts = []
        self.monitoring_active = True
        self.admin_chat_id = None  # Configurar para recibir alertas
    
    async def start_monitoring(self):
        """Iniciar monitoreo de seguridad"""
        while self.monitoring_active:
            await self.check_security_threats()
            await asyncio.sleep(300)  # Verificar cada 5 minutos
    
    async def check_security_threats(self):
        """Verificar amenazas de seguridad"""
        threats_detected = []
        
        # Verificar actividad sospechosa
        for user_id in self.db.users.keys():
            alerts = self.detect_suspicious_patterns(user_id)
            if alerts['risk_level'] == 'high':
                threats_detected.append({
                    'type': 'suspicious_activity',
                    'user_id': user_id,
                    'details': alerts
                })
        
        # Verificar intentos de bypass
        bypass_attempts = self.check_bypass_attempts()
        if bypass_attempts:
            threats_detected.extend(bypass_attempts)
        
        # Verificar flood/spam
        flood_attempts = self.check_flood_attempts()
        if flood_attempts:
            threats_detected.extend(flood_attempts)
        
        # Enviar alertas si hay amenazas
        if threats_detected and self.admin_chat_id:
            await self.send_security_alert(threats_detected)
    
    def detect_suspicious_patterns(self, user_id: str) -> Dict:
        """Detectar patrones sospechosos de usuario"""
        security_logs = self.db.security_settings.get('security_logs', [])
        user_logs = [log for log in security_logs if log['user_id'] == user_id]
        
        # Análisis de últimas 24 horas
        since = datetime.now() - timedelta(hours=24)
        recent_logs = [
            log for log in user_logs
            if datetime.fromisoformat(log['timestamp']) > since
        ]
        
        alerts = {
            'failed_commands': 0,
            'rapid_fire': False,
            'permission_denials': 0,
            'risk_level': 'low'
        }
        
        # Contar fallas y denegaciones
        for log in recent_logs:
            if log['event_type'] == 'COMMAND_ERROR':
                alerts['failed_commands'] += 1
            elif log['event_type'] == 'PERMISSION_DENIED':
                alerts['permission_denials'] += 1
        
        # Detectar rapid fire (más de 50 comandos en una hora)
        last_hour = datetime.now() - timedelta(hours=1)
        recent_hour_logs = [
            log for log in recent_logs
            if datetime.fromisoformat(log['timestamp']) > last_hour
        ]
        
        if len(recent_hour_logs) > 50:
            alerts['rapid_fire'] = True
            alerts['risk_level'] = 'high'
        elif alerts['failed_commands'] > 20 or alerts['permission_denials'] > 10:
            alerts['risk_level'] = 'medium'
        
        return alerts
    
    def check_bypass_attempts(self) -> List[Dict]:
        """Verificar intentos de bypass de seguridad"""
        threats = []
        
        # Verificar intentos de escalación de privilegios
        security_logs = self.db.security_settings.get('security_logs', [])
        recent_logs = [
            log for log in security_logs
            if datetime.fromisoformat(log['timestamp']) > datetime.now() - timedelta(hours=1)
        ]
        
        # Agrupar por usuario
        user_activities = {}
        for log in recent_logs:
            user_id = log['user_id']
            if user_id not in user_activities:
                user_activities[user_id] = []
            user_activities[user_id].append(log)
        
        # Detectar patrones sospechosos
        for user_id, activities in user_activities.items():
            permission_denials = sum(1 for a in activities if a['event_type'] == 'PERMISSION_DENIED')
            
            if permission_denials > 5:  # Más de 5 denegaciones en una hora
                threats.append({
                    'type': 'privilege_escalation_attempt',
                    'user_id': user_id,
                    'details': f"{permission_denials} intentos de escalación en una hora"
                })
        
        return threats
    
    def check_flood_attempts(self) -> List[Dict]:
        """Verificar intentos de flood/DoS"""
        threats = []
        
        # Verificar rate limiting excedido
        current_time = datetime.now()
        
        for key, timestamps in self.db.security_settings.items():
            if isinstance(timestamps, list) and len(timestamps) > 0:
                # Verificar si hay más de 100 requests en 10 minutos
                recent_requests = [
                    ts for ts in timestamps
                    if isinstance(ts, str) and (current_time - datetime.fromisoformat(ts)).seconds < 600
                ]
                
                if len(recent_requests) > 100:
                    user_id = key.split('_')[0] if '_' in key else key
                    threats.append({
                        'type': 'potential_flood',
                        'user_id': user_id,
                        'details': f"{len(recent_requests)} requests en 10 minutos"
                    })
        
        return threats
    
    async def send_security_alert(self, threats: List[Dict]):
        """Enviar alerta de seguridad a administradores"""
        if not self.admin_chat_id:
            return
        
        alert_message = "🚨 **ALERTA DE SEGURIDAD** 🚨\n\n"
        
        for threat in threats:
            alert_message += f"⚠️ **Tipo:** {threat['type']}\n"
            alert_message += f"👤 **Usuario:** `{threat['user_id']}`\n"
            alert_message += f"📝 **Detalles:** {threat['details']}\n"
            alert_message += f"⏰ **Tiempo:** {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        alert_message += "💡 **Revisa los logs para más información**"
        
        try:
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=alert_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Log error but don't crash monitoring
            print(f"Error enviando alerta de seguridad: {e}")
    
    def set_admin_chat(self, chat_id: str):
        """Configurar chat de administrador para alertas"""
        self.admin_chat_id = chat_id
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring_active = False
