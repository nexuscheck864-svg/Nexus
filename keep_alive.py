from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return """
    <h1>🤖 CC Checker Ultra Pro Bot - ACTIVO</h1>
    <p>✅ Estado: Funcionando correctamente</p>
    <p>⏰ Tiempo: {}</p>
    <p>🔗 Para UptimeRobot monitoring</p>
    """.format(time.strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/status')
def status():
    return {
        "status": "active",
        "bot": "CC Checker Ultra Pro",
        "timestamp": time.time(),
        "uptime": "24/7"
    }

def keep_alive():
    def run():
        app.run(host='0.0.0.0', port=8080, debug=False)
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Servidor web iniciado en puerto 8080 para UptimeRobot")
