
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

@bot_admin_only
async def security_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver estado de seguridad del bot"""
    security_logs = db.security_settings.get('security_logs', [])
    recent_logs = [
        log for log in security_logs[-100:]  # Últimos 100 logs
    ]
    
    # Estadísticas
    total_events = len(recent_logs)
    failed_commands = sum(1 for log in recent_logs if log['event_type'] == 'COMMAND_ERROR')
    permission_denials = sum(1 for log in recent_logs if log['event_type'] == 'PERMISSION_DENIED')
    blocked_attempts = sum(1 for log in recent_logs if log['event_type'] == 'BLOCKED_ACCESS_ATTEMPT')
    
    # Usuarios más activos
    user_activity = {}
    for log in recent_logs:
        user_id = log['user_id']
        user_activity[user_id] = user_activity.get(user_id, 0) + 1
    
    top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    
    response = f"🔒 **ESTADO DE SEGURIDAD** 🔒\n\n"
    response += f"📊 **Eventos recientes:** {total_events}\n"
    response += f"❌ **Comandos fallidos:** {failed_commands}\n"
    response += f"🚫 **Permisos denegados:** {permission_denials}\n"
    response += f"🛡️ **Accesos bloqueados:** {blocked_attempts}\n\n"
    
    if top_users:
        response += f"👥 **Usuarios más activos:**\n"
        for user_id, count in top_users:
            response += f"• `{user_id}`: {count} eventos\n"
    
    response += f"\n⏰ **Última actualización:** {datetime.now().strftime('%H:%M:%S')}"
    
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

@bot_admin_only 
async def grant_permission_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Otorgar permiso específico a usuario"""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "**Uso:** `/grant_permission [user_id] [permission]`\n\n"
            "**Permisos disponibles:**\n"
            "• `post_content` - Publicar contenido\n"
            "• `verify_cards` - Verificar tarjetas\n"
            "• `manage_users` - Gestionar usuarios\n"
            "• `send_links` - Enviar enlaces\n"
            "• `bypass_rate_limit` - Bypass de límites",
            parse_mode=ParseMode.MARKDOWN)
        return
    
    user_id = args[0]
    permission = args[1]
    
    if not db.validate_user_id(user_id):
        await update.message.reply_text("❌ ID de usuario inválido")
        return
    
    db.set_user_permission(user_id, permission, True)
    
    response = f"✅ **PERMISO OTORGADO** ✅\n\n"
    response += f"👤 **Usuario:** `{user_id}`\n"
    response += f"🔐 **Permiso:** `{permission}`\n"
    response += f"👮‍♂️ **Otorgado por:** {update.effective_user.first_name}\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

@bot_admin_only
async def security_lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bloquear usuario por seguridad"""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "**Uso:** `/security_lock [user_id] [duration_minutes] [reason]`\n\n"
            "**Ejemplo:** `/security_lock 123456789 60 Actividad sospechosa`",
            parse_mode=ParseMode.MARKDOWN)
        return
    
    user_id = args[0]
    duration = int(args[1]) if args[1].isdigit() else 30
    reason = ' '.join(args[2:]) if len(args) > 2 else "Bloqueo de seguridad"
    
    db.lock_user(user_id, duration, reason)
    
    response = f"🔒 **USUARIO BLOQUEADO** 🔒\n\n"
    response += f"👤 **Usuario:** `{user_id}`\n"
    response += f"⏰ **Duración:** {duration} minutos\n"
    response += f"📝 **Razón:** {reason}\n"
    response += f"👮‍♂️ **Bloqueado por:** {update.effective_user.first_name}"
    
    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
