#!/usr/bin/env python3
"""
Script principal para ejecutar el CC Checker Ultra Pro Bot
"""

import os
import sys
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_requirements():
    """Verifica que todos los requisitos estén instalados"""
    try:
        import telegram
        from telegram.ext import Application
        import requests
        logger.info("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        logger.error(f"❌ Falta dependencia: {e}")
        logger.error("Ejecuta: pip install -r requirements_bot.txt")
        return False

def check_environment():
    """Verifica variables de entorno"""
    # Verificar variables de entorno críticas
    required_vars = ['BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        logger.error("💡 Configura las variables en Secrets:")
        logger.error("   - BOT_TOKEN: Token de tu bot de Telegram")
        return False

    # Verificar variables de MongoDB (opcionales pero recomendadas)
    mongodb_url = os.getenv('MONGODB_URL') or os.getenv('MONGODB_CONNECTION_STRING')
    if not mongodb_url:
        logger.warning("⚠️ MONGODB_URL no configurado")
        logger.info("💡 Para usar MongoDB, configura en Secrets:")
        logger.info("   - MONGODB_URL: Cadena de conexión de MongoDB Atlas")
        logger.info("   - MONGODB_DB_NAME: Nombre de la base de datos (opcional)")
    else:
        logger.info("✅ Variables de MongoDB encontradas")

    logger.info("✅ Variables de entorno configuradas")
    return True

def main():
    """Función principal"""
    logger.info("🚀 Iniciando CC Checker Ultra Pro Bot...")

    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)

    if not check_environment():
        sys.exit(1)

    try:
        # Importar y ejecutar el bot
        from telegram_bot import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Obtener el token del bot desde las variables de entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(',') if admin_id] if os.getenv("ADMIN_IDS") else []

# Diccionario para almacenar usuarios silenciados (user_id: timestamp_fin)
muted_users = {}

async def start(update, context):
    """Maneja el comando /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Hola {user.mention_html()}! Soy el CC Checker Ultra Pro Bot.\n\n"
        "Utiliza /help para ver los comandos disponibles.",
        quote=False
    )

async def help_command(update, context):
    """Maneja el comando /help"""
    help_text = (
        "Estos son los comandos que puedes usar:\n"
        "/start - Inicia el bot y muestra un mensaje de bienvenida.\n"
        "/help - Muestra este mensaje de ayuda.\n"
        "/mute <usuario> <tiempo> - Silencia a un usuario. Ejemplo: /mute @usuario 1h\n"
        "/unmute <usuario> - Desilencia a un usuario.\n"
        "/mutelist - Muestra la lista de usuarios silenciados.\n"
    )
    await update.message.reply_text(help_text)

async def mute(update, context):
    """Maneja el comando /mute"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Uso: /mute <usuario> <tiempo>")
        return

    try:
        user_id = context.args[0]
        mute_time = context.args[1]

        # Extract username and user_id from the argument
        try:
            user_id = int(user_id)  # If user_id is already an integer
        except ValueError:
            # If it's a username, try to get user_id
            if not user_id.startswith('@'):
                await update.message.reply_text("El usuario debe comenzar con @.")
                return
            try:
                user = await context.bot.get_chat(user_id)
                user_id = user.id
            except Exception as e:
                await update.message.reply_text(f"No se pudo obtener el ID del usuario: {e}")
                return

        # Calculate mute end time
        if mute_time.endswith('s'):
            mute_seconds = int(mute_time[:-1])
        elif mute_time.endswith('m'):
            mute_seconds = int(mute_time[:-1]) * 60
        elif mute_time.endswith('h'):
            mute_seconds = int(mute_time[:-1]) * 3600
        elif mute_time.endswith('d'):
            mute_seconds = int(mute_time[:-1]) * 86400
        else:
            await update.message.reply_text("Formato de tiempo inválido. Usa s, m, h, o d.")
            return

        mute_end_time = datetime.now().timestamp() + mute_seconds

        # Mute user
        muted_users[user_id] = mute_end_time
        await update.message.reply_text(f"Usuario {user_id} silenciado hasta {datetime.fromtimestamp(mute_end_time).strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        logger.error(f"Error al silenciar usuario: {e}")
        await update.message.reply_text("Ocurrió un error temporal.")

async def unmute(update, context):
    """Maneja el comando /unmute"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Uso: /unmute <usuario>")
        return

    try:
        user_id = context.args[0]

        # Extract username and user_id from the argument
        try:
            user_id = int(user_id)  # If user_id is already an integer
        except ValueError:
            # If it's a username, try to get user_id
            if not user_id.startswith('@'):
                await update.message.reply_text("El usuario debe comenzar con @.")
                return
            try:
                user = await context.bot.get_chat(user_id)
                user_id = user.id
            except Exception as e:
                await update.message.reply_text(f"No se pudo obtener el ID del usuario: {e}")
                return

        if user_id in muted_users:
            del muted_users[user_id]
            await update.message.reply_text(f"Usuario {user_id} desilenciado.")
        else:
            await update.message.reply_text("Este usuario no está silenciado.")

    except Exception as e:
        logger.error(f"Error al desilenciar usuario: {e}")
        await update.message.reply_text("Ocurrió un error temporal.")

async def mutelist(update, context):
    """Maneja el comando /mutelist"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    if not muted_users:
        await update.message.reply_text("No hay usuarios silenciados.")
        return

    try:
        mute_list_text = "Lista de usuarios silenciados:\n"
        for user_id, mute_end_time in muted_users.items():
            mute_list_text += f"- {user_id} (Hasta {datetime.fromtimestamp(mute_end_time).strftime('%Y-%m-%d %H:%M:%S')})\n"
        await update.message.reply_text(mute_list_text)

    except Exception as e:
        logger.error(f"Error al mostrar la lista de silenciados: {e}")
        await update.message.reply_text("Ocurrió un error temporal.")

async def check_mute_status(update, context):
    """Verifica si el usuario está silenciado y elimina mensajes"""
    user_id = update.effective_user.id
    if user_id in muted_users:
        mute_end_time = muted_users[user_id]
        if datetime.now().timestamp() < mute_end_time:
            try:
                await update.message.delete()
                logger.info(f"Mensaje de usuario silenciado {user_id} eliminado.")
            except Exception as e:
                logger.warning(f"No se pudo eliminar el mensaje: {e}")
        else:
            del muted_users[user_id]
            logger.info(f"Usuario {user_id} desilenciado automáticamente.")

async def post_init(app, context):
    """Envia un mensaje de inicio al admin"""
    from datetime import datetime

    # Enviar mensaje de inicio (opcional)
    try:
        if ADMIN_IDS:
            admin_id = ADMIN_IDS[0]
            await context.bot.send_message(
                chat_id=admin_id,
                text="🤖 **Bot iniciado correctamente**\n"
                "📱 Estado: Online\n"
                f"⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        logger.warning(f"No se pudo enviar mensaje de inicio: {e}")

    print("✅ Bot iniciado correctamente")


def main():
    """Función principal del bot - Versión corregida"""
    logger.info("🚀 Iniciando aplicación de Telegram Bot...")

    try:
        # Crear aplicación
        app = Application.builder().token(BOT_TOKEN).build()

        # Registrar handlers
        register_handlers(app)

        # Configurar post_init
        app.post_init = post_init

        # Iniciar el bot con run_polling (forma más simple y estable)
        logger.info("✅ Bot iniciado y esperando mensajes...")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False  # No cerrar el loop automáticamente
        )

    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico en el bot: {e}")
        raise

def register_handlers(app):
    """Registra todos los handlers"""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("mutelist", mutelist))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_mute_status))

if __name__ == "__main__":
    main()
