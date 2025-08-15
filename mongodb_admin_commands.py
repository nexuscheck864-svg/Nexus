import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

async def mongodb_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dbstatus - Verificar estado de MongoDB"""
    from telegram_bot import db, ADMIN_IDS

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Verificar permisos de administrador usando ADMIN_IDS
    if user_id_int not in ADMIN_IDS:
        await update.message.reply_text(
            "❌ **ACCESO DENEGADO**\n\n"
            "🔒 Solo administradores pueden usar este comando",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Verificar variables de entorno
    mongodb_url = os.getenv('MONGODB_URL') or os.getenv('MONGODB_CONNECTION_STRING')
    db_name = os.getenv('MONGODB_DB_NAME', 'telegram_bot_db')

    # Obtener información de conexión
    connection_info = db.get_connection_info()
    stats = db.get_stats()

    status_emoji = "🟢" if connection_info['connected'] else "🔴"
    status_text = "CONECTADO" if connection_info['connected'] else "DESCONECTADO"

    # Verificar configuración y validez de URL
    config_emoji = "🟢" if mongodb_url else "🔴"
    config_text = "CONFIGURADO" if mongodb_url else "NO CONFIGURADO"

    # Validación adicional de URL si está configurada
    url_valid = True
    if mongodb_url:
        import re
        patterns = [
            r'^mongodb\+srv://[^:]+:[^@]+@[^/]+\.mongodb\.net/',
            r'^mongodb://[^:]+:[^@]+@[^/]+/',
            r'^mongodb://[^/]+/',
            r'^mongodb\+srv://[^/]+\.mongodb\.net/'
        ]
        url_valid = any(re.match(pattern, mongodb_url) for pattern in patterns)
        if not url_valid:
            config_emoji = "🟡"
            config_text = "CONFIGURADO (FORMATO INVÁLIDO)"

    response = f"📊 *ESTADO DE MONGODB ATLAS* 📊\n\n"
    response += f"⚙️ *Configuración:* {config_emoji} {config_text}\n"

    if mongodb_url and not url_valid:
        response += f"⚠️ *URL Format:* Inválido\n"

    response += f"🔗 *Estado:* {status_emoji} {status_text}\n"
    response += f"🗄️ *Base de datos:* {connection_info['database']}\n"
    response += f"🔄 *Intentos reconexión:* {connection_info['reconnect_attempts']}/{connection_info['max_attempts']}\n\n"

    if not mongodb_url:
        response += f"⚠️ *VARIABLES FALTANTES:*\n"
        response += f"• MONGODB\\_URL no configurado en Secrets\n"
        response += f"• Configura tu cadena de conexión Atlas\n\n"
    elif not url_valid:
        response += f"⚠️ *URL INVÁLIDA:*\n"
        response += f"• Formato de URL incorrecto\n"
        response += f"• Formatos válidos:\n"
        response += f"  \\- mongodb\\+srv://user:pass@cluster\\.mongodb\\.net/db\n"
        response += f"  \\- mongodb://user:pass@host:port/db\n\n"

    if connection_info['last_attempt']:
        last_attempt = datetime.fromisoformat(connection_info['last_attempt'])
        response += f"⏰ *Último intento:* {last_attempt.strftime('%d/%m/%Y %H:%M:%S')}\n\n"

    response += f"📈 *ESTADÍSTICAS:*\n"
    response += f"👥 *Total usuarios:* {stats.get('total_users', 0)}\n"
    response += f"💎 *Usuarios premium:* {stats.get('premium_users', 0)}\n"
    response += f"👑 *Staff total:* {stats.get('total_staff', 0)}\n"
    response += f"🏛️ *Fundadores:* {stats.get('total_founders', 0)}\n"
    response += f"📝 *Logs totales:* {stats.get('total_logs', 0)}\n\n"

    response += f"📂 *Colecciones:*\n"
    for collection in connection_info.get('collections', []):
        response += f"• {collection}\n"

    # Botones de acción
    keyboard = []

    if connection_info['connected']:
        keyboard.append([
            InlineKeyboardButton("🔄 Reconectar", callback_data='db_reconnect'),
            InlineKeyboardButton("🧹 Limpiar datos", callback_data='db_cleanup')
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🔌 Conectar", callback_data='db_connect')
        ])

    keyboard.append([
        InlineKeyboardButton("📊 Actualizar", callback_data='db_refresh'),
        InlineKeyboardButton("❌ Cerrar", callback_data='db_close')
    ])

    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def mongodb_reconnect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dbreconnect - Forzar reconexión"""
    from telegram_bot import db, ADMIN_IDS

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Verificar permisos usando ADMIN_IDS
    if user_id_int not in ADMIN_IDS:
        await update.message.reply_text("❌ Acceso denegado")
        return

    processing_msg = await update.message.reply_text(
        "🔄 **RECONECTANDO A MONGODB...**\n\n"
        "⏳ Cerrando conexión actual...",
        parse_mode=ParseMode.MARKDOWN
    )

    # Cerrar conexión actual
    await db.close_connection()
    await asyncio.sleep(1)

    await processing_msg.edit_text(
        "🔄 **RECONECTANDO A MONGODB...**\n\n"
        "🔌 Estableciendo nueva conexión...",
        parse_mode=ParseMode.MARKDOWN
    )

    # Intentar reconectar
    success = await db.connect()

    if success:
        await processing_msg.edit_text(
            "✅ *RECONEXIÓN EXITOSA* ✅\n\n"
            "🟢 *Estado:* Conectado\n"
            "⚡ *Base de datos:* Lista para usar\n"
            "🔄 *Intentos:* Reiniciados\n\n"
            "💡 El bot puede continuar operando normalmente",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await processing_msg.edit_text(
            "❌ *ERROR EN RECONEXIÓN* ❌\n\n"
            "🔴 *Estado:* Desconectado\n"
            "⚠️ *Problema:* No se pudo establecer conexión\n\n"
            "🛠️ *Verificar:*\n"
            "• Variables de entorno \\(MONGODB\\_URL\\)\n"
            "• Conexión a internet\n"
            "• Estado de MongoDB Atlas\n"
            "• Configuración de IP whitelist",
            parse_mode=ParseMode.MARKDOWN
        )

async def mongodb_cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dbcleanup - Limpiar datos antiguos"""
    from telegram_bot import db, ADMIN_IDS

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Solo administradores pueden limpiar datos
    if user_id_int not in ADMIN_IDS:
        await update.message.reply_text("❌ Solo administradores pueden limpiar la base de datos")
        return

    # Verificar si se especificó días como argumento
    args = context.args
    if args and args[0].isdigit():
        days = int(args[0])
        if days < 1 or days > 365:
            await update.message.reply_text(
                "❌ **Días inválidos**\n\n"
                "🔢 Debe ser entre 1 y 365 días\n"
                "📝 **Uso:** `/dbcleanup [días]`\n"
                "💡 **Ejemplo:** `/dbcleanup 15`"
            )
            return

        # Ejecutar limpieza directamente
        processing_msg = await update.message.reply_text(
            f"🧹 **LIMPIANDO DATOS...**\n\n"
            f"⏳ Eliminando datos de más de {days} días...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Limpieza profunda si son más de 60 días
        deep_clean = days >= 60
        results = await db.cleanup_old_data(days, deep_clean=deep_clean)

        response = f"✅ *LIMPIEZA COMPLETADA* ✅\n\n"
        response += f"📊 *Resultados:*\n"
        response += f"• Logs eliminados: {results.get('logs_deleted', 0)}\n"
        response += f"• Sesiones eliminadas: {results.get('sessions_deleted', 0)}\n"
        response += f"• Usuarios inactivos: {results.get('inactive_users_deleted', 0)}\n\n"
        response += f"🗃️ *Período:* Datos > {days} días"

        await processing_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)
        return

    # Mostrar opciones interactivas
    keyboard = [
        [
            InlineKeyboardButton("🗑️ 3 días", callback_data='cleanup_3'),
            InlineKeyboardButton("🗑️ 7 días", callback_data='cleanup_7')
        ],
        [
            InlineKeyboardButton("🗑️ 15 días", callback_data='cleanup_15'),
            InlineKeyboardButton("🗑️ 30 días", callback_data='cleanup_30')
        ],
        [
            InlineKeyboardButton("🗑️ 60 días", callback_data='cleanup_60'),
            InlineKeyboardButton("🗑️ 90 días", callback_data='cleanup_90')
        ],
        [
            InlineKeyboardButton("❌ Cancelar", callback_data='cleanup_cancel')
        ]
    ]

    await update.message.reply_text(
        "⚠️ **LIMPIEZA DE BASE DE DATOS** ⚠️\n\n"
        "🗑️ **Esto eliminará:**\n"
        "• Logs antiguos\n"
        "• Sesiones expiradas\n"
        "• Usuarios inactivos sin premium\n\n"
        "⚡ **Selecciona el período:**\n"
        "💡 **O usa:** `/dbcleanup [días]`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

async def mongodb_backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dbbackup - Crear respaldo de datos importantes y enviar archivos JSON"""
    from telegram_bot import db, ADMIN_IDS

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Solo administradores pueden hacer backup
    if user_id_int not in ADMIN_IDS:
        await update.message.reply_text("❌ Solo administradores pueden crear respaldos de la base de datos")
        return

    processing_msg = await update.message.reply_text(
        "📦 **CREANDO RESPALDO...**\n\n"
        "⏳ Extrayendo datos de MongoDB...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Verificar conexión
        if not await db.ensure_connection():
            await processing_msg.edit_text(
                "❌ **ERROR DE CONEXIÓN**\n\n"
                "🔴 No se puede conectar a MongoDB para crear respaldo",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        await processing_msg.edit_text(
            "📦 **CREANDO RESPALDO...**\n\n"
            "📊 Extrayendo usuarios...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Extraer datos importantes
        backup_data = {
            'backup_info': {
                'created_at': datetime.now().isoformat(),
                'created_by': user_id,
                'version': '1.0',
                'bot_name': 'ChernobilChLv Bot',
                'description': 'Respaldo completo de datos del bot de Telegram'
            },
            'users': [],
            'staff': [],
            'founders': [],
            'stats': db.get_stats()
        }

        # Extraer usuarios
        users_cursor = db.collections['users'].find({})
        for user in users_cursor:
            user.pop('_id', None)  # Remover ID de MongoDB
            backup_data['users'].append(user)

        await processing_msg.edit_text(
            "📦 **CREANDO RESPALDO...**\n\n"
            "👑 Extrayendo staff y fundadores...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Extraer staff
        staff_cursor = db.collections['staff'].find({})
        for staff in staff_cursor:
            staff.pop('_id', None)
            backup_data['staff'].append(staff)

        # Extraer fundadores
        founders_cursor = db.collections['founders'].find({})
        for founder in founders_cursor:
            founder.pop('_id', None)
            backup_data['founders'].append(founder)

        await processing_msg.edit_text(
            "📦 **CREANDO RESPALDO...**\n\n"
            "💾 Generando archivos JSON...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Crear archivos de respaldo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        import json

        # Respaldo completo
        full_backup_file = f"backup_full_{timestamp}.json"
        with open(full_backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        # Respaldo solo usuarios (más ligero)
        users_backup_file = f"backup_users_{timestamp}.json"
        with open(users_backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'backup_info': backup_data['backup_info'],
                'users': backup_data['users']
            }, f, indent=2, ensure_ascii=False)

        # Respaldo configuración crítica
        config_backup_file = f"backup_config_{timestamp}.json"
        with open(config_backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'backup_info': backup_data['backup_info'],
                'staff': backup_data['staff'],
                'founders': backup_data['founders'],
                'stats': backup_data['stats']
            }, f, indent=2, ensure_ascii=False)

        # Estadísticas del respaldo
        total_users = len(backup_data['users'])
        total_staff = len(backup_data['staff'])
        total_founders = len(backup_data['founders'])

        await processing_msg.edit_text(
            "📦 **CREANDO RESPALDO...**\n\n"
            "📤 Enviando archivos JSON...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Enviar archivos como documentos descargables
        try:
            # Enviar respaldo completo
            with open(full_backup_file, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=full_backup_file,
                    caption=f"📦 **RESPALDO COMPLETO**\n\n"
                           f"📊 Usuarios: {total_users}\n"
                           f"👮 Staff: {total_staff}\n"
                           f"👑 Fundadores: {total_founders}\n"
                           f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                           f"💡 Archivo completo con todos los datos",
                    parse_mode=ParseMode.MARKDOWN
                )

            # Enviar respaldo de usuarios
            with open(users_backup_file, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=users_backup_file,
                    caption=f"👥 **RESPALDO DE USUARIOS**\n\n"
                           f"📊 Total usuarios: {total_users}\n"
                           f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                           f"💡 Solo datos de usuarios (archivo más ligero)",
                    parse_mode=ParseMode.MARKDOWN
                )

            # Enviar respaldo de configuración
            with open(config_backup_file, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=config_backup_file,
                    caption=f"⚙️ **RESPALDO DE CONFIGURACIÓN**\n\n"
                           f"👮 Staff: {total_staff}\n"
                           f"👑 Fundadores: {total_founders}\n"
                           f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                           f"💡 Solo configuración crítica del bot",
                    parse_mode=ParseMode.MARKDOWN
                )

            # Mensaje final de confirmación
            await processing_msg.edit_text(
                "✅ **RESPALDO COMPLETADO** ✅\n\n"
                "📤 **Archivos enviados:**\n"
                "• Respaldo completo\n"
                "• Respaldo de usuarios\n"
                "• Respaldo de configuración\n\n"
                f"📊 **Datos extraídos:**\n"
                f"👥 Usuarios: {total_users}\n"
                f"👮 Staff: {total_staff}\n"
                f"👑 Fundadores: {total_founders}\n\n"
                f"⏰ **Completado:** {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"💡 **Para Render:** Los archivos JSON están listos para usar",
                parse_mode=ParseMode.MARKDOWN
            )

        except Exception as upload_error:
            logger.error(f"Error enviando archivos: {upload_error}")
            await processing_msg.edit_text(
                f"⚠️ **RESPALDO CREADO CON ADVERTENCIA** ⚠️\n\n"
                f"✅ Los archivos JSON se generaron correctamente:\n"
                f"• `{full_backup_file}`\n"
                f"• `{users_backup_file}`\n"
                f"• `{config_backup_file}`\n\n"
                f"❌ Error enviando archivos: {str(upload_error)[:100]}...\n\n"
                f"💡 Los archivos están guardados en el servidor",
                parse_mode=ParseMode.MARKDOWN
            )

        # Limpiar archivos temporales después de enviar
        try:
            import os
            os.remove(full_backup_file)
            os.remove(users_backup_file)
            os.remove(config_backup_file)
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales: {cleanup_error}")

        # Log de la acción
        db.log_action(user_id, "database_backup", {
            "files_created": [full_backup_file, users_backup_file, config_backup_file],
            "total_users": total_users,
            "total_staff": total_staff,
            "total_founders": total_founders,
            "backup_sent_via_telegram": True
        })

    except Exception as e:
        logger.error(f"Error creando respaldo: {e}")
        await processing_msg.edit_text(
            f"❌ **ERROR EN RESPALDO** ❌\n\n"
            f"🔴 **Error:** {str(e)[:100]}...\n\n"
            f"💡 Verifica la conexión con MongoDB y vuelve a intentar",
            parse_mode=ParseMode.MARKDOWN
        )

async def mongodb_render_backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /renderbackup - Crear respaldo específico para Render"""
    from telegram_bot import db, ADMIN_IDS

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Solo administradores pueden hacer backup
    if user_id_int not in ADMIN_IDS:
        await update.message.reply_text("❌ Solo administradores pueden crear respaldos para Render")
        return

    processing_msg = await update.message.reply_text(
        "🚀 **CREANDO RESPALDO PARA RENDER** 🚀\n\n"
        "⏳ Preparando datos para migración...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Verificar conexión
        if not await db.ensure_connection():
            await processing_msg.edit_text(
                "❌ **ERROR DE CONEXIÓN**\n\n"
                "🔴 No se puede conectar a MongoDB para crear respaldo",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        await processing_msg.edit_text(
            "🚀 **CREANDO RESPALDO PARA RENDER** 🚀\n\n"
            "📊 Extrayendo todos los datos...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Extraer TODOS los datos necesarios para Render
        render_backup = {
            'migration_info': {
                'created_at': datetime.now().isoformat(),
                'created_by': user_id,
                'version': '2.0',
                'platform': 'render',
                'bot_name': 'ChernobilChLv Bot',
                'description': 'Respaldo completo para migración a Render',
                'mongodb_collections': list(db.collections.keys())
            },
            'users': {},  # Formato compatible con JSON original
            'staff_roles': {},
            'founders_list': [],
            'bot_stats': db.get_stats(),
            'raw_data': {
                'users_collection': [],
                'staff_collection': [],
                'founders_collection': [],
                'logs_sample': []  # Solo últimos 100 logs para no hacer el archivo demasiado grande
            }
        }

        # Extraer usuarios en formato compatible
        users_cursor = db.collections['users'].find({})
        for user in users_cursor:
            user_id_key = user['user_id']
            user.pop('_id', None)
            user.pop('user_id', None)  # Se usa como key
            render_backup['users'][user_id_key] = user
            render_backup['raw_data']['users_collection'].append({
                'user_id': user_id_key,
                **user
            })

        # Extraer staff
        staff_cursor = db.collections['staff'].find({})
        for staff in staff_cursor:
            staff_user_id = staff['user_id']
            staff.pop('_id', None)
            render_backup['staff_roles'][staff_user_id] = staff
            render_backup['raw_data']['staff_collection'].append(staff)

        # Extraer fundadores
        founders_cursor = db.collections['founders'].find({})
        for founder in founders_cursor:
            founder.pop('_id', None)
            render_backup['founders_list'].append(founder['user_id'])
            render_backup['raw_data']['founders_collection'].append(founder)

        # Extraer muestra de logs (últimos 100)
        logs_cursor = db.collections['logs'].find({}).sort('timestamp', -1).limit(100)
        for log in logs_cursor:
            log.pop('_id', None)
            render_backup['raw_data']['logs_sample'].append(log)

        await processing_msg.edit_text(
            "🚀 **CREANDO RESPALDO PARA RENDER** 🚀\n\n"
            "💾 Generando archivo JSON optimizado...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Crear archivo específico para Render
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        render_file = f"render_migration_{timestamp}.json"

        import json
        with open(render_file, 'w', encoding='utf-8') as f:
            json.dump(render_backup, f, indent=2, ensure_ascii=False)

        # También crear un bot_data.json compatible para fácil restauración
        bot_data_file = f"bot_data_render_{timestamp}.json"
        with open(bot_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'users': render_backup['users'],
                'staff_roles': render_backup['staff_roles'],
                'founders': render_backup['founders_list'],
                'bot_stats': render_backup['bot_stats']
            }, f, indent=2, ensure_ascii=False)

        # Estadísticas
        total_users = len(render_backup['users'])
        total_staff = len(render_backup['staff_roles'])
        total_founders = len(render_backup['founders_list'])

        await processing_msg.edit_text(
            "🚀 **CREANDO RESPALDO PARA RENDER** 🚀\n\n"
            "📤 Enviando archivos optimizados...",
            parse_mode=ParseMode.MARKDOWN
        )

        # Enviar archivo principal de migración
        with open(render_file, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=render_file,
                caption=f"🚀 **RESPALDO PARA RENDER** 🚀\n\n"
                       f"📊 **Datos incluidos:**\n"
                       f"👥 Usuarios: {total_users}\n"
                       f"👮 Staff: {total_staff}\n"
                       f"👑 Fundadores: {total_founders}\n"
                       f"📝 Logs de muestra: {len(render_backup['raw_data']['logs_sample'])}\n\n"
                       f"💡 **Archivo completo para migración a Render**\n"
                       f"🔧 **Incluye:** Datos raw + formato compatible",
                parse_mode=ParseMode.MARKDOWN
            )

        # Enviar bot_data.json compatible
        with open(bot_data_file, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=bot_data_file,
                caption=f"📁 **BOT_DATA COMPATIBLE** 📁\n\n"
                       f"📊 Formato: JSON tradicional\n"
                       f"🔧 Compatible con: Sistema de archivos JSON\n"
                       f"💡 Úsalo como `bot_data.json` en Render\n\n"
                       f"⚡ **Listo para usar directamente**",
                parse_mode=ParseMode.MARKDOWN
            )

        # Instrucciones para Render
        instructions = (
            "📋 **INSTRUCCIONES PARA RENDER** 📋\n\n"
            "**1. Configurar variables de entorno:**\n"
            "• `BOT_TOKEN` - Token del bot\n"
            "• `MONGODB_URL` - URL de MongoDB Atlas\n"
            "• `MONGODB_DB_NAME` - Nombre de la base de datos\n\n"
            "**2. Subir archivos:**\n"
            "• Sube el código del bot a tu repositorio\n"
            "• Los archivos JSON son para referencia/migración\n\n"
            "**3. Comando de inicio en Render:**\n"
            "`python telegram_bot.py` o `python run_bot.py`\n\n"
            "**4. Puerto recomendado:**\n"
            "No necesario para bots de Telegram\n\n"
            f"⏰ **Respaldo creado:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"🎯 **Listo para Render!**"
        )

        await update.message.reply_text(instructions, parse_mode=ParseMode.MARKDOWN)

        # Limpiar archivos temporales
        try:
            import os
            os.remove(render_file)
            os.remove(bot_data_file)
        except Exception as cleanup_error:
            logger.warning(f"Error limpiando archivos temporales: {cleanup_error}")

        # Log de la acción
        db.log_action(user_id, "render_backup", {
            "files_created": [render_file, bot_data_file],
            "total_users": total_users,
            "total_staff": total_staff,
            "total_founders": total_founders,
            "platform": "render"
        })

    except Exception as e:
        logger.error(f"Error creando respaldo para Render: {e}")
        await processing_msg.edit_text(
            f"❌ **ERROR EN RESPALDO RENDER** ❌\n\n"
            f"🔴 **Error:** {str(e)[:100]}...\n\n"
            f"💡 Verifica la conexión con MongoDB y vuelve a intentar",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_mongodb_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar callbacks de MongoDB"""
    from telegram_bot import db, ADMIN_IDS

    query = update.callback_query
    user_id = str(query.from_user.id)
    user_id_int = query.from_user.id

    # Responder al callback primero para evitar timeout
    await query.answer("⏳ Procesando...")

    # Verificar permisos usando ADMIN_IDS
    if user_id_int not in ADMIN_IDS:
        await query.edit_message_text("❌ Acceso denegado")
        return

    # Manejar confirmaciones de limpieza
    if query.data.startswith('confirm_cleanup_'):
        try:
            days = int(query.data.split('_')[2])
            
            await query.edit_message_text(
                f"🧹 **EJECUTANDO LIMPIEZA** 🧹\n\n"
                f"⏳ Eliminando datos de más de {days} días...\n"
                f"💥 Esto puede tomar unos momentos...",
                parse_mode=ParseMode.MARKDOWN
            )

            # Ejecutar limpieza
            deep_clean = days >= 60
            results = await db.cleanup_old_data(days, deep_clean=deep_clean)

            response = f"✅ **LIMPIEZA COMPLETADA** ✅\n\n"
            response += f"📊 **Resultados:**\n"
            response += f"• Logs eliminados: {results.get('logs_deleted', 0)}\n"
            response += f"• Sesiones eliminadas: {results.get('sessions_deleted', 0)}\n"
            response += f"• Usuarios inactivos: {results.get('inactive_users_deleted', 0)}\n\n"
            
            if deep_clean and 'all_logs_deleted' in results:
                response += f"• Logs profundos: {results.get('all_logs_deleted', 0)}\n"
                response += f"• Staff antiguo: {results.get('old_staff_deleted', 0)}\n\n"
            
            response += f"🗃️ **Período:** Datos > {days} días\n"
            response += f"⏰ **Completado:** {datetime.now().strftime('%H:%M:%S')}"

            await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)

        except ValueError:
            await query.edit_message_text("❌ Error en los parámetros de limpieza")
        except Exception as e:
            await query.edit_message_text(
                f"❌ **ERROR EN LIMPIEZA** ❌\n\n"
                f"🔴 **Error:** {str(e)[:100]}...\n\n"
                f"💡 Intenta nuevamente o contacta soporte",
                parse_mode=ParseMode.MARKDOWN
            )
        return

    if query.data == 'db_reconnect':
        await query.edit_message_text(
            "🔄 **RECONECTANDO...**\n⏳ Por favor espera...",
            parse_mode=ParseMode.MARKDOWN
        )

        await db.close_connection()
        await asyncio.sleep(1)
        success = await db.connect()

        if success:
            await query.edit_message_text(
                "✅ **RECONEXIÓN EXITOSA**\n\n"
                "🟢 MongoDB Atlas conectado correctamente",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ **ERROR EN RECONEXIÓN**\n\n"
                "🔴 No se pudo conectar a MongoDB Atlas",
                parse_mode=ParseMode.MARKDOWN
            )

    elif query.data == 'db_connect':
        await query.edit_message_text(
            "🔌 **CONECTANDO...**\n⏳ Estableciendo conexión...",
            parse_mode=ParseMode.MARKDOWN
        )

        success = await db.connect()

        if success:
            await query.edit_message_text(
                "✅ **CONEXIÓN ESTABLECIDA**\n\n"
                "🟢 MongoDB Atlas listo para usar",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ **ERROR DE CONEXIÓN**\n\n"
                "🔴 Verifica la configuración de MongoDB",
                parse_mode=ParseMode.MARKDOWN
            )

    elif query.data == 'db_cleanup':
        # Mostrar opciones de limpieza
        keyboard = [
            [
                InlineKeyboardButton("🗑️ 30 días", callback_data='cleanup_30'),
                InlineKeyboardButton("🗑️ 7 días", callback_data='cleanup_7')
            ],
            [InlineKeyboardButton("❌ Cancelar", callback_data='db_refresh')]
        ]

        await query.edit_message_text(
            "⚠️ **LIMPIEZA DE DATOS** ⚠️\n\n"
            "🗑️ Selecciona período de limpieza:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data.startswith('cleanup_'):
        if query.data == 'cleanup_cancel':
            await query.edit_message_text(
                "❌ **Limpieza cancelada**\n\n"
                "💡 Usa `/dbcleanup` para acceder nuevamente",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        try:
            days = int(query.data.split('_')[1])
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Error en la selección")
            return

        # Determinar tipo de limpieza
        cleanup_type = "LIMPIEZA PROFUNDA" if days >= 60 else "LIMPIEZA ESTÁNDAR"
        cleanup_description = "TODOS los datos antiguos" if days >= 60 else "datos básicos"

        # Mostrar confirmación antes de proceder
        confirm_keyboard = [
            [
                InlineKeyboardButton(f"✅ Confirmar ({days}d)", callback_data=f'confirm_cleanup_{days}'),
                InlineKeyboardButton("❌ Cancelar", callback_data='cleanup_cancel')
            ]
        ]

        await query.edit_message_text(
            f"⚠️ **CONFIRMAR {cleanup_type}** ⚠️\n\n"
            f"🗑️ **Período:** Más de {days} días\n"
            f"💥 **Se eliminará:** {cleanup_description}\n\n"
            f"📊 **Incluye:**\n"
            f"• Logs antiguos del sistema\n"
            f"• Sesiones expiradas\n"
            f"• Usuarios inactivos sin premium\n"
            + (f"• Datos de staff muy antiguos\n" if days >= 60 else "") +
            f"\n❓ **¿Confirmas la eliminación?**",
            reply_markup=InlineKeyboardMarkup(confirm_keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data.startswith('confirm_cleanup_'):
        try:
            days = int(query.data.split('_')[2])
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Error en la confirmación")
            return

        await query.edit_message_text(
            f"🧹 **LIMPIANDO DATOS...**\n\n"
            f"⏳ Eliminando datos de más de {days} días...\n"
            f"⚡ Por favor espera...",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            results = await db.cleanup_old_data(days)

            response = f"✅ **LIMPIEZA COMPLETADA** ✅\n\n"
            response += f"📊 **Resultados:**\n"
            response += f"• Logs eliminados: {results.get('logs_deleted', 0)}\n"
            response += f"• Sesiones eliminadas: {results.get('sessions_deleted', 0)}\n"
            response += f"• Usuarios inactivos: {results.get('inactive_users_deleted', 0)}\n\n"
            response += f"🗃️ **Período:** Datos > {days} días\n"
            response += f"⏰ **Completado:** {datetime.now().strftime('%H:%M:%S')}"

            await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            await query.edit_message_text(
                f"❌ **ERROR EN LIMPIEZA** ❌\n\n"
                f"🔴 **Error:** {str(e)[:100]}...\n\n"
                f"💡 Intenta nuevamente o contacta soporte",
                parse_mode=ParseMode.MARKDOWN
            )

    elif query.data == 'db_refresh':
        # Actualizar estado
        connection_info = db.get_connection_info()
        stats = db.get_stats()

        status_emoji = "🟢" if connection_info['connected'] else "🔴"
        status_text = "CONECTADO" if connection_info['connected'] else "DESCONECTADO"

        response = f"📊 **ESTADO ACTUALIZADO** 📊\n\n"
        response += f"🔗 **Estado:** {status_emoji} {status_text}\n"
        response += f"👥 **Usuarios:** {stats.get('total_users', 0)}\n"
        response += f"💎 **Premium:** {stats.get('premium_users', 0)}\n"
        response += f"📝 **Logs:** {stats.get('total_logs', 0)}\n\n"
        response += f"⏰ **Actualizado:** {datetime.now().strftime('%H:%M:%S')}"

        # Recrear botones
        keyboard = []
        if connection_info['connected']:
            keyboard.append([
                InlineKeyboardButton("🔄 Reconectar", callback_data='db_reconnect'),
                InlineKeyboardButton("🧹 Limpiar datos", callback_data='db_cleanup')
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🔌 Conectar", callback_data='db_connect')
            ])

        keyboard.append([
            InlineKeyboardButton("📊 Actualizar", callback_data='db_refresh'),
            InlineKeyboardButton("❌ Cerrar", callback_data='db_close')
        ])

        await query.edit_message_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

    elif query.data.startswith('deepclean_'):
        if query.data == 'deepclean_cancel':
            await query.edit_message_text(
                "❌ **Limpieza profunda cancelada**\n\n"
                "💡 Usa `/dbdeepclean` para acceder nuevamente",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        try:
            parts = query.data.split('_')
            collection = parts[1]
            days = int(parts[2])
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Error en los parámetros")
            return

        await query.edit_message_text(
            f"🗑️ **EJECUTANDO LIMPIEZA PROFUNDA** 🗑️\n\n"
            f"⏳ Eliminando datos de {collection} > {days} días...\n"
            f"💥 Procesando eliminación permanente...",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            if collection == 'all':
                # Limpiar todas las colecciones
                results = await db.cleanup_old_data(days, deep_clean=True)
                total_deleted = sum(results.values())

                response = f"✅ **LIMPIEZA PROFUNDA COMPLETADA** ✅\n\n"
                response += f"🗑️ **Resultados por colección:**\n"
                for key, count in results.items():
                    response += f"• {key.replace('_', ' ').title()}: {count}\n"
                response += f"\n💥 **Total eliminado:** {total_deleted} documentos\n"
                response += f"📅 **Período:** Datos > {days} días\n"
                response += f"⏰ **Completado:** {datetime.now().strftime('%H:%M:%S')}"
            else:
                # Limpiar colección específica
                results = await db.cleanup_specific_collection(collection, days=days)

                response = f"✅ **LIMPIEZA ESPECÍFICA COMPLETADA** ✅\n\n"
                response += f"🗑️ **Colección:** {collection}\n"
                response += f"💥 **Documentos eliminados:** {results.get('deleted_count', 0)}\n"
                response += f"📅 **Período:** > {days} días\n"
                response += f"⏰ **Completado:** {datetime.now().strftime('%H:%M:%S')}\n\n"
                response += f"🔍 **Criterios usados:** {results.get('criteria_used', 'N/A')}"

            await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            await query.edit_message_text(
                f"❌ **ERROR EN LIMPIEZA PROFUNDA** ❌\n\n"
                f"🔴 **Error:** {str(e)[:100]}...\n\n"
                f"💡 Verifica la conexión y vuelve a intentar",
                parse_mode=ParseMode.MARKDOWN
            )

    elif query.data == 'db_close':
        await query.edit_message_text(
            "❌ **Panel de MongoDB cerrado**\n\n"
            "💡 Usa `/dbstatus` para acceder nuevamente",
            parse_mode=ParseMode.MARKDOWN
        )
