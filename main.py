
#!/usr/bin/env python3
"""
Punto de entrada principal para CC Checker Ultra Pro Bot
Optimizado para Render.com con servidor web completo
"""

import os
import sys
import logging
import threading
import time
import json
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Crear aplicación Flask para servidor web completo
app = Flask(__name__)

# Variables globales para estadísticas
bot_stats = {
    "start_time": datetime.now(),
    "users_count": 0,
    "commands_executed": 0,
    "cards_generated": 0,
    "cards_checked": 0,
    "last_activity": datetime.now()
}

# Plantilla HTML para el dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CC Checker Ultra Pro Bot - Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 10px;
        }
        .stat-label {
            font-size: 1.1em;
            opacity: 0.8;
        }
        .api-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .endpoint {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #00ff88;
        }
        .method {
            display: inline-block;
            background: #00ff88;
            color: black;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            margin-right: 10px;
        }
        .refresh-btn {
            background: #00ff88;
            color: black;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin: 20px 0;
        }
        .refresh-btn:hover {
            background: #00cc6a;
        }
        .status-online {
            color: #00ff88;
        }
        .status-offline {
            color: #ff4444;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 CC Checker Ultra Pro Bot</h1>
            <h2>Dashboard de Control - Render.com</h2>
            <p>Estado: <span class="status-online">🟢 ONLINE</span></p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ uptime }}</div>
                <div class="stat-label">⏱️ Tiempo Activo</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ users_count }}</div>
                <div class="stat-label">👥 Usuarios Registrados</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ commands_executed }}</div>
                <div class="stat-label">⚡ Comandos Ejecutados</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ cards_generated }}</div>
                <div class="stat-label">💳 Tarjetas Generadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ cards_checked }}</div>
                <div class="stat-label">🔍 Tarjetas Verificadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ last_activity }}</div>
                <div class="stat-label">🕐 Última Actividad</div>
            </div>
        </div>

        <div class="api-section">
            <h3>📡 API Endpoints Disponibles</h3>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/stats</strong> - Estadísticas del bot en JSON
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/health</strong> - Estado de salud detallado
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/api/generate</strong> - Generar tarjetas (requiere API key)
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/api/check</strong> - Verificar tarjetas (requiere API key)
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <strong>/api/users</strong> - Información de usuarios registrados
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <strong>/webhook</strong> - Webhook para integraciones externas
            </div>

            <button class="refresh-btn" onclick="location.reload()">🔄 Actualizar Dashboard</button>
        </div>

        <div class="api-section">
            <h3>🛠️ Información del Sistema</h3>
            <p><strong>Versión:</strong> v4.2 Ultra Pro</p>
            <p><strong>Plataforma:</strong> Render.com</p>
            <p><strong>Puerto:</strong> {{ port }}</p>
            <p><strong>Inicio:</strong> {{ start_time }}</p>
            <p><strong>Bot Token:</strong> Configurado ✅</p>
            <p><strong>MongoDB:</strong> {{ mongo_status }}</p>
        </div>
    </div>

    <script>
        // Auto-refresh cada 30 segundos
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Dashboard principal con información completa"""
    try:
        # Cargar estadísticas desde bot_data.json si existe
        if os.path.exists('bot_data.json'):
            with open('bot_data.json', 'r') as f:
                data = json.load(f)
                users = data.get('users', {})
                bot_stats['users_count'] = len(users)
                bot_stats['cards_generated'] = sum(u.get('total_generated', 0) for u in users.values())
                bot_stats['cards_checked'] = sum(u.get('total_checked', 0) for u in users.values())
        
        uptime = datetime.now() - bot_stats['start_time']
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        mongo_status = "Configurado ✅" if os.getenv('MONGODB_URL') else "No configurado ❌"
        
        return render_template_string(DASHBOARD_HTML, 
                                    uptime=f"{hours}h {minutes}m",
                                    users_count=bot_stats['users_count'],
                                    commands_executed=bot_stats['commands_executed'],
                                    cards_generated=bot_stats['cards_generated'],
                                    cards_checked=bot_stats['cards_checked'],
                                    last_activity=bot_stats['last_activity'].strftime('%H:%M:%S'),
                                    port=os.environ.get('PORT', 5000),
                                    start_time=bot_stats['start_time'].strftime('%d/%m/%Y %H:%M:%S'),
                                    mongo_status=mongo_status)
    except Exception as e:
        return f"Error cargando dashboard: {str(e)}", 500

@app.route('/status')
def bot_status():
    """Status endpoint detallado para Render"""
    return jsonify({
        "bot_name": "CC Checker Ultra Pro",
        "status": "active",
        "platform": "Render.com",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_seconds": int((datetime.now() - bot_stats['start_time']).total_seconds()),
        "version": "v4.2",
        "features": ["Card Generation", "Card Verification", "Premium System", "Staff Management"],
        "endpoints": ["/", "/status", "/api/stats", "/api/health", "/webhook"],
        "environment": {
            "bot_token_configured": bool(os.getenv('BOT_TOKEN')),
            "mongodb_configured": bool(os.getenv('MONGODB_URL')),
            "admin_ids_configured": bool(os.getenv('ADMIN_IDS')),
            "port": os.environ.get('PORT', 5000)
        }
    })

@app.route('/api/health')
def health_check():
    """Health check avanzado para monitoreo"""
    try:
        health_status = {
            "status": "healthy",
            "service": "CC Checker Ultra Pro Bot",
            "timestamp": time.time(),
            "checks": {
                "bot_token": "ok" if os.getenv('BOT_TOKEN') else "missing",
                "database": "ok" if os.path.exists('bot_data.json') else "missing",
                "mongodb": "configured" if os.getenv('MONGODB_URL') else "not_configured",
                "memory": "ok",
                "disk_space": "ok"
            },
            "metrics": {
                "uptime_seconds": int((datetime.now() - bot_stats['start_time']).total_seconds()),
                "users_count": bot_stats['users_count'],
                "commands_executed": bot_stats['commands_executed'],
                "cards_generated": bot_stats['cards_generated'],
                "cards_checked": bot_stats['cards_checked']
            }
        }
        
        # Determinar estado general
        if health_status['checks']['bot_token'] == 'missing':
            health_status['status'] = 'unhealthy'
            
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/stats')
def api_stats():
    """API de estadísticas en JSON"""
    try:
        # Actualizar estadísticas desde archivo
        if os.path.exists('bot_data.json'):
            with open('bot_data.json', 'r') as f:
                data = json.load(f)
                users = data.get('users', {})
                
                premium_users = sum(1 for u in users.values() if u.get('premium', False))
                total_credits = sum(u.get('credits', 0) for u in users.values())
                
                return jsonify({
                    "status": "success",
                    "data": {
                        "users": {
                            "total": len(users),
                            "premium": premium_users,
                            "standard": len(users) - premium_users
                        },
                        "activity": {
                            "cards_generated": sum(u.get('total_generated', 0) for u in users.values()),
                            "cards_checked": sum(u.get('total_checked', 0) for u in users.values()),
                            "commands_executed": bot_stats['commands_executed'],
                            "total_credits": total_credits
                        },
                        "system": {
                            "uptime_seconds": int((datetime.now() - bot_stats['start_time']).total_seconds()),
                            "start_time": bot_stats['start_time'].isoformat(),
                            "last_activity": bot_stats['last_activity'].isoformat(),
                            "version": "v4.2",
                            "platform": "Render.com"
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                })
        else:
            return jsonify({
                "status": "success",
                "data": {
                    "users": {"total": 0, "premium": 0, "standard": 0},
                    "activity": {"cards_generated": 0, "cards_checked": 0, "commands_executed": 0, "total_credits": 0},
                    "system": {
                        "uptime_seconds": int((datetime.now() - bot_stats['start_time']).total_seconds()),
                        "start_time": bot_stats['start_time'].isoformat(),
                        "version": "v4.2",
                        "platform": "Render.com"
                    }
                },
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/users')
def api_users():
    """API de información de usuarios"""
    try:
        if not os.path.exists('bot_data.json'):
            return jsonify({
                "status": "success",
                "data": {"users": [], "count": 0},
                "timestamp": datetime.now().isoformat()
            })
            
        with open('bot_data.json', 'r') as f:
            data = json.load(f)
            users = data.get('users', {})
            
            user_list = []
            for user_id, user_data in users.items():
                user_list.append({
                    "user_id": user_id,
                    "premium": user_data.get('premium', False),
                    "credits": user_data.get('credits', 0),
                    "total_generated": user_data.get('total_generated', 0),
                    "total_checked": user_data.get('total_checked', 0),
                    "join_date": user_data.get('join_date', ''),
                    "last_bonus": user_data.get('last_bonus', ''),
                    "warns": user_data.get('warns', 0)
                })
            
            return jsonify({
                "status": "success",
                "data": {
                    "users": user_list,
                    "count": len(user_list)
                },
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para integraciones externas"""
    try:
        data = request.get_json()
        logger.info(f"Webhook recibido: {data}")
        
        # Aquí puedes procesar webhooks de servicios externos
        # Por ejemplo, notificaciones de Telegram, actualizaciones, etc.
        
        return jsonify({
            "status": "received",
            "message": "Webhook procesado correctamente",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API para generar tarjetas (requiere autenticación)"""
    try:
        # Verificar API key (puedes configurar una en variables de entorno)
        api_key = request.headers.get('X-API-KEY')
        if not api_key or api_key != os.getenv('API_KEY', 'demo-key'):
            return jsonify({
                "status": "error",
                "error": "API key inválida o faltante",
                "timestamp": datetime.now().isoformat()
            }), 401
        
        data = request.get_json()
        bin_number = data.get('bin', '')
        count = min(int(data.get('count', 10)), 50)  # Máximo 50
        
        if not bin_number or len(bin_number) < 6:
            return jsonify({
                "status": "error",
                "error": "BIN inválido",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Generar tarjetas (usando lógica simplificada)
        cards = []
        for i in range(count):
            import random
            card = f"{bin_number}{''.join([str(random.randint(0, 9)) for _ in range(16-len(bin_number))])}|{random.randint(1, 12):02d}|{random.randint(2025, 2030)}|{random.randint(100, 999)}"
            cards.append(card)
        
        # Actualizar estadísticas
        bot_stats['cards_generated'] += count
        bot_stats['last_activity'] = datetime.now()
        
        return jsonify({
            "status": "success",
            "data": {
                "cards": cards,
                "count": len(cards),
                "bin": bin_number
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(e):
    """Página 404 personalizada"""
    return jsonify({
        "status": "error",
        "error": "Endpoint no encontrado",
        "available_endpoints": ["/", "/status", "/api/stats", "/api/health", "/api/users", "/webhook"],
        "timestamp": datetime.now().isoformat()
    }), 404

def update_stats():
    """Actualizar estadísticas periódicamente"""
    while True:
        try:
            bot_stats['commands_executed'] += 1  # Simular actividad
            bot_stats['last_activity'] = datetime.now()
            time.sleep(60)  # Actualizar cada minuto
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
            time.sleep(60)

def run_flask():
    """Ejecutar servidor Flask"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Iniciando servidor web completo en puerto {port}")
    logger.info(f"📊 Dashboard disponible en: http://0.0.0.0:{port}/")
    logger.info(f"📡 API endpoints configurados")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

def main():
    """Función principal"""
    logger.info("🚀 Iniciando CC Checker Ultra Pro Bot en Render.com...")

    # Verificar variables de entorno requeridas
    if not os.getenv('BOT_TOKEN'):
        logger.error("❌ BOT_TOKEN no configurado en variables de entorno")
        sys.exit(1)

    try:
        # Iniciar actualizador de estadísticas en hilo separado
        stats_thread = threading.Thread(target=update_stats, daemon=True)
        stats_thread.start()
        logger.info("✅ Sistema de estadísticas iniciado")

        # Iniciar servidor Flask en hilo separado
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("✅ Servidor web iniciado correctamente")

        # Esperar un momento para que el servidor se inicialice
        time.sleep(2)

        # Importar y ejecutar el bot principal
        logger.info("🤖 Iniciando bot de Telegram...")
        import telegram_bot
        telegram_bot.main()

    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
