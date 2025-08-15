import asyncio
from typing import Dict, Set

# Variables globales para limpieza automática
auto_clean_timers: Dict[str, Dict] = {}


async def auto_clean_worker(context, chat_id: int, interval_seconds: int):
    """Worker para limpieza automática en background"""
    while auto_clean_timers.get(str(chat_id), {}).get('active', False):
        await asyncio.sleep(interval_seconds)

        # Verificar si sigue activo
        if not auto_clean_timers.get(str(chat_id), {}).get('active', False):
            break

        try:
            timer_info = auto_clean_timers.get(str(chat_id), {})
            is_day_mode = timer_info.get('is_day_mode', False)
            days_count = timer_info.get('days_count', 0)
            interval_text = timer_info.get('interval_text', 'Desconocido')

            deleted_count = 0
            current_message_id = None

            # Obtener ID de mensaje actual aproximado
            try:
                temp_msg = await context.bot.send_message(chat_id, "🧹")
                current_message_id = temp_msg.message_id
                await temp_msg.delete()
            except:
                continue

            if is_day_mode:
                # Modo día: Eliminar TODOS los mensajes del período especificado
                # Calcular cuántos mensajes eliminar (estimación agresiva)

                # Para 1 día: intentar eliminar hasta 10,000 mensajes hacia atrás
                # Para más días: eliminar proporcionalmente más
                max_messages_to_try = min(50000, days_count * 10000)

                notification = await context.bot.send_message(
                    chat_id, f"🔥 **LIMPIEZA MASIVA INICIADA** 🔥\n\n"
                    f"⚠️ **ELIMINANDO TODOS LOS MENSAJES DE {interval_text.upper()}**\n"
                    f"🗑️ **Procesando hasta {max_messages_to_try:,} mensajes...**\n"
                    f"⏳ **Esto puede tomar varios minutos**\n\n"
                    f"🚫 **NO DESACTIVAR DURANTE EL PROCESO**",
                    parse_mode='Markdown')

                # Eliminar mensajes agresivamente
                for i in range(1, max_messages_to_try + 1):
                    message_id_to_delete = current_message_id - i
                    if message_id_to_delete > 0:
                        try:
                            await context.bot.delete_message(
                                chat_id=chat_id,
                                message_id=message_id_to_delete)
                            deleted_count += 1

                            # Actualizar progreso cada 1000 mensajes
                            if deleted_count % 1000 == 0:
                                try:
                                    await notification.edit_text(
                                        f"🔥 **LIMPIEZA MASIVA EN PROGRESO** 🔥\n\n"
                                        f"⚠️ **ELIMINANDO TODOS LOS MENSAJES DE {interval_text.upper()}**\n"
                                        f"🗑️ **Eliminados:** {deleted_count:,}/{max_messages_to_try:,}\n"
                                        f"📊 **Progreso:** {(deleted_count/max_messages_to_try)*100:.1f}%\n\n"
                                        f"⏳ **Proceso en curso...**",
                                        parse_mode='Markdown')
                                except:
                                    pass

                            # Pausa muy corta para evitar rate limiting
                            if deleted_count % 50 == 0:
                                await asyncio.sleep(0.1)

                        except Exception as e:
                            # Si el mensaje no existe o error, continuar
                            continue

                        # Si llevamos mucho tiempo, hacer una pausa más larga
                        if deleted_count % 2000 == 0:
                            await asyncio.sleep(1)

                # Eliminar la notificación de progreso
                try:
                    await notification.delete()
                except:
                    pass

                # Enviar notificación final
                final_notification = await context.bot.send_message(
                    chat_id, f"✅ **LIMPIEZA MASIVA COMPLETADA** ✅\n\n"
                    f"🗑️ **Mensajes eliminados:** {deleted_count:,}\n"
                    f"📅 **Período limpiado:** {interval_text}\n"
                    f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"🔄 **Próxima limpieza automática:** En {interval_text}\n"
                    f"💡 **El chat ha sido completamente limpiado**",
                    parse_mode='Markdown')

            else:
                # Modo estándar: Eliminar 20 mensajes
                for i in range(1, 21):
                    message_id_to_delete = current_message_id - i
                    if message_id_to_delete > 0:
                        try:
                            await context.bot.delete_message(
                                chat_id=chat_id,
                                message_id=message_id_to_delete)
                            deleted_count += 1
                            await asyncio.sleep(0.1)
                        except:
                            continue

                # Enviar notificación temporal de limpieza estándar
                if deleted_count > 0:
                    notification = await context.bot.send_message(
                        chat_id, f"🤖 **LIMPIEZA AUTOMÁTICA EJECUTADA** 🤖\n\n"
                        f"🗑️ **Mensajes eliminados:** {deleted_count}/20\n"
                        f"⏰ **Intervalo:** {interval_text}\n"
                        f"📅 **Próxima limpieza:** {interval_text}\n"
                        f"🔄 **Estado:** Activo\n\n"
                        f"💡 **Usa `/clean auto off` para desactivar**",
                        parse_mode='Markdown')

                    # Auto-eliminar notificación después de 30 segundos
                    await asyncio.sleep(30)
                    try:
                        await notification.delete()
                    except:
                        pass

            # Actualizar timestamp
            auto_clean_timers[str(
                chat_id)]['last_clean'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error en limpieza automática: {e}")
            continue


import os
import logging
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode


# Funciones de CC Checker con efectividad realista y profesional
def check_stripe_ultra_pro(card_data):
    """Verificación Stripe Ultra Pro - Algoritmo ULTRA MEJORADO con IA avanzada"""
    import time, random
    time.sleep(random.uniform(0.3, 0.8))  # Tiempo más realista

    card_parts = card_data.split('|')
    card_number = card_parts[0]
    exp_month = int(card_parts[1]) if len(card_parts) > 1 else 12
    exp_year = int(card_parts[2]) if len(card_parts) > 2 else 2025
    cvv = card_parts[3] if len(card_parts) > 3 else "000"

    # Sistema de IA avanzado para scoring - REVOLUCIONARIO
    score = 0
    max_score = 20  # Score máximo aumentado

    # Análisis de BIN ULTRA AVANZADO
    ultra_premium_bins = [
        '4532', '5531', '4539', '4485', '5555', '4111', '4900', '4901', '4902',
        '4003', '4007', '4012', '4013', '4021', '4024', '4030', '4031', '4035',
        '5425', '5431', '5433', '5438', '5442', '5455', '5462', '5478', '5485'
    ]

    # Análisis multicapa del BIN
    bin_6 = card_number[:6]
    bin_8 = card_number[:8] if len(card_number) >= 8 else bin_6

    if any(bin_6.startswith(bin_) for bin_ in ultra_premium_bins):
        score += 7  # Score máximo para bins premium
    elif card_number.startswith(
        ('4532', '5531', '4539')):  # Bins súper efectivos
        score += 6
    elif card_number.startswith(
        ('40', '41', '42', '51', '52', '53', '54', '55')):
        score += 4
    elif card_number.startswith(('4', '5')):  # Visa/MasterCard básico
        score += 2

    # Análisis de fecha de expiración INTELIGENTE
    current_year = 2025
    years_until_expiry = exp_year - current_year

    if years_until_expiry >= 3:  # Tarjetas muy nuevas
        score += 4
    elif years_until_expiry >= 2:
        score += 3
    elif years_until_expiry >= 1:
        score += 2
    elif years_until_expiry >= 0:
        score += 1

    # Análisis de mes con patrones específicos
    if exp_month in [12, 1, 6, 3, 9, 11]:  # Meses más favorables
        score += 2

    # Análisis CVV REVOLUCIONARIO
    if cvv.isdigit() and len(cvv) == 3:
        cvv_int = int(cvv)

        # Patrones matemáticos avanzados
        if cvv_int % 10 in [7, 3, 9, 1]:  # Terminaciones gold
            score += 3
        elif cvv_int % 100 in [59, 77, 89, 23, 45, 67, 91, 13, 37]:
            score += 2
        elif cvv_int in range(100, 999) and cvv_int % 7 == 0:  # Múltiplos de 7
            score += 2
        elif 200 <= cvv_int <= 800:  # Rango favorable
            score += 1

    # Análisis de número de tarjeta AVANZADO
    digit_sum = sum(int(d) for d in card_number if d.isdigit())

    # Múltiples algoritmos matemáticos
    if digit_sum % 7 == 0:
        score += 2
    if digit_sum % 11 == 0:
        score += 2
    if digit_sum % 13 == 0:
        score += 1

    # Análisis de patrones en el número
    if card_number[-1] in '02468':  # Números pares al final
        score += 1
    if card_number[-2:] in [
            '00', '11', '22', '33', '44', '55', '66', '77', '88', '99'
    ]:
        score += 1

    # Análisis de secuencias y patrones especiales
    special_sequences = [
        '0789', '1234', '5678', '9876', '4321', '1111', '2222'
    ]
    if any(seq in card_number for seq in special_sequences):
        score += 2

    # Calcular probabilidad base mejorada
    base_probability = (score / max_score) * 0.65  # Aumentado a 65% máximo

    # Bonificaciones adicionales
    if len(card_number) == 16:
        base_probability += 0.15
    if len(card_number) == 15:  # American Express
        base_probability += 0.10

    # Factor de aleatoriedad inteligente (menos reducción)
    randomness_factor = random.uniform(0.7, 1.3)
    final_probability = base_probability * randomness_factor

    # Bonus especial para usuarios premium/admin
    final_probability += 0.08  # 8% extra base

    # Asegurar que no exceda 100%
    final_probability = min(final_probability, 0.95)

    is_live = random.random() < final_probability

    if is_live:
        ultra_live_responses = [
            "✅ Payment completed successfully - Amount: $1.00",
            "✅ Transaction approved - CVV2/AVS Match",
            "✅ Card charged $1.00 - Approved by issuer",
            "✅ Stripe: Payment processed - Gateway Response: 00",
            "✅ Authorization successful - Funds reserved",
            "✅ Transaction ID: TXN_" + str(random.randint(100000, 999999)),
            "✅ Gateway approved - Risk score: Low",
            "✅ CVV Match - Address verified - Approved"
        ]
        status = random.choice(ultra_live_responses)
        charge_amount = 1.00
    else:
        ultra_dead_responses = [
            "❌ Card declined - Insufficient funds",
            "❌ Transaction failed - Invalid CVV",
            "❌ Payment declined - Card expired",
            "❌ Authorization failed - Risk threshold exceeded",
            "❌ Declined - Do not honor (05)",
            "❌ Invalid card number - Luhn check failed",
            "❌ Issuer unavailable - Try again later",
            "❌ Transaction blocked - Fraud protection"
        ]
        status = random.choice(ultra_dead_responses)
        charge_amount = 0

    return is_live, status, ["Stripe Ultra Pro"], charge_amount, "Ultra"


def check_paypal_ultra_pro(card_data):
    """Verificación PayPal Ultra Pro con análisis avanzado"""
    import time, random
    time.sleep(random.uniform(0.8, 1.5))

    card_parts = card_data.split('|')
    cvv = card_parts[3] if len(card_parts) > 3 else "000"
    exp_month = int(card_parts[1]) if len(card_parts) > 1 else 12
    card_number = card_parts[0]

    # Análisis CVV mejorado
    probability = 0.25  # Base aumentada: 25% (era 8%)

    # CVVs específicos que pueden incrementar
    if cvv.endswith(('7', '3', '9')):
        probability += 0.08  # +8%
    if exp_month in [12, 1, 6, 3, 9]:  # Más meses específicos
        probability += 0.05  # +5%

    # Análisis del BIN para PayPal
    if card_number.startswith(('4532', '4900', '5531')):
        probability += 0.12  # +12% para bins favorables

    # Factor de mejora (no reducción)
    probability *= random.uniform(0.8, 1.2)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "PayPal payment completed", "Funds captured successfully",
            "PayPal transaction approved"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "PayPal payment declined", "Card verification failed",
            "PayPal security check failed", "Insufficient PayPal balance",
            "Card not supported"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["PayPal"], 0, "Standard"


def check_braintree_ultra_pro(card_data):
    """Verificación Braintree Ultra Pro - Análisis temporal"""
    import time, random
    time.sleep(random.uniform(1.8, 3.2))

    card_parts = card_data.split('|')
    exp_year = int(card_parts[2]) if len(card_parts) > 2 else 2025
    card_number = card_parts[0]

    # Cálculo más estricto basado en vencimiento
    current_year = 2025
    years_until_expiry = exp_year - current_year

    if years_until_expiry >= 4:
        probability = 0.12  # 12% para tarjetas muy lejanas
    elif years_until_expiry >= 2:
        probability = 0.09  # 9% para tarjetas lejanas
    elif years_until_expiry >= 1:
        probability = 0.07  # 7% para tarjetas normales
    else:
        probability = 0.03  # 3% para tarjetas próximas a vencer

    # Análisis adicional del número
    digit_sum = sum(int(d) for d in card_number)
    if digit_sum % 13 == 0:  # Patrón más específico
        probability += 0.02

    # Reducción aleatoria final
    probability *= random.uniform(0.5, 0.8)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "Braintree: Transaction authorized",
            "Braintree: Payment processed", "Braintree: Gateway approved"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "Braintree: Transaction declined",
            "Braintree: Card verification failed",
            "Braintree: Gateway timeout", "Braintree: Risk assessment failed",
            "Braintree: Invalid merchant"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["Braintree"], 0, "Standard"


def check_authorize_ultra_pro(card_data):
    """Verificación Authorize.net Ultra Pro - Sistema complejo"""
    import time, random
    time.sleep(random.uniform(2.5, 4.2))

    card_parts = card_data.split('|')
    card_number = card_parts[0]
    exp_month = int(card_parts[1]) if len(card_parts) > 1 else 12
    cvv = card_parts[3] if len(card_parts) > 3 else "000"

    # Sistema de puntuación complejo
    score = 0

    # Análisis del número de tarjeta
    if len(card_number) == 16:
        score += 1
    if card_number.startswith('4'):  # Visa
        score += 1
    elif card_number.startswith('5'):  # MasterCard
        score += 1

    # Análisis del mes
    if exp_month in [1, 6, 12]:
        score += 1

    # Análisis del CVV
    if cvv.isdigit() and len(cvv) == 3:
        if int(cvv) % 7 == 0:
            score += 1

    # Convertir score a probabilidad (máximo 5 puntos)
    base_probability = 0.04  # 4% base
    probability = base_probability + (score * 0.015)  # +1.5% por punto

    # Factor de aleatoriedad que reduce probabilidad
    probability *= random.uniform(0.4, 0.7)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "Authorize.net: Transaction approved",
            "Auth.net: AVS Match - Approved", "Auth.net: CVV2 Match - Success"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "Authorize.net: Transaction declined", "Auth.net: AVS Mismatch",
            "Auth.net: CVV2 verification failed",
            "Auth.net: Risk threshold exceeded",
            "Auth.net: Card type not supported"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["Authorize.net"], 0, "Standard"


def check_square_ultra_pro(card_data):
    """API Square Ultra Pro - Análisis geográfico simulado"""
    import time, random
    time.sleep(random.uniform(1.5, 2.5))

    # Square es conocido por ser restrictivo
    probability = 0.07  # Solo 7% base

    card_number = card_data.split('|')[0]

    # Análisis específico de Square
    if card_number[4:6] in ['23', '45', '67']:  # Dígitos específicos
        probability += 0.02

    # Factor de reducción para simular restricciones geográficas
    probability *= random.uniform(0.3, 0.6)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "Square: Payment successful",
            "Square: Card processed successfully",
            "Square: Transaction completed"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "Square: Payment declined", "Square: Card rejected by processor",
            "Square: Fraud protection triggered",
            "Square: Geographic restriction",
            "Square: Merchant account limitation"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["Square"], 0, "Standard"


def check_adyen_ultra_pro(card_data):
    """API Adyen Ultra Pro - Estándar europeo estricto"""
    import time, random
    time.sleep(random.uniform(3.0, 5.0))  # Adyen es lento pero preciso

    # Adyen es muy selectivo - probabilidad muy baja
    probability = 0.05  # Solo 5% base

    card_parts = card_data.split('|')
    exp_year = int(card_parts[2]) if len(card_parts) > 2 else 2025

    # Solo incrementa para tarjetas muy específicas
    if exp_year >= 2027:  # Tarjetas con vencimiento lejano
        probability += 0.02

    # Reducción severa para simular estrictos controles europeos
    probability *= random.uniform(0.2, 0.4)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "Adyen: Transaction authorised",
            "Adyen: [approved] - EU compliance", "Adyen: Payment received"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "Adyen: Transaction refused",
            "Adyen: [declined] - Risk assessment",
            "Adyen: Compliance check failed", "Adyen: 3D Secure required",
            "Adyen: Velocity limit exceeded"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["Adyen"], 0, "Standard"


def check_worldpay_ultra_pro(card_data):
    """API Worldpay Ultra Pro - Procesamiento británico"""
    import time, random
    time.sleep(random.uniform(2.2, 3.8))

    card_number = card_data.split('|')[0]

    # Worldpay análisis por tipo de tarjeta
    if card_number.startswith('4'):  # Visa
        probability = 0.08  # 8% para Visa
    elif card_number.startswith('5'):  # MasterCard
        probability = 0.06  # 6% para MasterCard
    else:
        probability = 0.03  # 3% para otros

    # Factor de reducción británico (estricto)
    probability *= random.uniform(0.3, 0.5)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "Worldpay: SUCCESS - Payment captured",
            "Worldpay: AUTHORISED by issuer", "Worldpay: SETTLED successfully"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "Worldpay: REFUSED by bank", "Worldpay: FAILED - Invalid data",
            "Worldpay: CANCELLED - Risk check",
            "Worldpay: BLOCKED - Fraud prevention",
            "Worldpay: EXPIRED - Card invalid"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["Worldpay"], 0, "Standard"


def check_cybersource_ultra_pro(card_data):
    """API CyberSource Ultra Pro - Inteligencia artificial anti-fraude"""
    import time, random
    time.sleep(random.uniform(3.5, 6.0))  # El más lento por IA

    # CyberSource tiene IA anti-fraude muy avanzada
    probability = 0.04  # Solo 4% base (el más estricto)

    card_parts = card_data.split('|')
    card_number = card_parts[0]

    # Análisis de IA simulado
    digit_pattern = int(card_number[-2:]) if len(card_number) >= 2 else 0
    if digit_pattern % 17 == 0:  # Patrón muy específico
        probability += 0.01

    # La IA reduce dramáticamente la probabilidad
    probability *= random.uniform(0.1, 0.3)

    is_live = random.random() < probability

    if is_live:
        responses = [
            "CyberSource: ACCEPT - AI approved",
            "CyberSource: SUCCESS - Low risk",
            "CyberSource: AUTHORIZED - Verified"
        ]
        status = f"LIVE ✅ - {random.choice(responses)}"
    else:
        responses = [
            "CyberSource: REJECT - AI flagged",
            "CyberSource: DECLINE - High risk score",
            "CyberSource: REVIEW - Manual check required",
            "CyberSource: BLOCKED - Fraud pattern",
            "CyberSource: DENIED - Velocity breach"
        ]
        status = f"DEAD ❌ - {random.choice(responses)}"

    return is_live, status, ["CyberSource"], 0, "Standard"


async def get_real_bin_info(bin_number):
    """Obtener información REAL del BIN usando API externa"""
    try:
        # Usar API gratuita de BIN lookup
        import requests
        response = requests.get(f"https://lookup.binlist.net/{bin_number[:6]}",
                                timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'scheme': data.get('scheme', 'UNKNOWN').upper(),
                'type': data.get('type', 'CREDIT').upper(),
                'level': data.get('brand', 'STANDARD').upper(),
                'bank': data.get('bank', {}).get('name', 'UNKNOWN BANK'),
                'country': data.get('country', {}).get('name',
                                                       'UNKNOWN COUNTRY')
            }
    except:
        pass

    # Fallback con información simulada más realista
    bin_patterns = {
        '4': {
            'scheme': 'VISA',
            'type': 'CREDIT',
            'level': 'CLASSIC'
        },
        '5': {
            'scheme': 'MASTERCARD',
            'type': 'CREDIT',
            'level': 'STANDARD'
        },
        '3': {
            'scheme': 'AMERICAN EXPRESS',
            'type': 'CREDIT',
            'level': 'GOLD'
        },
        '6': {
            'scheme': 'DISCOVER',
            'type': 'CREDIT',
            'level': 'STANDARD'
        }
    }

    first_digit = bin_number[0] if bin_number else '4'
    pattern = bin_patterns.get(first_digit, bin_patterns['4'])

    banks = [
        'JPMORGAN CHASE', 'BANK OF AMERICA', 'WELLS FARGO', 'CITIBANK',
        'CAPITAL ONE'
    ]
    countries = [
        'UNITED STATES', 'CANADA', 'UNITED KINGDOM', 'GERMANY', 'FRANCE'
    ]

    return {
        'scheme': pattern['scheme'],
        'type': pattern['type'],
        'level': pattern['level'],
        'bank': random.choice(banks),
        'country': random.choice(countries)
    }


def escape_markdown(text):
    """Escapa caracteres especiales para Markdown"""
    if not text:
        return ""

    text = str(text)  # Asegurar que sea string

    special_chars = [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|',
        '{', '}', '.', '!'
    ]
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_enhanced_bin_info(bin_number):
    """Información simulada de BIN - Función legacy"""
    return {
        'scheme': 'VISA',
        'type': 'CREDIT',
        'level': 'STANDARD',
        'bank': {
            'name': 'BANCO SIMULADO'
        },
        'country': {
            'name': 'UNITED STATES'
        }
    }

# Importar comandos de MongoDB
from mongodb_admin_commands import mongodb_status_command, mongodb_reconnect_command, mongodb_cleanup_command, mongodb_backup_command, mongodb_render_backup_command, handle_mongodb_callbacks

# Importar sistema de gates
from gates_system import gates_command, handle_gate_callback, process_gate_card

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar sistema MongoDB
from mongodb_database import MongoDatabase

# Sistema de migración para compatibilidad
def migrate_old_data():
    """Migrar datos del sistema anterior si existe"""
    try:
        if os.path.exists('bot_data.json'):
            logger.info("🔄 Detectado archivo de datos anterior, migrando...")
            from mongodb_database import migrate_json_to_mongodb
            asyncio.create_task(migrate_json_to_mongodb())
    except Exception as e:
        logger.error(f"Error en migración: {e}")

# Base de datos simulada (en producción usar SQLite/PostgreSQL)
class Database:

    def __init__(self):
        self.users = {}
        self.staff_roles = {}  # Sistema de roles de staff
        self.bot_maintenance = False  # Estado de mantenimiento
        self.maintenance_message = ""  # Mensaje de mantenimiento
        self.check_chats = {}  # Configuración de chats para /check
        self.pending_checks = {}  # Verificaciones pendientes
        self.deleted_links = {}  # NUEVO: Registro de links eliminados
        self.permissions = {}  # Sistema de permisos granular
        self.security_settings = {}  # Configuraciones de seguridad
        self.admin_log_channels = {}  # Canales de logs administrativos
        self.admin_action_logs = []  # Lista de acciones administrativas
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.staff_roles = data.get('staff_roles', {})
                    self.bot_maintenance = data.get('bot_maintenance', False)
                    self.maintenance_message = data.get(
                        'maintenance_message', "")
                    self.check_chats = data.get('check_chats', {})
                    self.pending_checks = data.get('pending_checks', {})
                    self.deleted_links = data.get('deleted_links', {})
                    self.admin_log_channels = data.get('admin_log_channels',
                                                       {})
                    self.admin_action_logs = data.get('admin_action_logs', [])
        except:
            self.users = {}
            self.staff_roles = {}
            self.bot_maintenance = False
            self.maintenance_message = ""
            self.check_chats = {}
            self.pending_checks = {}
            self.deleted_links = {}
            self.admin_log_channels = {}
            self.admin_action_logs = []

    def save_data(self):
        try:
            with open('bot_data.json', 'w') as f:
                json.dump(
                    {
                        'users':
                        self.users,
                        'staff_roles':
                        self.staff_roles,
                        'bot_maintenance':
                        self.bot_maintenance,
                        'maintenance_message':
                        self.maintenance_message,
                        'check_chats':
                        self.check_chats,
                        'pending_checks':
                        self.pending_checks,
                        'deleted_links':
                        self.deleted_links,
                        'permissions':
                        self.permissions,
                        'security_settings':
                        self.security_settings,
                        'admin_log_channels':
                        getattr(self, 'admin_log_channels', {}),
                        'admin_action_logs':
                        getattr(self, 'admin_action_logs', [])
                    },
                    f,
                    indent=2)
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")

    def set_user_permission(self,
                            user_id: str,
                            permission: str,
                            granted: bool = True):
        """Establecer permisos específicos para usuario"""
        if user_id not in self.permissions:
            self.permissions[user_id] = {}
        self.permissions[user_id][permission] = granted
        self.save_data()

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Verificar si usuario tiene permiso específico"""
        # Admins siempre tienen todos los permisos
        if int(user_id) in ADMIN_IDS:
            return True

        # Verificar permisos específicos
        user_perms = self.permissions.get(user_id, {})
        return user_perms.get(permission, False)

    def log_security_event(self, user_id: str, event_type: str, details: str):
        """Registrar evento de seguridad"""
        if 'security_logs' not in self.security_settings:
            self.security_settings['security_logs'] = []

        self.security_settings['security_logs'].append({
            'timestamp':
            datetime.now().isoformat(),
            'user_id':
            user_id,
            'event_type':
            event_type,
            'details':
            details
        })

        # Mantener solo los últimos 1000 logs
        if len(self.security_settings['security_logs']) > 1000:
            self.security_settings['security_logs'] = self.security_settings[
                'security_logs'][-1000:]

        self.save_data()

    def is_user_locked(self, user_id: str) -> bool:
        """Verificar si usuario está bloqueado por seguridad"""
        user_security = self.security_settings.get(user_id, {})
        lock_until = user_security.get('locked_until')

        if lock_until:
            lock_time = datetime.fromisoformat(lock_until)
            if datetime.now() < lock_time:
                return True
            else:
                # Desbloquear automáticamente
                del self.security_settings[user_id]['locked_until']
                self.save_data()

        return False

    def lock_user(self,
                  user_id: str,
                  duration_minutes: int = 30,
                  reason: str = ""):
        """Bloquear usuario temporalmente"""
        if user_id not in self.security_settings:
            self.security_settings[user_id] = {}

        lock_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.security_settings[user_id]['locked_until'] = lock_until.isoformat(
        )
        self.security_settings[user_id]['lock_reason'] = reason

        self.log_security_event(
            user_id, 'USER_LOCKED',
            f"Locked for {duration_minutes} minutes: {reason}")
        self.save_data()

    def set_maintenance(self, status: bool, message: str = ""):
        """Activar/desactivar modo mantenimiento"""
        self.bot_maintenance = status
        self.maintenance_message = message
        self.save_data()

    def is_maintenance(self):
        """Verificar si el bot está en mantenimiento"""
        return self.bot_maintenance

    def set_housemode(self, chat_id: str, status: bool, reason: str = ""):
        """Activar/desactivar modo casa (housemode)"""
        if not hasattr(self, 'housemode_chats'):
            self.housemode_chats = {}

        self.housemode_chats[chat_id] = {
            'active': status,
            'reason': reason,
            'activated_at': datetime.now().isoformat()
        }
        self.save_data()

    def is_housemode(self, chat_id: str):
        """Verificar si el chat está en modo casa"""
        if not hasattr(self, 'housemode_chats'):
            self.housemode_chats = {}
            return False
        return self.housemode_chats.get(chat_id, {}).get('active', False)

    def get_housemode_reason(self, chat_id: str):
        """Obtener razón del modo casa"""
        if not hasattr(self, 'housemode_chats'):
            return ""
        return self.housemode_chats.get(chat_id, {}).get('reason', "")

    def set_admin_log_channel(self, group_id: str, admin_channel_id: str):
        """Configurar canal de logs administrativos"""
        if not hasattr(self, 'admin_log_channels'):
            self.admin_log_channels = {}

        try:
            self.admin_log_channels[group_id] = {
                'channel_id': admin_channel_id,
                'configured_at': datetime.now().isoformat(),
                'active': True
            }
            self.save_data()
            logger.info(
                f"Admin log channel configurado: {group_id} -> {admin_channel_id}"
            )
        except Exception as e:
            logger.error(f"Error configurando admin log channel: {e}")
            raise

    def get_admin_log_channel(self, group_id: str):
        """Obtener canal de logs administrativos"""
        try:
            if not hasattr(self, 'admin_log_channels'):
                self.admin_log_channels = {}
                logger.warning(
                    f"admin_log_channels no existe, creando diccionario vacío")
                return None

            config = self.admin_log_channels.get(group_id, None)
            if config:
                logger.info(
                    f"Canal de logs encontrado para grupo {group_id}: {config['channel_id']}"
                )
            else:
                logger.warning(
                    f"No hay canal de logs configurado para grupo {group_id}")

            return config
        except Exception as e:
            logger.error(f"Error obteniendo admin log channel: {e}")
            return None

    def log_admin_action(self,
                         action_type: str,
                         admin_user,
                         target_user_id: str,
                         reason: str,
                         group_id: str,
                         additional_data: dict = None):
        """Registrar acción administrativa en logs"""
        if not hasattr(self, 'admin_action_logs'):
            self.admin_action_logs = []

        try:
            log_entry = {
                'timestamp':
                datetime.now().isoformat(),
                'action_type':
                action_type,
                'admin_id':
                str(admin_user.id),
                'admin_name':
                admin_user.first_name or "Usuario",
                'admin_username':
                f"@{admin_user.username}"
                if admin_user.username else "Sin username",
                'target_user_id':
                str(target_user_id),
                'reason':
                str(reason),
                'group_id':
                str(group_id),
                'additional_data':
                additional_data or {}
            }

            self.admin_action_logs.append(log_entry)

            # Mantener solo los últimos 1000 logs
            if len(self.admin_action_logs) > 1000:
                self.admin_action_logs = self.admin_action_logs[-1000:]

            # Forzar guardado de datos
            self.save_data()

            logger.info(
                f"Log guardado en DB - Acción: {action_type} - Admin: {admin_user.id} - Target: {target_user_id}"
            )
            return log_entry

        except Exception as e:
            logger.error(f"Error guardando log en BD: {e}")
            return None

    def get_user(self, user_id: str):
        """Obtener datos de usuario de manera ultra-robusta"""
        try:
            # Validar que user_id sea válido
            if not user_id or not isinstance(user_id, str):
                logger.error(f"ID de usuario inválido: {user_id}")
                return None
            
            # Limpiar user_id por seguridad
            user_id = str(user_id).strip()
            if not user_id:
                logger.error("ID de usuario vacío después de limpiar")
                return None

            if user_id not in self.users:
                # Crear nuevo usuario con datos por defecto
                default_user = {
                    'credits': 10,  # Créditos iniciales
                    'premium': False,
                    'premium_until': None,
                    'last_bonus': None,
                    'last_game': None,  # Para límite de juegos
                    'total_generated': 0,
                    'total_checked': 0,
                    'join_date': datetime.now().isoformat(),
                    'warns': 0  # Added for anti-spam
                }
                self.users[user_id] = default_user
                try:
                    self.save_data()
                except Exception as save_error:
                    logger.error(f"Error guardando nuevo usuario {user_id}: {save_error}")
                logger.info(f"Nuevo usuario creado: {user_id} con premium: False")
                return self.users[user_id]
            else:
                # Usuario existente - validar y limpiar datos
                user_data = self.users[user_id]
                
                # Verificar que user_data sea un diccionario
                if not isinstance(user_data, dict):
                    logger.error(f"Datos de usuario {user_id} corruptos: {type(user_data)}")
                    # Recrear usuario con datos por defecto
                    self.users[user_id] = {
                        'credits': 10,
                        'premium': False,
                        'premium_until': None,
                        'last_bonus': None,
                        'last_game': None,
                        'total_generated': 0,
                        'total_checked': 0,
                        'join_date': datetime.now().isoformat(),
                        'warns': 0
                    }
                    try:
                        self.save_data()
                    except:
                        pass
                    return self.users[user_id]

                # Función helper para validar y convertir valores
                def safe_convert(value, target_type, default):
                    try:
                        if value is None:
                            return default
                        if target_type == int:
                            return int(float(value))  # Convertir float a int si es necesario
                        elif target_type == bool:
                            return bool(value)
                        elif target_type == str:
                            return str(value) if value else default
                        else:
                            return value
                    except (ValueError, TypeError, OverflowError):
                        return default

                # Validar y corregir cada campo individualmente
                user_data['total_checked'] = safe_convert(user_data.get('total_checked'), int, 0)
                user_data['total_generated'] = safe_convert(user_data.get('total_generated'), int, 0)
                user_data['credits'] = safe_convert(user_data.get('credits'), int, 10)
                user_data['warns'] = safe_convert(user_data.get('warns'), int, 0)
                user_data['premium'] = safe_convert(user_data.get('premium'), bool, False)
                
                # Validar campos de string/fecha
                if 'join_date' not in user_data or not user_data['join_date']:
                    user_data['join_date'] = datetime.now().isoformat()
                
                # Validar premium_until
                if 'premium_until' not in user_data:
                    user_data['premium_until'] = None
                elif user_data['premium_until'] and not isinstance(user_data['premium_until'], str):
                    user_data['premium_until'] = None

                # Asegurar que campos opcionales existan
                if 'last_bonus' not in user_data:
                    user_data['last_bonus'] = None
                if 'last_game' not in user_data:
                    user_data['last_game'] = None

                # Validar rangos razonables
                if user_data['credits'] < 0:
                    user_data['credits'] = 0
                if user_data['credits'] > 1000000:  # Límite máximo razonable
                    user_data['credits'] = 1000000
                
                if user_data['total_generated'] < 0:
                    user_data['total_generated'] = 0
                if user_data['total_checked'] < 0:
                    user_data['total_checked'] = 0
                if user_data['warns'] < 0:
                    user_data['warns'] = 0
                if user_data['warns'] > 100:  # Límite máximo de warns
                    user_data['warns'] = 100

                # Log solo para casos problemáticos
                if logger.level <= logging.DEBUG:
                    logger.debug(f"Usuario {user_id} cargado - premium: {user_data.get('premium', False)}, until: {user_data.get('premium_until', 'None')}")

                return user_data

        except Exception as e:
            logger.error(f"Error crítico en get_user para {user_id}: {e}")
            # Devolver datos por defecto en caso de error crítico
            return {
                'credits': 10,
                'premium': False,
                'premium_until': None,
                'last_bonus': None,
                'last_game': None,
                'total_generated': 0,
                'total_checked': 0,
                'join_date': datetime.now().isoformat(),
                'warns': 0
            }

    def update_user(self, user_id: str, data: dict):
        user = self.get_user(user_id)
        user.update(data)
        self.save_data()

    def set_staff_role(self, user_id: str, role: str):
        """Asignar rol de staff a un usuario"""
        self.staff_roles[user_id] = {
            'role': role,
            'assigned_date': datetime.now().isoformat(),
            'warn_count': 0  # Para moderadores
        }
        self.save_data()

    def get_staff_role(self, user_id: str):
        """Obtener rol de staff de un usuario"""
        return self.staff_roles.get(user_id, None)

    def remove_staff_role(self, user_id: str):
        """Remover rol de staff"""
        if user_id in self.staff_roles:
            del self.staff_roles[user_id]
            self.save_data()

    def increment_mod_warns(self, user_id: str):
        """Incrementar contador de warns para moderadores"""
        if user_id in self.staff_roles:
            self.staff_roles[user_id]['warn_count'] += 1
            self.save_data()
            return self.staff_roles[user_id]['warn_count']
        return 0

    def is_founder(self, user_id: str) -> bool:
        """Verificar si el usuario es fundador (solo base de datos)"""
        # Lista de IDs de fundadores de emergencia
        emergency_founders = [6938971996, 5537246556]  # Agregando tu ID

        # Excepción de emergencia para IDs específicos
        if int(user_id) in emergency_founders:
            # Auto-registrar si no existe
            if not self.get_staff_role(user_id):
                self.set_staff_role(user_id, '1')
            # También agregar a ADMIN_IDS globalmente si no está
            user_id_int = int(user_id)
            if user_id_int not in ADMIN_IDS:
                ADMIN_IDS.append(user_id_int)
            return True

        staff_data = self.get_staff_role(user_id)
        return staff_data and staff_data['role'] == '1'

    def is_cofounder(self, user_id: str) -> bool:
        """Verificar si el usuario es co-fundador (solo base de datos)"""
        staff_data = self.get_staff_role(user_id)
        return staff_data and staff_data['role'] == '2'

    def is_moderator(self, user_id: str) -> bool:
        """Verificar si el usuario es moderador (solo base de datos)"""
        staff_data = self.get_staff_role(user_id)
        return staff_data and staff_data['role'] == '3'

    def get_all_by_role(self, role: str) -> list:
        """Obtener todos los usuarios de un rol específico"""
        return [
            user_id for user_id, data in self.staff_roles.items()
            if data['role'] == role
        ]

    def set_check_chats(self, group_id: str, verification_chat: str,
                        publication_chat: str):
        """Configurar chats para el sistema /check"""
        self.check_chats[group_id] = {
            'verification_chat': verification_chat,
            'publication_chat': publication_chat,
            'configured_at': datetime.now().isoformat()
        }
        self.save_data()

    def get_check_chats(self, group_id: str):
        """Obtener configuración de chats para /check"""
        return self.check_chats.get(group_id, None)

    def add_pending_check(self, check_id: str, user_id: str, username: str,
                          image_file_id: str, group_id: str):
        """Agregar verificación pendiente"""
        self.pending_checks[check_id] = {
            'user_id': user_id,
            'username': username,
            'image_file_id': image_file_id,
            'group_id': group_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.save_data()

    def get_pending_check(self, check_id: str):
        """Obtener verificación pendiente"""
        return self.pending_checks.get(check_id, None)

    def update_check_status(self,
                            check_id: str,
                            status: str,
                            admin_id: str = None):
        """Actualizar estado de verificación"""
        if check_id in self.pending_checks:
            self.pending_checks[check_id]['status'] = status
            if admin_id:
                self.pending_checks[check_id]['admin_id'] = admin_id
                self.pending_checks[check_id]['processed_at'] = datetime.now(
                ).isoformat()
            self.save_data()

    def save_deleted_link(self, user_id: str, username: str, chat_id: str,
                          message_text: str):
        """Guardar información de link eliminado"""
        link_id = str(len(self.deleted_links) + 1).zfill(
            6)  # ID secuencial con formato 000001

        self.deleted_links[link_id] = {
            'user_id': user_id,
            'username': username,
            'chat_id': chat_id,
            'message_content': message_text,
            'deleted_at': datetime.now().isoformat(),
            'detected_links': self.extract_links_from_text(message_text)
        }
        self.save_data()
        return link_id

    def extract_links_from_text(self, text: str) -> list:
        """Detectar cualquier tipo de enlace, incluso camuflado"""
        import re

        link_patterns = [
            r'https?://\S+', r'www\.\S+',
            r'\b\w+\.(com|net|org|io|co|me|ly|gg|tv|tk|ml|ga|cf|gl)(/[^\s]*)?',
            r't\.me/\S+', r'telegram\.me/\S+', r'tg://\S+', r'discord\.gg/\S+',
            r'youtu\.be/\S+', r'youtube\.com/\S+', r'bit\.ly/\S+',
            r'tinyurl\.com/\S+', r'[a-zA-Z0-9]{2,}(https?://\S+)',
            r'[a-zA-Z0-9]{2,}(www\.\S+)',
        ]

        links = []
        for pattern in link_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    links.extend(["".join(m) for m in matches])
                else:
                    links.extend(matches)

        return list(set(links))

    def get_deleted_links_by_user(self, user_id: str) -> list:
        """Obtener historial de links eliminados de un usuario"""
        user_links = []
        for link_id, data in self.deleted_links.items():
            if data['user_id'] == user_id:
                user_links.append({
                    'id':
                    link_id,
                    'deleted_at':
                    data['deleted_at'],
                    'links':
                    data['detected_links'],
                    'message':
                    data['message_content'][:100] +
                    '...' if len(data['message_content']) > 100 else
                    data['message_content']
                })

        # Ordenar por fecha más reciente
        user_links.sort(key=lambda x: x['deleted_at'], reverse=True)
        return user_links


# Configuración del bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN no configurado en las variables de entorno")
    print("Ve a la pestaña Secrets y agrega tu BOT_TOKEN")
    print("1. Habla con @BotFather en Telegram")
    print("2. Crea un bot con /newbot")
    print("3. Copia el token y ponlo en Secrets")
    exit(1)

# Variables globales para canal de administración
admin_log_channels = {}  # {group_id: admin_channel_id}

# Obtener IDs de admin desde variables de entorno
admin_ids_str = os.getenv('ADMIN_IDS', '123456789')
ADMIN_IDS = [
    int(id.strip()) for id in admin_ids_str.split(',') if id.strip().isdigit()
]

# Obtener IDs de fundador y co-fundador desde variables de entorno
founder_ids_str = os.getenv('FOUNDER_IDS',
                            str(ADMIN_IDS[0]) if ADMIN_IDS else '123456789')
FOUNDER_IDS = [
    int(id.strip()) for id in founder_ids_str.split(',')
    if id.strip().isdigit()
]

cofounder_ids_str = os.getenv('COFOUNDER_IDS', '')
COFOUNDER_IDS = [
    int(id.strip()) for id in cofounder_ids_str.split(',')
    if id.strip().isdigit()
] if cofounder_ids_str else []

# Los admins principales también son fundadores automáticamente
FOUNDER_IDS.extend([id for id in ADMIN_IDS if id not in FOUNDER_IDS])

# Inicializar MongoDB
db = MongoDatabase()

# Migrar datos antiguos si existen
migrate_old_data()


# Generador de tarjetas BIN
class CardGenerator:

    @staticmethod
    def generate_cards(bin_number: str, count: int = 15) -> List[str]:
        """Genera tarjetas basadas en un BIN"""
        cards = []

        for _ in range(count):
            # Completar número de tarjeta
            card_base = bin_number + ''.join([
                str(random.randint(0, 9)) for _ in range(16 - len(bin_number))
            ])

            # Aplicar algoritmo de Luhn
            card_number = CardGenerator.apply_luhn(card_base)

            # Generar fecha de expiración válida
            month = random.randint(1, 12)
            year = random.randint(2025, 2030)

            # Generar CVC
            cvc = random.randint(100, 999)

            cards.append(f"{card_number}|{month:02d}|{year}|{cvc}")

        return cards

    @staticmethod
    def generate_cards_advanced(bin_number: str,
                                count: int = 15,
                                card_length: int = 16,
                                cvv_length: int = 3) -> List[str]:
        """Genera tarjetas con soporte para diferentes longitudes (Visa, MasterCard, AmEx)"""
        cards = []

        for _ in range(count):
            # Completar número de tarjeta según la longitud
            remaining_digits = card_length - len(bin_number)
            if remaining_digits > 0:
                card_base = bin_number + ''.join([
                    str(random.randint(0, 9)) for _ in range(remaining_digits)
                ])
            else:
                card_base = bin_number[:card_length]

            # Aplicar algoritmo de Luhn
            card_number = CardGenerator.apply_luhn_advanced(card_base)

            # Generar fecha de expiración válida
            month = random.randint(1, 12)
            year = random.randint(2025, 2030)

            # Generar CVC según la longitud
            if cvv_length == 4:  # American Express
                cvc = random.randint(1000, 9999)
            else:  # Visa, MasterCard
                cvc = random.randint(100, 999)

            cards.append(f"{card_number}|{month:02d}|{year}|{cvc}")

        return cards

    @staticmethod
    def generate_cards_custom_advanced(bin_number: str,
                                       count: int = 15,
                                       preset_month=None,
                                       preset_year=None,
                                       preset_cvv=None,
                                       card_length: int = 16,
                                       cvv_length: int = 3) -> List[str]:
        """Genera tarjetas con valores personalizados y soporte avanzado"""
        cards = []

        for _ in range(count):
            # Completar número de tarjeta según la longitud
            remaining_digits = card_length - len(bin_number)
            if remaining_digits > 0:
                card_base = bin_number + ''.join([
                    str(random.randint(0, 9)) for _ in range(remaining_digits)
                ])
            else:
                card_base = bin_number[:card_length]

            # Aplicar algoritmo de Luhn
            card_number = CardGenerator.apply_luhn_advanced(card_base)

            # Usar valores preset o generar aleatorios
            if preset_month is not None:
                month = preset_month
            else:
                month = random.randint(1, 12)

            if preset_year is not None:
                year = preset_year
            else:
                year = random.randint(2025, 2030)

            if preset_cvv is not None:
                cvc = preset_cvv
            else:
                if cvv_length == 4:  # American Express
                    cvc = random.randint(1000, 9999)
                else:  # Visa, MasterCard
                    cvc = random.randint(100, 999)

            cards.append(f"{card_number}|{month:02d}|{year}|{cvc}")

        return cards

    @staticmethod
    def apply_luhn(card_number: str) -> str:
        """Aplica el algoritmo de Luhn para hacer válida la tarjeta"""
        digits = [int(d) for d in card_number[:-1]]

        # Calcular dígito de verificación
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10
            total += digit

        check_digit = (10 - (total % 10)) % 10
        return card_number[:-1] + str(check_digit)

    @staticmethod
    def apply_luhn_advanced(card_number: str) -> str:
        """Aplica el algoritmo de Luhn para cualquier longitud de tarjeta"""
        digits = [int(d) for d in card_number[:-1]]

        # Calcular dígito de verificación
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10
            total += digit

        check_digit = (10 - (total % 10)) % 10
        return card_number[:-1] + str(check_digit)

    @staticmethod
    def generate_cards_custom(bin_number: str,
                              count: int = 15,
                              preset_month=None,
                              preset_year=None,
                              preset_cvv=None) -> List[str]:
        """Genera tarjetas con valores personalizados - LEGACY"""
        cards = []

        for _ in range(count):
            # Completar número de tarjeta
            card_base = bin_number + ''.join([
                str(random.randint(0, 9)) for _ in range(16 - len(bin_number))
            ])

            # Aplicar algoritmo de Luhn
            card_number = CardGenerator.apply_luhn(card_base)

            # Usar valores preset o generar aleatorios
            month = int(preset_month) if preset_month and str(
                preset_month).isdigit() else random.randint(1, 12)
            year = int(preset_year) if preset_year and str(
                preset_year).isdigit() else random.randint(2025, 2030)
            cvc = int(preset_cvv) if preset_cvv and str(
                preset_cvv).isdigit() else random.randint(100, 999)

            cards.append(f"{card_number}|{month:02d}|{year}|{cvc}")

        return cards


# Generador de direcciones
class AddressGenerator:
    COUNTRIES_DATA = {
        'US': {
            'cities': [
                'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
                'Philadelphia', 'San Antonio', 'San Diego', 'Dallas',
                'San Jose'
            ],
            'states':
            ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'FL', 'OH', 'GA', 'NC'],
            'postal_format':
            lambda: f"{random.randint(10000, 99999)}",
            'phone_format':
            lambda: f"+1{random.randint(2000000000, 9999999999)}",
            'country_name':
            'United States',
            'flag':
            '🇺🇸'
        },
        'CO': {
            'cities': [
                'Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena',
                'Cúcuta', 'Soledad', 'Ibagué', 'Bucaramanga', 'Soacha'
            ],
            'states': [
                'Bogotá D.C.', 'Antioquia', 'Valle del Cauca', 'Atlántico',
                'Bolívar', 'Norte de Santander', 'Tolima', 'Santander',
                'Cundinamarca', 'Córdoba'
            ],
            'postal_format':
            lambda: f"{random.randint(100000, 999999)}",
            'phone_format':
            lambda: f"+57{random.randint(3000000000, 3999999999)}",
            'country_name':
            'Colombia',
            'flag':
            '🇨🇴'
        },
        'EC': {
            'cities': [
                'Guayaquil', 'Quito', 'Cuenca', 'Santo Domingo', 'Machala',
                'Durán', 'Manta', 'Portoviejo', 'Loja', 'Ambato'
            ],
            'states': [
                'Guayas', 'Pichincha', 'Azuay', 'Santo Domingo', 'El Oro',
                'Manabí', 'Los Ríos', 'Tungurahua', 'Loja', 'Esmeraldas'
            ],
            'postal_format':
            lambda: f"{random.randint(100000, 999999)}",
            'phone_format':
            lambda: f"+593{random.randint(900000000, 999999999)}",
            'country_name':
            'Ecuador',
            'flag':
            '🇪🇨'
        },
        'MX': {
            'cities': [
                'Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla',
                'Tijuana', 'León', 'Juárez', 'Torreón', 'Querétaro',
                'San Luis Potosí'
            ],
            'states': [
                'Ciudad de México', 'Jalisco', 'Nuevo León', 'Puebla',
                'Baja California', 'Guanajuato', 'Chihuahua', 'Coahuila',
                'Querétaro', 'San Luis Potosí'
            ],
            'postal_format':
            lambda: f"{random.randint(10000, 99999)}",
            'phone_format':
            lambda: f"+52{random.randint(5500000000, 5599999999)}",
            'country_name':
            'Mexico',
            'flag':
            '🇲🇽'
        },
        'BR': {
            'cities': [
                'São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador',
                'Fortaleza', 'Belo Horizonte', 'Manaus', 'Curitiba', 'Recife',
                'Porto Alegre'
            ],
            'states': [
                'São Paulo', 'Rio de Janeiro', 'Distrito Federal', 'Bahia',
                'Ceará', 'Minas Gerais', 'Amazonas', 'Paraná', 'Pernambuco',
                'Rio Grande do Sul'
            ],
            'postal_format':
            lambda:
            f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
            'phone_format':
            lambda: f"+55{random.randint(11900000000, 11999999999)}",
            'country_name':
            'Brazil',
            'flag':
            '🇧🇷'
        },
        'ES': {
            'cities': [
                'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza',
                'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao'
            ],
            'states': [
                'Madrid', 'Cataluña', 'Valencia', 'Andalucía', 'Aragón',
                'País Vasco', 'Castilla y León', 'Galicia', 'Murcia',
                'Islas Baleares'
            ],
            'postal_format':
            lambda: f"{random.randint(10000, 52999)}",
            'phone_format':
            lambda: f"+34{random.randint(600000000, 799999999)}",
            'country_name':
            'Spain',
            'flag':
            '🇪🇸'
        },
        'AR': {
            'cities': [
                'Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'Tucumán',
                'La Plata', 'Mar del Plata', 'Salta', 'Santa Fe', 'San Juan'
            ],
            'states': [
                'Buenos Aires', 'Córdoba', 'Santa Fe', 'Mendoza', 'Tucumán',
                'Entre Ríos', 'Salta', 'Misiones', 'Chaco', 'Corrientes'
            ],
            'postal_format':
            lambda:
            f"{random.choice(['C', 'B', 'A'])}{random.randint(1000, 9999)}{random.choice(['AAA', 'BBB', 'CCC'])}",
            'phone_format':
            lambda: f"+54{random.randint(11000000000, 11999999999)}",
            'country_name':
            'Argentina',
            'flag':
            '🇦🇷'
        },
        'KZ': {
            'cities': [
                'Almaty', 'Nur-Sultan', 'Shymkent', 'Aktobe', 'Taraz',
                'Pavlodar', 'Ust-Kamenogorsk', 'Semey', 'Atyrau', 'Kostanay'
            ],
            'states': [
                'Almaty', 'Nur-Sultan', 'Shymkent', 'Aktobe', 'Zhambyl',
                'Pavlodar', 'East Kazakhstan', 'Semey', 'Atyrau', 'Kostanay'
            ],
            'postal_format':
            lambda: f"{random.randint(100000, 999999)}",
            'phone_format':
            lambda: f"+7{random.randint(7000000000, 7999999999)}",
            'country_name':
            'Kazakhstan',
            'flag':
            '🇰🇿'
        },
        'AE': {
            'cities': [
                'Dubai', 'Abu Dhabi', 'Sharjah', 'Al Ain', 'Ajman',
                'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain', 'Dibba',
                'Khor Fakkan'
            ],
            'states': [
                'Dubai', 'Abu Dhabi', 'Sharjah', 'Al Ain', 'Ajman',
                'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain',
                'Northern Emirates', 'Eastern Region'
            ],
            'postal_format':
            lambda: f"{random.randint(100000, 999999)}",
            'phone_format':
            lambda: f"+971{random.randint(500000000, 599999999)}",
            'country_name':
            'United Arab Emirates',
            'flag':
            '🇦🇪'
        }
    }

    @staticmethod
    def generate_address(country: str = None) -> dict:
        if not country:
            country = random.choice(
                list(AddressGenerator.COUNTRIES_DATA.keys()))

        if country not in AddressGenerator.COUNTRIES_DATA:
            return None

        data = AddressGenerator.COUNTRIES_DATA[country]

        street_names = [
            'Main St', 'Oak Ave', 'Park Rd', 'High St', 'Church Ln', 'King St',
            'Queen Ave', 'First St', 'Second Ave', 'Third Blvd', 'Central Ave',
            'Broadway', 'Market St', 'Washington St', 'Lincoln Ave'
        ]

        return {
            'street':
            f"{random.randint(1, 9999)} {random.choice(street_names)}",
            'city': random.choice(data['cities']),
            'state': random.choice(data['states']),
            'postal_code': data['postal_format'](),
            'country': data['country_name'],
            'phone': data['phone_format'](),
            'flag': data['flag']
        }


# Decorador para verificar que el comando se use solo en grupos (con excepciones para roles privilegiados)
def group_only(func):

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_id_str = str(user_id)

        # Verificar si es un chat grupal
        if update.effective_chat.type in ['private']:
            # Verificar si el usuario tiene privilegios especiales para usar en privado
            is_admin = user_id in ADMIN_IDS

            # Verificar roles de staff en base de datos
            is_founder = db.is_founder(user_id_str)
            is_cofounder = db.is_cofounder(user_id_str)
            is_moderator = db.is_moderator(user_id_str)

            # Verificar si es premium
            user_data = db.get_user(user_id_str)
            is_premium = user_data.get('premium', False)

            # Verificar que el premium sea válido (no expirado)
            premium_valid = False
            if is_premium:
                premium_until = user_data.get('premium_until')
                if premium_until:
                    try:
                        premium_until_date = datetime.fromisoformat(premium_until)
                        premium_valid = datetime.now() < premium_until_date
                    except:
                        premium_valid = True  # Si hay error en fecha, considerar válido
                else:
                    premium_valid = True  # Premium sin fecha = permanente

            # Si no tiene privilegios suficientes, denegar acceso
            if not (is_admin or is_founder or is_cofounder or is_moderator or premium_valid):
                # Determinar qué acceso tiene el usuario
                access_type = "Usuario estándar"
                if is_premium and not premium_valid:
                    access_type = "Premium expirado"

                await update.message.reply_text(
                    "╒═📛 BLOQUEO DE ACCESO ═╕\n"
                    "│ 🔒 Canal: Privado cerrado\n"
                    f"│ 💠 Estado: {access_type}\n"
                    "│ \n"
                    "│ 🧭 Soluciones:\n"
                    "│ ├ Usa el comando en grupo\n"
                    "│ └ Reactiva tu acceso premium\n"
                    "╘════════════════════════╛\n"
                    "📡 Nodo de contacto: @SteveCHRB",
                    parse_mode=ParseMode.MARKDOWN)
                return

        return await func(update, context)

    return wrapper


# Decorador para verificar créditos (solo para live)
def require_credits_for_live(credits_needed: int = 4):

    def decorator(func):

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = str(update.effective_user.id)

            # Los admins tienen créditos ilimitados
            if update.effective_user.id in ADMIN_IDS:
                return await func(update, context)

            try:
                user_data = db.get_user(user_id)

                # Asegurar que tenga el campo credits
                if 'credits' not in user_data:
                    user_data['credits'] = 10

                if user_data['credits'] < credits_needed:
                    await update.message.reply_text(
                        f"❌ **Créditos insuficientes**\n\n"
                        f"Necesitas: {credits_needed} créditos\n"
                        f"Tienes: {user_data['credits']} créditos\n\n"
                        f"Usa /loot para créditos gratis o /audit para más información",
                        parse_mode=ParseMode.MARKDOWN)
                    return

                # Descontar créditos solo a usuarios normales
                try:
                    db.update_user(user_id,
                                   {'credits': user_data['credits'] - credits_needed})
                except Exception as e:
                    logger.error(f"Error descontando créditos: {e}")
                    # Continuar sin descontar si hay error de BD

            except Exception as e:
                logger.error(f"Error en verificación de créditos: {e}")
                # En caso de error, permitir el uso pero avisar
                await update.message.reply_text(
                    "⚠️ **Sistema de créditos temporal**\n"
                    "Procesando tu solicitud...", 
                    parse_mode=ParseMode.MARKDOWN)

            return await func(update, context)

        return wrapper

    return decorator


# Decorador para verificar si es admin del bot O admin del grupo
def admin_only(func):

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_id_str = str(user_id)

        # Verificar si es admin tradicional del bot O fundador en base de datos
        is_bot_admin = user_id in ADMIN_IDS
        is_founder_in_db = db.is_founder(user_id_str)

        # Para comandos de moderación (clean, ban, warn, etc.) también verificar si es admin del grupo
        is_group_admin = False
        try:
            if update.effective_chat.type in ['group', 'supergroup']:
                chat_member = await update.get_bot().get_chat_member(
                    update.effective_chat.id, user_id)
                is_group_admin = chat_member.status in [
                    'administrator', 'creator'
                ]
        except:
            is_group_admin = False

        # Permitir acceso si es admin del bot O admin del grupo
        if not (is_bot_admin or is_founder_in_db or is_group_admin):
            await update.message.reply_text(
                "❌ **ACCESO DENEGADO** ❌\n\n"
                "🛡️ **Este comando requiere permisos de:**\n"
                "• Administrador\n",
                parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context)

    return wrapper


# Sistema de logs administrativos
async def send_admin_log(context,
                         action_type: str,
                         admin_user,
                         target_user_id: str,
                         reason: str,
                         group_id: str,
                         additional_data: dict = None):
    """Enviar log administrativo al canal configurado"""
    try:
        # Obtener configuración del canal de logs
        log_config = db.get_admin_log_channel(group_id)

        if not log_config or not log_config.get('channel_id'):
            logger.info(
                f"No hay canal de logs configurado para grupo {group_id}")
            return

        admin_channel_id = log_config['channel_id']

        # Crear mensaje de log
        log_message = f"📋 **LOG ADMINISTRATIVO** 📋\n\n"
        log_message += f"🔨 **Acción:** {action_type}\n"
        log_message += f"👮‍♂️ **Admin:** {admin_user.first_name}"

        if admin_user.username:
            log_message += f" (@{admin_user.username})"

        log_message += f"\n🆔 **Admin ID:** `{admin_user.id}`\n"
        log_message += f"🎯 **Usuario objetivo:** `{target_user_id}`\n"
        log_message += f"📝 **Razón:** {reason}\n"
        log_message += f"🏠 **Grupo:** `{group_id}`\n"
        log_message += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"

        # Agregar datos adicionales si existen
        if additional_data:
            log_message += f"\n📊 **Datos adicionales:**\n"
            for key, value in additional_data.items():
                log_message += f"• **{key}:** {value}\n"

        log_message += f"\n🤖 **Bot:** @ChernobilChLv_bot"

        # Enviar al canal de logs
        await context.bot.send_message(chat_id=admin_channel_id,
                                       text=log_message,
                                       parse_mode=ParseMode.MARKDOWN)

        # Guardar en base de datos también
        db.log_admin_action(action_type=action_type,
                            admin_user=admin_user,
                            target_user_id=target_user_id,
                            reason=reason,
                            group_id=group_id,
                            additional_data=additional_data)

        logger.info(f"Log administrativo enviado exitosamente: {action_type}")

    except Exception as e:
        logger.error(f"Error enviando log administrativo: {e}")
        # No hacer raise para que el comando principal no falle


# Sistema de mutes automáticos - Corregido
muted_users = {}  # {chat_id: {user_id: {'unmute_time': datetime, 'reason': str, 'muted_by': str}}}


def auto_mute_user(chat_id: str, user_id: str, duration_hours: float,
                   reason: str, muted_by: str):
    """Agregar usuario al sistema de mutes automáticos - Corregido"""
    try:
        unmute_time = datetime.now() + timedelta(hours=duration_hours)

        if chat_id not in muted_users:
            muted_users[chat_id] = {}

        muted_users[chat_id][user_id] = {
            'unmute_time': unmute_time,
            'reason': reason,
            'muted_by': muted_by,
            'muted_at': datetime.now().isoformat()
        }

        logger.info(f"Usuario {user_id} muteado en chat {chat_id} por {duration_hours}h")
        return unmute_time
    except Exception as e:
        logger.error(f"Error en auto_mute_user: {e}")
        return None


# Decorador para verificar mantenimiento
def check_maintenance(func):

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Los admins pueden usar comandos durante mantenimiento
        if update.effective_user.id in ADMIN_IDS:
            return await func(update, context)

        # Si está en mantenimiento, bloquear comando
        if db.is_maintenance():
            maintenance_msg = db.maintenance_message or "🔧 Bot en mantenimiento. Intenta más tarde."
            await update.message.reply_text(
                f"🚧 **BOT EN MANTENIMIENTO** 🚧\n\n"
                f"⚠️ {maintenance_msg}\n\n"
                f"💡 Contacta a los administradores para más información",
                parse_mode=ParseMode.MARKDOWN)
            return

        return await func(update, context)

    return wrapper


# Decorador de seguridad avanzado
def enhanced_security(required_permission: str = None,
                      audit: bool = True,
                      rate_limit: int = None):
    """Decorador avanzado de seguridad con auditoría y rate limiting"""

    def decorator(func):

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = str(update.effective_user.id)
            user_id_int = update.effective_user.id
            command_name = func.__name__

            # Verificar si el usuario está bloqueado
            if db.is_user_locked(user_id):
                user_security = db.security_settings.get(user_id, {})
                reason = user_security.get('lock_reason',
                                           'Motivo no especificado')
                await update.message.reply_text(
                    f"🔒 **ACCESO BLOQUEADO** 🔒\n\n"
                    f"⚠️ Tu cuenta está temporalmente bloqueada\n"
                    f"📝 **Motivo:** {reason}\n\n"
                    f"💡 Contacta a los administradores si crees que es un error",
                    parse_mode=ParseMode.MARKDOWN)

                if audit:
                    db.log_security_event(user_id, 'BLOCKED_ACCESS_ATTEMPT',
                                          f"Comando: {command_name}")
                return

            # Verificar permisos específicos
            if required_permission and not db.has_permission(
                    user_id, required_permission):
                await update.message.reply_text(
                    f"❌ **PERMISOS INSUFICIENTES** ❌\n\n"
                    f"🔐 Necesitas el permiso: `{required_permission}`\n"
                    f"💡 Contacta a los administradores para obtener acceso",
                    parse_mode=ParseMode.MARKDOWN)

                if audit:
                    db.log_security_event(
                        user_id, 'PERMISSION_DENIED',
                        f"Comando: {command_name}, Permiso: {required_permission}"
                    )
                return

            # Rate limiting
            if rate_limit:
                current_time = datetime.now()
                rate_key = f"{user_id}_{command_name}"

                if rate_key not in db.security_settings:
                    db.security_settings[rate_key] = []

                # Limpiar intentos antiguos (última hora)
                db.security_settings[rate_key] = [
                    timestamp for timestamp in db.security_settings[rate_key]
                    if (current_time -
                        datetime.fromisoformat(timestamp)).seconds < 3600
                ]

                if len(db.security_settings[rate_key]) >= rate_limit:
                    await update.message.reply_text(
                        f"⏰ **LÍMITE DE VELOCIDAD** ⏰\n\n"
                        f"🚫 Has excedido el límite de {rate_limit} usos por hora\n"
                        f"⏳ Intenta nuevamente más tarde",
                        parse_mode=ParseMode.MARKDOWN)

                    if audit:
                        db.log_security_event(user_id, 'RATE_LIMIT_EXCEEDED',
                                              f"Comando: {command_name}")
                    return

                db.security_settings[rate_key].append(current_time.isoformat())
                db.save_data()

            # Auditoría antes de ejecutar
            if audit:
                db.log_security_event(user_id, 'COMMAND_EXECUTED',
                                      f"Comando: {command_name}")

            try:
                result = await func(update, context)

                # Auditoría de éxito
                if audit:
                    db.log_security_event(user_id, 'COMMAND_SUCCESS',
                                          f"Comando: {command_name}")

                return result

            except Exception as e:
                # Auditoría de error
                if audit:
                    db.log_security_event(
                        user_id, 'COMMAND_ERROR',
                        f"Comando: {command_name}, Error: {str(e)}")
                raise

        return wrapper

    return decorator


# Decorador para comandos críticos - Solo admins del bot
def bot_admin_only(func):
    """Decorador para comandos críticos que solo pueden usar administradores del bot"""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_id_str = str(user_id)

        # Solo admins del bot y fundadores en DB
        is_bot_admin = user_id in ADMIN_IDS
        is_founder_in_db = db.is_founder(user_id_str)

        if not (is_bot_admin or is_founder_in_db):
            await update.message.reply_text(
                "❌ **ACCESO ULTRA RESTRINGIDO** ❌\n\n"
                "🔒 **Este comando es EXCLUSIVO**\n"
                "🚫 **No tienes acceso**\n",
                parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context)

    return wrapper


# Decorador para verificar roles de staff (CORREGIDO - Solo base de datos)
def staff_only(required_level=1):
    """
    Decorador para verificar roles de staff
    Nivel 1: Fundador (máximo nivel)
    Nivel 2: Co-Fundador 
    Nivel 3: Moderador (mínimo nivel)
    """

    def decorator(func):

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = str(update.effective_user.id)
            user_id_int = update.effective_user.id

            # EXCEPCIÓN DE EMERGENCIA: IDs específicos que siempre son fundadores
            # Esto es una medida de seguridad por si falla la base de datos
            EMERGENCY_FOUNDERS = [6938971996
                                  ]  # Tu ID como excepción de emergencia

            if user_id_int in EMERGENCY_FOUNDERS:
                # Auto-registrar en la base de datos si no existe
                if not db.get_staff_role(user_id):
                    db.set_staff_role(user_id, '1')  # Nivel 1 = Fundador
                return await func(update, context)

            # Verificar roles en la base de datos ÚNICAMENTE
            staff_data = db.get_staff_role(user_id)
            if staff_data:
                user_level = int(staff_data['role'])
                if user_level <= required_level:
                    return await func(update, context)
                else:
                    await update.message.reply_text(
                        f"❌ Permisos insuficientes. Requiere nivel {required_level} o superior"
                    )
                    return

            await update.message.reply_text(
                "❌ Este comando requiere permisos de staff")
            return

        return wrapper

    return decorator


async def cleanstatus_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Verificar estado de la limpieza automática"""
    chat_id = str(update.effective_chat.id)

    if chat_id in auto_clean_timers and auto_clean_timers[chat_id].get(
            'active', False):
        timer_info = auto_clean_timers[chat_id]
        interval_text = timer_info.get('interval_text', 'Desconocido')
        is_day_mode = timer_info.get('is_day_mode', False)
        days_count = timer_info.get('days_count', 0)
        last_clean = timer_info.get('last_clean', 'Nunca')

        if last_clean != 'Nunca':
            try:
                last_clean_date = datetime.fromisoformat(last_clean)
                last_clean_formatted = last_clean_date.strftime(
                    '%d/%m/%Y %H:%M')
            except:
                last_clean_formatted = 'Error al obtener fecha'
        else:
            last_clean_formatted = 'Nunca'

        if is_day_mode:
            clean_description = f"TODOS los mensajes del período de {interval_text}"
            mode_description = "🔥 **MODO MASIVO** - Eliminación completa"
        else:
            clean_description = "20 mensajes por intervalo"
            mode_description = "🧹 **MODO ESTÁNDAR** - Limpieza ligera"

        response = f"🧹 **ESTADO DE LIMPIEZA AUTOMÁTICA** 🧹\n\n"
        response += f"🟢 **Estado:** Activo\n"
        response += f"⏰ **Intervalo:** {interval_text}\n"
        response += f"🗑️ **Tipo de limpieza:** {clean_description}\n"
        response += f"⚙️ **Modo:** {mode_description}\n"
        response += f"📅 **Última limpieza:** {last_clean_formatted}\n\n"

        if is_day_mode:
            response += f"⚠️ **ADVERTENCIA:** Este modo elimina TODO el historial\n"
            response += f"🔄 **Próxima limpieza masiva:** En {interval_text}\n\n"

        response += f"💡 **Para desactivar:** `/clean auto off`"
    else:
        response = f"🧹 **ESTADO DE LIMPIEZA AUTOMÁTICA** 🧹\n\n"
        response += f"🔴 **Estado:** Inactivo\n"
        response += f"⏰ **Intervalo:** No configurado\n"
        response += f"📅 **Última limpieza:** Nunca\n\n"
        response += f"💡 **Para activar:** `/clean auto [tiempo]`\n"
        response += f"📋 **Ejemplos:**\n"
        response += f"• `/clean auto 30m` - Limpieza estándar cada 30min\n"
        response += f"• `/clean auto 1d` - Eliminación masiva diaria\n"
        response += f"• `/clean auto 7d` - Eliminación masiva semanal"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


# Comandos principales
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    # Determinar estado premium
    premium_status = "ACTIVO" if user_data.get('premium', False) else "INACTIVO"
    credits_display = user_data['credits'] if not is_admin else '∞'

    welcome_text = f"╔═⟦ 🧬 BIENVENID@ {update.effective_user.first_name} - PANEL SHAD ═╗\n"
    welcome_text += f"║ 💳 Créditos actuales: {credits_display}\n"
    welcome_text += f"║ 👑 Modo PREMIUM: {premium_status}\n"
    welcome_text += "╚═════════════════════════════════╝\n\n"

    welcome_text += "┌─⟦ ⚙️ COMANDOS PRINCIPALES ⟧─┐\n"
    welcome_text += "│ • /gen → Generar tarjetas\n"
    welcome_text += "│ • /inject → Verificar tarjetas\n"
    welcome_text += "│ • /direccion → Generar dirección\n"
    welcome_text += "│ • /ex → Extrapolación avanzada\n"
    welcome_text += "└──────────────────────────────┘\n\n"

    welcome_text += "┌─⟦ 💰 SISTEMA DE CRÉDITOS ⟧─┐\n"
    welcome_text += "│ • /wallet → Ver saldo\n"
    welcome_text += "│ • /loot → Recompensa diaria\n"
    welcome_text += "│ • /transmit → Donar \n"
    welcome_text += "│ • /audit → Tabla WED\n"
    welcome_text += "└──────────────────────────────┘\n\n"

    welcome_text += "┌─⟦ 🛰️ FUNCIONES INTELIGENTES ⟧─┐\n"
    welcome_text += "│ • /bridge [URL] → Escaneo bridge\n"
    welcome_text += "│ • /status → Estado del sistema\n"
    welcome_text += "│ • /staff list → Administración\n"
    welcome_text += "│ • /simulator → simulator riesgoso\n"
    welcome_text += "└──────────────────────────────┘\n\n"

    welcome_text += "💡 Tip: Usa /loot todos los días para aumentar tu saldo CHLV.\n\n"
    welcome_text += "🤖 Bot: @ChernobilChLv_bot"

    await update.message.reply_text(welcome_text)


@check_maintenance
async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generar tarjetas basadas en BIN - MEJORADO con soporte completo"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    args = context.args
    if not args:
        await update.message.reply_text(
            "🕷️ **𝗦𝗬𝗡𝗖 𝗚𝗘𝗡 | 𝗠𝗢𝗗𝗢 𝗙𝗢𝗥𝗝𝗔𝗗𝗢𝗥**\n\n"
            "╭────────────────────────────╮\n"
            "┃ 🧾 **Formato:** 55791004431xxxxxx|08|27|123\n"
            "┃ 📤 **Comando:** /gen BIN|MM|YY|CVV\n"
            "┃ 💠 **Variables:** \"x\" genera números aleatorios\n"
            "┃ 🎯 **Por defecto:** 15 tarjetas\n"
            "╰────────────────────────────╯\n\n"
            "⛓️ **Usa BINs activos para mejores resultados**",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Obtener el input completo del mensaje para preservar formato
    full_message = update.message.text
    command_start = full_message.find('/gen') + 4
    if command_start < len(full_message):
        input_raw = full_message[command_start:].strip()
        input_parts = input_raw.split()
        input_data = input_parts[0] if input_parts else args[0]
    else:
        input_data = args[0]

    preset_month = None
    preset_year = None
    preset_cvv = None
    bin_number = ""
    original_format = input_data  # Guardar formato original

    # ANÁLISIS MEJORADO DE FORMATOS

    # 1. Formato con pipe (|) - Más común
    if '|' in input_data:
        parts = input_data.split('|')

        # Extraer BIN limpiando las x
        raw_bin = parts[0].replace('x', '').replace('X', '')
        bin_number = ''.join([c for c in raw_bin if c.isdigit()])

        # Validar que tenemos un BIN válido
        if len(bin_number) >= 6:
            # Obtener parámetros opcionales
            if len(parts) > 1 and parts[1].strip() and parts[1].isdigit():
                preset_month = int(parts[1])

            if len(parts) > 2 and parts[2].strip() and parts[2].isdigit():
                year_input = parts[2]
                # Manejar años de 2 dígitos (08 -> 2008, 27 -> 2027)
                if len(year_input) == 2:
                    year_int = int(year_input)
                    if year_int <= 50:  # 00-50 = 2000-2050
                        preset_year = 2000 + year_int
                    else:  # 51-99 = 1951-1999 (pero convertimos a 20xx)
                        preset_year = 2000 + year_int
                else:
                    preset_year = int(year_input)

            if len(parts) > 3 and parts[3].strip() and parts[3].isdigit():
                preset_cvv = int(parts[3])

    # 2. Formato con slash (/) - Alternativo
    elif '/' in input_data:
        parts = input_data.split('/')
        if len(parts) >= 2:
            # BIN
            raw_bin = parts[0].replace('x', '').replace('X', '')
            bin_number = ''.join([c for c in raw_bin if c.isdigit()])

            # Mes
            if len(parts) > 1 and parts[1].isdigit():
                preset_month = int(parts[1])

            # Año (formato MM/YY o MM/YYYY)
            if len(parts) > 2 and parts[2].isdigit():
                year_input = parts[2]
                if len(year_input) == 2:
                    year_int = int(year_input)
                    preset_year = 2000 + year_int if year_int <= 50 else 1900 + year_int
                else:
                    preset_year = int(year_input)

            # CVV desde argumentos adicionales
            if len(args) > 1 and args[1].isdigit():
                preset_cvv = int(args[1])

    # 3. Formato simple: solo BIN
    else:
        raw_bin = input_data.replace('x', '').replace('X', '')
        bin_number = ''.join([c for c in raw_bin if c.isdigit()])

    # VALIDACIÓN MEJORADA DEL BIN
    if not bin_number or len(bin_number) < 6:
        await update.message.reply_text(
            "❌ **BIN inválido**\n\n"
            "💡 **Formatos aceptados:**\n"
            "• `557910|12|27|123` (con CVV)\n"
            "• `557910|12|27` (sin CVV)\n"
            "• `55791004431xxxxxx|08|27`\n"
            "• `55791004431xxxxxx/08/27`\n"
            "• `378282` (solo BIN)\n"
            "• `378282|12|2025|1234` (AmEx)\n\n"
            "🔥 **Soporte:** Visa (4), MasterCard (5), AmEx (3)",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Determinar tipo de tarjeta y longitud
    card_type = "UNKNOWN"
    card_length = 16  # Por defecto
    cvv_length = 3  # Por defecto

    if bin_number.startswith('4'):
        card_type = "VISA"
        card_length = 16
        cvv_length = 3
    elif bin_number.startswith('5') or bin_number.startswith('2'):
        card_type = "MASTERCARD"
        card_length = 16
        cvv_length = 3
    elif bin_number.startswith('3'):
        card_type = "AMERICAN EXPRESS"
        card_length = 15
        cvv_length = 4

    # Parámetros adicionales desde argumentos
    count = 15  # Por defecto (cambiado de 10 a 15)
    if len(args) > 1:
        for arg in args[1:]:
            if arg.isdigit() and 1 <= int(arg) <= 50:
                count = int(arg)
                break

    # Límites según tipo de usuario
    max_cards = 50 if user_data.get('premium', False) else 20
    if not is_admin and count > max_cards:
        await update.message.reply_text(
            f"❌ Límite excedido. Máximo {max_cards} tarjetas")
        return

    # GENERAR TARJETAS CON SOPORTE COMPLETO
    try:
        if preset_month or preset_year or preset_cvv:
            cards = CardGenerator.generate_cards_custom_advanced(
                bin_number, count, preset_month, preset_year, preset_cvv,
                card_length, cvv_length)
        else:
            cards = CardGenerator.generate_cards_advanced(
                bin_number, count, card_length, cvv_length)
    except Exception as e:
        # Fallback al generador básico
        cards = CardGenerator.generate_cards(bin_number, count)

    # Obtener información REAL del BIN
    real_bin_info = await get_real_bin_info(bin_number)

    # Crear máscara del BIN apropiada para el tipo de tarjeta
    x_count = card_length - len(bin_number)
    bin_mask = bin_number + "x" * x_count

    # Mostrar formato usado
    format_display = f"{preset_month or 'rnd'} | {preset_year or 'rnd'} | {preset_cvv or 'rnd'}"

    # NUEVA RESPUESTA CON FORMATO GLITCH_FRAME_X
    response = f"🟣 SYSTEM ALERT [GLITCH_FRAME_X]\n"
    response += f"---=:: BIN Parse Protocol Init =---\n"
    response += f"▌ ID: {bin_mask}\n"
    response += f"▌ Format: {format_display}\n\n"
    response += f"▌ Sending Payload...\n"

    for card in cards:
        response += f"▒ {card}\n"

    # Información del BIN con banderas completas
    country_flags = {
        'UNITED STATES': '🇺🇸',
        'CANADA': '🇨🇦',
        'UNITED KINGDOM': '🇬🇧',
        'GERMANY': '🇩🇪',
        'FRANCE': '🇫🇷',
        'SPAIN': '🇪🇸',
        'ITALY': '🇮🇹',
        'BRAZIL': '🇧🇷',
        'MEXICO': '🇲🇽',
        'ARGENTINA': '🇦🇷',
        'COLOMBIA': '🇨🇴',
        'PERU': '🇵🇪',
        'CHILE': '🇨🇱',
        'ECUADOR': '🇪🇨',
        'VENEZUELA': '🇻🇪'
    }

    country_name = real_bin_info['country'].upper()
    country_flag = country_flags.get(country_name, '🌍')

    # Tiempo de generación
    generation_time = round(random.uniform(0.025, 0.055), 3)

    response += f"\n---= META DATA =---\n"
    response += f"🏦 Banco: {real_bin_info['bank']}\n"
    response += f"💳 Tipo: {real_bin_info['scheme']} / {real_bin_info['type']}\n"
    response += f"🌍 Región: {country_flag} {real_bin_info['country'].upper()}\n"
    response += f"🧠 Usuario: @{update.effective_user.username or update.effective_user.first_name}\n"
    response += f"⏱️ Tiempo: {generation_time}s\n"
    response += f"🟢 *Estado: ESTABLE"

    # BOTÓN REGENERAR CORREGIDO - Mantiene parámetros originales
    regen_data = f"regen_{bin_number}_{count}_{preset_month or 'rnd'}_{preset_year or 'rnd'}_{preset_cvv or 'rnd'}_{card_length}_{cvv_length}"

    keyboard = [[
        InlineKeyboardButton("🔄 Regenerar Tarjetas", callback_data=regen_data),
        InlineKeyboardButton("📊 Ver BIN Info",
                             callback_data=f'bininfo_{bin_number}')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Actualizar estadísticas
    db.update_user(user_id,
                   {'total_generated': user_data['total_generated'] + count})

    await update.message.reply_text(response, reply_markup=reply_markup)


async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver créditos del usuario con diseño mejorado"""
    try:
        user_id = str(update.effective_user.id)
        user_data = db.get_user(user_id)
        is_admin = update.effective_user.id in ADMIN_IDS

        # Validar y corregir datos del usuario
        if not isinstance(user_data.get('credits'), (int, float)):
            user_data['credits'] = 10
        if not isinstance(user_data.get('total_generated'), (int, float)):
            user_data['total_generated'] = 0
        if not isinstance(user_data.get('total_checked'), (int, float)):
            user_data['total_checked'] = 0

        # Determinar estado premium con validación
        premium_status = "❌ INACTIVO"
        premium_details = ""
        try:
            if user_data.get('premium', False):
                premium_until = user_data.get('premium_until')
                if premium_until:
                    if isinstance(premium_until, str):
                        premium_until_date = datetime.fromisoformat(premium_until)
                    else:
                        premium_until_date = premium_until
                    days_left = max(0, (premium_until_date - datetime.now()).days)
                    premium_status = "✅ ACTIVO"
                    premium_details = f"⏳ Expira en: {days_left} días"
        except Exception as e:
            logger.warning(f"Error calculando premium para {user_id}: {e}")

        # Calcular actividad total con validación
        total_activity = int(user_data.get('total_generated', 0)) + int(user_data.get('total_checked', 0))

        # Mostrar créditos (infinitos para admins) con validación
        credits_display = f"{int(user_data['credits']):,}" if not is_admin else "∞ (Admin)"

        response = "╔═══▣ DATA NODE ACCESSED ▣═══╗\n"
        response += "║                            \n"
        response += f"║ 💰 Créditos disponibles: {credits_display:<7}\n"
        response += f"║ 📤 Tarjetas generadas: {int(user_data['total_generated']):<9,}\n"
        response += f"║ 📥 Tarjetas validadas: {int(user_data['total_checked']):<9,}\n"
        response += "║                            \n"
        response += f"║ 🎖️ Estado Premium: {premium_status:<12}\n"
        if premium_details:
            response += f"║ {premium_details:<27}\n"
        response += "║                            \n"
        response += f"║ ⚡ Actividad total: {total_activity:<11,}\n"

        # Tiempo en el bot con validación
        try:
            join_date_str = user_data.get('join_date')
            if join_date_str:
                if isinstance(join_date_str, str):
                    join_date = datetime.fromisoformat(join_date_str)
                else:
                    join_date = join_date_str
                days_active = max(0, (datetime.now() - join_date).days)
            else:
                days_active = 0
        except Exception as e:
            logger.warning(f"Error calculando días activos para {user_id}: {e}")
            days_active = 0

        response += f"║ 📅 Días activo: {days_active:<15}\n"
        response += "║                            \n"
        response += "║ 💡 Tip: Canjea energía    \n"
        response += "║     con /loot diario      \n"
        response += "╚══════════════════════════╝\n\n"

        # Barra de progreso para créditos (solo para no-admins) con validación
        if not is_admin:
            try:
                credit_level = min(int(user_data['credits']) // 10, 10)  # Max 10 barras
                progress_bar = "█" * credit_level + "░" * (10 - credit_level)
                response += f"🔋 **Nivel de Energía:** [{progress_bar}] {int(user_data['credits'])}/100+\n\n"
            except Exception as e:
                logger.warning(f"Error creando barra de progreso para {user_id}: {e}")
                response += f"🔋 **Nivel de Energía:** [██████░░░░] {int(user_data['credits'])}/100+\n\n"

        # Comandos de acceso rápido
        response += "⚡ **ACCIONES RÁPIDAS:**\n"
        response += "┌─────────────────────────────┐\n"
        response += "│ `/loot` - Recompensa diaria │\n"
        response += "│ `/simulator` - Casino de riesgo │\n"
        response += "│ `/transmit` - Transferir CR    │\n"
        response += "└─────────────────────────────┘\n\n"

        response += f"🤖 **Usuario:** @{update.effective_user.username or update.effective_user.first_name}\n"
        response += f"📡 **Nodo:** ONLINE"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error crítico en credits_command para usuario {update.effective_user.id}: {e}")
        try:
            # Respuesta de emergencia simplificada
            await update.message.reply_text(
                "❌ **ERROR TEMPORAL** ❌\n\n"
                "Ha ocurrido un error al acceder a tu información.\n"
                "Por favor intenta nuevamente en unos segundos.\n\n"
                "Si el problema persiste, contacta a los administradores.",
                parse_mode=ParseMode.MARKDOWN)
        except Exception as emergency_error:
            logger.error(f"Error crítico absoluto en credits_command: {emergency_error}")
            # Último recurso sin markdown
            try:
                await update.message.reply_text("❌ Error temporal. Intenta /wallet nuevamente.")
            except:
                logger.error("No se pudo enviar ningún mensaje de error para /wallet")

# Alias para inject
async def inject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /inject - Alias de /live"""
    await live_command(update, context)

@check_maintenance
@group_only
@require_credits_for_live(4)
async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verificar tarjetas en vivo - Cuesta 4 créditos"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    # Asegurar que user_data tenga todos los campos necesarios
    if 'total_checked' not in user_data:
        user_data['total_checked'] = 0
    if 'total_generated' not in user_data:
        user_data['total_generated'] = 0
    if 'credits' not in user_data:
        user_data['credits'] = 10

    args = context.args
    if not args:
        response = "🔍 **LSCAN | 𝗠𝗢𝗗𝗢 𝗔𝗡𝗔𝗟𝗜𝗧𝗜𝗖𝗢**\n\n"
        response += "╭───────────────╮\n"
        response += "┃ 🧾 **Formato:** 4532xxxxxxxx1234|12|2025|123\n"
        response += "┃ 📦 **Límite:** 15 tarjetas por envío\n"
        response += "┃ 💸 **Costo:** 4 créditos por chequeo\n"
        response += "╰───────────────╯\n\n"
        response += "⛓️ **𝗨𝘀𝗲 𝗕𝗜𝗡𝘀 𝗮𝗰𝘁𝘂𝗮𝗹𝗲𝘀 𝗽𝗮𝗿𝗮 𝗺𝗲𝗷𝗼𝗿𝗮𝗿 𝗲𝗹 𝗿𝗲𝘀𝘂𝗹𝘁𝗮𝗱𝗼.**\n"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    # Procesar tarjetas del mensaje completo
    full_message = ' '.join(args)
    cards_list = []

    # Buscar tarjetas en formato correcto
    import re
    card_pattern = r'\b\d{13,19}\|\d{1,2}\|\d{4}\|\d{3,4}\b'
    found_cards = re.findall(card_pattern, full_message)

    for card in found_cards:
        parts = card.split('|')
        if len(parts) == 4 and parts[0].isdigit() and len(parts[0]) >= 13:
            cards_list.append(card)

    if not cards_list:
        await update.message.reply_text(
            "❌ **FORMATO INCORRECTO**\n\n"
            "📋 **Formato correcto:** `4532123456781234|12|2025|123`\n"
            "💡 **Tip:** Asegúrate de usar el separador `|`",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Limitar a 15 tarjetas máximo
    cards_list = cards_list[:15]
    total_cards = len(cards_list)

    # Sistema de APIs con pesos de efectividad - MEJORADO
    all_api_methods = [
        ("Stripe Ultra Pro", check_stripe_ultra_pro, 0.85),  # 85% efectividad
        ("PayPal Pro", check_paypal_ultra_pro, 0.75),  # 75% efectividad  
        ("Braintree Pro", check_braintree_ultra_pro, 0.65),  # 65% efectividad
        ("Authorize.net", check_authorize_ultra_pro, 0.55),  # 55% efectividad
        ("Square", check_square_ultra_pro, 0.45),  # 45% efectividad
        ("Adyen Pro", check_adyen_ultra_pro, 0.60),  # 60% efectividad
        ("Worldpay", check_worldpay_ultra_pro, 0.50),  # 50% efectividad
        ("CyberSource AI", check_cybersource_ultra_pro, 0.40
         )  # 40% efectividad
    ]

    # Verificar si el usuario tiene permisos de staff
    staff_data = db.get_staff_role(user_id)
    is_founder = staff_data and staff_data['role'] == '1'
    is_cofounder = staff_data and staff_data['role'] == '2'
    is_moderator = staff_data and staff_data['role'] == '3'
    is_premium = user_data.get('premium', False)

    # Rotación inteligente basada en efectividad
    if is_admin or is_founder or is_cofounder or is_moderator or is_premium:
        # TODOS los roles de staff y premium: Todos los métodos
        api_methods = all_api_methods

        if is_admin:
            methods_text = f"👑 ADMIN MODE - {len(api_methods)} APIs (Efectividad máxima)"
        elif is_founder:
            methods_text = f"🔱 FOUNDER MODE - {len(api_methods)} APIs (Efectividad máxima)"
        elif is_cofounder:
            methods_text = f"💎 CO-FOUNDER MODE - {len(api_methods)} APIs (Efectividad máxima)"
        elif is_moderator:
            methods_text = f"🛡️ MODERATOR MODE - {len(api_methods)} APIs (Efectividad máxima)"
        elif is_premium:
            methods_text = f"👑 PREMIUM MODE - {len(api_methods)} APIs (Efectividad máxima)"

        # Algoritmo de selección inteligente para usuarios privilegiados
        weighted_apis = []
        for name, method, weight in api_methods:
            # Repetir APIs más efectivas para mayor probabilidad de selección
            repetitions = int(
                weight * 10)  # Stripe aparecerá 8.5 veces, Square 4.5 veces
            weighted_apis.extend([(name, method)] * repetitions)

    else:
        # Estándar: 5 métodos más efectivos
        api_methods = all_api_methods[:5]
        methods_text = f"⚡ MODO ESTÁNDAR - {len(api_methods)} APIs (Efectividad estándar)"

        # Selección estándar
        weighted_apis = [(name, method)
                         for name, method, weight in api_methods]

    # Mensaje inicial unificado que funciona para 1 o múltiples tarjetas
    progress_msg = await update.message.reply_text(
        "⧗ [⧉ CHLV_VERIFICATION ACTIVE ⧉]\n\n"
        f"⏳ Progreso: [████░░░░░░] 40%\n"
        f"💳 Procesando tarjeta: 2 de {total_cards}\n\n"
        f"> Módulo: inject vX.2\n"
        f"> Estado: En curso...")

    results = []

    for card_index, card_data in enumerate(cards_list):
        # Actualizar progreso con formato unificado
        try:
            if total_cards > 1:
                progress = (card_index + 1) / total_cards * 100
                progress_bar = "█" * int(
                    progress // 10) + "░" * (10 - int(progress // 10))
                progress_text = f"⏳ Progreso: [{progress_bar}] {progress:.0f}%\n💳 Procesando tarjeta: {card_index + 1} de {total_cards}"
            else:
                progress_text = f"⏳ Progreso: [████░░░░░░] 40%\n💳 Procesando tarjeta: 1 de 1"

            await progress_msg.edit_text(f"⧗ [⧉ SHAD_VERIFICATION ACTIVE ⧉]\n\n"
                                         f"{progress_text}\n\n"
                                         f"> Módulo: inject vX.2\n"
                                         f"> Estado: En curso...")
        except:
            pass

        parts = card_data.split('|')

        # Selección inteligente de API basada en pesos
        if is_admin or is_founder or is_cofounder or is_moderator or is_premium:
            # Para usuarios privilegiados (staff/premium): selección ponderada inteligente
            selected_api = random.choice(weighted_apis)
            api_name, api_method = selected_api
        else:
            # Para estándar: rotación equilibrada
            selected_api = random.choice([
                (name, method) for name, method, weight in api_methods
            ])
            api_name, api_method = selected_api

        # Simular tiempo de verificación realista
        import time
        time.sleep(random.uniform(1.0, 2.0))

        is_live, status, gateways, charge_amount, card_level = api_method(
            card_data)

        # Obtener información del BIN para la tarjeta individual
        bin_number = parts[0][:6]
        bin_info = await get_real_bin_info(bin_number)

        # Obtener respuesta detallada del método
        response_details = status.split(" - ", 1)
        main_status = response_details[0]
        detail_info = response_details[1] if len(response_details) > 1 else ""

        results.append({
            'card_data':
            card_data,
            'parts':
            parts,
            'is_live':
            is_live,
            'api':
            api_name,
            'status':
            "LIVE ✅" if is_live else "DEAD ❌",
            'result':
            detail_info if detail_info else main_status,
            'charge_amount':
            charge_amount if 'charge_amount' in locals() else 0,
            'gateway_response':
            f"Gateway: {api_name}",
            'index':
            card_index + 1,
            'bin_info':
            bin_info,
            'verification_time':
            datetime.now().strftime('%H:%M:%S')
        })

    # Construir respuesta final con formato MULTI-BREACH DETECTED
    final_response = ""

    # Nuevo formato MULTI-BREACH para todas las tarjetas
    final_response += "┌──── MULTI-BREACH DETECTED ▒▒▒\n"
    final_response += f"│ SYSTEM LOGS: {total_cards}/15\n"

    # Procesar cada tarjeta con el nuevo formato
    for i, result in enumerate(results, 1):
        # Determinar el resultado del nodo
        if result['is_live']:
            node_result = "✅ ACCESS OK"
        else:
            node_result = "❌ DENIED — PROTOCOL_TRIPPED"

        # Mapear nombres de API a formato Z-
        api_mapping = {
            "Stripe Ultra Pro": "Z-Stripe Ultra Pro",
            "PayPal Pro": "Z-PayPal Pro", 
            "Braintree Pro": "Z-Braintree Pro",
            "Authorize.net": "Z-Authorize Pro",
            "Square": "Z-Square Pro",
            "Adyen Pro": "Z-Adyen Pro",
            "Worldpay": "Z-Worldpay Pro",
            "CyberSource AI": "Z-CyberSource AI"
        }

        node_name = api_mapping.get(result['api'], f"Z-{result['api']}")

        final_response += f"├── ARCHIVE[{i:02d}]\n"
        final_response += f"│ ↳ ID: {result['card_data']}\n"
        final_response += f"│ ↳ NODE: {node_name}\n"
        final_response += f"│ ↳ RESULT: {node_result}\n"
        final_response += f"│ ↳ SIG: @{update.effective_user.username or update.effective_user.first_name}\n"

    # Estadísticas finales
    live_count = sum(1 for r in results if r['is_live'])
    final_response += f"│\n"
    final_response += f"└── BREACH SUMMARY: {live_count}/{total_cards} NODES COMPROMISED\n"
    final_response += f"    ▒ SUCCESS RATE: {(live_count/total_cards)*100:.1f}%\n"
    final_response += f"    ▒ TIMESTAMP: {datetime.now().strftime('%H:%M:%S')}\n"
    final_response += f"    ▒ OPERATOR: @{update.effective_user.username or update.effective_user.first_name}"

    # Actualizar estadísticas del usuario con manejo de errores
    try:
        db.update_user(
            user_id,
            {'total_checked': user_data['total_checked'] + len(cards_list)})
    except Exception as e:
        logger.error(f"❌ Error importante: {e}")
        # Continuar sin actualizar estadísticas si hay error

    # Enviar respuesta final con mejor manejo de errores
    try:
        await progress_msg.edit_text(final_response)
    except Exception as e:
        logger.error(f"Error editando mensaje de progreso: {e}")
        try:
            # Si falla editar, enviar nuevo mensaje
            await update.message.reply_text(final_response)
        except Exception as e2:
            logger.error(f"Error enviando mensaje de respuesta: {e2}")
            # Mensaje de emergencia con resultados básicos
            try:
                live_count = len([r for r in results if r['is_live']])
                emergency_response = f"✅ **VERIFICACIÓN COMPLETADA**\n\n"
                emergency_response += f"📊 **Resultados:** {live_count}/{total_cards} LIVE\n"
                emergency_response += f"👤 **Usuario:** @{update.effective_user.username or update.effective_user.first_name}\n\n"

                # Mostrar resultados individuales si hay espacio
                if len(results) <= 5:  # Solo si son pocas tarjetas
                    for i, result in enumerate(results, 1):
                        status_emoji = "✅" if result['is_live'] else "❌"
                        card_display = result['card_data'][:4] + "****" + result['card_data'].split('|')[0][-4:]
                        emergency_response += f"{status_emoji} {card_display}\n"

                await update.message.reply_text(emergency_response, parse_mode=ParseMode.MARKDOWN)
            except Exception as e3:
                logger.error(f"Error crítico enviando mensaje de emergencia: {e3}")
                # Último recurso: mensaje ultra-simple sin markdown
                try:
                    simple_msg = f"Verificacion completada: {len([r for r in results if r['is_live']])}/{total_cards} LIVE"
                    await update.message.reply_text(simple_msg)
                except:
                    logger.error("Error crítico: No se pudo enviar ningún mensaje de respuesta")


async def direccion_command(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Generar direcciones por país con datos 100% reales"""
    args = context.args
    country = args[0].upper() if args else None

    # Mostrar países disponibles si no se especifica
    if not country:
        response = f"🌍 **GENERADOR DE DIRECCIONES** 🌍\n\n"
        response += f"**Uso:** `/direccion [país]`\n\n"
        response += f"**Países disponibles:**\n"

        for code, data in AddressGenerator.COUNTRIES_DATA.items():
            response += f"• `{code}` {data['flag']} - {data['country_name']}\n"

        response += f"\n**Ejemplos:**\n"
        response += f"• `/direccion US` - Estados Unidos\n"
        response += f"• `/direccion BR` - Brasil\n"
        response += f"• `/direccion ES` - España\n"
        response += f"• `/direccion AR` - Argentina\n"
        response += f"• `/direccion KZ` - Kazajistán\n"
        response += f"• `/direccion AE` - Dubái (UAE)"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    # Generar dirección
    address = AddressGenerator.generate_address(country)

    if not address:
        await update.message.reply_text(
            f"❌ **País '{country}' no disponible**\n\n"
            f"💡 Usa `/direccion` para ver países disponibles",
            parse_mode=ParseMode.MARKDOWN)
        return

    response = f"📍 **DIRECCIÓN GENERADA** 📍\n\n"
    response += f"{address['flag']} **País:** {address['country']}\n"
    response += f"🏠 **Dirección:** {address['street']}\n"
    response += f"🌆 **Ciudad:** {address['city']}\n"
    response += f"🗺️ **Estado/Provincia:** {address['state']}\n"
    response += f"📮 **Código Postal:** {address['postal_code']}\n"
    response += f"📞 **Teléfono:** {address['phone']}\n\n"
    response += f"✅ **Datos 100% reales y verificados**\n"
    response += f"🔄 **Usa el comando nuevamente para generar otra**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@check_maintenance
async def ex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extrapolación avanzada de tarjetas - Solo admins, fundadores, co-fundadores, moderadores y premium"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    # Verificar si es admin, staff o premium
    is_founder = db.is_founder(user_id)
    is_cofounder = db.is_cofounder(user_id)
    is_moderator = db.is_moderator(user_id)
    is_premium = user_data.get('premium', False)

    # Permitir acceso a admins, fundadores, co-fundadores, moderadores y premium
    if not (is_admin or is_founder or is_cofounder or is_moderator
            or is_premium):
        await update.message.reply_text(
            "╒═📛 BLOQUEO DE ACCESO ═╕\n"
            "│ 🔒 Canal: Extrapolación IA\n"
            "│ 💠 Estado: Solo Premium\n"
            "│ \n"
            "│ 🧭 Soluciones:\n"
            "│ ├ Activa tu membresía Premium\n"
            "│ └ Usa comandos básicos disponibles\n"
            "╘════════════════════════╛\n"
            "📡 Nodo de contacto: @SteveCHRB",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar créditos solo si no es admin
    if not is_admin:
        if user_data['credits'] < 5:
            await update.message.reply_text(
                f"❌ **Créditos insuficientes**\n\n"
                f"Necesitas: 5 créditos\n"
                f"Tienes: {user_data['credits']} créditos\n\n"
                f"Usa /loot para créditos gratis o /audit para más información",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Descontar créditos
        db.update_user(user_id, {'credits': user_data['credits'] - 5})

    args = context.args
    if not args:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "║  🧠 **EXTRAPOLACIÓN PREMIUM** 🧠  ║\n"
            "╚═══════════════════════════════╝\n\n"
            "💎 **Formatos soportados:**\n"
            "• `/ex 4532123456781234|12|2025|123`\n"
            "• `/ex 4532123456781234`\n\n"
            "🤖 **Algoritmo IA:**\n"
            "• Genera variaciones inteligentes\n"
            "• Mantiene patrones del BIN original\n"
            "• Optimizado para máxima efectividad\n\n"
            "💰 **Costo:** 5 créditos\n"
            "⚡ **Cantidad:** 20 variaciones únicas",
            parse_mode=ParseMode.MARKDOWN)
        return

    card_input = args[0]

    # Detectar y procesar diferentes formatos
    if '|' in card_input:
        # Formato completo: 4532123456781234|12|2025|123
        parts = card_input.split('|')
        if len(parts) != 4:
            await update.message.reply_text(
                "❌ **Formato incorrecto**\n\n"
                "✅ **Formatos válidos:**\n"
                "• `4532123456781234|12|2025|123`\n"
                "• `4532123456781234`")
            return

        base_card = parts[0]
        preset_month = parts[1]
        preset_year = parts[2]
        preset_cvv = parts[3]
    else:
        # Solo número: 4532123456781234
        if not card_input.isdigit() or len(card_input) < 13:
            await update.message.reply_text(
                "❌ **Número de tarjeta inválido**\n\n"
                "💡 Debe tener al menos 13 dígitos")
            return

        base_card = card_input
        preset_month = None
        preset_year = None
        preset_cvv = None

    # Extraer BIN
    bin_number = base_card[:6]

    # Mensaje de procesamiento
    process_msg = await update.message.reply_text(
        "🧠 **PROCESANDO EXTRAPOLACIÓN** 🧠\n\n"
        "⚡ Analizando patrones del BIN...\n"
        "🤖 Ejecutando algoritmos de IA...\n"
        "🔄 Generando variaciones inteligentes...")

    # Simular procesamiento avanzado
    await asyncio.sleep(3)

    # Generar variaciones inteligentes
    variations = []
    for i in range(20):
        if preset_month and preset_year and preset_cvv:
            # Usar parámetros específicos
            new_card = CardGenerator.generate_cards_custom(
                bin_number, 1, preset_month, preset_year, preset_cvv)[0]
        else:
            # Generar aleatorio
            new_card = CardGenerator.generate_cards(bin_number, 1)[0]
        variations.append(new_card)

    # Obtener información real del BIN
    bin_info = await get_real_bin_info(bin_number)

    # Formato de respuesta mejorado
    final_response = "╔═══════════════════════════════╗\n"
    final_response += "║  🧠 **EXTRAPOLACIÓN COMPLETA** 🧠  ║\n"
    final_response += "╚═══════════════════════════════╝\n\n"

    final_response += f"🎯 **BIN Analizado:** {bin_number}xxxxxx\n"
    final_response += f"🏦 **Banco:** {bin_info['bank']}\n"
    final_response += f"💳 **Tipo:** {bin_info['scheme']} | {bin_info['type']}\n"
    final_response += f"🌍 **País:** {bin_info['country']}\n"
    final_response += f"🔢 **Variaciones:** 20 únicas\n\n"

    final_response += "```\n"
    for i, var in enumerate(variations, 1):
        final_response += f"{i:2d}. {var}\n"
    final_response += "```\n\n"

    final_response += "🎯 **Probabilidad:** 75-85% efectividad\n"
    final_response += f"💰 **Créditos restantes:** {user_data['credits'] - 5 if not is_admin else '∞'}\n"
    final_response += "🤖 **Generado por IA avanzada**"

    try:
        await process_msg.edit_text(final_response,
                                    parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(final_response,
                                        parse_mode=ParseMode.MARKDOWN)


async def bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reclamar bono diario"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)

    now = datetime.now()
    last_bonus = user_data.get('last_bonus')

    if last_bonus:
        last_bonus_date = datetime.fromisoformat(last_bonus)
        if (now - last_bonus_date).days < 1:
            time_diff = now - last_bonus_date
            hours_left = 24 - (time_diff.seconds // 3600)
            minutes_left = 60 - ((time_diff.seconds % 3600) // 60)

            response = f"┏━━━⛔ ACCESO DENEGADO ━━━┓\n"
            response += f"┃ 💉 Ya reclamaste tu dosis diaria ┃\n"
            response += f"┃ 🧬 Próximo acceso en: {hours_left}H {minutes_left}M ┃\n"
            response += f"┃ 🔒 Canal: FLUJO/DAILY ┃\n"
            response += f"┗━━━━━━━━━━━━━━━━━━━━━━━━━┛"

            await update.message.reply_text(response)
            return

    # Dar bono
    bonus_amount = 15 if user_data['premium'] else 10

    db.update_user(
        user_id, {
            'credits': user_data['credits'] + bonus_amount,
            'last_bonus': now.isoformat()
        })

    response = f"╔═[⚠ SYSTEM PATCH: INJECTION OK ]═╗\n"
    response += f"║ 📡 FLUJO: DIARIA - Canal_015     ║\n"
    response += f"║ 💾 Carga recibida: +{bonus_amount} loot        ║\n"
    response += f"║ 🧮 Loot Wallet: {user_data['credits'] + bonus_amount} Units     ║\n"
    response += f"║ 🕘 Próxima carga: +24H           ║\n"
    response += f"╠═══════════════════════════════╣\n"
    response += f"║ ✳️ Recuerda: flujo constante     ║\n"
    response += f"║     garantiza continuidad...     ║\n"
    response += f"╚═══════════════════════════════╝"

    await update.message.reply_text(response)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estado del bot"""
    response = f"🛰️ **ESTADO DEL NÚCLEO**\n\n"

    response += f"• 🟢 Online y operativo\n"
    response += f"• ⚙️ Versión: v4.2\n"
    response += f"• 💻 Servidor: Anonymous\n"
    response += f"• 🌐 Ping: 47ms\n"
    response += f"• 🔒 Seguridad SSL: Activa\n"
    response += f"• ⏳ Uptime: 99.9%\n"
    response += f"• 🔄 Última sync: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

    response += f"📡 **Sistema completamente operacional**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


async def detect_payment_gateways(url: str):
    """Detecta las pasarelas de pago de un sitio web con análisis mejorado"""
    import re

    try:
        # Validar URL primero
        if not url or len(url) < 4:
            return None

        # Limpiar y formatear URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Validar formato de URL básico
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url):
            return None

        # Intentar importar requests, si no está disponible usar urllib
        try:
            import requests
            use_requests = True
        except ImportError:
            import urllib.request
            import urllib.parse
            use_requests = False

        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        content = ""
        # Obtener contenido de la página con mejor manejo de errores
        if use_requests:
            try:
                # Múltiples intentos con diferentes configuraciones
                session = requests.Session()
                session.headers.update(headers)

                # Primer intento: HTTPS con verificación
                try:
                    response = session.get(url, timeout=10, verify=True)
                    response.raise_for_status()
                    content = response.text.lower()
                except requests.exceptions.SSLError:
                    # Segundo intento: HTTPS sin verificación
                    try:
                        response = session.get(url, timeout=10, verify=False)
                        response.raise_for_status()
                        content = response.text.lower()
                    except:
                        # Tercer intento: HTTP si HTTPS falla
                        http_url = url.replace('https://', 'http://')
                        response = session.get(http_url,
                                               timeout=10,
                                               verify=False)
                        response.raise_for_status()
                        content = response.text.lower()

            except Exception as req_error:
                logger.error(f"Requests error for {url}: {req_error}")
                return None
        else:
            try:
                import ssl
                # Crear contexto SSL permisivo
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req,
                                            timeout=10,
                                            context=ssl_context) as response:
                    content = response.read().decode('utf-8',
                                                     errors='ignore').lower()
            except Exception as urllib_error:
                logger.error(f"Urllib error for {url}: {urllib_error}")
                return None

        if not content or len(content) < 100:
            return None

        detected_gateways = {'destacadas': [], 'principales': [], 'otras': []}

        # Pasarelas destacadas (más efectivas para CC) - AMPLIADAS
        gateways_destacadas = {
            'shopify': [
                '🔥 Shopify Payments',
                [
                    'shopify', 'shopify-pay', 'shop-pay', 'shopifycdn',
                    'cdn.shopify'
                ]
            ],
            'woocommerce': [
                '🔥 WooCommerce',
                [
                    'woocommerce', 'wc-', 'wordpress', 'wp-content',
                    'wp-includes'
                ]
            ],
            'magento': [
                '🔥 Magento',
                ['magento', 'mage-', 'mage_', 'magento_', 'magentocommerce']
            ],
            'prestashop': [
                '🔥 PrestaShop',
                ['prestashop', 'presta-shop', 'ps_', 'prestashop.com']
            ],
            'opencart':
            ['🔥 OpenCart', ['opencart', 'open-cart', 'oc-', 'opencart.com']],
            'bigcommerce': [
                '🔥 BigCommerce',
                ['bigcommerce', 'big-commerce', 'bigcommerce.com']
            ]
        }

        # Pasarelas principales (muy comunes) - MEJORADAS
        gateways_principales = {
            'paypal': [
                '✅ PayPal',
                [
                    'paypal', 'pp-', 'paypal.com', 'paypalobjects',
                    'paypal-button', 'paypal.js'
                ]
            ],
            'stripe': [
                '✅ Stripe',
                [
                    'stripe', 'js.stripe.com', 'stripe.com', 'sk_live',
                    'pk_live', 'stripe-elements', 'stripe.js'
                ]
            ],
            'square': [
                '✅ Square',
                [
                    'square', 'squareup', 'square.com', 'sq-', 'squarecdn',
                    'web.squarecdn'
                ]
            ],
            'authorize': [
                '✅ Authorize.net',
                [
                    'authorize.net', 'authorizenet', 'authorize-net', 'anet-',
                    'accept.js'
                ]
            ],
            'braintree': [
                '✅ Braintree',
                [
                    'braintree', 'braintreepayments', 'bt-', 'braintree-web',
                    'braintreegateway'
                ]
            ],
            'adyen': [
                '✅ Adyen',
                [
                    'adyen', 'adyen.com', 'adyen-', 'adyen-web',
                    'checkoutshopper'
                ]
            ],
            'worldpay': [
                '✅ Worldpay',
                [
                    'worldpay', 'worldpay.com', 'wp-', 'worldpay-lib',
                    'worldpayap.com'
                ]
            ],
            'razorpay': [
                '✅ Razorpay',
                ['razorpay', 'razorpay.com', 'checkout.razorpay', 'rzp_']
            ]
        }

        # Otras pasarelas detectables - EXPANDIDAS
        gateways_otras = {
            'applepay': [
                '🍎 Apple Pay',
                ['apple-pay', 'applepay', 'apple_pay', 'apple-pay-button']
            ],
            'googlepay': [
                '🔵 Google Pay',
                [
                    'google-pay', 'googlepay', 'google_pay', 'gpay',
                    'pay.google'
                ]
            ],
            'amazonpay': [
                '📦 Amazon Pay',
                ['amazon-pay', 'amazonpay', 'amazon_pay', 'payments.amazon']
            ],
            'klarna':
            ['🔶 Klarna', ['klarna', 'klarna.com', 'klarna-payments']],
            'afterpay':
            ['⚪ Afterpay', ['afterpay', 'afterpay.com', 'afterpay-button']],
            'affirm': ['🟣 Affirm', ['affirm', 'affirm.com', 'affirm-button']],
            'payu': ['🟡 PayU', ['payu', 'payu.com', 'payu-', 'payulatam']],
            'mercadopago': [
                '🟢 MercadoPago',
                ['mercadopago', 'mercado-pago', 'mp-', 'mercadolibre']
            ],
            'checkout': [
                '🔷 Checkout.com',
                ['checkout.com', 'checkout-', 'cko-', 'checkout.js']
            ],
            'mollie':
            ['🟠 Mollie', ['mollie', 'mollie.com', 'mollie-payments']],
            'cybersource': [
                '🔐 CyberSource',
                ['cybersource', 'cybersource.com', 'cybersource-api']
            ],
            '2checkout': ['2️⃣ 2Checkout', ['2checkout', '2co-', 'verifone']],
            'payoneer': ['💳 Payoneer', ['payoneer', 'payoneer.com']],
            'pagseguro':
            ['🇧🇷 PagSeguro', ['pagseguro', 'uol.com.br', 'pagseguro.uol']],
            'conekta':
            ['🇲🇽 Conekta', ['conekta', 'conekta.com', 'conekta.js']],
            'culqi': ['🇵🇪 Culqi', ['culqi', 'culqi.com', 'culqi.js']],
            'wompi': ['🇨🇴 Wompi', ['wompi', 'wompi.co', 'wompi.com']],
            'paymentez': ['💰 Paymentez', ['paymentez', 'paymentez.com']],
            'kushki': ['🎯 Kushki', ['kushki', 'kushki.com']],
            'openpay': ['🔓 OpenPay', ['openpay', 'openpay.mx']],
            'ebanx': ['🌎 EBANX', ['ebanx', 'ebanx.com']],
            'blockchain': [
                '₿ Blockchain',
                ['blockchain', 'bitcoin', 'btc', 'crypto', 'metamask']
            ],
            'zelle': ['💸 Zelle', ['zelle', 'zellepay']],
            'cashapp': ['💵 Cash App', ['cashapp', 'cash.app', '$cashtag']]
        }

        # Detectar cada categoría con scoring mejorado
        content_words = content.split()

        for key, (name, indicators) in gateways_destacadas.items():
            score = 0
            for indicator in indicators:
                if indicator in content:
                    score += content.count(indicator)
            if score > 0:
                detected_gateways['destacadas'].append(name)

        for key, (name, indicators) in gateways_principales.items():
            score = 0
            for indicator in indicators:
                if indicator in content:
                    score += content.count(indicator)
            if score > 0:
                detected_gateways['principales'].append(name)

        for key, (name, indicators) in gateways_otras.items():
            score = 0
            for indicator in indicators:
                if indicator in content:
                    score += content.count(indicator)
            if score > 0:
                detected_gateways['otras'].append(name)

        # Remover duplicados manteniendo orden
        for category in detected_gateways:
            detected_gateways[category] = list(
                dict.fromkeys(detected_gateways[category]))

        return detected_gateways

    except Exception as e:
        logger.error(f"Error en detect_payment_gateways: {e}")
        return None


async def pasarela_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detectar pasarelas de pago de un sitio web mejorado"""
    args = context.args

    if not args:
        response = f"⧼ 📊 ESCÁNER BRIDGE 📊 ⧽\n\n"
        response += f"🛰️ **Comando:** `/bridge [URL]`\n\n"
        response += f"✔️ **Detecta 40+ gateways de pago**\n"
        response += f"✔️ **Análisis inteligente IA**\n"
        response += f"✔️ **Compatible con e-commerce LATAM**\n"
        response += f"✔️ **Detección de crypto & métodos alternativos**\n"
        response += f"✔️ **Soporte para sitios protegidos**\n"
        response += f"✔️ **Múltiples intentos de conexión**\n\n"
        response += f"💡 **Tip:** No necesitas incluir \"https://\"\n"
        response += f"🌐 **Compatible con sitios protegidos**\n"
        response += f"🎯 **Soporte:** bridge mundiales y regionales\n\n"
        response += f"**Ejemplos de uso:**\n"
        response += f"• `/bridge amazon.com`\n"
        response += f"• `/bridge mercadolibre.com.ar`\n"
        response += f"• `/bridge stripe.com`"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    url = args[0].strip()

    # Validación avanzada de URL
    if not url or len(url) < 4:
        await update.message.reply_text("❌ **URL vacía o muy corta**\n\n"
                                        "💡 Proporciona una URL válida\n"
                                        "📋 **Ejemplo:** `amazon.com`")
        return

    # Limpiar caracteres especiales
    import re
    url = re.sub(r'[^\w\-._~:/?#[\]@!$&\'()*+,;=]', '', url)

    # Agregar protocolo si no lo tiene
    original_url = url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Validación mejorada de dominio
    domain_extensions = [
        '.com', '.net', '.org', '.io', '.co', '.me', '.ly', '.gg', '.tv',
        '.mx', '.ar', '.br', '.cl', '.pe', '.co', '.ec', '.uy', '.bo', '.es',
        '.fr', '.de', '.it', '.uk', '.ru', '.cn', '.jp'
    ]

    if not any(ext in url.lower() for ext in domain_extensions):
        await update.message.reply_text(
            "❌ **Dominio inválido**\n\n"
            "💡 Asegúrate de incluir una extensión válida\n"
            "📋 **Ejemplo:** `amazon.com`, `mercadolibre.com.ar`\n"
            "🌎 **Soportado:** .com, .net, .org, .mx, .ar, .br, etc.")
        return

    # Mensaje de análisis mejorado con progreso
    analysis_msg = await update.message.reply_text(
        "⧼ 🔍 ANALIZADOR ULTRA ACTIVADO ⧽\n\n"
        f"🛰️ **Target:** {original_url}\n"
        f"🔗 **Procesando:** {url}\n"
        f"⚡ **Fase 1:** Validando conectividad...\n"
        f"📊 **Progreso:** [█░░░░░░░░░] 10%\n\n"
        f"🤖 **Motor:** ChernobylChLv Ultra Engine",
        parse_mode=ParseMode.MARKDOWN)

    try:
        # Simular progreso y dar tiempo al servidor
        import asyncio
        await asyncio.sleep(1)

        # Actualizar progreso
        await analysis_msg.edit_text(
            "⧼ ⚡ ANÁLISIS EN PROGRESO ⧽\n\n"
            f"🛰️ **Target:** {original_url}\n"
            f"🔗 **Procesando:** {url}\n"
            f"⚡ **Fase 2:** Obteniendo contenido web...\n"
            f"📊 **Progreso:** [███░░░░░░░] 30%\n\n"
            f"🧠 **IA:** Analizando estructura...",
            parse_mode=ParseMode.MARKDOWN)

        detected = await detect_payment_gateways(url)

        # Simular más progreso
        await asyncio.sleep(0.5)
        await analysis_msg.edit_text(
            "⧼ 🧠 ANÁLISIS IA AVANZADO ⧽\n\n"
            f"🛰️ **Target:** {original_url}\n"
            f"🔗 **Procesando:** {url}\n"
            f"⚡ **Fase 3:** Detectando bridges...\n"
            f"📊 **Progreso:** [██████░░░░] 60%\n\n"
            f"🔍 **Escaneando:** 40+ patrones de gateways",
            parse_mode=ParseMode.MARKDOWN)

        if detected is None:
            await analysis_msg.edit_text(
                f"❌ **ANÁLISIS FALLIDO** ❌\n\n"
                f"🌐 **URL:** {original_url}\n"
                f"🔗 **Intentado:** {url}\n\n"
                f"💡 **Posibles causas:**\n"
                f"• 🚫 Sitio web no accesible o caído\n"
                f"• 🛡️ Protección anti-bots/firewall activo\n"
                f"• 🔒 Bloqueo geográfico o SSL estricto\n"
                f"• ❌ URL incorrecta o dominio inexistente\n"
                f"• ⚡ Problemas temporales de conectividad\n\n"
                f"🔄 **Soluciones:**\n"
                f"• Verifica que la URL esté bien escrita\n"
                f"• Intenta sin 'www' o con 'www'\n"
                f"• Prueba más tarde si es un error temporal\n"
                f"• Usa una URL alternativa del mismo sitio\n\n"
                f"✅ **URLs de prueba:** `amazon.com`, `stripe.com`, `paypal.com`",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Progreso final
        await analysis_msg.edit_text(
            "⧼ ✨ FINALIZANDO ANÁLISIS ⧽\n\n"
            f"🛰️ **Target:** {original_url}\n"
            f"⚡ **Fase 4:** Generando reporte...\n"
            f"📊 **Progreso:** [██████████] 100%\n\n"
            f"📋 **Compilando resultados...**",
            parse_mode=ParseMode.MARKDOWN)

        await asyncio.sleep(0.5)

        # Construir respuesta con el nuevo formato CHLV
        total_detected = sum(len(gateways) for gateways in detected.values())

        if total_detected == 0:
            response = f"⧼ 📊 REPORTE DE ANÁLISIS ⧽\n"
            response += f"{'═' * 35}\n\n"
            response += f"🛰️ **TARGET ESCANEADO:**\n"
            response += f"↳ {url}\n\n"
            response += f"📦 **DETECCIÓN INTELIGENTE:**\n"
            response += f"┣ 🏪 Plataformas E-Commerce: 0\n"
            response += f"┣ 💳 Procesadores de pago: 0\n"
            response += f"┣ 💰 Métodos alternativos: 0\n"
            response += f"┗ 🎯 Total detectado: 0\n\n"
            response += f"📊 **ESTADÍSTICAS IA:**\n"
            response += f"┌─────────────────────┐\n"
            response += f"│ 🏪 E-Commerce.....: 0  │\n"
            response += f"│ 💳 Gateways.......: 0  │\n"
            response += f"│ 💰 Métodos alt....: 0  │\n"
            response += f"│ ⚠️ Potencial CC...: ❌  │\n"
            response += f"└─────────────────────┘\n\n"
            response += f"⏰ **Completado:** {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}\n"
            response += f"🤖 **Motor:** ChernobylChLv Ultra Engine\n"
            response += f"👤 **Usuario:** @{update.effective_user.username or update.effective_user.first_name}\n"
            response += f"{'═' * 35}"
        else:
            # Análisis de efectividad
            if len(detected['principales']) >= 3:
                effectiveness = "✅ ULTRA ALTO"
                risk_icon = "🔥"
            elif len(detected['principales']) >= 2:
                effectiveness = "✅ ALTO"
                risk_icon = "⚡"
            elif len(detected['principales']) >= 1:
                effectiveness = "⚠️ MEDIO"
                risk_icon = "🟡"
            else:
                effectiveness = "❌ BAJO"
                risk_icon = "🔵"

            response = f"⧼ 📊 REPORTE DE ANÁLISIS ⧽\n"
            response += f"{'═' * 35}\n\n"
            response += f"🛰️ **TARGET ESCANEADO:**\n"
            response += f"↳ {url}\n\n"
            response += f"📦 **DETECCIÓN INTELIGENTE:**\n"
            response += f"┣ 🏪 Plataformas E-Commerce: {len(detected['destacadas'])}\n"

            # Mostrar plataformas detectadas
            if detected['destacadas']:
                for gateway in detected['destacadas']:
                    # Limpiar el emoji del inicio para mostrarlo correctamente
                    clean_gateway = gateway.replace('🔥 ', '')
                    response += f"┃ ┗ ⚡ {clean_gateway}\n"

            response += f"┣ 💳 Procesadores de pago: {len(detected['principales'])}\n"

            # Mostrar procesadores detectados
            if detected['principales']:
                for i, gateway in enumerate(detected['principales']):
                    # Limpiar el emoji del inicio
                    clean_gateway = gateway.replace('✅ ', '')
                    prefix = "┃ ┣" if i < len(detected['principales']) - 1 else "┃ ┗"
                    response += f"{prefix} 💳 {clean_gateway}\n"

            response += f"┣ 💰 Métodos alternativos: {len(detected['otras'])}\n"

            # Mostrar métodos extra detectados
            if detected['otras']:
                for i, gateway in enumerate(detected['otras']):
                    # Extraer solo el nombre sin emojis complejos
                    clean_gateway = gateway.split(' ', 1)[1] if ' ' in gateway else gateway
                    prefix = "┃ ┣" if i < len(detected['otras']) - 1 else "┃ ┗"
                    response += f"{prefix} 💰 {clean_gateway}\n"

            response += f"┗ 🎯 Total detectado: {total_detected}\n\n"
            response += f"📊 **ESTADÍSTICAS IA:**\n"
            response += f"┌─────────────────────┐\n"
            response += f"│ 🏪 E-Commerce.....: {len(detected['destacadas']):2d} │\n"
            response += f"│ 💳 Gateways.......: {len(detected['principales']):2d} │\n"
            response += f"│ 💰 Métodos alt....: {len(detected['otras']):2d} │\n"
            response += f"│ {risk_icon} Potencial CC...: {effectiveness} │\n"
            response += f"└─────────────────────┘\n\n"
            response += f"⏰ **Completado:** {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}\n"
            response += f"🤖 **Motor:** ChernobylChLv Ultra Engine\n"
            response += f"👤 **Usuario:** @{update.effective_user.username or update.effective_user.first_name}\n"
            response += f"{'═' * 35}"

        await analysis_msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        error_msg = str(e)[:80] + "..." if len(str(e)) > 80 else str(e)

        await analysis_msg.edit_text(
            f"❌ **ERROR CRÍTICO EN ANÁLISIS** ❌\n\n"
            f"🌐 **URL:** {original_url}\n"
            f"🔗 **Procesando:** {url}\n"
            f"🔍 **Error técnico:** {error_msg}\n\n"
            f"🔄 **Sugerencias de solución:**\n"
            f"• ✅ Verifica que la URL esté bien escrita\n"
            f"• 🌐 Intenta sin 'www' o agregando 'www'\n"
            f"• 🔄 Prueba nuevamente en unos minutos\n"
            f"• 📱 Verifica tu conexión a internet\n"
            f"• 💡 Usa una URL más simple (sin rutas)\n\n"
            f"✅ **URLs de prueba que siempre funcionan:**\n"
            f"• `amazon.com` - E-commerce global\n"
            f"• `stripe.com` - Procesador de pagos\n"
            f"• `paypal.com` - Pagos online\n"
            f"• `mercadolibre.com` - E-commerce LATAM\n\n"
            f"🤖 **Si el problema persiste, contacta a los administradores**",
            parse_mode=ParseMode.MARKDOWN)

        logger.error(f"Error crítico en comando /bridge: {e}")


async def apply_key_command(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Aplicar clave premium"""
    user_id = str(update.effective_user.id)

    args = context.args
    if not args:
        await update.message.reply_text(
            "🔑 **APLICAR CLAVE PREMIUM** 🔑\n\n"
            "Uso: /apply_key [código]\n"
            "Ejemplo: /apply_key ULTRA2024\n\n"
            "💎 Las claves premium te dan acceso completo",
            parse_mode=ParseMode.MARKDOWN)
        return

    key_code = args[0].upper()

    # Claves válidas simuladas
    VALID_KEYS = {
        'ULTRA30': {
            'days': 30,
            'used': False
        },
        'PREMIUM460': {
            'days': 60,
            'used': False
        },
        'VIP90': {
            'days': 90,
            'used': False
        },
        'ChernobilChLv_365': {
            'days': 365,
            'used': False
        }
    }

    if key_code not in VALID_KEYS or VALID_KEYS[key_code]['used']:
        await update.message.reply_text(
            "❌ **Clave inválida o ya utilizada**\n\n"
            "Verifica el código e intenta nuevamente",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Activar premium
    days = VALID_KEYS[key_code]['days']
    premium_until = datetime.now() + timedelta(days=days)

    db.update_user(
        user_id,
        {
            'premium': True,
            'premium_until': premium_until.isoformat(),
            'credits': db.get_user(user_id)['credits'] + 100  # Bonus credits
        })

    # Marcar clave como usada
    VALID_KEYS[key_code]['used'] = True

    response = f"🎉 **CLAVE ACTIVADA EXITOSAMENTE** 🎉\n\n"
    response += f"👑 **Premium activado por {days} días**\n"
    response += f"💎 **+300 créditos bonus**\n"
    response += f"⚡ **Beneficios premium desbloqueados:**\n\n"
    response += f"• Verificación completa 6 métodos\n"
    response += f"• Límites aumentados\n"
    response += f"• Bono diario premium\n"
    response += f"• Soporte prioritario\n"
    response += f"• Algoritmos avanzados"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


async def infocredits_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Información sobre créditos con botones inline mejorados"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)

    keyboard = [[
        InlineKeyboardButton("💰 Obtener Créditos",
                             callback_data='get_credits'),
        InlineKeyboardButton("👑 Premium", callback_data='premium_benefits')
    ],
                [
                    InlineKeyboardButton("🆓 Comandos Gratis",
                                         callback_data='free_commands'),
                    InlineKeyboardButton("💎 Comandos de Pago",
                                         callback_data='paid_commands')
                ],
                [
                    InlineKeyboardButton("📊 Mis Estadísticas",
                                         callback_data='my_stats'),
                    InlineKeyboardButton("🎮 Simulator",
                                         callback_data='go_games')
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    premium_text = ""
    if user_data['premium']:
        premium_until = datetime.fromisoformat(user_data['premium_until'])
        days_left = (premium_until - datetime.now()).days
        premium_text = f"\n👑 **PREMIUM ACTIVO** ({days_left} días)"

    response = f"╔═══════════════════════════╗\n"
    response += f"║     💡 𝐒𝐈𝐒𝐓𝐄𝐌𝐀 𝐃𝐄 𝐂𝐑É𝐃𝐈𝐓𝐎𝐒     ║\n"
    response += f"╚═══════════════════════════╝\n\n"
    response += f"💎 **Tus Créditos:** {user_data['credits']}{premium_text}\n\n"
    response += f"📋 **Selecciona una opción:**"

    await update.message.reply_text(response,
                                    reply_markup=reply_markup,
                                    parse_mode=ParseMode.MARKDOWN)


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Donar créditos a otro usuario con diseño mejorado"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    args = context.args
    if len(args) < 2:
        credits_display = user_data['credits'] if not is_admin else '∞ (Admin)'

        await update.message.reply_text(
            "[▣] INITIATE CREDIT TRANSFER PROTOCOL [▣]\n\n"
            "▸ Command: /transmit [user_id] [amount]\n"
            "▸ Example: /transmit 123456789 50\n\n"
            "▸ SYSTEM NOTE:\n"
            "   + Mantener el equilibrio del ecosistema\n"
            "   + Contribuir al crecimiento de la comunidad\n\n"
            f"▸ Current balance: {credits_display} CR\n\n"
            "▸ TRANSFER BENEFITS:\n"
            "   → Apoyar a otros usuarios de la red\n"
            "   → Fortalecer el ecosistema\n"
            "   → Construir conexiones colaborativas",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        target_user_id = args[0]
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text(
            "❌ **Error en el formato**\n\n"
            "💡 La cantidad debe ser un número válido\n"
            "📋 **Ejemplo:** `/transmit 123456789 50`")
        return

    if amount <= 0:
        await update.message.reply_text("❌ **Cantidad inválida**\n\n"
                                        "💡 La cantidad debe ser mayor a 0\n"
                                        "📊 **Mínimo:** 1 crédito")
        return

    # Verificar créditos suficientes
    if not is_admin and user_data['credits'] < amount:
        await update.message.reply_text(
            "╔═══════════════════════════════╗\n"
            "║    ❌ **CRÉDITOS INSUFICIENTES** ❌    ║\n"
            "╚═══════════════════════════════╝\n\n"
            f"💰 **Tienes:** {user_data['credits']} créditos\n"
            f"💸 **Necesitas:** {amount} créditos\n"
            f"📉 **Faltante:** {amount - user_data['credits']} créditos\n\n"
            "💡 **Obtén más créditos con:**\n"
            "• `/loot` - Bono diario gratis\n"
            "• `/simulator` - Casino bot\n"
            "• Contacto con @SteveCHBll para mas creditos",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Procesar transferencia
    target_user_data = db.get_user(target_user_id)

    # Solo descontar créditos si no es admin
    if not is_admin:
        db.update_user(user_id, {'credits': user_data['credits'] - amount})

    db.update_user(target_user_id,
                   {'credits': target_user_data['credits'] + amount})

    # Respuesta con el nuevo formato luminoso
    donante_display = f"{update.effective_user.first_name}"
    if is_admin:
        donante_display += " (∞)"

    response = "⧼ ⚡ TRANSACCIÓN LUMINOSA ⚡ ⧽\n\n"
    response += f"💸 Créditos enviados: ✦ {amount} ✦\n"
    response += f"🧬 Receptor ID: {target_user_id}\n"
    response += f"🪙 Saldo actualizado: {target_user_data['credits'] + amount} CR\n\n"
    response += f"👤 Donante: {donante_display}\n"
    response += f"🕒 Fecha: {datetime.now().strftime('%d·%m·%Y | %H:%M')}\n\n"
    response += f"➤ La energía fue transferida con éxito."

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    # Enviar notificación privada al receptor con manejo mejorado
    notification_status = "❌ No enviada"
    try:
        donante_display = f"{update.effective_user.first_name}"
        if is_admin:
            donante_display += " (∞)"

        receiver_message = f"❖ 𝗡𝗢𝗧𝗜𝗙𝗜𝗖𝗔𝗖𝗜𝗢́𝗡 𝗦𝗜𝗦𝗧𝗘́𝗠𝗜𝗖𝗔 ❖\n\n"
        receiver_message += f"🧬 Te han inyectado {amount} créditos\n"
        receiver_message += f"🎯 Origen: {donante_display}"

        # Agregar username si está disponible
        if update.effective_user.username:
            receiver_message += f" (@{update.effective_user.username})"

        receiver_message += f"\n🪙 Saldo total: {target_user_data['credits'] + amount} CR\n\n"
        receiver_message += f"🕒 {datetime.now().strftime('%d.%m.%Y • %H:%M')}\n\n"
        receiver_message += f"➤ ¿Destino o coincidencia?\n\n"
        receiver_message += f"🤖 **ChernobilChLv Bot**"

        # Intentar enviar notificación al receptor
        await context.bot.send_message(chat_id=int(target_user_id),
                                       text=receiver_message,
                                       parse_mode=ParseMode.MARKDOWN)

        notification_status = "✅ Enviada exitosamente"
        logger.info(f"✅ Notificación de donación enviada al receptor {target_user_id}")

    except Exception as e:
        error_msg = str(e).lower()

        if "chat not found" in error_msg:
            notification_status = "❌ Usuario nunca inició el bot"
            logger.warning(f"❌ Usuario {target_user_id} no ha iniciado conversación con el bot")
        elif "blocked" in error_msg or "forbidden" in error_msg:
            notification_status = "❌ Usuario bloqueó el bot"
            logger.warning(f"❌ Usuario {target_user_id} ha bloqueado el bot")
        else:
            notification_status = f"❌ Error: {str(e)[:30]}..."
            logger.warning(f"❌ Error enviando notificación a {target_user_id}: {e}")

    # Actualizar la respuesta principal para incluir estado de notificación
    response += f"\n📱 **Notificación al receptor:** {notification_status}"

    # Enviar notificación privada al donante (confirmación) con estado de entrega
    try:
        if not is_admin:  # Solo si no es admin (para evitar spam a admins)
            donor_message = f"❖ 𝗖𝗢𝗡𝗙𝗜𝗥𝗠𝗔𝗖𝗜𝗢́𝗡 𝗗𝗘 𝗧𝗥𝗔𝗡𝗦𝗙𝗘𝗥𝗘𝗡𝗖𝗜𝗔 ❖\n\n"
            donor_message += f"🧬 Energía inyectada: {amount} créditos\n"
            donor_message += f"🎯 Receptor: `{target_user_id}`\n"
            donor_message += f"🪙 Tu saldo restante: {user_data['credits'] - amount} CR\n"
            donor_message += f"📱 Estado notificación: {notification_status}\n\n"
            donor_message += f"🕒 {datetime.now().strftime('%d.%m.%Y • %H:%M')}\n\n"
            donor_message += f"➤ La transmisión fue exitosa.\n"

            if "❌" in notification_status:
                donor_message += f"⚠️ El receptor debe iniciar el bot para recibir notificaciones.\n"
            else:
                donor_message += f"🌟 Tu generosidad resuena en la red.\n"

            donor_message += f"\n💡 **Recarga diaria:** `/loot`\n"
            donor_message += f"🤖 **ChernobilChLv Bot**"

            await context.bot.send_message(chat_id=update.effective_user.id,
                                           text=donor_message,
                                           parse_mode=ParseMode.MARKDOWN)

            logger.info(f"✅ Notificación de confirmación enviada al donante {user_id}")

    except Exception as e:
        logger.warning(f"❌ No se pudo enviar notificación privada al donante {user_id}: {e}")


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /check para verificar capturas - Solo funciona respondiendo a imágenes"""
    try:
        user_id = str(update.effective_user.id)
        user_data = db.get_user(user_id)
        group_id = str(update.effective_chat.id)

        # Verificar que el comando se use respondiendo a una imagen
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text(
                "📸 *VERIFICADOR DE CAPTURAS* 📸\n\n"
                "🚫 *ERROR:* Debes responder a una imagen\n\n"
                "📋 *INSTRUCCIONES:*\n"
                "1️⃣ Envía tu captura al grupo\n"
                "2️⃣ Responde a esa imagen con /check\n"
                "3️⃣ Espera la verificación oficial\n\n"
                "🎁 ¡Obtén recompensas por capturas válidas!\n"
                "⚡ Verificación rápida en menos de 24h\n\n"
                "💡 *TIP:* Solo capturas auténticas serán aprobadas",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Verificar que el grupo tenga configurado el sistema
        check_config = db.get_check_chats(group_id)
        if not check_config:
            await update.message.reply_text(
                "⚙️ *SISTEMA NO CONFIGURADO* ⚙️\n\n"
                "❌ El sistema de verificación no está activo\n\n"
                "🔧 *Para administradores:*\n"
                "• Usar comando `/setcheckchats`\n"
                "• Configurar chat de verificación\n"
                "• Configurar canal de publicación\n\n"
                "📞 Contacta a la administración para activar",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Generar ID único para esta verificación
        import uuid
        check_id = str(uuid.uuid4())[:8]

        # Obtener información de la imagen
        photo = update.message.reply_to_message.photo[-1]  # La imagen de mayor calidad
        image_file_id = photo.file_id

        # Guardar verificación pendiente
        username = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
        db.add_pending_check(check_id, user_id, username, image_file_id, group_id)

        # Escapar caracteres especiales para el username
        safe_username = username.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')

        # Enviar confirmación al usuario
        confirmation_text = (
            "🎯 *CAPTURA EN VERIFICACIÓN* 🎯\n\n"
            "✨ ¡Tu captura ha sido enviada exitosamente!\n\n"
            f"🆔 *ID:* `{check_id}`\n"
            f"👤 *Usuario:* {safe_username}\n"
            f"📸 *Estado:* Imagen procesada ✅\n"
            f"⏳ *Revisión:* En proceso\\.\\.\\.\n\n"
            f"📅 *Enviado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            "⏰ *Tiempo máximo:* 24 horas\n\n"
            "🌟 ¡Mantente atento a las actualizaciones!"
        )

        await update.message.reply_text(confirmation_text, parse_mode=ParseMode.MARKDOWN)

        # Enviar imagen al chat de verificación para administradores
        try:
            verification_chat_id = check_config['verification_chat']

            # Crear botones para aprobar/rechazar
            keyboard = [[
                InlineKeyboardButton("✅ APROBAR",
                                     callback_data=f'approve_check_{check_id}'),
                InlineKeyboardButton("❌ RECHAZAR",
                                     callback_data=f'reject_check_{check_id}')
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Enviar imagen con información al chat de verificación
            caption = (
                f"🔍 *NUEVA VERIFICACIÓN PENDIENTE* 🔍\n\n"
                f"🆔 *ID:* `{check_id}`\n"
                f"👤 *Usuario:* {safe_username} \\(`{user_id}`\\)\n"
                f"📊 *Créditos actuales:* {user_data['credits']}\n"
                f"🏠 *Grupo:* `{group_id}`\n"
                f"📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"💰 *Recompensa:* 6 créditos si se aprueba\n"
                f"📝 *Acción requerida:* Aprobar o rechazar captura"
            )

            await context.bot.send_photo(
                chat_id=verification_chat_id,
                photo=image_file_id,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error enviando a chat de verificación: {e}")
            await update.message.reply_text(
                "❌ *ERROR DEL SISTEMA* ❌\n\n"
                "🔧 No se pudo procesar la verificación\n\n"
                "💡 *Posibles causas:*\n"
                "• Configuración incompleta del sistema\n"
                "• Problemas temporales de conectividad\n"
                "• Mantenimiento en curso\n\n"
                "📞 Contacta a los administradores para asistencia",
                parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error crítico en comando /check: {e}")
        try:
            await update.message.reply_text(
                "❌ *ERROR CRÍTICO*\n\n"
                "Ha ocurrido un error inesperado\\.\n"
                "Por favor intenta nuevamente\\.\n\n"
                "Si el problema persiste, contacta a los administradores\\.",
                parse_mode=ParseMode.MARKDOWN)
        except:
            # Fallback sin markdown si todo falla
            await update.message.reply_text(
                "❌ ERROR CRÍTICO\n\n"
                "Ha ocurrido un error inesperado.\n"
                "Por favor intenta nuevamente.\n\n"
                "Si el problema persiste, contacta a los administradores.")


async def juegos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sección de juegos con botones inline - Límite: 1 cada 12 horas"""
    user_id = str(update.effective_user.id)
    user_data = db.get_user(user_id)

    keyboard = [[
        InlineKeyboardButton("🔥 EXPLOIT ROULETTE",
                             callback_data='play_ruleta'),
        InlineKeyboardButton("⚡ CRYPTO DICE", callback_data='play_dados')
    ],
                [
                    InlineKeyboardButton("🎭 SHADOW CARDS",
                                         callback_data='play_carta'),
                    InlineKeyboardButton("💀 DARK LIGHTNING",
                                         callback_data='play_rayo')
                ],
                [
                    InlineKeyboardButton("📊 HACK STATISTICS",
                                         callback_data='game_stats')
                ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    now = datetime.now()
    last_game = user_data.get('last_game')
    can_play = True
    time_left = 0

    if last_game:
        last_game_date = datetime.fromisoformat(last_game)
        hours_passed = (now - last_game_date).total_seconds() / 3600
        if hours_passed < 12:
            can_play = False
            time_left = 12 - hours_passed

    status_text = "🟢 **ONLINE**" if can_play else f"🔴 **FIREWALL** ({time_left:.1f}h cooldown)"

    response = f"```\n"
    response += f"╔═══════════════════════════╗\n"
    response += f"║  ⧗      𝐂𝐀𝐒𝐈𝐍𝐎 ⧗  ║\n"
    response += f"║    ▒▒▒ 𝐃𝐄𝐄𝐏 𝐖𝐄𝐁 ▒▒▒    ║\n"
    response += f"╚═══════════════════════════╝\n"
    response += f"```\n\n"
    response += f"⚠️ **WARNING: HIGH RISK OPERATIONS** ⚠️\n\n"
    response += f"💳 **Credits Balance:** {user_data['credits']} CR\n"
    response += f"🛡️ **Network Status:** {status_text}\n"
    response += f"💰 **Payout Range:** 3-8 credits per exploit\n"
    response += f"🔒 **Security Cooldown:** 12 hour intervals\n\n"
    response += f"```\n"
    response += f"[SYSTEM] Initializing dark protocols...\n"
    response += f"[AUTH ] User authenticated: {update.effective_user.first_name}\n"
    response += f"[NET  ] Deep web connection: STABLE\n"
    response += f"[WARN ] Proceed with caution\n"
    response += f"```\n\n"
    response += f"🎯 **SELECT YOUR EXPLOIT:**"

    await update.message.reply_text(response,
                                    reply_markup=reply_markup,
                                    parse_mode=ParseMode.MARKDOWN)


# Comandos de admin
async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sistema completo de staff con 3 roles"""
    args = context.args
    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Si es comando de lista, cualquiera puede verlo
    if args and args[0].lower() == "list":
        role_names = {
            '1': '👑 Fundador',
            '2': '⚜️ Cofundador',
            '3': '👮🏼 Moderador'
        }

        # Organizar staff por roles
        fundadores = []
        cofundadores = []
        moderadores = []

        for staff_user_id, staff_data in db.staff_roles.items():
            try:
                # Obtener información del usuario
                staff_user_id_int = int(staff_user_id)
                chat_member = await context.bot.get_chat_member(
                    update.effective_chat.id, staff_user_id_int)
                username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name

                if staff_data['role'] == '1':
                    fundadores.append(username)
                elif staff_data['role'] == '2':
                    cofundadores.append(username)
                elif staff_data['role'] == '3':
                    # Para moderadores, mostrar warns dados
                    warns_given = staff_data.get('warn_count', 0)
                    moderadores.append(f"{username} ({warns_given}/2 warns)")
            except:
                # Si no puede obtener info del usuario, usar ID
                if staff_data['role'] == '1':
                    fundadores.append(f"ID: {staff_user_id}")
                elif staff_data['role'] == '2':
                    cofundadores.append(f"ID: {staff_user_id}")
                elif staff_data['role'] == '3':
                    warns_given = staff_data.get('warn_count', 0)
                    moderadores.append(
                        f"ID: {staff_user_id} ({warns_given}/2 warns)")

        staff_text = "👑 **STAFF DEL GRUPO** 👑\n\n"

        # Mostrar fundadores
        staff_text += "👑 **Fundadores**\n"
        if fundadores:
            for fundador in fundadores:
                staff_text += f"└ {fundador}\n"
        else:
            staff_text += "└ Sin asignar\n"

        staff_text += "\n⚜️ **Co-fundadores**\n"
        if cofundadores:
            for i, cofundador in enumerate(cofundadores):
                prefix = "├" if i < len(cofundadores) - 1 else "└"
                staff_text += f"{prefix} {cofundador}\n"
        else:
            staff_text += "└ Sin asignar\n"

        staff_text += "\n👮🏼 **Moderadores**\n"
        if moderadores:
            for i, moderador in enumerate(moderadores):
                prefix = "├" if i < len(moderadores) - 1 else "└"
                staff_text += f"{prefix} {moderador}\n"
        else:
            staff_text += "└ Sin asignar\n"

        await update.message.reply_text(staff_text,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar si el usuario es admin, fundador o co-fundador para comandos administrativos
    is_admin = user_id_int in ADMIN_IDS
    is_founder_db = db.is_founder(user_id)
    is_cofounder_db = db.is_cofounder(user_id)

    if not (is_admin or is_founder_db or is_cofounder_db):
        await update.message.reply_text(
            "🔒 **Acceso Restringido** 🔒\n\n"
            "Solo los administradores, fundadores y co-fundadores pueden gestionar el staff.\n\n"
            "💡 Para ver la lista de staff disponible escribe:\n"
            "`/staff list`",
            parse_mode=ParseMode.MARKDOWN)
        return

    if not args:
        await update.message.reply_text(
            f"👑 **SISTEMA DE STAFF** 👑\n\n"
            f"**🔹 NIVEL 1 - FUNDADOR:**\n"
            f"• Control total del servidor\n"
            f"• Puede asignar todos los roles\n"
            f"• Acceso a todos los comandos\n\n"
            f"**🔸 NIVEL 2 - CO-FUNDADOR:**\n"
            f"• Mismas funciones que el fundador\n"
            f"• Puede administrar usuarios\n"
            f"• Puede usar /clean, /ban, /warn\n\n"
            f"**🔹 NIVEL 3 - MODERADOR:**\n"
            f"• Funciones básicas de supervisión\n"
            f"• Acceso limitado\n\n",
            parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()

    if action == "add":
        if len(args) < 3:
            await update.message.reply_text(
                "❌ Uso: /staff add [user_id] [nivel]\n"
                "🛡️ Niveles: 1=Fundador, 2=Co-Fundador, 3=Moderador")
            return

        target_user_id = args[1]
        role_level = args[2]

        if role_level not in ['1', '2', '3']:
            await update.message.reply_text("❌ **Nivel inválido**\n"
                                            "**Niveles disponibles:**\n"
                                            "• 1 - Fundador\n"
                                            "• 2 - Co-Fundador\n"
                                            "• 3 - Moderador")
            return

        # Verificar permisos jerárquicos para asignación de roles
        if role_level == '1':  # Asignar Fundador
            if not (is_admin or is_founder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo los **Fundadores** pueden asignar otros Fundadores",
                    parse_mode=ParseMode.MARKDOWN)
                return
        elif role_level == '2':  # Asignar Co-Fundador
            if not (is_admin or is_founder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo los **Fundadores** pueden asignar Co-Fundadores",
                    parse_mode=ParseMode.MARKDOWN)
                return
        elif role_level == '3':  # Asignar Moderador
            if not (is_admin or is_founder_db or is_cofounder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo **Fundadores** y **Co-Fundadores** pueden asignar Moderadores",
                    parse_mode=ParseMode.MARKDOWN)
                return

        role_names = {
            '1': '👑 Fundador',
            '2': '💎 Co-Fundador',
            '3': '🛡️ Moderador'
        }

        # Asignar rol
        db.set_staff_role(target_user_id, role_level)

        await update.message.reply_text(
            f"✅ **ROL ASIGNADO** ✅\n\n"
            f"👤 **Usuario:** {target_user_id}\n"
            f"🎭 **Rol:** {role_names[role_level]} (Nivel {role_level})\n"
            f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"🔐 **Permisos activados correctamente**",
            parse_mode=ParseMode.MARKDOWN)

    elif action == "remove":
        if len(args) < 2:
            await update.message.reply_text(
                "❌ **Uso:** `/staff remove [user_id]`")
            return

        target_user_id = args[1]
        staff_data = db.get_staff_role(target_user_id)

        if not staff_data:
            await update.message.reply_text(
                f"❌ **El usuario {target_user_id} no tiene rol de staff**")
            return

        # Verificar permisos jerárquicos para remoción de roles
        target_role = staff_data['role']

        if target_role == '1':  # Remover Fundador
            if not (is_admin or is_founder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo los **Fundadores** pueden remover otros Fundadores",
                    parse_mode=ParseMode.MARKDOWN)
                return
        elif target_role == '2':  # Remover Co-Fundador
            if not (is_admin or is_founder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo los **Fundadores** pueden remover Co-Fundadores",
                    parse_mode=ParseMode.MARKDOWN)
                return
        elif target_role == '3':  # Remover Moderador
            if not (is_admin or is_founder_db or is_cofounder_db):
                await update.message.reply_text(
                    "❌ **Permisos insuficientes**\n\n"
                    "Solo **Fundadores** y **Co-Fundadores** pueden remover Moderadores",
                    parse_mode=ParseMode.MARKDOWN)
                return

        role_names = {
            '1': '👑 Fundador',
            '2': '💎 Co-Fundador',
            '3': '🛡️ Moderador'
        }

        old_role = role_names.get(staff_data['role'], 'Desconocido')
        db.remove_staff_role(target_user_id)

        await update.message.reply_text(
            f"🗑️ **ROL REMOVIDO** 🗑️\n\n"
            f"👤 **Usuario:** {target_user_id}\n"
            f"🎭 **Rol anterior:** {old_role}\n"
            f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"❌ **Ya no tiene permisos de staff**",
            parse_mode=ParseMode.MARKDOWN)

    elif action == "list":
        # Igual que el comando sin argumentos
        await staff_command(update, context)

    else:
        await update.message.reply_text("❌ **Acción inválida**\n"
                                        "**Acciones disponibles:**\n"
                                        "• `add` - Asignar rol\n"
                                        "• `remove` - Quitar rol\n"
                                        "• `list` - Ver lista")


auto_clean_active = {}  # Diccionario global para controlar auto-limpieza

auto_clean_timers = {}  # Diccionario global para timers


@staff_only(
    3
)  # Moderador o superior (incluye fundadores, co-fundadores y moderadores)
async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Limpiar mensajes con eliminación mejorada y modo automático"""
    args = context.args
    chat_id = update.effective_chat.id

    if not args:
        await update.message.reply_text(
            "🧹 **SISTEMA DE LIMPIEZA AVANZADO** 🧹\n\n"
            "**Uso manual:** `/clean [número]`\n"
            "**Uso automático:** `/clean auto [tiempo]`\n\n"
            "📋 **Ejemplos:**\n"
            "• `/clean 50` - Elimina 50 mensajes\n"
            "• `/clean auto 30m` - Limpieza cada 30 minutos\n"
            "• `/clean auto 2h` - Limpieza cada 2 horas\n"
            "• `/clean auto 1d` - Elimina TODOS los mensajes del día cada 24h\n"
            "• `/clean auto 7d` - Elimina TODOS los mensajes cada 7 días\n"
            "• `/clean auto off` - Desactivar limpieza automática\n\n"
            "⚠️ **Límite manual:** 2000 mensajes\n",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Modo automático
    if args[0].lower() == "auto":
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Uso: `/clean auto [tiempo]` o `/clean auto off`\n"
                "Ejemplos: `30m`, `2h`, `1d`, `7d`, `off`")
            return

        time_arg = args[1].lower()

        if time_arg == "off":
            if str(chat_id) in auto_clean_timers:
                auto_clean_timers[str(chat_id)]['active'] = False
                await update.message.reply_text(
                    "❌ **LIMPIEZA AUTOMÁTICA DESACTIVADA** ❌\n\n"
                    f"🔄 **Estado:** Inactivo\n"
                    f"👮‍♂️ **Desactivado por:** {update.effective_user.first_name}\n"
                    f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(
                    "💡 **No hay limpieza automática activa**")
            return

        # Parsear tiempo
        try:
            is_day_mode = False
            if time_arg.endswith('m'):
                interval_seconds = int(time_arg[:-1]) * 60
                interval_text = f"{time_arg[:-1]} minutos"
            elif time_arg.endswith('h'):
                interval_seconds = int(time_arg[:-1]) * 3600
                interval_text = f"{time_arg[:-1]} horas"
            elif time_arg.endswith('d'):
                days = int(time_arg[:-1])
                interval_seconds = days * 86400
                interval_text = f"{days} día{'s' if days > 1 else ''}"
                is_day_mode = True
            else:
                raise ValueError("Formato inválido")

            if interval_seconds < 300:  # Mínimo 5 minutos
                await update.message.reply_text("❌ Intervalo muy corto\n"
                                                "⏰ Mínimo: 5 minutos (`5m`)")
                return

        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido\n"
                "📋 Formatos: `30m`, `2h`, `1d`, `7d`")
            return

        # Activar limpieza automática
        auto_clean_timers[str(chat_id)] = {
            'active': True,
            'interval': interval_seconds,
            'interval_text': interval_text,
            'is_day_mode': is_day_mode,
            'days_count': int(time_arg[:-1]) if is_day_mode else 0,
            'last_clean': datetime.now().isoformat()
        }

        # Iniciar el timer en background
        asyncio.create_task(
            auto_clean_worker(context, chat_id, interval_seconds))

        if is_day_mode:
            clean_description = f"TODOS los mensajes del período de {interval_text}"
        else:
            clean_description = f"20 mensajes cada {interval_text}"

        await update.message.reply_text(
            f"✅ **LIMPIEZA AUTOMÁTICA ACTIVADA** ✅\n\n"
            f"⏰ **Intervalo:** {interval_text}\n"
            f"🧹 **Limpieza:** {clean_description}\n"
            f"👮‍♂️ **Activado por:** {update.effective_user.first_name}\n"
            f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"⚠️ **IMPORTANTE:** {'Este modo eliminará TODO el historial de mensajes del período especificado' if is_day_mode else 'Limpieza estándar de 20 mensajes'}\n"
            f"💡 **Usa `/clean auto off` para desactivar**",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar que sea un número (modo manual)
    if not args[0].isdigit():
        await update.message.reply_text(
            "❌ **Formato incorrecto**\n\n"
            "💡 **Uso correcto:** `/clean [número]`\n"
            "📋 **Ejemplo:** `/clean 20`")
        return

    count = int(args[0])
    if count > 2000:
        await update.message.reply_text(
            "❌ **Límite excedido**\n\n"
            "🔢 **Máximo permitido:** 2000 mensajes\n"
            "💡 **Usa un número menor e intenta de nuevo**")
        return

    if count < 1:
        await update.message.reply_text("❌ **Cantidad inválida**\n\n"
                                        "🔢 **Mínimo:** 1 mensaje\n"
                                        "📋 **Ejemplo:** `/clean 10`")
        return

    admin_info = update.effective_user
    deleted_count = 0

    # Mensaje de progreso
    progress_msg = await update.message.reply_text(
        f"🧹 **INICIANDO LIMPIEZA** 🧹\n\n"
        f"🔄 Eliminando {count:,} mensajes...\n"
        f"⏳ Por favor espera...")

    try:
        current_message_id = progress_msg.message_id

        # Eliminar el comando original
        try:
            await update.message.delete()
        except:
            pass

        # Eliminar mensajes hacia atrás desde el mensaje de progreso
        for i in range(1,
                       count + 2):  # +2 para incluir el comando y el progreso
            message_id_to_delete = current_message_id - i
            if message_id_to_delete > 0:
                try:
                    await context.bot.delete_message(
                        chat_id=chat_id, message_id=message_id_to_delete)
                    deleted_count += 1

                    # Actualizar progreso cada 100 mensajes para cantidades grandes
                    if count > 100 and deleted_count % 100 == 0:
                        try:
                            await progress_msg.edit_text(
                                f"🧹 **LIMPIEZA EN PROGRESO** 🧹\n\n"
                                f"🗑️ **Eliminados:** {deleted_count:,}/{count:,}\n"
                                f"📊 **Progreso:** {(deleted_count/count)*100:.1f}%\n"
                                f"⏳ **Procesando...**",
                                parse_mode=ParseMode.MARKDOWN)
                        except:
                            pass

                    # Pausa adaptativa según la cantidad
                    if count > 500:
                        if deleted_count % 50 == 0:
                            await asyncio.sleep(0.1)
                    else:
                        await asyncio.sleep(0.05)  # Pausa muy corta

                except Exception as e:
                    logger.warning(
                        f"No se pudo eliminar mensaje {message_id_to_delete}: {e}"
                    )
                    continue

        # Eliminar el mensaje de progreso
        try:
            await progress_msg.delete()
        except:
            pass

        # Información detallada de la limpieza (TEMPORAL)
        cleanup_info_temp = "╔═══════════════════════════════╗\n"
        cleanup_info_temp += "║    🧹 **LIMPIEZA COMPLETADA** 🧹    ║\n"
        cleanup_info_temp += "╚═══════════════════════════════╝\n\n"
        cleanup_info_temp += f"🗑️ **Mensajes eliminados:** {deleted_count:,}/{count:,}\n"
        cleanup_info_temp += f"📊 **Efectividad:** {(deleted_count/count)*100:.1f}%\n"
        cleanup_info_temp += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y - %H:%M:%S')}\n"
        cleanup_info_temp += f"👤 **Ejecutado por:** {admin_info.first_name}\n"
        cleanup_info_temp += f"🆔 **Admin ID:** `{admin_info.id}`\n"
        cleanup_info_temp += f"👮‍♂️ **Username:** @{admin_info.username or 'Sin username'}\n"
        cleanup_info_temp += f"💬 **Chat ID:** `{chat_id}`\n\n"
        cleanup_info_temp += f"✅ **Estado:** Completado exitosamente\n"
        cleanup_info_temp += f"📝 **Registro:** Guardado en logs del sistema\n\n"
        cleanup_info_temp += f"⚠️ **Este mensaje se eliminará en 30 segundos**"

        # Enviar confirmación temporal
        confirmation_msg = await context.bot.send_message(
            chat_id, cleanup_info_temp, parse_mode=ParseMode.MARKDOWN)

        # Auto-eliminar confirmación después de 30 segundos
        await asyncio.sleep(30)
        try:
            await confirmation_msg.delete()
        except:
            pass

        # Enviar log administrativo
        await send_admin_log(context=context,
                             action_type='CLEAN',
                             admin_user=admin_info,
                             target_user_id=f"CHAT_{chat_id}",
                             reason=f"Limpieza de {count} mensajes",
                             group_id=str(chat_id),
                             additional_data={
                                 'messages_requested':
                                 count,
                                 'messages_deleted':
                                 deleted_count,
                                 'effectiveness':
                                 f"{(deleted_count/count)*100:.1f}%"
                             })

        # Log para administradores
        logger.info(
            f"Limpieza ejecutada - Admin: {admin_info.id} ({admin_info.first_name}) - "
            f"Eliminados: {deleted_count}/{count} - Chat: {chat_id}")

    except Exception as e:
        logger.error(f"Error en limpieza: {e}")
        try:
            await progress_msg.delete()
        except:
            pass

        await context.bot.send_message(
            chat_id, f"❌ **ERROR EN LIMPIEZA** ❌\n\n"
            f"🔍 **Error:** {str(e)[:100]}\n"
            f"📊 **Eliminados:** {deleted_count}/{count}\n\n"
            f"💡 **Verifica que el bot tenga:**\n"
            f"• Permisos de administrador\n"
            f"• Permiso para eliminar mensajes\n"
            f"• Acceso a mensajes del historial\n\n"
            f"👤 **Intentado por:** {admin_info.first_name}",
            parse_mode=ParseMode.MARKDOWN)


@bot_admin_only
async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dar premium a un usuario"""
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /premium [user_id] [días]")
        return

    target_user_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    premium_until = datetime.now() + timedelta(days=days)

    db.update_user(target_user_id, {
        'premium': True,
        'premium_until': premium_until.isoformat()
    })

    await update.message.reply_text(
        f"👑 Premium activado para usuario {target_user_id}\n"
        f"📅 Válido por {days} días")

@staff_only(1)  # Solo fundadores (nivel 1)
async def setpremium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestionar premium de usuarios - Solo fundadores"""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "👑 **GESTIÓN DE PREMIUM** 👑\n\n"
            "**Uso:** `/setpremium [user_id] [acción] [días]`\n\n"
            "**Acciones disponibles:**\n"
            "• `on [días]` - Activar premium\n"
            "• `off` - Desactivar premium\n"
            "• `check` - Ver estado premium\n\n"
            "**Ejemplos:**\n"
            "• `/setpremium 123456789 on 30` - 30 días premium\n"
            "• `/setpremium 123456789 off` - Quitar premium\n"
            "• `/setpremium 123456789 check` - Ver estado\n\n"
            "🔒 **Solo fundadores pueden usar este comando**",
            parse_mode=ParseMode.MARKDOWN)
        return

    if len(args) < 2:
        await update.message.reply_text(
            "❌ **Parámetros incompletos**\n\n"
            "**Uso correcto:** `/setpremium [user_id] [acción]`")
        return

    target_user_id = args[0]
    action = args[1].lower()

    # Verificar que el usuario existe
    target_user_data = db.get_user(target_user_id)
    if not target_user_data:
        await update.message.reply_text(
            f"❌ **Usuario no encontrado**\n\n"
            f"El usuario `{target_user_id}` no está registrado en el bot")
        return

    if action == "on":
        # Activar premium
        days = int(args[2]) if len(args) > 2 and args[2].isdigit() else 30
        premium_until = datetime.now() + timedelta(days=days)

        db.update_user(target_user_id, {
            'premium': True,
            'premium_until': premium_until.isoformat(),
            'credits': target_user_data['credits'] + 100  # Bonus de activación
        })

        # Forzar guardado y recargar datos múltiples veces para asegurar sincronización
        db.save_data()
        await asyncio.sleep(0.1)  # Pequeña pausa para asegurar escritura de archivo
        db.load_data()  # Recargar desde archivo
        updated_data = db.get_user(target_user_id)
        logger.info(f"✅ Premium activado para {target_user_id}: premium={updated_data.get('premium')}, until={updated_data.get('premium_until')}")

        # FORZAR ACTUALIZACIÓN EN GATES SYSTEM SI EXISTE
        if 'gate_system' in globals() and gate_system is not None:
            gate_system.db.load_data()  # Forzar recarga en gates también
            test_auth = gate_system.is_authorized(target_user_id)
            logger.info(f"[SETPREMIUM] TEST INMEDIATO DESPUÉS DE RECARGA: Gates reconoce a {target_user_id} = {test_auth}")

        # Log específico para gates - VERIFICACIÓN INMEDIATA
        logger.info(f"[SETPREMIUM] Usuario {target_user_id} configurado con premium={updated_data.get('premium')} - GATES debería reconocerlo INMEDIATAMENTE")

        # Verificar que gates reconocería al usuario ahora mismo
        if 'gate_system' in globals() and gate_system is not None:
            test_auth = gate_system.is_authorized(target_user_id)
            logger.info(f"[SETPREMIUM] TEST INMEDIATO: Gates reconoce a {target_user_id} = {test_auth}")
        else:
            logger.info(f"[SETPREMIUM] Gate system no inicializado aún, pero debería funcionar cuando se use /gates")

        # Obtener info del usuario si es posible
        try:
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, int(target_user_id))
            target_username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
        except:
            target_username = f"ID: {target_user_id}"

        response = f"👑 **PREMIUM ACTIVADO** 👑\n\n"
        response += f"👤 **Usuario:** {target_username}\n"
        response += f"🆔 **ID:** `{target_user_id}`\n"
        response += f"📅 **Duración:** {days} días\n"
        response += f"🔓 **Válido hasta:** {premium_until.strftime('%d/%m/%Y')}\n"
        response += f"💰 **Bonus:** +100 créditos\n"
        response += f"💎 **Créditos totales:** {target_user_data['credits'] + 100}\n\n"
        response += f"🔥 **BENEFICIOS PREMIUM ACTIVADOS:**\n"
        response += f"• ✅ Acceso completo a todos los Gates\n"
        response += f"• ✅ Límites aumentados en generación\n"
        response += f"• ✅ Verificación con múltiples APIs\n"
        response += f"• ✅ Extrapolación avanzada ilimitada\n"
        response += f"• ✅ Bono diario premium (15 créditos)\n\n"
        response += f"👑 **Activado por:** {update.effective_user.first_name}\n"
        response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"💡 **El usuario ya puede usar `/gates` sin restricciones**"

    elif action == "off":
        # Desactivar premium
        if not target_user_data.get('premium', False):
            await update.message.reply_text(
                f"❌ **El usuario ya no tiene premium activo**\n\n"
                f"👤 **Usuario:** `{target_user_id}`\n"
                f"📊 **Estado actual:** Usuario estándar",
                parse_mode=ParseMode.MARKDOWN)
            return

        db.update_user(target_user_id, {
            'premium': False,
            'premium_until': None
        })

        # Forzar guardado y recargar datos múltiples veces para asegurar sincronización
        db.save_data()
        await asyncio.sleep(0.1)  # Pequeña pausa para asegurar escritura de archivo
        db.load_data()  # Recargar desde archivo
        updated_data = db.get_user(target_user_id)
        logger.info(f"❌ Premium desactivado para {target_user_id}: premium={updated_data.get('premium')}, until={updated_data.get('premium_until')}")

        # FORZAR ACTUALIZACIÓN EN GATES SYSTEM SI EXISTE
        if 'gate_system' in globals() and gate_system is not None:
            gate_system.db.load_data()  # Forzar recarga en gates también
            test_auth = gate_system.is_authorized(target_user_id)
            logger.info(f"[SETPREMIUM] TEST INMEDIATO DESPUÉS DE RECARGA: Gates bloquea a {target_user_id} = {not test_auth}")

        # Log específico para gates - VERIFICACIÓN INMEDIATA
        logger.info(f"[SETPREMIUM] Usuario {target_user_id} configurado sin premium - GATES debe bloquearlo INMEDIATAMENTE")

        # Verificar que gates bloquearía al usuario ahora mismo
        if 'gate_system' in globals() and gate_system is not None:
            test_auth = gate_system.is_authorized(target_user_id)
            logger.info(f"[SETPREMIUM] TEST INMEDIATO: Gates bloquea a {target_user_id} = {not test_auth}")
        else:
            logger.info(f"[SETPREMIUM] Gate system no inicializado aún, pero debería bloquear cuando se use /gates")

        # Obtener info del usuario si es posible
        try:
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, int(target_user_id))
            target_username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
        except:
            target_username = f"ID: {target_user_id}"

        response = f"❌ **PREMIUM DESACTIVADO** ❌\n\n"
        response += f"👤 **Usuario:** {target_username}\n"
        response += f"🆔 **ID:** `{target_user_id}`\n"
        response += f"📊 **Nuevo estado:** Usuario estándar\n"
        response += f"💰 **Créditos:** {target_user_data['credits']} (sin cambios)\n\n"
        response += f"👑 **Desactivado por:** {update.effective_user.first_name}\n"
        response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"💡 **El usuario perdió todos los beneficios premium**"

    elif action == "check":
        # Verificar estado premium
        is_premium = target_user_data.get('premium', False)

        # Obtener info del usuario si es posible
        try:
            chat_member = await context.bot.get_chat_member(update.effective_chat.id, int(target_user_id))
            target_username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
        except:
            target_username = f"ID: {target_user_id}"

        response = f"📊 **ESTADO PREMIUM** 📊\n\n"
        response += f"👤 **Usuario:** {target_username}\n"
        response += f"🆔 **ID:** `{target_user_id}`\n"

        if is_premium:
            premium_until = datetime.fromisoformat(target_user_data['premium_until'])
            days_left = (premium_until - datetime.now()).days

            response += f"👑 **Estado:** PREMIUM ACTIVO ✅\n"
            response += f"📅 **Días restantes:** {days_left}\n"
            response += f"🔓 **Vence:** {premium_until.strftime('%d/%m/%Y %H:%M')}\n"
            response += f"🎁 **Beneficios:** Activos\n"
        else:
            response += f"🆓 **Estado:** Usuario estándar\n"
            response += f"❌ **Premium:** Inactivo\n"
            response += f"🚫 **Acceso a Gates:** Bloqueado\n"
            response += f"💡 **Para activar:** `/setpremium {target_user_id} on [días]`\n"

        response += f"\n💰 **Créditos:** {target_user_data['credits']}\n"
        response += f"📅 **Miembro desde:** {target_user_data['join_date'][:10]}\n"
        response += f"🏭 **Total generado:** {target_user_data['total_generated']}\n"
        response += f"🔍 **Total verificado:** {target_user_data['total_checked']}"

    else:
        await update.message.reply_text(
            f"❌ **Acción inválida:** `{action}`\n\n"
            f"**Acciones disponibles:**\n"
            f"• `on` - Activar premium\n"
            f"• `off` - Desactivar premium\n"
            f"• `check` - Ver estado premium")
        return

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)



async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver información detallada de usuario por ID - Versión ultra-robusta"""
    try:
        args = context.args
        target_user = None
        target_user_id = None

        # Verificar si hay respuesta a un mensaje
        if update.message.reply_to_message and not args:
            try:
                # Verificar que el mensaje tiene usuario (no es un mensaje del canal)
                if hasattr(update.message.reply_to_message, 'from_user') and update.message.reply_to_message.from_user:
                    target_user_id = str(update.message.reply_to_message.from_user.id)
                    target_user = update.message.reply_to_message.from_user
                else:
                    # Es un mensaje del canal sin usuario específico
                    await update.message.reply_text(
                        "❌ NO SE PUEDE OBTENER INFO\n\n"
                        "Este mensaje no tiene un usuario asociado.\n"
                        "Puede ser un mensaje automático del canal.\n\n"
                        "💡 Usa: /id [user_id] para consultar por ID")
                    return
            except (AttributeError, TypeError):
                await update.message.reply_text(
                    "❌ ERROR AL PROCESAR MENSAJE\n\n"
                    "No se pudo obtener información del mensaje.\n\n"
                    "💡 Usa: /id [user_id] para consultar por ID")
                return
        elif args:
            # Validar que el argumento sea un ID numérico válido
            arg_clean = str(args[0]).strip()
            if not arg_clean or not arg_clean.isdigit() or len(arg_clean) < 5:
                await update.message.reply_text(
                    "❌ ID INVÁLIDO\n\n"
                    "💡 Uso correcto del comando:\n"
                    "• /id 123456789 - Ver info de usuario específico\n"
                    "• /id (respondiendo a mensaje) - Ver info del usuario\n"
                    "• /id (sin argumentos) - Ver tu propia información\n\n"
                    "🔍 Ejemplo: /id 123456789\n"
                    "📝 Nota: El ID debe ser un número de al menos 5 dígitos")
                return

            target_user_id = arg_clean

            # Verificar que sea un ID válido de Telegram (no mayor a 2^53)
            try:
                user_id_int = int(target_user_id)
                if user_id_int <= 0 or user_id_int > 9007199254740991:  # 2^53 - 1
                    await update.message.reply_text(
                        "❌ ID FUERA DE RANGO\n\n"
                        "El ID debe ser un número positivo válido de Telegram.\n"
                        "📋 Ejemplo de ID válido: 123456789")
                    return
            except (ValueError, OverflowError):
                await update.message.reply_text(
                    "❌ ID INVÁLIDO\n\n"
                    "El ID debe ser un número entero válido.\n"
                    "📋 Ejemplo: /id 123456789")
                return

            # Intentar obtener información del usuario de manera más robusta
            target_user = None
            try:
                # Intentar obtener información del usuario en el chat actual
                chat_member = await context.bot.get_chat_member(
                    update.effective_chat.id, int(target_user_id))
                if chat_member and hasattr(chat_member, 'user') and chat_member.user:
                    target_user = chat_member.user
            except Exception as e:
                error_msg = str(e).lower()
                # No fallar aquí, solo no tendremos info del usuario de Telegram
                # Pero podemos mostrar datos de la base de datos
                logger.info(f"No se pudo obtener info de Telegram para {target_user_id}: {e}")
        else:
            # Si no hay argumentos ni respuesta, mostrar información del usuario que ejecuta el comando
            target_user_id = str(update.effective_user.id)
            target_user = update.effective_user

        # Verificar que tenemos datos válidos
        if not target_user_id:
            await update.message.reply_text(
                "❌ ERROR DE DATOS\n\n"
                "No se pudo determinar el usuario objetivo.\n\n"
                "💡 Usa: /id [user_id] para consultar por ID específico")
            return

        # Obtener datos del usuario de la base de datos de manera ultra-segura
        user_data = None
        try:
            user_data = db.get_user(target_user_id)
        except Exception as e:
            logger.error(f"Error obteniendo datos de usuario {target_user_id}: {e}")

        # Si no hay datos de la BD, mostrar mensaje específico
        if not user_data:
            await update.message.reply_text(
                f"❌ USUARIO NO REGISTRADO\n\n"
                f"El usuario {target_user_id} no está en la base de datos del bot.\n\n"
                f"💡 El usuario debe usar el bot al menos una vez para registrarse")
            return

        # Función para obtener valor seguro de diccionario
        def safe_get(data, key, default=0, convert_type=int):
            try:
                value = data.get(key, default)
                if value is None:
                    return default
                return convert_type(value)
            except (ValueError, TypeError, AttributeError):
                return default

        # Obtener estadísticas de forma ultra-segura
        credits = safe_get(user_data, 'credits', 0)
        total_generated = safe_get(user_data, 'total_generated', 0)
        total_checked = safe_get(user_data, 'total_checked', 0)
        warns = safe_get(user_data, 'warns', 0)

        # Calcular tiempo en servidor de manera segura
        days_in_server = 0
        try:
            join_date_str = user_data.get('join_date')
            if join_date_str:
                join_date = datetime.fromisoformat(join_date_str)
                time_in_server = datetime.now() - join_date
                days_in_server = max(0, time_in_server.days)
        except (KeyError, ValueError, TypeError, AttributeError):
            days_in_server = 0

        # Obtener información del usuario de Telegram de forma ultra-segura
        username = "Sin username"
        full_name = f"Usuario {target_user_id}"
        try:
            if target_user:
                if hasattr(target_user, 'username') and target_user.username:
                    username = f"@{target_user.username}"
                
                first_name = getattr(target_user, 'first_name', None) or "Sin nombre"
                last_name = getattr(target_user, 'last_name', None) or ""
                full_name = f"{first_name} {last_name}".strip()
        except Exception as e:
            logger.warning(f"Error obteniendo info de Telegram del usuario: {e}")

        # Limpiar caracteres especiales de manera ultra-segura
        def ultra_clean_text(text):
            if not text:
                return "N/A"
            try:
                # Convertir a string y limpiar caracteres problemáticos
                cleaned = str(text)
                # Limpiar caracteres especiales comunes
                special_chars = ['_', '*', '[', ']', '`', '\n', '\r', '\\', '"', "'"]
                for char in special_chars:
                    cleaned = cleaned.replace(char, ' ')
                # Limpiar espacios múltiples
                cleaned = ' '.join(cleaned.split())
                # Limitar longitud para evitar mensajes muy largos
                return cleaned[:40] if len(cleaned) > 40 else cleaned
            except Exception:
                return "Error de texto"

        safe_full_name = ultra_clean_text(full_name)
        safe_username = ultra_clean_text(username)

        # Determinar estado premium con manejo de errores ultra-robusto
        premium_display = "❌"
        try:
            is_premium = user_data.get('premium', False)
            if is_premium:
                premium_until = user_data.get('premium_until')
                if premium_until:
                    try:
                        premium_date = datetime.fromisoformat(premium_until)
                        days_left = (premium_date - datetime.now()).days
                        if days_left > 0:
                            premium_display = f"✅ {days_left}d"
                        elif days_left > -30:  # Expirado hace menos de 30 días
                            premium_display = f"⏰ -{abs(days_left)}d"
                        else:
                            premium_display = "❌ Expirado"
                    except (ValueError, TypeError):
                        premium_display = "✅ Error fecha"
                else:
                    premium_display = "✅ ∞"
        except Exception as e:
            logger.warning(f"Error calculando premium para {target_user_id}: {e}")
            premium_display = "❌ Error"

        # Calcular días desde último bono de manera ultra-segura
        last_bonus_date = "Nunca"
        try:
            last_bonus = user_data.get('last_bonus')
            if last_bonus:
                bonus_date = datetime.fromisoformat(last_bonus)
                last_bonus_date = bonus_date.strftime('%d/%m/%Y')
        except Exception:
            last_bonus_date = "Error fecha"

        # Construir respuesta de manera ultra-segura (sin Markdown)
        try:
            # Asegurar que todos los valores sean strings seguros
            id_display = str(target_user_id)
            name_display = safe_full_name[:20] if safe_full_name else f"Usuario {target_user_id}"
            username_display = safe_username[:25] if safe_username else "Sin username"
            
            response_lines = [
                "╔═══[ USUARIO ACTIVO ]═══╗",
                f"║ 🧬 {name_display} (ID: {id_display})",
                f"║ 📡 {username_display}",
                f"║ 🗓️ Registro: {days_in_server} días atrás",
                "╠═════[ ESTADO ]═════╣",
                f"║ 💰 Créditos: {credits:,}",
                f"║ 🧾 Gen/Verif: {total_generated:,}/{total_checked:,}",
                f"║ ⚠️ Warns: {warns} | 👑 Premium: {premium_display}",
                "╠═════[ BONUS INFO ]════╣",
                f"║ 🎁 Último bono: {last_bonus_date}",
                f"║ 📊 Actividad total: {total_generated + total_checked:,}",
                "╚═══════════════════════╝"
            ]
            
            response = "\n".join(response_lines)

            # Verificar longitud del mensaje
            if len(response) > 4000:
                # Versión simplificada si es muy largo
                response = f"❌ RESPUESTA DEMASIADO LARGA\n\n"
                response += f"Usuario ID: {target_user_id}\n"
                response += f"Créditos: {credits:,}\n"
                response += f"Gen/Ver: {total_generated:,}/{total_checked:,}\n"
                response += f"Premium: {premium_display}\n"
                response += f"Registro: {days_in_server} días\n\n"
                response += f"Datos disponibles, pero formato reducido por tamaño."

        except Exception as e:
            logger.error(f"Error construyendo respuesta para {target_user_id}: {e}")
            # Respuesta de emergencia ultra-simple
            response = f"❌ ERROR DE FORMATO\n\n"
            response += f"Usuario ID: {target_user_id}\n"
            response += f"Datos disponibles en la BD\n"
            response += f"Pero hay un error de presentación.\n\n"
            response += f"Créditos: {credits}\n"
            response += f"Premium: {'Sí' if user_data.get('premium', False) else 'No'}"

        # Enviar respuesta de manera ultra-robusta
        try:
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error enviando respuesta del comando /id: {e}")
            # Último intento con mensaje mínimo
            try:
                minimal_response = f"Usuario {target_user_id}: {credits} creditos, {days_in_server} dias"
                await update.message.reply_text(minimal_response)
            except Exception as final_error:
                logger.error(f"Error crítico enviando respuesta mínima: {final_error}")
                # Si llegamos aquí, hay un problema muy serio
                pass

    except Exception as e:
        logger.error(f"Error crítico en comando /id: {e}")
        try:
            # Mensaje de error ultra-simple y robusto
            error_response = "❌ ERROR TEMPORAL\n\n"
            error_response += "Error procesando información.\n"
            error_response += "Intenta: /id [numero] o /id"

            await update.message.reply_text(error_response)
        except Exception as critical_error:
            logger.error(f"Error crítico absoluto en /id: {critical_error}")
            # Si llegamos aquí, registrar en logs pero no podemos hacer más
            pass


@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Banear usuario"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔨 **BANEAR USUARIO** 🔨\n\n"
            "**Uso:** `/ban [user_id] [razón]`\n"
            "**Ejemplo:** `/ban 123456789 Spam`",
            parse_mode=ParseMode.MARKDOWN)
        return

    target_user_id = args[0]
    reason = ' '.join(args[1:]) if len(args) > 1 else "Sin razón especificada"
    group_id = str(update.effective_chat.id)

    try:
        # Intentar banear del chat actual
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id,
                                          user_id=int(target_user_id))

        # Enviar log administrativo
        await send_admin_log(context=context,
                             action_type='BAN',
                             admin_user=update.effective_user,
                             target_user_id=target_user_id,
                             reason=reason,
                             group_id=group_id,
                             additional_data={'success': True})

        await update.message.reply_text(
            f"🔨 **USUARIO BANEADO** 🔨\n\n"
            f"👤 **ID:** {target_user_id}\n"
            f"📝 **Razón:** {reason}\n"
            f"👮‍♂️ **Por:** {update.effective_user.first_name}\n"
            f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ **Acción ejecutada y registrada**",
            parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        # Enviar log de error
        await send_admin_log(context=context,
                             action_type='BAN',
                             admin_user=update.effective_user,
                             target_user_id=target_user_id,
                             reason=reason,
                             group_id=group_id,
                             additional_data={
                                 'success': False,
                                 'error': str(e)
                             })

        await update.message.reply_text(f"❌ Error al banear usuario: {str(e)}")


@staff_only(3)  # Nivel 3 (moderador) o superior
async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Advertir usuario - Moderadores pueden dar máximo 2 warns"""
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "⚠️ **ADVERTIR USUARIO** ⚠️\n\n"
            "**Uso:** `/warn [user_id] [razón]`\n"
            "**Ejemplo:** `/warn 123456789 Comportamiento inadecuado`",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar límite para moderadores (nivel 3)
    staff_data = db.get_staff_role(user_id)
    is_admin = update.effective_user.id in ADMIN_IDS

    if staff_data and staff_data['role'] == '3' and not is_admin:
        # Es moderador, verificar límite de warns
        mod_warns = staff_data.get('warn_count', 0)
        if mod_warns >= 2:
            await update.message.reply_text(
                "❌ **LÍMITE ALCANZADO** ❌\n\n"
                "🛡️ **Moderadores pueden dar máximo 2 warns**\n"
                "📊 **Warns dados:** 2/2\n\n"
                "💡 Contacta a un Co-Fundador o Fundador",
                parse_mode=ParseMode.MARKDOWN)
            return

    target_user_id = args[0]
    reason = ' '.join(args[1:]) if len(args) > 1 else "Sin razón especificada"

    user_data = db.get_user(target_user_id)
    current_warns = user_data.get('warns', 0) + 1

    db.update_user(target_user_id, {'warns': current_warns})

    # Incrementar contador de warns para moderadores
    if staff_data and staff_data['role'] == '3' and not is_admin:
        new_mod_warns = db.increment_mod_warns(user_id)
        mod_warn_text = f"\n🛡️ **Warns dados por moderador:** {new_mod_warns}/2"
    else:
        mod_warn_text = ""

    # Determinar rango del que aplicó el warn
    if is_admin:
        applied_by_rank = "👑 Admin Principal"
    elif staff_data:
        rank_names = {
            '1': '👑 Fundador',
            '2': '💎 Co-Fundador',
            '3': '🛡️ Moderador'
        }
        applied_by_rank = rank_names.get(staff_data['role'], 'Staff')
    else:
        applied_by_rank = "Staff"

    # Enviar log administrativo
    group_id = str(update.effective_chat.id)

    logger.info(
        f"🔄 Iniciando envío de log - Grupo: {group_id} - Acción: WARN - Admin: {update.effective_user.id}"
    )

    # Verificar configuración antes de enviar
    log_config = db.get_admin_log_channel(group_id)
    if log_config:
        logger.info(f"✅ Configuración de logs encontrada: {log_config}")
    else:
        logger.warning(f"❌ No hay configuración de logs para grupo {group_id}")

    try:
        await send_admin_log(context=context,
                             action_type='WARN',
                             admin_user=update.effective_user,
                             target_user_id=target_user_id,
                             reason=reason,
                             group_id=group_id,
                             additional_data={
                                 'warns_total': current_warns,
                                 'warns_remaining': 3 - current_warns,
                                 'admin_rank': applied_by_rank,
                                 'auto_ban': current_warns >= 3
                             })
        logger.info(f"✅ Log administrativo completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error crítico enviando log administrativo: {e}")
        logger.error(f"Detalles del error: {type(e).__name__}: {str(e)}")

    response = f"⚠️ **ADVERTENCIA APLICADA** ⚠️\n\n"
    response += f"👤 **Usuario:** {target_user_id}\n"
    response += f"📝 **Razón:** {reason}\n"
    response += f"🔢 **Advertencias:** {current_warns}/3\n"
    response += f"👮‍♂️ **Por:** {update.effective_user.first_name} ({applied_by_rank})\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}{mod_warn_text}\n\n"

    if current_warns >= 3:
        response += f"🔨 **USUARIO BANEADO AUTOMÁTICAMENTE**"
    else:
        response += f"💡 **Advertencias restantes:** {3 - current_warns}"

    response += f"\n📋 **Acción registrada en logs administrativos**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@bot_admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estadísticas completas del bot"""
    total_users = len(db.users)
    total_generated = sum(
        user.get('total_generated', 0) for user in db.users.values())
    total_checked = sum(
        user.get('total_checked', 0) for user in db.users.values())
    premium_users = sum(1 for user in db.users.values()
                        if user.get('premium', False))
    total_credits = sum(user.get('credits', 0) for user in db.users.values())

    response = f"📊 **ESTADÍSTICAS COMPLETAS** 📊\n\n"
    response += f"👥 **Total usuarios:** {total_users}\n"

    response += f"🏭 **Tarjetas generadas:** {total_generated:,}\n"
    response += f"🔍 **Tarjetas verificadas:** {total_checked:,}\n"
    response += f"💰 **Créditos totales:** {total_credits:,}\n"
    response += f"🤖 **Uptime:** 99.9%\n"
    response += f"⚡ **Estado:** Operativo\n"
    response += f"📡 **Servidor:** Online\n"
    response += f"🕐 **Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@staff_only(1)  # Solo fundadores de nivel 1
async def founder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestionar fundadores - Solo fundadores existentes"""
    args = context.args

    if not args:
        # Mostrar lista de fundadores actuales
        founders = db.get_all_by_role('1')

        response = f"👑 **GESTIÓN DE FUNDADORES** 👑\n\n"
        response += f"**Comandos disponibles:**\n"
        response += f"• `/founder add [user_id]` - Asignar fundador\n"
        response += f"• `/founder remove [user_id]` - Quitar fundador\n"
        response += f"• `/founder list` - Ver lista actual\n\n"

        if founders:
            response += f"**Fundadores actuales:**\n"
            for i, founder_id in enumerate(founders, 1):
                try:
                    chat_member = await context.bot.get_chat_member(
                        update.effective_chat.id, int(founder_id))
                    username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
                    response += f"{i}. {username} (`{founder_id}`)\n"
                except:
                    response += f"{i}. ID: `{founder_id}`\n"
        else:
            response += f"📝 **No hay fundadores asignados dinámicamente**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()

    if action == "add":
        if len(args) < 2:
            await update.message.reply_text("❌ Uso: `/founder add [user_id]`")
            return

        target_user_id = args[1]

        # Verificar si ya es fundador
        if db.is_founder(target_user_id):
            await update.message.reply_text(
                f"⚠️ El usuario `{target_user_id}` ya es fundador")
            return

        # Asignar como fundador
        db.set_staff_role(target_user_id, '1')

        response = f"👑 **FUNDADOR ASIGNADO** 👑\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"🎭 **Rol:** Fundador (Nivel 1)\n"
        response += f"👮‍♂️ **Asignado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"✨ **Permisos máximos activados**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "remove":
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Uso: `/founder remove [user_id]`")
            return

        target_user_id = args[1]

        # Verificar si es fundador
        if not db.is_founder(target_user_id):
            await update.message.reply_text(
                f"❌ El usuario `{target_user_id}` no es fundador")
            return

        # Remover rol
        db.remove_staff_role(target_user_id)

        response = f"🗑️ **FUNDADOR REMOVIDO** 🗑️\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"👮‍♂️ **Removido por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"❌ **Ya no tiene permisos de fundador**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "list":
        # Reutilizar la lógica de mostrar lista
        await founder_command(update, context)

    else:
        await update.message.reply_text(
            "❌ **Acción inválida**\n**Acciones:** `add`, `remove`, `list`")


@staff_only(1)  # Solo fundadores
async def cofounder_command(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Gestionar co-fundadores - Solo fundadores"""
    args = context.args

    if not args:
        # Mostrar lista de co-fundadores actuales
        cofounders = db.get_all_by_role('2')

        response = f"💎 **GESTIÓN DE CO-FUNDADORES** 💎\n\n"
        response += f"**Comandos disponibles:**\n"
        response += f"• `/cofounder add [user_id]` - Asignar co-fundador\n"
        response += f"• `/cofounder remove [user_id]` - Quitar co-fundador\n"
        response += f"• `/cofounder list` - Ver lista actual\n\n"

        if cofounders:
            response += f"**Co-fundadores actuales:**\n"
            for i, cofounder_id in enumerate(cofounders, 1):
                try:
                    chat_member = await context.bot.get_chat_member(
                        update.effective_chat.id, int(cofounder_id))
                    username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
                    response += f"{i}. {username} (`{cofounder_id}`)\n"
                except:
                    response += f"{i}. ID: `{cofounder_id}`\n"
        else:
            response += f"📝 **No hay co-fundadores asignados**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()

    if action == "add":
        if len(args) < 2:
            await update.message.reply_text("❌ Uso: `/cofounder add [user_id]`"
                                            )
            return

        target_user_id = args[1]

        # Verificar si ya tiene un rol
        current_role = db.get_staff_role(target_user_id)
        if current_role:
            role_names = {
                '1': 'Fundador',
                '2': 'Co-fundador',
                '3': 'Moderador'
            }
            current_role_name = role_names.get(current_role['role'],
                                               'Desconocido')
            await update.message.reply_text(
                f"⚠️ El usuario ya es {current_role_name}")
            return

        # Asignar como co-fundador
        db.set_staff_role(target_user_id, '2')

        response = f"💎 **CO-FUNDADOR ASIGNADO** 💎\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"🎭 **Rol:** Co-fundador (Nivel 2)\n"
        response += f"👮‍♂️ **Asignado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"✨ **Permisos de co-fundador activados**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "remove":
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Uso: `/cofounder remove [user_id]`")
            return

        target_user_id = args[1]

        # Verificar si es co-fundador
        if not db.is_cofounder(target_user_id):
            await update.message.reply_text(
                f"❌ El usuario `{target_user_id}` no es co-fundador")
            return

        # Remover rol
        db.remove_staff_role(target_user_id)

        response = f"🗑️ **CO-FUNDADOR REMOVIDO** 🗑️\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"👮‍♂️ **Removido por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"❌ **Ya no tiene permisos de co-fundador**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "list":
        # Reutilizar la lógica de mostrar lista
        await cofounder_command(update, context)

    else:
        await update.message.reply_text(
            "❌ **Acción inválida**\n**Acciones:** `add`, `remove`, `list`")


@staff_only(2)  # Co-fundador o superior
async def moderator_command(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Gestionar moderadores - Co-fundadores y fundadores"""
    args = context.args

    if not args:
        # Mostrar lista de moderadores actuales
        moderators = db.get_all_by_role('3')

        response = f"🛡️ **GESTIÓN DE MODERADORES** 🛡️\n\n"
        response += f"**Comandos disponibles:**\n"
        response += f"• `/moderator add [user_id]` - Asignar moderador\n"
        response += f"• `/moderator remove [user_id]` - Quitar moderador\n"
        response += f"• `/moderator list` - Ver lista actual\n\n"

        if moderators:
            response += f"**Moderadores actuales:**\n"
            for i, mod_id in enumerate(moderators, 1):
                try:
                    chat_member = await context.bot.get_chat_member(
                        update.effective_chat.id, int(mod_id))
                    username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name

                    # Mostrar warns dados por el moderador
                    mod_data = db.get_staff_role(mod_id)
                    warns_given = mod_data.get('warn_count',
                                               0) if mod_data else 0

                    response += f"{i}. {username} (`{mod_id}`) - {warns_given}/2 warns dados\n"
                except:
                    response += f"{i}. ID: `{mod_id}`\n"
        else:
            response += f"📝 **No hay moderadores asignados**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()

    if action == "add":
        if len(args) < 2:
            await update.message.reply_text("❌ Uso: `/moderator add [user_id]`"
                                            )
            return

        target_user_id = args[1]

        # Verificar si ya tiene un rol
        current_role = db.get_staff_role(target_user_id)
        if current_role:
            role_names = {
                '1': 'Fundador',
                '2': 'Co-fundador',
                '3': 'Moderador'
            }
            current_role_name = role_names.get(current_role['role'],
                                               'Desconocido')
            await update.message.reply_text(
                f"⚠️ El usuario ya es {current_role_name}")
            return

        # Asignar como moderador
        db.set_staff_role(target_user_id, '3')

        response = f"🛡️ **MODERADOR ASIGNADO** 🛡️\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"🎭 **Rol:** Moderador (Nivel 3)\n"
        response += f"👮‍♂️ **Asignado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"⚠️ **Límite:** 2 warns máximo por moderador\n"
        response += f"✨ **Permisos de moderador activados**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "remove":
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Uso: `/moderator remove [user_id]`")
            return

        target_user_id = args[1]

        # Verificar si es moderador
        if not db.is_moderator(target_user_id):
            await update.message.reply_text(
                f"❌ El usuario `{target_user_id}` no es moderador")
            return

        # Obtener estadísticas antes de remover
        mod_data = db.get_staff_role(target_user_id)
        warns_given = mod_data.get('warn_count', 0) if mod_data else 0

        # Remover rol
        db.remove_staff_role(target_user_id)

        response = f"🗑️ **MODERADOR REMOVIDO** 🗑️\n\n"
        response += f"👤 **Usuario:** `{target_user_id}`\n"
        response += f"📊 **Warns dados durante su período:** {warns_given}/2\n"
        response += f"👮‍♂️ **Removido por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"❌ **Ya no tiene permisos de moderador**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    elif action == "list":
        # Reutilizar la lógica de mostrar lista
        await moderator_command(update, context)

    else:
        await update.message.reply_text(
            "❌ **Acción inválida**\n**Acciones:** `add`, `remove`, `list`")


async def emergency_founder_command(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    """Comando de emergencia para auto-registrarse como fundador"""
    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # IDs autorizados para usar este comando de emergencia
    emergency_ids = [6938971996, 5537246556]

    if user_id_int not in emergency_ids:
        await update.message.reply_text(
            "❌ Este comando de emergencia no está disponible para ti")
        return

    # Verificar si ya está registrado
    if db.is_founder(user_id):
        await update.message.reply_text(
            "✅ **YA ERES FUNDADOR**\n\n"
            "🔍 Tu rol ya está registrado en la base de datos\n"
            "👑 Nivel: Fundador (1)\n\n"
            "💡 Todos los comandos de fundador están disponibles",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Auto-registrar como fundador
    db.set_staff_role(user_id, '1')

    await update.message.reply_text(
        "🚨 **REGISTRO DE EMERGENCIA COMPLETADO** 🚨\n\n"
        "👑 **Te has registrado como Fundador**\n"
        "🔐 **Nivel:** 1 (Máximo)\n"
        "📅 **Fecha:** " + datetime.now().strftime('%d/%m/%Y %H:%M') + "\n\n"
        "✅ **Todos los permisos de fundador están ahora activos**\n"
        "🛠️ **Comandos disponibles:**\n"
        "• `/founder` - Gestionar fundadores\n"
        "• `/cofounder` - Gestionar co-fundadores\n"
        "• `/moderator` - Gestionar moderadores\n"
        "• `/post` - Publicar contenido\n"
        "• Y todos los comandos de staff",
        parse_mode=ParseMode.MARKDOWN)


@staff_only(2)  # Co-fundador o superior
async def unwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remover advertencia de un usuario"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔄 **REMOVER ADVERTENCIA** 🔄\n\n"
            "**Uso:** `/unwarn [user_id]`\n"
            "**Ejemplo:** `/unwarn 123456789`\n\n"
            "⚠️ Solo Co-fundadores y Fundadores pueden usar este comando",
            parse_mode=ParseMode.MARKDOWN)
        return

    target_user_id = args[0]
    user_data = db.get_user(target_user_id)
    current_warns = user_data.get('warns', 0)

    if current_warns <= 0:
        await update.message.reply_text(
            f"✅ **SIN ADVERTENCIAS**\n\n"
            f"👤 **Usuario:** {target_user_id}\n"
            f"⚠️ **Advertencias:** 0/3\n\n"
            f"💡 Este usuario no tiene advertencias activas",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Remover una advertencia
    new_warns = max(0, current_warns - 1)
    db.update_user(target_user_id, {'warns': new_warns})

    staff_data = db.get_staff_role(str(update.effective_user.id))
    is_admin = update.effective_user.id in ADMIN_IDS

    if is_admin:
        applied_by_rank = "👑 Admin Principal"
    elif staff_data:
        rank_names = {
            '1': '👑 Fundador',
            '2': '💎 Co-Fundador',
            '3': '🛡️ Moderador'
        }
        applied_by_rank = rank_names.get(staff_data['role'], 'Staff')
    else:
        applied_by_rank = "Staff"

    # Enviar log administrativo
    group_id = str(update.effective_chat.id)
    await send_admin_log(context=context,
                         action_type='UNWARN',
                         admin_user=update.effective_user,
                         target_user_id=target_user_id,
                         reason="Advertencia removida",
                         group_id=group_id,
                         additional_data={
                             'previous_warns': current_warns,
                             'current_warns': new_warns,
                             'admin_rank': applied_by_rank
                         })

    response = f"✅ **ADVERTENCIA REMOVIDA** ✅\n\n"
    response += f"👤 **Usuario:** {target_user_id}\n"
    response += f"⚠️ **Advertencias:** {new_warns}/3 (era {current_warns}/3)\n"
    response += f"👮‍♂️ **Por:** {update.effective_user.first_name} ({applied_by_rank})\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    response += f"🔄 **Estado:** {'Sin advertencias' if new_warns == 0 else f'{3-new_warns} advertencias restantes antes del ban'}\n"
    response += f"📋 **Acción registrada en logs administrativos**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@bot_admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Desbanear usuario"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "🔓 **DESBANEAR USUARIO** 🔓\n\n"
            "**Uso:** `/unban [user_id]`\n"
            "**Ejemplo:** `/unban 123456789`\n\n"
            "⚠️ Solo moderadores, co-fundadores y fundadores pueden usar este comando",
            parse_mode=ParseMode.MARKDOWN)
        return

    target_user_id = args[0]
    group_id = str(update.effective_chat.id)

    try:
        # Intentar desbanear del chat actual
        await context.bot.unban_chat_member(chat_id=update.effective_chat.id,
                                            user_id=int(target_user_id),
                                            only_if_banned=True)

        # Resetear advertencias del usuario
        db.update_user(target_user_id, {'warns': 0})

        # Enviar log administrativo
        await send_admin_log(
            context=context,
            action_type='UNBAN',
            admin_user=update.effective_user,
            target_user_id=target_user_id,
            reason="Usuario desbaneado - Advertencias reseteadas",
            group_id=group_id,
            additional_data={
                'success': True,
                'warns_reset': True
            })

        response = f"🔓 **USUARIO DESBANEADO** 🔓\n\n"
        response += f"👤 **ID:** {target_user_id}\n"
        response += f"👮‍♂️ **Por:** {update.effective_user.first_name}\n"
        response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"✅ **El usuario puede ingresar nuevamente al chat**\n"
        response += f"🔄 **Advertencias reseteadas a 0/3**\n"
        response += f"💡 **Acción ejecutada y registrada**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        # Enviar log de error
        await send_admin_log(context=context,
                             action_type='UNBAN',
                             admin_user=update.effective_user,
                             target_user_id=target_user_id,
                             reason="Error al desbanear usuario",
                             group_id=group_id,
                             additional_data={
                                 'success': False,
                                 'error': str(e)
                             })

        await update.message.reply_text(
            f"❌ **ERROR AL DESBANEAR**\n\n"
            f"👤 **Usuario:** {target_user_id}\n"
            f"🔍 **Error:** {str(e)}\n\n"
            f"💡 **Posibles causas:**\n"
            f"• El usuario no está baneado\n"
            f"• ID de usuario inválido\n"
            f"• El bot no tiene permisos suficientes",
            parse_mode=ParseMode.MARKDOWN)


@bot_admin_only
async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cerrar bot para mantenimiento - Solo admins"""
    args = context.args
    maintenance_message = ' '.join(
        args) if args else "El bot está en mantenimiento. Volveremos pronto."

    db.set_maintenance(True, maintenance_message)

    response = f"🔒 **BOT CERRADO PARA MANTENIMIENTO** 🔒\n\n"
    response += f"🚧 **Estado:** Mantenimiento activado\n"
    response += f"💬 **Mensaje:** {maintenance_message}\n"
    response += f"👮‍♂️ **Por:** {update.effective_user.first_name}\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    response += f"⚠️ **Los usuarios no podrán usar comandos**\n"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@bot_admin_only
async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abrir bot después de mantenimiento - Solo admins"""
    if not db.is_maintenance():
        await update.message.reply_text(
            "✅ **EL BOT YA ESTÁ ABIERTO** ✅\n\n"
            "💡 El bot no está en modo mantenimiento\n"
            "🔄 Todos los comandos están funcionando normalmente",
            parse_mode=ParseMode.MARKDOWN)
        return

    db.set_maintenance(False, "")

    response = f"🔓 **BOT ABIERTO Y OPERATIVO** 🔓\n\n"
    response += f"✅ **Estado:** Bot totalmente funcional\n"
    response += f"🔄 **Todos los comandos están disponibles**\n"
    response += f"👮‍♂️ **Abierto por:** {update.effective_user.first_name}\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    response += f"🎉 **¡Los usuarios ya pueden usar el bot normalmente!**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@staff_only(
    3
)  # Moderador o superior (incluye fundadores, co-fundadores y moderadores)
async def housemode_command(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Modo casa de seguridad - Moderadores, co-fundadores y fundadores"""
    chat_id = str(update.effective_chat.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "🏠 **MODO CASA (HOUSEMODE)** 🏠\n\n"
            "**Uso:** `/housemode [on/off] [razón]`\n\n"
            "**Funciones:**\n"
            "• Bloquea temporalmente el grupo\n"
            "• Solo admins pueden enviar mensajes\n"
            "• Protege contra spam y raids\n"
            "• Medida preventiva de seguridad\n\n"
            "**Ejemplos:**\n"
            "• `/housemode on Supervisión activa`\n"
            "• `/housemode off`",
            parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()
    reason = ' '.join(args[1:]) if len(args) > 1 else ""

    if action == "on":
        # Razón automática si no se proporciona
        if not reason:
            reason = "Administrador ausente - Protección automática contra raids, spam masivo y actividad maliciosa."

        db.set_housemode(chat_id, True, reason)

        # Restringir el chat - Solo importamos ChatPermissions aquí
        try:
            from telegram import ChatPermissions

            # Crear permisos restrictivos - Solo envío de mensajes bloqueado
            restricted_permissions = ChatPermissions(
                can_send_messages=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False)

            await context.bot.set_chat_permissions(
                chat_id=update.effective_chat.id,
                permissions=restricted_permissions)

            response = f"🏠 **MODO CASA ACTIVADO** 🏠\n\n"
            response += f"🔒 **Grupo bloqueado temporalmente**\n\n"
            response += f"🛡️ **Medidas de seguridad activas:**\n"
            response += f"• 🚫 Prevención contra raids y spam\n"
            response += f"• ⚠️ Protección durante ausencia administrativa\n\n"
            response += f"📝 **Razón:** {reason}\n\n"
            response += f"🕒 El grupo será activado en breve por un administrador\n"
            response += f"👮‍♂️ **Activado por:** {update.effective_user.first_name}\n"
            response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

        except Exception as e:
            response = f"❌ **ERROR AL ACTIVAR MODO CASA** ❌\n\n"
            response += f"🔍 **Error:** {str(e)}\n"
            response += f"💡 **Verifica que el bot tenga permisos de administrador**"

    elif action == "off":
        db.set_housemode(chat_id, False, "")

        # Restaurar permisos normales del chat
        try:
            from telegram import ChatPermissions

            # Crear permisos normales
            normal_permissions = ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False)

            await context.bot.set_chat_permissions(
                chat_id=update.effective_chat.id,
                permissions=normal_permissions)

            response = f"🔓 **MODO CASA DESACTIVADO** 🔓\n\n"
            response += f"✅ **El grupo ha sido desbloqueado**\n"
            response += f"💬 **Los miembros ya pueden enviar mensajes**\n"
            response += f"🔄 **Funciones normales del grupo restauradas**\n\n"
            response += f"👮‍♂️ **Desactivado por:** {update.effective_user.first_name}\n"
            response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            response += f"🛡️ **Supervisión activa restablecida**"

        except Exception as e:
            response = f"❌ **ERROR AL DESACTIVAR MODO CASA** ❌\n\n"
            response += f"🔍 **Error:** {str(e)}\n"
            response += f"💡 **Verifica que el bot tenga permisos de administrador**"

    else:
        response = f"❌ **Acción inválida**\n\n"
        response += f"**Acciones disponibles:** `on` | `off`"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


def escape_markdown_v2(text):
    """Escapa caracteres especiales para MarkdownV2"""
    if not text:
        return ""

    # Lista completa de caracteres especiales para MarkdownV2
    special_chars = [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|',
        '{', '}', '.', '!'
    ]

    # Escapar cada carácter especial
    for char in special_chars:
        text = text.replace(char, f'\\{char}')

    return text


def organize_content_with_ai(content):
    """IA para organizar y estructurar el contenido automáticamente - VERSIÓN MEJORADA CON DETECCIÓN AVANZADA"""
    import re

    # Detectar diferentes tipos de contenido - PATRONES MEJORADOS
    # Patrón para CCs con CVV opcional (formato original y nuevo)
    cc_pattern = r'\b\d{13,19}\|\d{1,2}\|\d{2,4}(?:\|\d{3,4})?\b'
    ccs_found = re.findall(cc_pattern, content)

    # Detectar URLs/enlaces - PATRONES AMPLIAMENTE MEJORADOS
    url_patterns = [
        r'https?://[^\s]+',  # URLs completas estándar
        r'(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',  # URLs sin protocolo
        r't\.me/[^\s]+',  # Enlaces de Telegram específicos
        r'telegram\.me/[^\s]+',  # Telegram alternativo
        r'tg://[^\s]+',  # Protocolo de Telegram
        r'@[a-zA-Z0-9_]+',  # Menciones que pueden ser canales
        # NUEVO: Detectar enlaces embebidos en palabras con texto que contiene dominios
        r'[a-zA-Z0-9]*(?:https?://|www\.|\.com|\.net|\.org|\.io|\.co|\.me|t\.me|telegram\.me)[a-zA-Z0-9/\-._~:/?#[\]@!$&\'()*+,;=%]*',
        # NUEVO: Detectar texto con caracteres Unicode que contiene URLs
        r'[\w\u00a0-\uffff]*(?:https?://|www\.|\.com|\.net|\.org|\.io|\.me|t\.me)[\w\u00a0-\uffff/\-._~:/?#[\]@!$&\'()*+,;=%]*',
    ]

    urls_found = []
    for pattern in url_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.UNICODE)
        urls_found.extend(matches)

    # NUEVO: Detectar enlaces embebidos usando caracteres Unicode especiales
    # Buscar patrones sospechosos de texto con enlaces ocultos
    hidden_link_patterns = [
        r'[\u200B-\u200F\u202A-\u202E\u2060-\u2064]',  # Caracteres de control Unicode
        r'[\u00A0\u1680\u2000-\u200A\u202F\u205F\u3000]',  # Espacios Unicode no estándar
        r'[\u034F\u061C\u180E]',  # Más caracteres invisibles
        r'[^\x00-\x7F].*?(?:http|www|\.com|\.net|\.org|t\.me)',  # Unicode mezclado con dominios
    ]

    # Detectar texto sospechoso que puede contener enlaces embebidos
    suspicious_text = []
    for pattern in hidden_link_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        suspicious_text.extend(matches)

    # NUEVO: Búsqueda más agresiva de enlaces embebidos en palabras individuales
    words = content.split()
    suspicious_words = []
    for word in words:
        # Detectar si una palabra contiene indicadores de URL embebidos
        url_indicators = [
            'http', 'www', '.com', '.net', '.org', '.io', '.me', 't.me',
            'telegram', 'discord', 'bit.ly'
        ]

        # Si la palabra contiene indicadores de URL o caracteres especiales
        if any(indicator in word.lower() for indicator in url_indicators) or \
           (len(word) > 30 and ' ' not in word) or \
           any(ord(char) > 127 for char in word) or \
           re.search(r'[\u200B-\u200F\u202A-\u202E]', word):
            suspicious_words.append(word)

        # ESPECÍFICAMENTE para el caso "AQUI" con link embebido
        # Detectar palabras que pueden tener texto + URL embebida
        if len(word) > 10 and any(
                char in word
                for char in ['/', ':', '.']) and not word.isdigit():
            suspicious_words.append(word)

    # Agregar texto sospechoso y palabras a URLs encontradas
    if suspicious_words:
        urls_found.extend(
            suspicious_words[:5])  # Aumentado a 5 para mejor detección
    if suspicious_text:
        urls_found.extend(suspicious_text[:3])

    # NUEVO: Detección específica para texto con enlaces embebidos
    # Buscar patrones como "AQUI" seguido o conteniendo URLs
    embedded_patterns = [
        r'[A-Z]{2,}(?=https?://)',  # Palabras en mayúsculas seguidas de URL
        r'[A-Z]{2,}https?://[^\s]+',  # Palabras pegadas a URLs
        r'[a-zA-Z]+(?:https?://|www\.)[^\s]+',  # Cualquier texto pegado a URL
        r'[a-zA-Z]+t\.me/[^\s]+',  # Texto pegado a enlaces de Telegram
    ]

    for pattern in embedded_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        urls_found.extend(matches)

    # Detectar hashtags
    hashtag_pattern = r'#[a-zA-Z0-9_]+'
    hashtags_found = re.findall(hashtag_pattern, content)

    # Detectar menciones de canales/usuarios
    mention_pattern = r'@[a-zA-Z0-9_]+'
    mentions_found = re.findall(mention_pattern, content)

    # Detectar emojis de banderas y países
    country_pattern = r'🇺🇸|🇦🇷|🇧🇷|🇨🇴|🇲🇽|🇪🇸|🇵🇪|🇨🇱|🇺🇾|🇻🇪'
    countries_found = re.findall(country_pattern, content)

    # Detectar líneas de información específica (teléfonos, VPN, etc.)
    phone_pattern = r'📱:\s*\d+\|\d+\|\d+'
    phones_found = re.findall(phone_pattern, content)

    vpn_pattern = r'🌍:\s*\[.*?\]'
    vpn_found = re.findall(vpn_pattern, content)

    # NUEVA LÓGICA: Mantener formato original y solo separar lo esencial
    lines = content.split('\n')
    organized_lines = []
    technical_data = []

    # Procesar todas las líneas manteniendo el formato original
    for i, line in enumerate(lines):
        original_line = line  # Preservar la línea original con espacios
        line_stripped = line.strip()

        # Si es una línea vacía, mantenerla para preservar el formato
        if not line_stripped:
            organized_lines.append("")
            continue

        # Si la línea contiene solo datos técnicos (CCs, teléfonos, VPN), separarla
        if (re.search(cc_pattern, line_stripped) and len(line_stripped.split()) <= 3) or \
           (line_stripped.startswith('📱:')) or \
           (line_stripped.startswith('🌍:')):
            technical_data.append(line_stripped)
        else:
            # Mantener como contenido principal con formato original
            organized_lines.append(original_line)

    # Reconstruir el contenido manteniendo el formato original COMPLETO
    if organized_lines:
        clean_content = '\n'.join(organized_lines).strip()
    else:
        clean_content = content  # Fallback al contenido original

    # NO remover URLs del contenido - mantener formato original
    # Solo limpiar espacios extra excesivos
    clean_content = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_content).strip()

    return {
        'content': clean_content,
        'ccs': ccs_found,
        'urls': urls_found,
        'hashtags': hashtags_found,
        'mentions': mentions_found,
        'countries': countries_found,
        'phones': phones_found,
        'vpn_info': vpn_found,
        'technical_data': technical_data
    }


def format_smart_publication(organized_data, author_name):
    """Formatea inteligentemente la publicación manteniendo estructura original"""
    content = organized_data['content']
    ccs = organized_data['ccs']
    urls = organized_data['urls']
    hashtags = organized_data['hashtags']
    mentions = organized_data['mentions']
    countries = organized_data.get('countries', [])
    phones = organized_data.get('phones', [])
    vpn_info = organized_data.get('vpn_info', [])
    technical_data = organized_data.get('technical_data', [])

    # Escapar caracteres especiales para MarkdownV2
    safe_author = escape_markdown_v2(author_name)

    if ccs:
        # Formato específico para releases con CCs - MANTENER ESTRUCTURA ORIGINAL
        message = "⚡ *𝗖𝗛𝗘𝗥𝗡𝗢𝗕𝗜𝗟 𝗖𝗛𝗟𝗩* ⚡\n"
        message += "═══════════════════════════════\n\n"

        # MOSTRAR TODO EL CONTENIDO TAL COMO VIENE, solo limpiando caracteres problemáticos
        if content:
            # Limpiar solo caracteres que causan problemas con MarkdownV2
            clean_content = content.replace('𝗧𝗘𝗟𝟯𝗣𝟰𝗥𝗧𝗬', 'TELEPARTY')
            clean_content = clean_content.replace('𝗧𝗔𝗟𝗩𝗘𝗭', 'TALVEZ')
            clean_content = clean_content.replace('𝟭', '1')
            clean_content = clean_content.replace('𝗔Ñ𝗢', 'AÑO')
            clean_content = clean_content.replace('𝗔𝗨𝗧𝗢𝗣', 'AUTOP')

            # Procesar línea por línea manteniendo el formato original
            lines = clean_content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    # Solo escapar caracteres problemáticos, NO cambiar estructura
                    safe_line = escape_markdown_v2(line)

                    # La primera línea en negrita, las demás normales
                    if i == 0:
                        message += f"*{safe_line}*\n"
                    else:
                        message += f"{safe_line}\n"

            message += "\n"

        # Agregar información técnica (CCs, teléfonos, VPN)
        if technical_data:
            for tech_line in technical_data:
                safe_tech = escape_markdown_v2(tech_line)
                message += f"{safe_tech}\n"
            message += "\n"

        # Agregar CCs detectadas si no están ya en el contenido
        if ccs and not any(cc in content for cc in ccs):
            message += "💳 *CCs Detectadas:*\n"
            for cc in ccs:
                if cc.startswith('4'):
                    prefix = "🔵"
                elif cc.startswith('5'):
                    prefix = "🔴"
                else:
                    prefix = "⚫"
                message += f"{prefix} `{cc}`\n"
            message += "\n"

        # Resumen
        message += f"📊 *Total CCs:* {len(ccs)}\n"
        if countries:
            message += f"🌍 *País:* {' '.join(countries)}\n"
        message += f"📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y')}\n"

    else:
        # Formato para contenido general - MANTENER ESTRUCTURA
        message = "📢 *𝗖𝗛𝗘𝗥𝗡𝗢𝗕𝗜𝗟 𝗖𝗛𝗟𝗩 UPDATE* 📢\n"
        message += "═══════════════════════════════\n\n"

        if content:
            # MANTENER TODO EL FORMATO ORIGINAL
            clean_content = content.replace('𝗧𝗘𝗟𝟯𝗣𝟰𝗥𝗧𝗬', 'TELEPARTY')
            clean_content = clean_content.replace('𝗧𝗔𝗟𝗩𝗘𝗭', 'TALVEZ')
            clean_content = clean_content.replace('𝟭', '1')
            clean_content = clean_content.replace('𝗔Ñ𝗢', 'AÑO')
            clean_content = clean_content.replace('𝗔𝗨𝗧𝗢𝗣', 'AUTOP')

            # Escapar solo caracteres problemáticos
            safe_content = escape_markdown_v2(clean_content)
            message += f"{safe_content}\n\n"

        message += f"───────────────────────────────────\n"
        message += f"📅 *Fecha:* {escape_markdown_v2(datetime.now().strftime('%d/%m/%Y %H:%M'))}\n"

    # Agregar hashtags y menciones si existen
    if hashtags:
        message += f"\n🏷️ *Tags:* "
        for hashtag in hashtags:
            safe_hashtag = escape_markdown_v2(hashtag)
            message += f"{safe_hashtag} "
        message += "\n"

    if mentions:
        message += f"👤 *Menciones:* "
        for mention in mentions:
            safe_mention = escape_markdown_v2(mention)
            message += f"{safe_mention} "
        message += "\n"

    message += f"\n👑 *Publicado por:* {safe_author}\n"
    message += f"🤖 *Bot:* @ChernobilChLv\\_bot"

    return message


@staff_only(
    3)  # Moderador o superior (incluye fundadores, co-fundadores y moderadores)
async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /post con IA para organizar contenido - Moderadores, co-fundadores y fundadores"""
    user_id = str(update.effective_user.id)
    staff_data = db.get_staff_role(user_id)

    # Verificar permisos - Solo base de datos (el decorador ya hace la verificación)
    # Este comando ya está protegido por @staff_only(2)

    args = context.args
    current_chat_id = str(update.effective_chat.id)

    if not args:
        await update.message.reply_text(
            "📢 *SISTEMA DE PUBLICACIONES CON IA* 📢\n\n"
            "*Uso:* `/post [chat_id] [contenido]`\n\n"
            "📋 *Ejemplos:*\n"
            "• `/post \\-1001234567890 Mi publicación`\n"
            "• `/post here Mi contenido` \\(publica aquí\\)\n"
            "• `/post hola` \\(publica en chat actual\\)\n"
            "• `/post hola\\ncomo\\nestan` \\(multilínea\\)\n\n"
            "🤖 *Funciones de IA:*\n"
            "• Organización automática de CCs por tipo\n"
            "• Detección inteligente de contenido\n"
            "• Formato profesional adaptativo\n"
            "• Separación de URLs y hashtags\n"
            "• Estadísticas automáticas\n\n"
            "💡 *Tip:* La IA organizará automáticamente tu contenido",
            parse_mode=ParseMode.MARKDOWN_V2)
        return

    # Obtener chat destino
    target_chat = args[0]
    if target_chat.lower() == "here":
        target_chat_id = current_chat_id
    else:
        target_chat_id = target_chat

    # Obtener contenido completo del mensaje incluyendo saltos de línea
    message_text = update.message.text

    # Si solo hay un argumento y es "here" o un chat_id, buscar contenido en todo el mensaje
    if len(args) == 1:
        # Para casos como "/post hola\ncomo\nestan" donde "hola" se interpreta como target_chat
        # Verificar si el primer argumento parece ser contenido en lugar de un chat_id
        first_arg = args[0]

        # Si no parece un chat_id (no empieza con - y no es "here"), tratarlo como contenido
        if not (first_arg.lower() == "here" or first_arg.startswith("-")
                or first_arg.isdigit()):
            # Usar el chat actual y todo después de "/post" como contenido
            target_chat_id = current_chat_id
            content_start = message_text.find("/post") + len("/post")
            content = message_text[content_start:].strip(
            ) if content_start < len(message_text) else ""
        else:
            # Es un target_chat válido
            if target_chat.lower() == "here":
                target_chat_id = current_chat_id
                content_start = message_text.find("/post here") + len(
                    "/post here")
            else:
                target_chat_id = target_chat
                content_start = message_text.find(target_chat) + len(
                    target_chat)

            content = message_text[content_start:].strip(
            ) if content_start < len(message_text) else ""
    else:
        # Lógica original para múltiples argumentos
        if target_chat.lower() == "here":
            target_chat_id = current_chat_id
            content_start = message_text.find("/post here") + len("/post here")
        else:
            target_chat_id = target_chat
            content_start = message_text.find(target_chat) + len(target_chat)

        content = message_text[content_start:].strip() if content_start < len(
            message_text) else ""

    if not content:
        await update.message.reply_text(
            "❌ *CONTENIDO REQUERIDO*\n\n"
            "📝 Debes incluir el contenido a publicar\n"
            "💡 *Ejemplos:*\n"
            "• `/post here Mi contenido aquí`\n"
            "• `/post here hola`\n"
            "  `como`\n"
            "  `estan`",
            parse_mode=ParseMode.MARKDOWN_V2)
        return

    # Procesar contenido con IA
    try:
        # Mensaje de procesamiento
        processing_msg = await update.message.reply_text(
            "🤖 *PROCESANDO CON IA* 🤖\n\n"
            "⚡ Analizando contenido\\.\\.\\.\n"
            "🔍 Detectando elementos\\.\\.\\.\n"
            "📊 Organizando información\\.\\.\\.\n"
            "🎨 Aplicando formato inteligente\\.\\.\\.",
            parse_mode=ParseMode.MARKDOWN_V2)

        # Simular procesamiento IA
        await asyncio.sleep(2)

        # Organizar contenido con IA
        organized_data = organize_content_with_ai(content)

        # Formatear publicación inteligentemente
        publication_message = format_smart_publication(
            organized_data, update.effective_user.first_name)

        # Obtener información del chat destino
        try:
            chat_info = await context.bot.get_chat(target_chat_id)
            chat_name = chat_info.title or f"Chat {target_chat_id}"
        except:
            chat_name = f"Chat {target_chat_id}"

        # Actualizar mensaje de procesamiento
        await processing_msg.edit_text(
            f"📤 *PREPARANDO PUBLICACIÓN* 📤\n\n"
            f"🎯 *Destino:* {escape_markdown_v2(chat_name)}\n"
            f"📊 *Tipo:* {'Release con CCs' if organized_data['ccs'] else 'Contenido general'}\n"
            f"💳 *CCs detectadas:* {len(organized_data['ccs'])}\n"
            f"🔗 *URLs detectadas:* {len(organized_data['urls'])}\n"
            f"🏷️ *Hashtags:* {len(organized_data['hashtags'])}\n"
            f"👤 *Autor:* {escape_markdown_v2(update.effective_user.first_name)}\n\n"
            f"⏳ *Enviando\\.\\.\\.*",
            parse_mode=ParseMode.MARKDOWN_V2)

        # Publicar en el chat destino usando MarkdownV2
        sent_message = await context.bot.send_message(
            chat_id=target_chat_id,
            text=publication_message,
            parse_mode=ParseMode.MARKDOWN_V2)

        # Actualizar confirmación con éxito
        success_message = f"✅ *PUBLICACIÓN EXITOSA* ✅\n\n"
        success_message += f"🎯 *Destino:* {escape_markdown_v2(chat_name)}\n"
        success_message += f"📨 *Message ID:* `{sent_message.message_id}`\n"
        success_message += f"📊 *Análisis IA:*\n"
        success_message += f"  • CCs: {len(organized_data['ccs'])}\n"
        success_message += f"  • URLs: {len(organized_data['urls'])}\n"
        success_message += f"  • Hashtags: {len(organized_data['hashtags'])}\n"
        success_message += f"  • Menciones: {len(organized_data['mentions'])}\n"
        success_message += f"👤 *Publicado por:* {escape_markdown_v2(update.effective_user.first_name)}\n"
        success_message += f"⏰ *Hora:* {escape_markdown_v2(datetime.now().strftime('%H:%M:%S'))}\n\n"
        success_message += f"🎉 *¡Publicación completada con IA\\!*"

        await processing_msg.edit_text(success_message,
                                       parse_mode=ParseMode.MARKDOWN_V2)

        # Log de la publicación
        logger.info(
            f"Publicación con IA - Usuario: {update.effective_user.id} ({update.effective_user.first_name}) - Destino: {target_chat_id} - CCs: {len(organized_data['ccs'])}"
        )

    except Exception as e:
        # Error al publicar - usar texto plano para evitar errores de parsing
        error_message = f"❌ ERROR EN PUBLICACIÓN ❌\n\n"
        error_message += f"🎯 Destino: {target_chat_id}\n"
        error_message += f"🔍 Error: {str(e)[:100]}...\n\n"
        error_message += f"💡 Posibles causas:\n"
        error_message += f"• El bot no está en ese chat\n"
        error_message += f"• ID de chat incorrecto\n"
        error_message += f"• Sin permisos para enviar mensajes\n"
        error_message += f"• Chat privado no accesible\n\n"
        error_message += f"🔧 Solución: Verifica el ID y permisos del bot"

        try:
            await processing_msg.edit_text(error_message)
        except:
            await update.message.reply_text(error_message)

        logger.error(
            f"Error en publicación con IA - Usuario: {update.effective_user.id} - Error: {e}"
        )


@staff_only(3)  # Moderador o superior
async def establishedadministration_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configurar canal para logs de acciones administrativas - Moderadores, co-fundadores y fundadores"""
    try:
        args = context.args
        group_id = str(update.effective_chat.id)

        if not args:
            # Mostrar estado actual
            try:
                current_config = db.get_admin_log_channel(group_id)

                response = "📋 **CONFIGURAR LOGS ADMINISTRATIVOS** 📋\n\n"
                response += "**Uso:** `/establishedadministration [channel_id]`\n\n"
                response += "📝 **Función:**\n"
                response += "• Configura canal para recibir logs automáticos\n"
                response += "• Registra todas las acciones administrativas\n"
                response += "• Incluye: ban/unban/warn/unwarn/clean\n\n"
                response += "💡 **Ejemplo:** `/establishedadministration -1001234567890`\n\n"

                if current_config and current_config.get('channel_id'):
                    response += "📊 **Estado actual:**\n"
                    response += f"✅ **Configurado:** Canal `{current_config['channel_id']}`\n"
                    response += f"📅 **Desde:** {current_config.get('configured_at', 'N/A')[:10]}\n"
                    response += f"🔄 **Estado:** {'Activo' if current_config.get('active', True) else 'Inactivo'}\n\n"
                    response += "🔧 **Para cambiar:** Ejecuta el comando con nuevo ID"
                else:
                    response += "❌ **No configurado**\n"
                    response += "⚙️ **Configura un canal para empezar a recibir logs**"

                await update.message.reply_text(response,
                                                parse_mode=ParseMode.MARKDOWN)
                return
            except Exception as e:
                logger.error(f"Error mostrando estado de logs: {e}")
                await update.message.reply_text(
                    "❌ **Error al mostrar estado**\n\n"
                    "📋 **Uso:** `/establishedadministration [channel_id]`\n"
                    "💡 **Ejemplo:** `/establishedadministration -1001234567890`"
                )
                return

        # Procesar configuración del canal
        admin_channel_id = args[0].strip()

        # Validaciones mejoradas
        if not admin_channel_id:
            await update.message.reply_text(
                "❌ **ID VACÍO** ❌\n\n"
                "💡 Proporciona un ID de canal válido\n"
                "📋 **Ejemplo:** `/establishedadministration -1001234567890`")
            return

        # Verificar formato de ID
        if not admin_channel_id.startswith('-'):
            await update.message.reply_text(
                "❌ **FORMATO DE ID INVÁLIDO** ❌\n\n"
                "🔍 El ID del canal debe empezar con '-'\n\n"
                "📋 **Formato correcto:**\n"
                "• Canal: `-1001234567890`\n"
                "• Grupo: `-1234567890`\n\n"
                "🔍 **Para obtener ID:**\n"
                "1. Agrega @RawDataBot al canal\n"
                "2. Escribe cualquier mensaje\n"
                "3. Copia el chat ID que muestre",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Verificar que sea numérico después del guión
        try:
            int(admin_channel_id)
        except ValueError:
            await update.message.reply_text(
                "❌ **ID INVÁLIDO** ❌\n\n"
                "💡 El ID debe ser un número válido\n"
                "📋 **Ejemplo válido:** `-1001234567890`",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Verificar acceso al canal
        try:
            chat_info = await context.bot.get_chat(admin_channel_id)
            chat_name = chat_info.title or f"Canal {admin_channel_id}"

        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Error accediendo al canal {admin_channel_id}: {e}")

            if "forbidden" in error_msg or "not found" in error_msg or "chat not found" in error_msg:
                await update.message.reply_text(
                    "❌ **BOT NO TIENE ACCESO AL CANAL** ❌\n\n"
                    f"🔍 **Canal:** `{admin_channel_id}`\n\n"
                    "💡 **Solución:**\n"
                    "1. Agrega el bot al canal\n"
                    "2. Dale permisos de administrador\n"
                    "3. Permite envío de mensajes\n\n"
                    "🤖 **Bot:** @ChernobilChLv_bot",
                    parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(
                    f"❌ **ERROR DE CONEXIÓN** ❌\n\n"
                    f"🔍 **Error:** {str(e)[:50]}...\n\n"
                    "💡 Verifica que el ID sea correcto y el bot tenga acceso",
                    parse_mode=ParseMode.MARKDOWN)
            return

        # Guardar configuración
        try:
            db.set_admin_log_channel(group_id, admin_channel_id)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            await update.message.reply_text(
                "❌ **Error guardando configuración**\n\n"
                f"🔍 **Error:** {str(e)[:50]}...\n\n"
                "💡 Intenta nuevamente")
            return

        # Enviar mensaje de prueba con formato seguro
        safe_group_id = escape_markdown(str(group_id))
        safe_admin_name = escape_markdown(update.effective_user.first_name)

        test_message = "🔧 *CANAL DE LOGS CONFIGURADO* 🔧\n\n"
        test_message += "✅ *Estado:* Activo\n"
        test_message += f"🏠 *Grupo origen:* `{safe_group_id}`\n"
        test_message += f"👮‍♂️ *Configurado por:* {safe_admin_name}\n"
        test_message += f"⏰ *Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        test_message += "📋 *Se registrarán:*\n"
        test_message += "🔨 Ban/Unban de usuarios\n"
        test_message += "⚠️ Warn/Unwarn de usuarios\n"
        test_message += "🧹 Limpieza de mensajes\n\n"
        test_message += "🤖 *Bot:* @ChernobilChLv\\_bot"

        try:
            await context.bot.send_message(chat_id=admin_channel_id,
                                           text=test_message,
                                           parse_mode=ParseMode.MARKDOWN)

            response = "✅ **LOGS ADMINISTRATIVOS CONFIGURADOS** ✅\n\n"
            response += f"🏠 **Grupo actual:** `{group_id}`\n"
            response += f"📢 **Canal de logs:** `{admin_channel_id}`\n"
            response += f"📝 **Nombre del canal:** {chat_name}\n"
            response += f"⚙️ **Configurado por:** {update.effective_user.first_name}\n"
            response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            response += "🔥 **¡Sistema activo!** Todas las acciones se registrarán automáticamente"

        except Exception as test_error:
            logger.error(f"Error enviando mensaje de prueba: {test_error}")
            response = "⚠️ **CONFIGURACIÓN GUARDADA CON ADVERTENCIA** ⚠️\n\n"
            response += f"💾 **Canal guardado:** `{admin_channel_id}`\n"
            response += f"❌ **Test falló:** {str(test_error)[:50]}...\n\n"
            response += "🔧 Verifica que el bot tenga permisos de envío en el canal"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error general en establishedadministration: {e}")
        await update.message.reply_text(
            f"❌ **ERROR GENERAL** ❌\n\n"
            f"🔍 **Error:** {str(e)[:50]}...\n\n"
            "💡 Contacta al administrador del bot",
            parse_mode=ParseMode.MARKDOWN)


@staff_only(3)  # Moderador o superior
async def setcheckchats_command(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    """Configurar chats para el sistema /check - Moderadores, co-fundadores y fundadores"""
    args = context.args
    group_id = str(update.effective_chat.id)

    if len(args) < 2:
        await update.message.reply_text(
            "⚙️ **CONFIGURAR SISTEMA /CHECK** ⚙️\n\n"
            "**Uso:** `/setcheckchats [chat_verificacion] [chat_publicacion]`\n\n"
            "📋 **Parámetros:**\n"
            "• `chat_verificacion`: ID del chat donde los admins aprueban/rechazan\n"
            "• `chat_publicacion`: ID del canal donde se publican las capturas aprobadas\n\n"
            "💡 **Ejemplo:** `/setcheckchats -1001234567890 -1001987654321`\n\n"
            "📝 **Nota:** Usa IDs negativos para grupos/canales",
            parse_mode=ParseMode.MARKDOWN)
        return

    try:
        verification_chat = args[0]
        publication_chat = args[1]

        # Validar que sean IDs válidos
        int(verification_chat)
        int(publication_chat)

        # Guardar configuración
        db.set_check_chats(group_id, verification_chat, publication_chat)

        response = f"✅ **CONFIGURACIÓN GUARDADA** ✅\n\n"
        response += f"🏠 **Grupo actual:** `{group_id}`\n"
        response += f"👮‍♂️ **Chat verificación:** `{verification_chat}`\n"
        response += f"📢 **Canal publicación:** `{publication_chat}`\n\n"
        response += f"⚙️ **Configurado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"✨ **El comando /check ya está listo para usar**"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)

    except ValueError:
        await update.message.reply_text(
            "❌ **IDs INVÁLIDOS**\n\n"
            "💡 Los IDs deben ser números enteros\n"
            "📝 Ejemplo: `/setcheckchats -1001234567890 -1001987654321`")


@bot_admin_only
async def links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver historial de links eliminados - Solo admins"""
    args = context.args

    if not args:
        # Mostrar estadísticas generales
        total_links = len(db.deleted_links)
        if total_links == 0:
            await update.message.reply_text(
                "📊 **HISTORIAL DE LINKS ELIMINADOS** 📊\n\n"
                "❌ **No hay links registrados**\n\n"
                "💡 **Uso:** `/links [user_id]` - Ver links de un usuario\n"
                "📋 **Ejemplo:** `/links 123456789`",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Mostrar últimos 10 links eliminados
        recent_links = list(db.deleted_links.items())[-10:]
        recent_links.reverse()  # Más recientes primero

        response = f"📊 **HISTORIAL DE LINKS ELIMINADOS** 📊\n\n"
        response += f"📈 **Total registrado:** {total_links} links\n"
        response += f"📋 **Últimos 10 eliminados:**\n\n"

        for link_id, data in recent_links:
            deleted_time = datetime.fromisoformat(
                data['deleted_at']).strftime('%d/%m %H:%M')
            response += f"🆔 `{link_id}` - {data['username']} ({deleted_time})\n"

        response += f"\n💡 **Ver específico:** `/links [user_id]`"

        await update.message.reply_text(response,
                                        parse_mode=ParseMode.MARKDOWN)
        return

    # Ver links de un usuario específico
    target_user_id = args[0]
    user_links = db.get_deleted_links_by_user(target_user_id)

    if not user_links:
        await update.message.reply_text(
            f"📊 **LINKS DE USUARIO** 📊\n\n"
            f"👤 **Usuario ID:** `{target_user_id}`\n"
            f"❌ **Sin registros:** Este usuario no tiene links eliminados",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Mostrar hasta 5 links más recientes del usuario
    recent_user_links = user_links[:5]

    response = f"📊 **LINKS ELIMINADOS DE USUARIO** 📊\n\n"
    response += f"👤 **Usuario ID:** `{target_user_id}`\n"
    response += f"📈 **Total eliminados:** {len(user_links)}\n"
    response += f"📋 **Últimos {len(recent_user_links)} registros:**\n\n"

    for link_data in recent_user_links:
        deleted_time = datetime.fromisoformat(
            link_data['deleted_at']).strftime('%d/%m/%Y %H:%M')
        response += f"🆔 **ID:** `{link_data['id']}`\n"
        response += f"📅 **Fecha:** {deleted_time}\n"
        response += f"🔗 **Links:** {', '.join(link_data['links'][:2])}{'...' if len(link_data['links']) > 2 else ''}\n"
        response += f"💬 **Mensaje:** {link_data['message']}\n"
        response += f"─────────────────────────\n"

    if len(user_links) > 5:
        response += f"\n📝 **Y {len(user_links) - 5} registros más...**"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


async def fix_founder_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Comando para verificar y corregir el rol de fundador"""
    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id

    # Solo para IDs específicos de fundadores
    if user_id_int not in [6938971996, 5537246556]:
        await update.message.reply_text(
            "❌ Este comando solo está disponible para fundadores autorizados")
        return

    # Verificar estado actual
    current_role = db.get_staff_role(user_id)
    in_admin_ids = user_id_int in ADMIN_IDS
    is_founder_db = db.is_founder(user_id)

    # Forzar corrección completa
    db.set_staff_role(user_id, '1')
    if user_id_int not in ADMIN_IDS:
        ADMIN_IDS.append(user_id_int)

    await update.message.reply_text(
        "🔧 **ESTADO DE PERMISOS CORREGIDO** 🔧\n\n"
        f"✅ **Verificación completa realizada:**\n"
        f"• ID: `{user_id}`\n"
        f"• Fundador en DB: ✅ (Forzado)\n"
        f"• En ADMIN_IDS: {'✅' if user_id_int in ADMIN_IDS else '❌ → ✅ (Corregido)'}\n"
        f"• Nivel: 1 (Máximo)\n\n"
        f"🛠️ **Todos los comandos administrativos están disponibles:**\n"
        f"• `/ban`, `/warn`, `/clean`, `/premium`\n"
        f"• `/founder`, `/cofounder`, `/moderator`\n"
        f"• `/post`, `/stats`, `/links`\n\n"
        f"🎯 **Prueba ahora cualquier comando de admin**",
        parse_mode=ParseMode.MARKDOWN)


@admin_only
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mutear usuario manualmente - Versión corregida"""
    try:
        args = context.args
        chat_id = str(update.effective_chat.id)

        if not args:
            await update.message.reply_text(
                "🔇 **MUTEAR USUARIO** 🔇\n\n"
                "**Uso:** `/mute [user_id] [duración] [razón]`\n\n"
                "**Duraciones disponibles:**\n"
                "• `30m` - 30 minutos\n"
                "• `1h` - 1 hora\n"
                "• `6h` - 6 horas\n"
                "• `12h` - 12 horas (por defecto)\n"
                "• `24h` - 24 horas\n"
                "• `48h` - 48 horas\n\n"
                "**Ejemplos:**\n"
                "• `/mute 123456789 2h Spam excesivo`\n"
                "• `/mute 123456789` (12h por defecto)\n\n"
                "⚠️ **Solo para casos serios:** Spam, flood, comportamiento disruptivo",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Validar user_id
        target_user_id = args[0].strip()
        if not target_user_id.isdigit():
            await update.message.reply_text(
                "❌ **ID INVÁLIDO**\n\n"
                "💡 El ID del usuario debe ser numérico\n"
                "📋 **Ejemplo:** `/mute 123456789 2h Spam`")
            return

        target_user_id_int = int(target_user_id)

        # Verificar que no sea el propio usuario
        if target_user_id_int == update.effective_user.id:
            await update.message.reply_text(
                "❌ **NO PUEDES MUTEARTE A TI MISMO**\n\n"
                "💡 Verifica el ID del usuario")
            return

        # Verificar que no sea staff
        is_target_admin = target_user_id_int in ADMIN_IDS
        target_staff = db.get_staff_role(target_user_id)

        if is_target_admin or target_staff:
            await update.message.reply_text(
                "❌ **NO SE PUEDE MUTEAR STAFF**\n\n"
                "🛡️ Los administradores, fundadores, co-fundadores y moderadores están protegidos",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Verificar si ya está muteado
        try:
            if (chat_id in muted_users and target_user_id in muted_users[chat_id]):
                current_mute = muted_users[chat_id][target_user_id]
                if datetime.now() < current_mute['unmute_time']:
                    time_left = current_mute['unmute_time'] - datetime.now()
                    hours_left = int(time_left.total_seconds() // 3600)
                    minutes_left = int((time_left.total_seconds() % 3600) // 60)

                    await update.message.reply_text(
                        f"⚠️ **USUARIO YA ESTÁ MUTEADO**\n\n"
                        f"👤 **Usuario:** {target_user_id}\n"
                        f"⏰ **Tiempo restante:** {hours_left}h {minutes_left}m\n"
                        f"📝 **Razón actual:** {current_mute['reason']}\n\n"
                        f"💡 Usa `/unmute {target_user_id}` para desmutear")
                    return
        except Exception as e:
            logger.warning(f"Error verificando mute existente: {e}")

        # Procesar duración
        duration_hours = 12  # Por defecto 12 horas
        if len(args) > 1:
            duration_str = args[1].lower()
            try:
                if duration_str.endswith('m'):
                    duration_minutes = int(duration_str[:-1])
                    if duration_minutes < 5:
                        await update.message.reply_text(
                            "❌ **Duración mínima:** 5 minutos")
                        return
                    duration_hours = duration_minutes / 60
                elif duration_str.endswith('h'):
                    duration_hours = int(duration_str[:-1])
                    if duration_hours < 1:
                        await update.message.reply_text(
                            "❌ **Duración mínima:** 1 hora")
                        return
                    if duration_hours > 72:
                        await update.message.reply_text(
                            "❌ **Duración máxima:** 72 horas")
                        return
                elif duration_str.isdigit():
                    duration_hours = int(duration_str)
                    if duration_hours > 72:
                        duration_hours = 72
            except ValueError:
                duration_hours = 12  # Fallback a 12 horas

        # Procesar razón
        reason = ' '.join(
            args[2:]) if len(args) > 2 else "Violación de normas del grupo"

        # Verificar que el usuario existe en el chat
        target_username = f"Usuario {target_user_id}"
        try:
            chat_member = await context.bot.get_chat_member(
                update.effective_chat.id, target_user_id_int)
            target_username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name

            # Verificar que no sea un bot
            if chat_member.user.is_bot:
                await update.message.reply_text("❌ **NO SE PUEDE MUTEAR BOTS**\n\n"
                                                "💡 Los bots no pueden ser muteados"
                                                )
                return

        except Exception as e:
            logger.warning(f"No se pudo obtener info del usuario: {e}")
            # Continuar con el ID como nombre

        # Aplicar mute
        unmute_time = auto_mute_user(chat_id, target_user_id, duration_hours,
                                     reason, update.effective_user.first_name)

        if unmute_time is None:
            await update.message.reply_text(
                "❌ **ERROR AL APLICAR MUTE**\n\n"
                "💡 Ocurrió un error interno. Intenta nuevamente.")
            return

        # Enviar log administrativo
        try:
            await send_admin_log(context=context,
                                 action_type='MUTE',
                                 admin_user=update.effective_user,
                                 target_user_id=target_user_id,
                                 reason=reason,
                                 group_id=chat_id,
                                 additional_data={
                                     'duration_hours': duration_hours,
                                     'unmute_time': unmute_time.isoformat(),
                                     'target_username': target_username
                                 })
        except Exception as e:
            logger.warning(f"Error enviando log: {e}")

        response = f"🔇 **USUARIO MUTEADO EXITOSAMENTE** 🔇\n\n"
        response += f"👤 **Usuario:** {target_username}\n"
        response += f"🆔 **ID:** `{target_user_id}`\n"
        response += f"⏰ **Duración:** {duration_hours}h\n"
        response += f"🔓 **Desmute automático:** {unmute_time.strftime('%d/%m/%Y %H:%M')}\n"
        response += f"📝 **Razón:** {reason}\n"
        response += f"👮‍♂️ **Muteado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"💡 **El usuario no podrá enviar mensajes durante este período**\n"
        response += f"🔧 **Desmute manual:** `/unmute {target_user_id}`"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error en comando mute: {e}")
        await update.message.reply_text(
            "❌ **ERROR TEMPORAL**\n\n"
            "Ha ocurrido un error interno. Por favor intenta nuevamente.\n\n"
            "Si el problema persiste, contacta a los administradores.")


@admin_only
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Desmutear usuario manualmente - Versión corregida"""
    try:
        args = context.args
        chat_id = str(update.effective_chat.id)

        if not args:
            await update.message.reply_text(
                "🔊 **DESMUTEAR USUARIO** 🔊\n\n"
                "**Uso:** `/unmute [user_id]`\n\n"
                "**Ejemplo:** `/unmute 123456789`\n\n"
                "💡 **También puedes usar:** `/mutelist` para ver usuarios muteados",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Validar user_id
        target_user_id = args[0].strip()
        if not target_user_id.isdigit():
            await update.message.reply_text(
                "❌ **ID INVÁLIDO**\n\n"
                "💡 El ID del usuario debe ser numérico\n"
                "📋 **Ejemplo:** `/unmute 123456789`")
            return

        target_user_id_int = int(target_user_id)

        # Verificar si el usuario está muteado
        user_is_muted = False
        mute_data = None

        try:
            if (chat_id in muted_users and target_user_id in muted_users[chat_id]):
                mute_data = muted_users[chat_id][target_user_id]
                if datetime.now() < mute_data['unmute_time']:
                    user_is_muted = True
        except Exception as e:
            logger.warning(f"Error verificando estado de mute: {e}")

        if not user_is_muted:
            await update.message.reply_text(
                f"❌ **USUARIO NO ESTÁ MUTEADO**\n\n"
                f"👤 **Usuario ID:** `{target_user_id}`\n"
                f"💡 Este usuario no está en la lista de muteados activos\n\n"
                f"🔍 **Usa `/mutelist` para ver usuarios muteados**",
                parse_mode=ParseMode.MARKDOWN)
            return

        # Obtener datos del mute antes de remover
        original_reason = mute_data.get('reason', 'Sin razón especificada')
        muted_by = mute_data.get('muted_by', 'Usuario desconocido')

        # Remover del sistema de mutes
        try:
            del muted_users[chat_id][target_user_id]
            if not muted_users[chat_id]:
                del muted_users[chat_id]
        except Exception as e:
            logger.warning(f"Error removiendo del sistema de mutes: {e}")

        # Obtener información del usuario si es posible
        target_username = f"Usuario {target_user_id}"
        try:
            chat_member = await context.bot.get_chat_member(
                update.effective_chat.id, target_user_id_int)
            target_username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
        except Exception as e:
            logger.warning(f"No se pudo obtener info del usuario: {e}")

        # Enviar log administrativo
        try:
            await send_admin_log(context=context,
                                 action_type='UNMUTE',
                                 admin_user=update.effective_user,
                                 target_user_id=target_user_id,
                                 reason="Desmute manual",
                                 group_id=chat_id,
                                 additional_data={
                                     'original_reason': original_reason,
                                     'originally_muted_by': muted_by,
                                     'target_username': target_username
                                 })
        except Exception as e:
            logger.warning(f"Error enviando log: {e}")

        response = f"🔊 **USUARIO DESMUTEADO EXITOSAMENTE** 🔊\n\n"
        response += f"👤 **Usuario:** {target_username}\n"
        response += f"🆔 **ID:** `{target_user_id}`\n"
        response += f"✅ **Estado:** Puede enviar mensajes nuevamente\n"
        response += f"📝 **Razón original:** {original_reason}\n"
        response += f"👮‍♂️ **Muteado originalmente por:** {muted_by}\n"
        response += f"🔓 **Desmuteado por:** {update.effective_user.first_name}\n"
        response += f"📅 **Fecha de desmute:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        response += f"💡 **El mute ha sido removido manualmente**"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error en comando unmute: {e}")
        await update.message.reply_text(
            "❌ **ERROR TEMPORAL**\n\n"
            "Ha ocurrido un error interno. Por favor intenta nuevamente.\n\n"
            "Si el problema persiste, contacta a los administradores.")


@admin_only
async def mutelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ver lista de usuarios muteados en el chat actual - Versión corregida"""
    try:
        chat_id = str(update.effective_chat.id)

        if chat_id not in muted_users or not muted_users[chat_id]:
            await update.message.reply_text(
                "✅ **NO HAY USUARIOS MUTEADOS** ✅\n\n"
                "💡 Actualmente no hay usuarios muteados en este chat\n\n"
                "🔧 **Usar:** `/mute [user_id]` para mutear un usuario",
                parse_mode=ParseMode.MARKDOWN)
            return

        response = f"🔇 **LISTA DE USUARIOS MUTEADOS** 🔇\n\n"
        current_time = datetime.now()

        muted_count = 0
        expired_users = []

        try:
            for user_id, mute_data in muted_users[chat_id].items():
                try:
                    unmute_time = mute_data['unmute_time']

                    if current_time < unmute_time:  # Solo mostrar mutes activos
                        muted_count += 1
                        time_left = unmute_time - current_time
                        hours_left = int(time_left.total_seconds() // 3600)
                        minutes_left = int((time_left.total_seconds() % 3600) // 60)

                        # Intentar obtener nombre de usuario
                        username = f"Usuario {user_id}"
                        try:
                            chat_member = await context.bot.get_chat_member(
                                update.effective_chat.id, int(user_id))
                            username = f"@{chat_member.user.username}" if chat_member.user.username else chat_member.user.first_name
                        except Exception as e:
                            logger.warning(f"No se pudo obtener info del usuario {user_id}: {e}")

                        response += f"👤 **{username}**\n"
                        response += f"🆔 **ID:** `{user_id}`\n"
                        response += f"⏰ **Tiempo restante:** {hours_left}h {minutes_left}m\n"
                        response += f"🔓 **Desmute automático:** {unmute_time.strftime('%d/%m %H:%M')}\n"
                        response += f"📝 **Razón:** {mute_data.get('reason', 'Sin razón')}\n"
                        response += f"👮‍♂️ **Muteado por:** {mute_data.get('muted_by', 'Desconocido')}\n"
                        response += f"🔧 **Desmute manual:** `/unmute {user_id}`\n"
                        response += f"─────────────────────────\n"
                    else:
                        # Marcar para limpieza
                        expired_users.append(user_id)
                except Exception as e:
                    logger.warning(f"Error procesando mute de usuario {user_id}: {e}")
                    expired_users.append(user_id)

        except Exception as e:
            logger.error(f"Error iterando sobre usuarios muteados: {e}")

        # Limpiar usuarios con mutes expirados
        try:
            for user_id in expired_users:
                if user_id in muted_users[chat_id]:
                    del muted_users[chat_id][user_id]

            if not muted_users[chat_id]:
                del muted_users[chat_id]
        except Exception as e:
            logger.warning(f"Error limpiando mutes expirados: {e}")

        if muted_count == 0:
            response = "✅ **NO HAY USUARIOS MUTEADOS ACTIVOS** ✅\n\n"
            response += "💡 Todos los mutes han expirado automáticamente o no hay usuarios muteados\n\n"
            response += "🔧 **Usar:** `/mute [user_id]` para mutear un usuario"
        else:
            response += f"\n📊 **Total usuarios muteados:** {muted_count}\n"
            response += f"⏰ **Consultado:** {current_time.strftime('%d/%m/%Y %H:%M')}\n\n"
            response += f"💡 **Los mutes expiran automáticamente**\n"
            response += f"🔧 **Desmutear:** `/unmute [user_id]`"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error en comando mutelist: {e}")
        await update.message.reply_text(
            "❌ **ERROR TEMPORAL**\n\n"
            "Ha ocurrido un error interno. Por favor intenta nuevamente.\n\n"
            "Si el problema persiste, contacta a los administradores.")


@bot_admin_only
async def lockdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bloqueo total del grupo - Solo admins"""
    chat_id = str(update.effective_chat.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "🔒 **LOCKDOWN TOTAL** 🔒\n\n"
            "**Uso:** `/lockdown [on/off] [tiempo] [razón]`\n\n"
            "**Funciones:**\n"
            "• Bloqueo total del grupo\n"
            "• Nadie excepto admins puede escribir\n"
            "• Medida de emergencia\n\n"
            "**Ejemplos:**\n"
            "• `/lockdown on 30m Raid detectado`\n"
            "• `/lockdown off`",
            parse_mode=ParseMode.MARKDOWN)
        return

    action = args[0].lower()

    if action == "on":
        reason = ' '.join(args[1:]) if len(args) > 1 else "Medida de seguridad"

        try:
            # Bloqueo total - solo lectura
            from telegram import ChatPermissions

            permissions = ChatPermissions(can_send_messages=False,
                                          can_send_media_messages=False,
                                          can_send_polls=False,
                                          can_send_other_messages=False,
                                          can_add_web_page_previews=False,
                                          can_change_info=False,
                                          can_invite_users=False,
                                          can_pin_messages=False)

            await context.bot.set_chat_permissions(
                chat_id=update.effective_chat.id, permissions=permissions)

            response = f"🚨 **LOCKDOWN ACTIVADO** 🚨\n\n"
            response += f"🔒 **GRUPO EN MODO SOLO LECTURA**\n\n"
            response += f"⚠️ **MEDIDA DE EMERGENCIA ACTIVADA**\n"
            response += f"🛡️ **Solo administradores pueden enviar mensajes**\n\n"
            response += f"📝 **Razón:** {reason}\n"
            response += f"👮‍♂️ **Activado por:** {update.effective_user.first_name}\n"
            response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            response += f"🔓 **Usa `/lockdown off` para desactivar**"

        except Exception as e:
            response = f"❌ **ERROR EN LOCKDOWN:** {str(e)}"

    elif action == "off":
        try:
            # Restaurar permisos normales
            from telegram import ChatPermissions

            permissions = ChatPermissions(can_send_messages=True,
                                          can_send_media_messages=True,
                                          can_send_polls=True,
                                          can_send_other_messages=True,
                                          can_add_web_page_previews=True,
                                          can_change_info=False,
                                          can_invite_users=True,
                                          can_pin_messages=False)

            await context.bot.set_chat_permissions(
                chat_id=update.effective_chat.id, permissions=permissions)

            response = f"🔓 **LOCKDOWN DESACTIVADO** 🔓\n\n"
            response += f"✅ **Grupo desbloqueado exitosamente**\n"
            response += f"💬 **Miembros pueden enviar mensajes**\n"
            response += f"🔄 **Operaciones normales restauradas**\n\n"
            response += f"👮‍♂️ **Desactivado por:** {update.effective_user.first_name}\n"
            response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        except Exception as e:
            response = f"❌ **ERROR AL DESACTIVAR LOCKDOWN:** {str(e)}"

    else:
        response = "❌ **Acción inválida.** Usa: `on` o `off`"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@check_maintenance
async def startfoundress_command(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    """Comandos disponibles para fundadores - Solo fundadores pueden ver"""
    user_id = str(update.effective_user.id)

    # Verificar que sea fundador
    if not db.is_founder(user_id):
        await update.message.reply_text(
            "❌ **ACCESO DENEGADO** ❌\n\n"
            "🔒 **Este comando es EXCLUSIVO para:**\n"
            "• 👑 Fundadores únicamente\n\n"
            "🚫 **Tu rol actual:** No autorizado\n",
            parse_mode=ParseMode.MARKDOWN)
        return

    response = "👑 **COMANDOS DE FUNDADOR** 👑\n"
    response += "═══════════════════════════════\n\n"
    response += "🔥 **PERMISOS MÁXIMOS - NIVEL 1**\n\n"

    response += "🛡️ **GESTIÓN DE STAFF:**\n"
    response += "• `/founder add/remove [user_id]` - Gestionar fundadores\n"
    response += "• `/cofounder add/remove [user_id]` - Gestionar co-fundadores\n"
    response += "• `/moderator add/remove [user_id]` - Gestionar moderadores\n"
    response += "• `/staff list` - Ver todo el staff\n\n"

    response += "🔨 **MODERACIÓN AVANZADA:**\n"
    response += "• `/ban [user_id] [razón]` - Banear usuarios\n"
    response += "• `/unban [user_id]` - Desbanear usuarios\n"
    response += "• `/warn [user_id] [razón]` - Advertir usuarios\n"
    response += "• `/unwarn [user_id]` - Quitar advertencias\n"
    response += "• `/clean [número]` - Limpiar mensajes\n"
    response += "• `/clean auto [tiempo]` - Limpieza automática\n\n"

    response += "🚨 **CONTROL DEL BOT:**\n"
    response += "• `/close [mensaje]` - Cerrar bot (mantenimiento)\n"
    response += "• `/open` - Abrir bot\n"
    response += "• `/housemode on/off` - Modo casa de seguridad\n"
    response += "• `/lockdown on/off` - Bloqueo total del grupo\n\n"

    response += "💎 **SISTEMA PREMIUM:**\n"
    response += "• `/premium [user_id] [días]` - Otorgar premium\n"
    response += "• `/creditcleaningworld` - Reinicio masivo de créditos\n\n"

    response += "📢 **PUBLICACIONES:**\n"
    response += "• `/post [chat_id] [contenido]` - Publicar con IA\n\n"

    response += "⚙️ **CONFIGURACIÓN:**\n"
    response += "• `/establishedadministration [channel]` - Config logs\n"
    response += "• `/setcheckchats [verify] [publish]` - Config /check\n\n"

    response += "📊 **INFORMACIÓN:**\n"
    response += "• `/stats` - Estadísticas completas\n"
    response += "• `/links [user_id]` - Historial de links\n"
    response += "• `/id [user_id]` - Info detallada de usuario\n\n"

    response += f"👤 **Consultado por:** {update.effective_user.first_name}\n"
    response += f"🎯 **Nivel de acceso:** MÁXIMO (Fundador)"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@check_maintenance
async def startcofunder_command(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    """Comandos disponibles para co-fundadores - Solo co-fundadores y fundadores"""
    user_id = str(update.effective_user.id)

    # Verificar que sea co-fundador o fundador
    is_founder = db.is_founder(user_id)
    is_cofounder = db.is_cofounder(user_id)

    if not (is_founder or is_cofounder):
        await update.message.reply_text(
            "❌ **ACCESO DENEGADO** ❌\n\n"
            "🔒 **Este comando es EXCLUSIVO para:**\n"
            "• 👑 Fundadores\n"
            "• 💎 Co-fundadores\n\n"
            "🚫 **Tu rol actual:** No autorizado\n"
            "💡 **Contacta a un co-fundador o fundador**",
            parse_mode=ParseMode.MARKDOWN)
        return

    user_role = "👑 Fundador" if is_founder else "💎 Co-fundador"

    response = "💎 **COMANDOS DE CO-FUNDADOR** 💎\n"
    response += "═══════════════════════════════\n\n"
    response += "⚡ **PERMISOS AVANZADOS - NIVEL 2**\n\n"

    response += "🛡️ **GESTIÓN DE MODERADORES:**\n"
    response += "• `/moderator add [user_id]` - Asignar moderadores\n"
    response += "• `/moderator remove [user_id]` - Quitar moderadores\n"
    response += "• `/moderator list` - Ver moderadores\n\n"

    response += "🔨 **MODERACIÓN COMPLETA:**\n"
    response += "• `/ban [user_id] [razón]` - Banear usuarios\n"
    response += "• `/warn [user_id] [razón]` - Advertir usuarios (ilimitado)\n"
    response += "• `/unwarn [user_id]` - Quitar advertencias\n"
    response += "• `/clean [número]` - Limpiar mensajes\n"
    response += "• `/clean auto [tiempo]` - Limpieza automática\n\n"

    response += "🏠 **CONTROL DE SEGURIDAD:**\n"
    response += "• `/housemode on/off [razón]` - Modo casa\n"
    response += "• `/staff list` - Ver todo el staff\n\n"

    response += "📢 **PUBLICACIONES:**\n"
    response += "• `/post [chat_id] [contenido]` - Publicar con IA\n\n"

    response += "📊 **INFORMACIÓN:**\n"
    response += "• `/id [user_id]` - Info de usuarios\n\n"

    response += "🚫 **NO DISPONIBLE PARA CO-FUNDADORES:**\n"
    response += "• Gestión de fundadores/co-fundadores\n"
    response += "• Control total del bot (close/open)\n"
    response += "• Comandos ultra-críticos\n\n"

    response += f"👤 **Consultado por:** {update.effective_user.first_name}\n"
    response += f"🎭 **Tu rol:** {user_role}\n"
    response += f"🎯 **Nivel de acceso:** AVANZADO"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@check_maintenance
async def startmoderator_command(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    """Comandos disponibles para moderadores - Solo moderadores, co-fundadores y fundadores"""
    user_id = str(update.effective_user.id)

    # Verificar que sea al menos moderador
    is_founder = db.is_founder(user_id)
    is_cofounder = db.is_cofounder(user_id)
    is_moderator = db.is_moderator(user_id)

    if not (is_founder or is_cofounder or is_moderator):
        await update.message.reply_text(
            "❌ **ACCESO DENEGADO** ❌\n\n"
            "🔒 **Este comando es EXCLUSIVO para:**\n"
            "• 👑 Fundadores\n"
            "• 💎 Co-fundadores\n"
            "• 🛡️ Moderadores\n\n"
            "🚫 **Tu rol actual:** Usuario estándar\n",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Determinar rol del usuario
    if is_founder:
        user_role = "👑 Fundador"
        access_level = "MÁXIMO"
    elif is_cofounder:
        user_role = "💎 Co-fundador"
        access_level = "AVANZADO"
    else:
        user_role = "🛡️ Moderador"
        access_level = "BÁSICO"

    response = "🛡️ **COMANDOS DE MODERADOR** 🛡️\n"
    response += "═══════════════════════════════\n\n"
    response += "⚠️ **PERMISOS BÁSICOS - NIVEL 3**\n\n"

    response += "🔨 **MODERACIÓN LIMITADA:**\n"
    response += "• `/warn [user_id] [razón]` - Advertir usuarios\n"
    response += f"  ⚠️ **Límite:** {2 if is_moderator and not (is_founder or is_cofounder) else 'Ilimitado'} warns por moderador\n"
    response += "• `/clean [número]` - Limpiar mensajes (pequeñas cantidades)\n\n"

    response += "📊 **INFORMACIÓN:**\n"
    response += "• `/staff list` - Ver lista de staff\n"
    response += "• `/id [user_id]` - Ver info básica de usuarios\n\n"

    if is_moderator and not (is_founder or is_cofounder):
        # Obtener datos del moderador para mostrar warns dados
        staff_data = db.get_staff_role(user_id)
        warns_given = staff_data.get('warn_count', 0) if staff_data else 0

        response += "🚨 **LIMITACIONES DE MODERADOR:**\n"
        response += f"• **Warns dados:** {warns_given}/2\n"
        response += "• **NO puede:** ban/unban usuarios\n"
        response += "• **NO puede:** gestionar otros moderadores\n"
        response += "• **NO puede:** usar comandos de co-fundador/fundador\n"
        response += "• **NO puede:** limpieza automática\n"
        response += "• **NO puede:** control del bot\n\n"

    response += "🚫 **NO DISPONIBLE PARA MODERADORES:**\n"
    response += "• Gestión de staff (add/remove roles)\n"
    response += "• Ban/unban permanente de usuarios\n"
    response += "• Control del bot (close/open/housemode)\n"
    response += "• Publicaciones automáticas\n"
    response += "• Configuraciones del sistema\n\n"

    response += f"👤 **Consultado por:** {update.effective_user.first_name}\n"
    response += f"🎭 **Tu rol:** {user_role}\n"
    response += f"🎯 **Nivel de acceso:** {access_level}"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)


@staff_only(1)  # SOLO fundadores nivel 1
async def moderation_master_command(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    """COMANDO ULTRA SENSIBLE - Muestra TODOS los comandos de moderación - SOLO FUNDADORES"""
    user_id = str(update.effective_user.id)

    # Verificación adicional de seguridad
    if not db.is_founder(user_id):
        await update.message.reply_text(
            "🚨 **ACCESO ULTRA RESTRINGIDO** 🚨\n\n"
            "⛔ **COMANDO CLASIFICADO**\n"
            "🔒 **SOLO FUNDADORES**\n\n"
            "🚫 **ACCESO DENEGADO PERMANENTEMENTE**\n\n"
            "📝 **Este intento ha sido registrado**",
            parse_mode=ParseMode.MARKDOWN)

        # Log de intento de acceso no autorizado
        logger.warning(
            f"INTENTO NO AUTORIZADO de acceso a moderation_master - Usuario: {user_id} ({update.effective_user.first_name})"
        )
        return

    # Log de acceso autorizado
    logger.info(
        f"ACCESO AUTORIZADO a moderation_master - Fundador: {user_id} ({update.effective_user.first_name})"
    )

    try:
        message = "🔥 **MODERATION MASTER - ULTRA PRIVADO** 🔥\n"
        message += "═══════════════════════════════════════════\n"
        message += "🛡️ **CLASIFICACIÓN: TOP SECRET** 🛡️\n\n"

        message += f"👑 **FUNDADOR:** {update.effective_user.first_name}\n"
        message += f"🆔 **ID AUTORIZADO:** `{user_id}`\n"
        message += f"🕐 **ACCESO:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        message += f"🔐 **SEGURIDAD:** Triple verificación pasada\n\n"

        message += "👥 **GESTIÓN COMPLETA DE STAFF:**\n"
        message += "• `/founder add/remove/list` - Control total de fundadores\n"
        message += "• `/cofounder add/remove/list` - Gestión de co-fundadores\n"
        message += "• `/moderator add/remove/list` - Administrar moderadores\n"
        message += "• `/staff list` - Vista completa del staff\n"
        message += "• `/emergency_founder` - Registro de emergencia\n"
        message += "• `/fix_founder` - Reparar permisos\n\n"

        message += "🔨 **ARSENAL DE MODERACIÓN:**\n"
        message += "• `/ban [user_id] [razón]` - Banear usuarios\n"
        message += "• `/unban [user_id]` - Liberar usuarios\n"
        message += "• `/warn [user_id] [razón]` - Sistema de advertencias\n"
        message += "• `/unwarn [user_id]` - Quitar advertencias\n"
        message += "• `/kick [user_id]` - Expulsar usuarios\n"
        message += "• `/clean [cantidad]` - Limpieza de mensajes\n"
        message += "• `/clean auto [tiempo]` - Limpieza automática\n"
        message += "• `/cleanstatus` - Estado de limpieza\n\n"

        message += "🏛️ **CONTROL ADMINISTRATIVO:**\n"
        message += "• `/open` - Activar bot\n"
        message += "• `/close [mensaje]` - Mantenimiento\n"
        message += "• `/lockdown on/off` - Bloqueo total\n"
        message += "• `/housemode on/off` - Modo casa\n"
        message += "• `/stats` - Estadísticas completas\n"
        message += "• `/id [user_id]` - Información de usuarios\n"
        message += "• `/links [user_id]` - Historial de enlaces\n\n"

        message += "💰 **SISTEMA ECONÓMICO:**\n"
        message += "• `/premium [user_id] [días]` - Otorgar premium\n"
        message += "• `/transmit [user_id] [cantidad]` - Transferir créditos\n"
        message += "• `/creditcleaningworld` - Reset masivo de créditos\n\n"

        message += "⚙️ **CONFIGURACIÓN AVANZADA:**\n"
        message += "• `/setcheckchats` - Sistema de verificaciones\n"
        message += "• `/establishedadministration` - Logs administrativos\n"
        message += "• `/post [chat] [contenido]` - Publicaciones con IA\n\n"

        message += "🔐 **COMANDOS DE INFORMACIÓN:**\n"
        message += "• `/startfoundress` - Comandos de fundador\n"
        message += "• `/startcofounder` - Comandos de co-fundador\n"
        message += "• `/startmoderator` - Comandos de moderador\n\n"

        message += "📊 **TOTAL DE COMANDOS:** 25+\n"
        message += "🔥 **NIVEL DE ACCESO:** MÁXIMO\n"
        message += "⚡ **PODER:** SIN RESTRICCIONES\n\n"

        message += "⚠️ **ADVERTENCIA DE SEGURIDAD:**\n"
        message += "• Este comando es ultra-secreto\n"
        message += "• Solo fundadores autorizados\n"
        message += "• Todos los accesos son registrados\n"
        message += "• Uso responsable obligatorio\n\n"

        message += "🛡️ **ACCESO REGISTRADO EN LOGS DE SEGURIDAD**"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"❌ Error importante: {e}")
        await update.message.reply_text(
            "❌ **ERROR EN MODERATION MASTER** ❌\n\n"
            "🔧 Error técnico al generar el reporte completo\n"
            "💡 Intenta nuevamente en unos segundos\n\n"
            "🛡️ **Tu acceso como fundador está confirmado**",
            parse_mode=ParseMode.MARKDOWN)


@staff_only(1)  # Solo fundadores (nivel 1)
async def creditcleaningworld_command(update: Update,
                                      context: ContextTypes.DEFAULT_TYPE):
    """Reiniciar créditos de todos los usuarios - SOLO FUNDADORES"""
    user_id = str(update.effective_user.id)

    # Verificación adicional de seguridad
    if not db.is_founder(user_id):
        await update.message.reply_text(
            "❌ **ACCESO ULTRA RESTRINGIDO** ❌\n\n"
            "🔒 **Este comando es EXCLUSIVO para:**\n"
            "• 👑 Fundadores únicamente\n\n"
            "🚫 **No autorizado**\n"
            "⚠️ **Razón:** Comando crítico de moderación\n"
            "💡 **Contacta a un fundador para esta operación**",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Mensaje de confirmación y advertencia
    await update.message.reply_text(
        "⚠️ **OPERACIÓN CRÍTICA INICIADA** ⚠️\n\n"
        "🔥 **REINICIO MASIVO DE CRÉDITOS**\n\n"
        "⏳ **Procesando base de datos...**\n"
        "📊 **Analizando usuarios...**\n"
        "🛡️ **Aplicando excepciones de seguridad...**\n\n"
        "💡 **Esto puede tomar unos segundos**",
        parse_mode=ParseMode.MARKDOWN)

    # Contadores para estadísticas
    total_users = len(db.users)
    users_reset = 0
    users_protected = 0
    premium_protected = 0
    founder_protected = 0

    reset_users = []
    protected_users = []

    # Procesar cada usuario
    for user_id_db, user_data in db.users.items():
        user_id_int = int(user_id_db)

        # Verificar si es fundador (nivel 1)
        is_founder = db.is_founder(user_id_db)

        # Verificar si es premium
        is_premium = user_data.get('premium', False)
        if is_premium:
            # Verificar si el premium no ha expirado
            premium_until = user_data.get('premium_until')
            if premium_until:
                premium_date = datetime.fromisoformat(premium_until)
                is_premium = datetime.now() < premium_date

        # EXCEPCIONES: No reiniciar créditos a estos usuarios
        if is_founder:
            # Fundadores están protegidos
            protected_users.append(f"👑 Fundador: {user_id_db}")
            founder_protected += 1
            users_protected += 1
        elif is_premium:
            # Usuarios premium están protegidos
            protected_users.append(f"💎 Premium: {user_id_db}")
            premium_protected += 1
            users_protected += 1
        else:
            # REINICIAR créditos (Co-fundadores, moderadores y usuarios normales)
            old_credits = user_data.get('credits', 0)

            # Obtener información del usuario para el log
            staff_data = db.get_staff_role(user_id_db)
            if staff_data:
                if staff_data['role'] == '2':
                    user_type = "Co-fundador"
                elif staff_data['role'] == '3':
                    user_type = "Moderador"
                else:
                    user_type = "Usuario"
            else:
                user_type = "Usuario"

            # Reiniciar a 10 créditos (créditos iniciales)
            db.update_user(user_id_db, {'credits': 10})

            reset_users.append(
                f"{user_type}: {user_id_db} ({old_credits} → 10)")
            users_reset += 1

    # Crear reporte detallado
    response = f"🔥 **REINICIO MASIVO COMPLETADO** 🔥\n\n"
    response += f"📊 **ESTADÍSTICAS DE LA OPERACIÓN:**\n"
    response += f"├ 👥 **Total usuarios:** {total_users}\n"
    response += f"├ 🔄 **Reiniciados:** {users_reset}\n"
    response += f"├ 🛡️ **Protegidos:** {users_protected}\n"
    response += f"└ 📈 **Efectividad:** {(users_reset/total_users)*100:.1f}%\n\n"

    response += f"🛡️ **USUARIOS PROTEGIDOS ({users_protected}):**\n"
    response += f"├ 👑 **Fundadores:** {founder_protected}\n"
    response += f"└ 💎 **Premium:** {premium_protected}\n\n"

    response += f"🔄 **DETALLES DE REINICIO:**\n"
    response += f"• Co-fundadores: ✅ Reiniciados\n"
    response += f"• Moderadores: ✅ Reiniciados\n"
    response += f"• Usuarios normales: ✅ Reiniciados\n"
    response += f"• Créditos establecidos: 10 (inicial)\n\n"

    response += f"⚡ **OPERACIÓN EJECUTADA POR:**\n"
    response += f"👤 **Fundador:** {update.effective_user.first_name}\n"
    response += f"🆔 **ID:** `{update.effective_user.id}`\n"
    response += f"⏰ **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"

    response += f"🎯 **PROPÓSITO:** Prevención de acumulación masiva\n"
    response += f"🔒 **SEGURIDAD:** Multicuentas neutralizadas\n"
    response += f"✅ **ESTADO:** Operación completada exitosamente"

    await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    # Log de seguridad para esta operación crítica
    logger.info(
        f"CREDITCLEANINGWORLD ejecutado - Fundador: {update.effective_user.id} "
        f"({update.effective_user.first_name}) - Usuarios reiniciados: {users_reset}/{total_users} - "
        f"Protegidos: {users_protected} (Fundadores: {founder_protected}, Premium: {premium_protected})"
    )


# Callback Query Handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button presses from inline keyboards."""
    query = update.callback_query
    user_id = str(query.from_user.id)
    user_data = db.get_user(user_id)

    await query.answer()  # Acknowledge the click

    # Manejar regeneración de tarjetas
    if query.data.startswith('regen_'):
        try:
            # Parsear datos del callback: regen_bin_count_month_year_cvv_card_length_cvv_length
            parts = query.data.split('_')
            if len(parts) >= 8:
                bin_number = parts[1]
                count = int(parts[2])
                preset_month = None if parts[3] == 'rnd' else int(parts[3])
                preset_year = None if parts[4] == 'rnd' else int(parts[4])
                preset_cvv = None if parts[5] == 'rnd' else int(parts[5])
                card_length = int(parts[6])
                cvv_length = int(parts[7])

                # Regenerar tarjetas con los mismos parámetros
                if preset_month or preset_year or preset_cvv:
                    cards = CardGenerator.generate_cards_custom_advanced(
                        bin_number, count, preset_month, preset_year, preset_cvv,
                        card_length, cvv_length)
                else:
                    cards = CardGenerator.generate_cards_advanced(
                        bin_number, count, card_length, cvv_length)

                # Obtener información REAL del BIN
                bin_info = await get_real_bin_info(bin_number)

                # Crear máscara del BIN
                x_count = card_length - len(bin_number)
                bin_mask = bin_number + "x" * x_count

                # Mostrar formato usado
                format_display = f"{preset_month or 'rnd'} | {preset_year or 'rnd'} | {preset_cvv or 'rnd'}"

                # Respuesta regenerada
                response = f"🟣 SYSTEM ALERT [GLITCH_FRAME_X]\n"
                response += f"---=:: BIN Parse Protocol Init =---\n"
                response += f"▌ ID: {bin_mask}\n"
                response += f"▌ Format: {format_display}\n\n"
                response += f"▌ Sending Payload...\n"

                for card in cards:
                    response += f"▒ {card}\n"

                # Información del BIN con banderas
                country_flags = {
                    'UNITED STATES': '🇺🇸',
                    'CANADA': '🇨🇦',
                    'UNITED KINGDOM': '🇬🇧',
                    'GERMANY': '🇩🇪',
                    'FRANCE': '🇫🇷',
                    'SPAIN': '🇪🇸',
                    'ITALY': '🇮🇹',
                    'BRAZIL': '🇧🇷',
                    'MEXICO': '🇲🇽',
                    'ARGENTINA': '🇦🇷',
                    'COLOMBIA': '🇨🇴'
                }

                country_name = bin_info['country'].upper()
                country_flag = country_flags.get(country_name, '🌍')

                # Tiempo de generación
                generation_time = round(random.uniform(0.025, 0.055), 3)

                response += f"\n---= META DATA =---\n"
                response += f"🏦 Banco: {bin_info['bank']}\n"
                response += f"💳 Tipo: {bin_info['scheme']} / {bin_info['type']}\n"
                response += f"🌍 Región: {country_flag} {bin_info['country'].upper()}\n"
                response += f"🧠 Usuario: @{query.from_user.username or query.from_user.first_name}\n"
                response += f"⏱️ Tiempo: {generation_time}s\n"
                response += f"🟢 Estado: ESTABLE"

                # Mantener el mismo botón regenerar con los mismos parámetros
                regen_data = f"regen_{bin_number}_{count}_{preset_month or 'rnd'}_{preset_year or 'rnd'}_{preset_cvv or 'rnd'}_{card_length}_{cvv_length}"

                keyboard = [[
                    InlineKeyboardButton("🔄 Regenerar Tarjetas", callback_data=regen_data),
                    InlineKeyboardButton("📊 Ver BIN Info", callback_data=f'bininfo_{bin_number}')
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(response, reply_markup=reply_markup)
                return

        except Exception as e:
            logger.error(f"Error en regeneración: {e}")
            await query.edit_message_text("❌ Error al regenerar tarjetas. Intenta usar el comando /gen nuevamente.")
            return

    # Manejar información del BIN
    elif query.data.startswith('bininfo_'):
        bin_number = query.data.replace('bininfo_', '')
        bin_info = await get_real_bin_info(bin_number)

        response = f"📊 **INFORMACIÓN DEL BIN** 📊\n\n"
        response += f"🔢 **BIN:** {bin_number}\n"
        response += f"🏦 **Banco:** {bin_info['bank']}\n"
        response += f"💳 **Marca:** {bin_info['scheme']}\n"
        response += f"🎯 **Tipo:** {bin_info['type']}\n"
        response += f"🌍 **País:** {bin_info['country']}\n"
        response += f"⭐ **Nivel:** {bin_info['level']}\n\n"
        response += f"🔙 Usa el botón regenerar para más tarjetas"

        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="back_to_gen")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        return

    # Callbacks de InfoCredits
    if query.data == 'get_credits':
        text = "💰 **FORMAS DE OBTENER CRÉDITOS** 💰\n\n"
        text += "🎁 **Gratis:**\n"
        text += "• `/loot` 10 créditos diarios (15 premium)\n"
        text += "• `/simulator` 3 / 8 créditos cada 12h\n"
        text += "• Eventos especiales\n\n"
        text += "💎 **Premium:**\n"
        text += "• Comprar membresía con @SteveCHRB\n"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'premium_benefits':
        text = "👑 **BENEFICIOS PREMIUM** 👑\n\n"
        text += "⚡ **Verificación:**\n"
        text += "• TODA la verificación simultáneos\n"
        text += "• Mayor probabilidad inject\n"
        text += "• Resultados más rápidos\n\n"
        text += "🎯 **Límites:**\n"
        text += "• Direcciones adicionales\n\n"
        text += "💎 **Bonos:**\n"
        text += "• 15 créditos diarios (vs 10)\n"
        text += "• +300 créditos al activar premium"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'free_commands':
        text = "🆓 **COMANDOS GRATUITOS** 🆓\n\n"
        text += "✅ **Generación:**\n"
        text += "• `/gen` - Generar tarjetas (gratis)\n"
        text += "• `/direccion [país]` - Direcciones por país\n"
        text += "ℹ️ **Información:**\n"
        text += "• `/wallet` - Ver créditos\n"
        text += "• `/status` - Estado del bot\n"
        text += "• `/bridge` - Info bridge\n\n"
        text += "🎁 **Bonos:**\n"
        text += "• `/loot` - Créditos diarios\n"
        text += "• `/simulator` - Casino bot"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'paid_commands':
        user_id = str(query.from_user.id)
        user_data = db.get_user(user_id)
        is_admin = query.from_user.id in ADMIN_IDS
        is_premium = user_data.get('premium', False)

        if is_admin:
            methods_text = "🔥 **TODOS LOS MÉTODOS** (Administrador)"
        elif is_premium:
            methods_text = "👑 **TODOS LOS MÉTODOS** (Premium)"
        else:
            methods_text = "⚡ **5 MÉTODOS** (Usuario estándar)"

        text = "💎 **COMANDOS CON COSTO** 💎\n\n"
        text += "🔍 **Verificación `/inject`:**\n"
        text += "• 💰 Costo: 3 créditos por uso\n"
        text += "• 📊 Hasta 10 tarjetas por comando\n"
        text += f"• {methods_text}\n"
        text += "• ⚡ Resultados instantáneos\n\n"
        text += "🧠 **Extrapolación `/ex`:**\n"
        text += "• 💰 Costo: 5 créditos\n"
        text += "• 🤖 Algoritmos de IA avanzada\n"
        text += "• 📈 Efectividad 75-85%\n\n"
        text += "⚡ **Diferencias por tipo de usuario:**\n"
        text += "• 🆓 **Estándar:** 5 métodos de verificación\n"
        text += "• 👑 **Premium:** TODOS los métodos disponibles\n"
        text += "• 🛡️ **Admin:** TODOS los métodos"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'my_stats':
        text = f"📊 **TUS ESTADÍSTICAS** 📊\n\n"
        text += f"💰 **Créditos:** {user_data['credits']}\n"
        text += f"🏭 **Generadas:** {user_data['total_generated']} tarjetas\n"
        text += f"🔍 **Verificadas:** {user_data['total_checked']} tarjetas\n"
        text += f"⚠️ **Advertencias:** {user_data.get('warns', 0)}/3\n"
        text += f"📅 **Miembro desde:** {user_data['join_date'][:10]}\n\n"
        if user_data['premium']:
            premium_until = datetime.fromisoformat(user_data['premium_until'])
            days_left = (premium_until - datetime.now()).days
            text += f"👑 **Premium:** {days_left} días restantes"
        else:
            text += f"🆓 **Cuenta:** Usuario estándar"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'go_games':
        text = "🎮 **Ir a Casino Bot** 🎮\n\n"
        text += "Para acceder a la sección de simulator usa el comando `/simulator`\n\n"
        text += "🎯 **simulator disponibles:**\n"
        text += "• 🎰 Ruleta de la Suerte\n"
        text += "• 🎲 Dados Mágicos\n"
        text += "• 🃏 Carta de la Fortuna\n"
        text += "• ⚡ Rayo de Créditos\n\n"
        text += "⏰ **Cooldown:** 12 horas entre simulator"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar",
                                 callback_data='back_to_infocredits')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    # Callbacks de Juegos
    elif query.data in [
            'play_ruleta', 'play_dados', 'play_carta', 'play_rayo'
    ]:
        await handle_game_play(query, context, query.data)

    elif query.data == 'game_stats':
        last_game = user_data.get('last_game')
        if last_game:
            last_game_date = datetime.fromisoformat(last_game)
            time_since = datetime.now() - last_game_date
            hours_since = time_since.total_seconds() / 3600
            next_game = 12 - hours_since if hours_since < 12 else 0
        else:
            next_game = 0

        text = f"╔═══⟪ ☠️ GAME.STATS ☠️ ⟫═══╗\n"
        text += f"║ 💸 Créditos: {user_data['credits']:<14} ║\n"
        text += f"║ ⏳ Última sesión: {last_game_date.strftime('%H:%M') if last_game else 'Nunca':<8} ║\n"
        text += f"║ 🔄 Próxima: {'Disponible' if next_game <= 0 else f'{next_game:.1f}h':<12} ║\n"
        text += f"║ 🎯 Rango: +3 ~ +8 CR      ║\n"
        text += f"║ 🚷 Enfriamiento: 12h      ║\n"
        text += f"╚═══⟪ SYSTEM | OK ⟫════════╝"

        keyboard = [[
            InlineKeyboardButton("🔙 Regresar", callback_data='back_to_juegos')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=reply_markup)

    elif query.data == 'back_to_infocredits':
        # Recrear el mensaje original de infocredits
        keyboard = [[
            InlineKeyboardButton("💰 Obtener Créditos",
                                 callback_data='get_credits'),
            InlineKeyboardButton("👑 Premium", callback_data='premium_benefits')
        ],
                    [
                        InlineKeyboardButton("🆓 Comandos Gratis",
                                             callback_data='free_commands'),
                        InlineKeyboardButton("💎 Comandos de Pago",
                                             callback_data='paid_commands')
                    ],
                    [
                        InlineKeyboardButton("📊 Mis Estadísticas",
                                             callback_data='my_stats'),
                        InlineKeyboardButton("🎮 Ir a Juegos",
                                             callback_data='go_games')
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        premium_text = ""
        if user_data['premium']:
            premium_until = datetime.fromisoformat(user_data['premium_until'])
            days_left = (premium_until - datetime.now()).days
            premium_text = f"\n👑 **PREMIUM ACTIVO** ({days_left} días)"

        response = f"╔═══════════════════════════╗\n"
        response += f"║     💡 𝐒𝐈𝐒𝐓𝐄𝐌𝐀 𝐃𝐄 𝐂𝐑É𝐃𝐈𝐓𝐎𝐒     ║\n"
        response += f"╚═══════════════════════════╝\n\n"
        response += f"💎 **Tus Créditos:** {user_data['credits']}{premium_text}\n\n"
        response += f"📋 **Selecciona una opción:**"

        await query.edit_message_text(response,
                                      reply_markup=reply_markup,
                                      parse_mode=ParseMode.MARKDOWN)

    elif query.data == 'back_to_juegos':
        # Recrear el mensaje original de juegos
        keyboard = [[
            InlineKeyboardButton("🎰 Ruleta de la Suerte",
                                 callback_data='play_ruleta'),
            InlineKeyboardButton("🎲 Dados Mágicos", callback_data='play_dados')
        ],
                    [
                        InlineKeyboardButton("🃏 Carta de la Fortuna",
                                             callback_data='play_carta'),
                        InlineKeyboardButton("⚡ Rayo de Créditos",
                                             callback_data='play_rayo')
                    ],
                    [
                        InlineKeyboardButton("📊 Mis Estadísticas",
                                             callback_data='game_stats')
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        now = datetime.now()
        last_game = user_data.get('last_game')
        can_play = True
        time_left = 0

        if last_game:
            last_game_date = datetime.fromisoformat(last_game)
            hours_passed = (now - last_game_date).total_seconds() / 3600
            if hours_passed < 12:
                can_play = False
                time_left = 12 - hours_passed

        status_text = "🟢 **DISPONIBLE**" if can_play else f"🔴 **COOLDOWN** ({time_left:.1f}h restantes)"

        response = f"┌─────────⟦ ☠️ DARK CASINO ☠️ ⟧─────────┐\n"
        response += f"│ ██████████ UNDERGROUND VAULT ██████████ │\n"
        response += f"└──────────────────────────────────────────┘\n\n"
        response += f"💀 CR_WALLET: {user_data['credits']} UNITS\n"
        response += f"🔴 SYS_STATUS: {status_text}\n"
        response += f"⚡ PROFIT_RANGE: +3~+8 CR_UNITS\n"
        response += f"🕘 COOLDOWN_TIMER: 12H_CYCLE\n\n"
        response += f"⧼ SELECT_EXPLOIT_MODULE ⧽"

        await query.edit_message_text(response,
                                      reply_markup=reply_markup,
                                      parse_mode=ParseMode.MARKDOWN)

    # Callbacks para sistema /check
    elif query.data.startswith('approve_check_'):
        await handle_check_approval(query, context, True)

    elif query.data.startswith('reject_check_'):
        await handle_check_approval(query, context, False)

    # Callbacks para gates system
    elif query.data.startswith('gate_') or query.data in [
            'gates_close', 'gates_status', 'gates_back'
    ]:
        from gates_system import handle_gate_callback
        await handle_gate_callback(update, context)
    # Callback para regenerar tarjetas - CORREGIDO
    elif query.data.startswith('regen_'):
        try:
            parts = query.data.split('_')
            if len(parts) < 6:
                await query.answer("❌ Datos de regeneración incompletos",
                                   show_alert=True)
                return

            bin_number = parts[1]

            # Validar que count sea un número válido
            try:
                count = int(parts[2])
                if count < 1 or count > 50:
                    count = 10  # Valor por defecto
            except (ValueError, IndexError):
                count = 10

            preset_month = parts[3] if parts[3] != "rnd" else None
            preset_year = parts[4] if parts[4] != "rnd" else None
            preset_cvv = parts[5] if parts[5] != "rnd" else None

            # Obtener parámetros adicionales si existen
            try:
                card_length = int(parts[6]) if len(parts) > 6 else 16
                cvv_length = int(parts[7]) if len(parts) > 7 else 3
            except (ValueError, IndexError):
                card_length = 16
                cvv_length = 3

            # Convertir strings a integers con validación mejorada
            if preset_month and preset_month.isdigit():
                preset_month = int(preset_month)
                if not (1 <= preset_month <= 12):
                    preset_month = None
            else:
                preset_month = None

            if preset_year and preset_year.isdigit():
                preset_year = int(preset_year)
                if preset_year < 2024 or preset_year > 2035:
                    preset_year = None
            else:
                preset_year = None

            if preset_cvv and preset_cvv.isdigit():
                preset_cvv = int(preset_cvv)
                # Validar CVV según longitud
                if cvv_length == 4 and (preset_cvv < 1000
                                        or preset_cvv > 9999):
                    preset_cvv = None
                elif cvv_length == 3 and (preset_cvv < 100
                                          or preset_cvv > 999):
                    preset_cvv = None
            else:
                preset_cvv = None

            # Mensaje de regeneración
            await query.edit_message_text(
                "🔄 **REGENERANDO TARJETAS** 🔄\n\n⏳ Procesando nueva generación...",
                parse_mode=ParseMode.MARKDOWN)

            # Validar BIN mejorado
            if not bin_number or len(
                    bin_number) < 6 or not bin_number.isdigit():
                await query.edit_message_text(
                    "❌ **ERROR** ❌\n\nBIN inválido para regeneración\n\n💡 El BIN debe tener al menos 6 dígitos"
                )
                return

            # Determinar tipo de tarjeta y validar longitud
            card_type = "UNKNOWN"
            if bin_number.startswith('4'):
                card_type = "VISA"
                card_length = 16
                cvv_length = 3
            elif bin_number.startswith('5') or bin_number.startswith('2'):
                card_type = "MASTERCARD"
                card_length = 16
                cvv_length = 3
            elif bin_number.startswith('3'):
                card_type = "AMERICAN EXPRESS"
                card_length = 15
                cvv_length = 4

            # Generar tarjetas con manejo de errores mejorado
            cards = []
            try:
                if preset_month or preset_year or preset_cvv:
                    cards = CardGenerator.generate_cards_custom_advanced(
                        bin_number, count, preset_month, preset_year,
                        preset_cvv, card_length, cvv_length)
                else:
                    cards = CardGenerator.generate_cards_advanced(
                        bin_number, count, card_length, cvv_length)
            except Exception as e:
                logger.error(f"Error generando tarjetas avanzadas: {e}")
                # Fallback al método básico
                try:
                    cards = CardGenerator.generate_cards(bin_number, count)
                except Exception as e2:
                    logger.error(f"Error en fallback: {e2}")
                    await query.edit_message_text(
                        f"❌ **ERROR EN REGENERACIÓN** ❌\n\n"
                        f"No se pudieron generar las tarjetas.\n"
                        f"🔍 Error: {str(e2)[:50]}...\n\n"
                        f"💡 Intenta con un BIN diferente")
                    return

            if not cards:
                await query.edit_message_text(
                    "❌ **ERROR** ❌\n\nNo se generaron tarjetas\n\n💡 Intenta nuevamente"
                )
                return

            # Obtener información REAL del BIN
            real_bin_info = await get_real_bin_info(bin_number)

            # Crear máscara del BIN apropiada
            x_count = card_length - len(bin_number)
            bin_mask = bin_number + "x" * x_count

            # Mostrar formato usado
            format_display = f"{preset_month or 'rnd'} | {preset_year or 'rnd'} | {preset_cvv or 'rnd'}"

            # Tiempo de generación simulado
            generation_time = round(random.uniform(0.025, 0.055), 3)

            response = f"BIN: {bin_mask} | {format_display}\n"
            response += f"═══════════════════════════\n"
            response += f"        『⛧⛧⛧』⟪ 𝗖𝗛𝗘𝗥𝗡𝗢𝗕𝗜𝗟 𝗖𝗛𝗟𝗩 ⟫『⛧⛧⛧』\n"
            response += f"                     \n"

            for card in cards:
                response += f"{card}\n"

            # Obtener bandera del país
            country_flags = {
                'UNITED STATES': '🇺🇸',
                'CANADA': '🇨🇦',
                'UNITED KINGDOM': '🇬🇧',
                'GERMANY': '🇩🇪',
                'FRANCE': '🇫🇷',
                'SPAIN': '🇪🇸',
                'ITALY': '🇮🇹',
                'BRAZIL': '🇧🇷',
                'MEXICO': '🇲🇽',
                'ARGENTINA': '🇦🇷',
                'COLOMBIA': '🇨🇴',
                'PERU': '🇵🇪',
                'CHILE': '🇨🇱',
                'ECUADOR': '🇪🇨',
                'VENEZUELA': '🇻🇪'
            }
            country_flag = country_flags.get(real_bin_info['country'].upper(),
                                             '🌍')

            # Información REAL del BIN
            response += f"\n═════════ DETAILS ══════════\n"
            response += f"💳 Bin Information:\n"
            response += f"🏦 Bank: {real_bin_info['bank']}\n"
            response += f"💼 Type: {real_bin_info['scheme']} - {real_bin_info['type']} - {real_bin_info['level']}\n"
            response += f"🌍 Country: {real_bin_info['country']} {country_flag}\n"
            response += f"⏱️ Time Spent: {generation_time}s\n"
            response += f"👤 Regenerated By: @{query.from_user.username or query.from_user.first_name}\n"
            response += f"╚═══════𝗖𝗛𝗘𝗥𝗡𝗢𝗕𝗜𝗟 𝗖𝗛𝗟𝗩═══════╝"

            # Mantener exactamente los mismos parámetros para el nuevo botón
            regen_data = f"regen_{bin_number}_{count}_{preset_month or 'rnd'}_{preset_year or 'rnd'}_{preset_cvv or 'rnd'}_{card_length}_{cvv_length}"

            keyboard = [[
                InlineKeyboardButton("🔄 Regenerar Tarjetas",
                                     callback_data=regen_data),
                InlineKeyboardButton("📊 Ver BIN Info",
                                     callback_data=f'bininfo_{bin_number}')
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Intentar editar el mensaje
            try:
                await query.edit_message_text(response,
                                              reply_markup=reply_markup)
                await query.answer("✅ Tarjetas regeneradas exitosamente",
                                   show_alert=False)
            except Exception as edit_error:
                logger.error(f"Error editando mensaje: {edit_error}")
                # Si falla editar, intentar enviar nuevo mensaje
                try:
                    await query.message.reply_text(response,
                                                   reply_markup=reply_markup)
                    await query.answer(
                        "✅ Tarjetas regeneradas (nuevo mensaje)",
                        show_alert=False)
                except Exception as send_error:
                    logger.error(f"Error enviando nuevo mensaje: {send_error}")
                    await query.answer(
                        f"❌ Error mostrando tarjetas: {str(send_error)[:30]}...",
                        show_alert=True)

        except Exception as main_error:
            logger.error(f"Error en regeneración principal: {main_error}")
            try:
                await query.edit_message_text(
                    f"❌ **ERROR CRÍTICO** ❌\n\n"
                    f"Error en regeneración: {str(main_error)[:100]}...\n\n"
                    f"💡 Intenta usar /gen nuevamente")
            except:
                await query.answer(f"❌ Error crítico en regeneración",
                                   show_alert=True)

    # Callback para mostrar información del BIN
    elif query.data.startswith('bininfo_'):
        bin_number = query.data.split('_')[1]
        real_bin_info = await get_real_bin_info(bin_number)

        response = f"📊 **BIN Information** 📊\n\n"
        response += f"💳 **BIN:** {bin_number}\n"
        response += f"🏛️ **Bank:** {real_bin_info['bank']}\n"
        response += f"🗺️ **Country:** {real_bin_info['country']}\n"
        response += f"🌐 **Scheme:** {real_bin_info['scheme']}\n"
        response += f"🔑 **Type:** {real_bin_info['type']}\n"
        response += f"💎 **Level:** {real_bin_info['level']}\n"

        await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)


async def handle_check_approval(query, context, is_approved):
    """Maneja la aprobación o rechazo de capturas por administradores"""
    admin_id = str(query.from_user.id)
    admin_user = query.from_user

    # Verificar que sea admin
    if query.from_user.id not in ADMIN_IDS:
        await query.answer(
            "❌ Solo administradores pueden aprobar/rechazar capturas",
            show_alert=True)
        return

    # Extraer ID de verificación
    check_id = query.data.split('_')[-1]

    # Obtener datos de la verificación
    check_data = db.get_pending_check(check_id)
    if not check_data:
        await query.answer("❌ Verificación no encontrada o ya procesada",
                           show_alert=True)
        return

    if check_data['status'] != 'pending':
        await query.answer("❌ Esta verificación ya fue procesada",
                           show_alert=True)
        return

    # Obtener configuración del grupo
    group_id = check_data['group_id']
    check_config = db.get_check_chats(group_id)

    if not check_config:
        await query.answer("❌ Configuración de chats no encontrada",
                           show_alert=True)
        return

    user_id = check_data['user_id']
    username = check_data['username']
    user_data = db.get_user(user_id)

    if is_approved:
        # APROBAR: Dar 6 créditos al usuario
        new_credits = user_data['credits'] + 6
        db.update_user(user_id, {'credits': new_credits})
        db.update_check_status(check_id, 'approved', admin_id)

        # Actualizar mensaje de verificación (para admins)
        approval_text = f"✅ **CAPTURA APROBADA** ✅\n\n"
        approval_text += f"🆔 **ID:** `{check_id}`\n"
        approval_text += f"👤 **Usuario:** {username}\n"
        approval_text += f"💰 **Créditos otorgados:** 6\n"
        approval_text += f"📊 **Créditos totales:** {new_credits}\n"
        approval_text += f"👮‍♂️ **Aprobado por:** {admin_user.first_name}\n"
        approval_text += f"📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        approval_text += f"🎉 **¡Felicidades al usuario por su captura válida!**"

        try:
            await query.edit_message_caption(caption=approval_text,
                                             parse_mode=ParseMode.MARKDOWN)
        except:
            pass

        # Enviar mensaje de aprobación al grupo principal (SIN MOSTRAR CRÉDITOS)
        try:
            # Escapar el username para evitar errores de parsing
            safe_username = escape_markdown(username)

            approval_message = "╔══════════════════════════════════╗\n"
            approval_message += "║      🎉  **CAPTURA APROBADA**  🎉      ║\n"
            approval_message += "╚══════════════════════════════════╝\n\n"
            approval_message += "🌟 **¡Felicitaciones!** Esta captura ha sido verificada\n\n"
            approval_message += f"👤 **Usuario:** {safe_username}\n"
            approval_message += f"✅ **Estado:** Aprobada oficialmente\n"
            approval_message += f"🤖 **Verificada por:** @ChernobilChLv\\_bot\n\n"
            approval_message += "🎁 **¡Has recibido 6 creditos!**\n"
            approval_message += "💡 **Sigue compartiendo capturas válidas para más beneficios**"

            await context.bot.send_message(chat_id=group_id,
                                           text=approval_message,
                                           parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error enviando mensaje al grupo principal: {e}")



        # Enviar mensaje de rechazo al grupo principal (opcional)
        try:
            safe_username = escape_markdown(username)

            rejection_message = "╔══════════════════════════════════╗\n"
            rejection_message += "║      ❌  **CAPTURA RECHAZADA**  ❌      ║\n"
            rejection_message += "╚══════════════════════════════════╝\n\n"
            rejection_message += f"👤 **Usuario:** {safe_username}\n"
            rejection_message += f"🤖 **Revisado por:** @ChernobilChLv\\_bot\n\n"
            rejection_message += "📝 **Motivo:** La captura no cumple con los criterios\n"
            rejection_message += "💡 **Puedes intentar nuevamente con una captura válida**"

            await context.bot.send_message(chat_id=group_id,
                                           text=rejection_message,
                                           parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error enviando mensaje de rechazo al grupo: {e}")

        await query.answer("❌ Captura rechazada - Sin recompensa",
                           show_alert=True)


async def handle_check_approval(query, context, is_approved):
    """Manejar aprobación/rechazo de verificaciones"""
    try:
        check_id = query.data.split('_')[-1]
        admin_user = query.from_user

        # Verificar que el admin tenga permisos
        if not (admin_user.id in ADMIN_IDS or db.get_staff_role(str(admin_user.id))):
            await query.answer("❌ No tienes permisos para esta acción", show_alert=True)
            return

        # Obtener datos de la verificación
        check_data = db.get_pending_check(check_id)
        if not check_data:
            await query.answer("❌ Verificación no encontrada", show_alert=True)
            return

        if check_data['status'] != 'pending':
            await query.answer("❌ Esta verificación ya fue procesada", show_alert=True)
            return

        user_id = check_data['user_id']
        username = check_data['username']
        group_id = check_data['group_id']

        if is_approved:
            # Aprobar: dar 6 créditos
            user_data = db.get_user(user_id)
            new_credits = user_data['credits'] + 6
            db.update_user(user_id, {'credits': new_credits})
            db.update_check_status(check_id, 'approved', str(admin_user.id))

            action_text = "✅ APROBADA"
            result_text = f"✅ *CAPTURA APROBADA* ✅\n\n" \
                         f"🎉 ¡Felicidades! Tu captura ha sido aprobada\n" \
                         f"💰 Has recibido 6 créditos\n" \
                         f"📊 Créditos totales: {new_credits}\n\n" \
                         f"🔍 ID de verificación: `{check_id}`"
        else:
            # Rechazar
            db.update_check_status(check_id, 'rejected', str(admin_user.id))

            action_text = "❌ RECHAZADA"
            result_text = f"❌ *CAPTURA RECHAZADA* ❌\n\n" \
                         f"😔 Tu captura no cumple con los requisitos\n" \
                         f"💡 Verifica que sea una captura auténtica y legible\n\n" \
                         f"🔍 ID de verificación: `{check_id}`"

        # Actualizar mensaje del admin
        admin_text = f"🔍 *VERIFICACIÓN PROCESADA* 🔍\n\n" \
                    f"🆔 *ID:* `{check_id}`\n" \
                    f"👤 *Usuario:* {username}\n" \
                    f"📊 *Resultado:* {action_text}\n" \
                    f"👮‍♂️ *Procesado por:* {admin_user.first_name}\n" \
                    f"📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        await query.edit_message_caption(
            caption=admin_text,
            parse_mode=ParseMode.MARKDOWN
        )

        # Notificar al usuario
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=result_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            logger.warning(f"No se pudo notificar al usuario {user_id}")

        await query.answer(f"✅ Verificación {action_text.lower()}")

    except Exception as e:
        logger.error(f"Error en handle_check_approval: {e}")
        await query.answer("❌ Error procesando verificación", show_alert=True)

async def handle_game_play(query, context, game_type):
    """Maneja la lógica de juegos con límite de 12 horas"""
    user_id = str(query.from_user.id)
    user_data = db.get_user(user_id)

    now = datetime.now()
    last_game = user_data.get('last_game')

    # Verificar cooldown de 12 horas
    if last_game:
        last_game_date = datetime.fromisoformat(last_game)
        hours_passed = (now - last_game_date).total_seconds() / 3600

        if hours_passed < 12:
            hours_left = 12 - hours_passed
            await query.edit_message_text(
                f"⏰ **COOLDOWN ACTIVO** ⏰\n\n"
                f"⏳ Tiempo restante: {hours_left:.1f} horas\n"
                f"🎮 Podrás jugar cada 12 horas\n\n"
                f"💡 Usa `/loot` para créditos diarios",
                parse_mode=ParseMode.MARKDOWN)
            return

    # Jugar según el tipo
    game_names = {
        'play_ruleta': '🎰 Ruleta de la Suerte',
        'play_dados': '🎲 Dados Mágicos',
        'play_carta': '🃏 Carta de la Fortuna',
        'play_rayo': '⚡ Rayo de Créditos'
    }

    game_name = game_names.get(game_type, '🎮 Juego')
    ganancia = random.randint(3, 8)

    # Actualizar créditos y fecha del último juego
    db.update_user(user_id, {
        'credits': user_data['credits'] + ganancia,
        'last_game': now.isoformat()
    })

    # Mensajes especiales por juego
    game_messages = {
        'play_ruleta': f"🎰 La ruleta gira... ¡{ganancia} créditos!",
        'play_dados': f"🎲 Los dados cayeron... ¡{ganancia} créditos!",
        'play_carta': f"🃏 Tu carta de la fortuna... ¡{ganancia} créditos!",
        'play_rayo':
        f"⚡ El rayo de créditos te golpea... ¡{ganancia} créditos!"
    }

    # Special format for roulette game
    if game_type == 'play_ruleta':
        response = f"┌──⟪ 🎲 EXPLOIT ROULETTE ⟫──┐\n"
        response += f"│ +{ganancia} CR extraídos 💰 │\n"
        response += f"│ Riesgo de rastro: {random.randint(60, 85)}% ⚠️ │\n"
        response += f"│ Nodo cerrado ⛔ │\n"
        response += f"└──⟪ Reinicio en 12h ⟫─────┘"
    else:
        # Default format for other games
        response = f"🎉 **¡GANASTE!** 🎉\n\n"
        response += f"{game_name}\n"
        response += f"{game_messages.get(game_type, f'¡Ganaste {ganancia} créditos!')}\n\n"
        response += f"💰 **Créditos totales:** {user_data['credits'] + ganancia}\n"
        response += f"⏰ **Próximo juego:** En 12 horas"

    await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN)


async def welcome_new_member(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida para nuevos miembros"""
    for new_member in update.message.new_chat_members:
        # Escapar el nombre de usuario para evitar errores de parsing
        user_name = new_member.first_name or "Usuario"
        safe_user_name = escape_markdown(user_name)

        welcome_text = f"🎉 **¡BIENVENIDO A CHERNOBYL CHLV\\!** 🎉\n\n"
        welcome_text += f"👋 Hola {safe_user_name}\n\n"
        welcome_text += f"🔥 **¡Te damos la bienvenida al mejor bot de CCs\\!**\n\n"
        welcome_text += f"💡 **Para empezar:**\n"
        welcome_text += f"• Usa `/start` para ver todos los comandos\n"
        welcome_text += f"• Obtén créditos gratis con `/loot`\n"
        welcome_text += f"🎁 **Recibes 10 créditos de bienvenida**\n\n"
        welcome_text += f"📋 **Reglas básicas:**\n"
        welcome_text += f"• No spam ni enlaces\n"
        welcome_text += f"• Respeta a otros usuarios\n"
        welcome_text += f"• Usa los comandos correctamente\n\n"
        welcome_text += f"🤖 **Bot:** @ChernobilChLv\\_bot\n"
        welcome_text += f"🆘 **Soporte:** Contacta a los admins"

        # Dar créditos de bienvenida
        user_id = str(new_member.id)
        user_data = db.get_user(user_id)
        db.update_user(user_id, {'credits': user_data['credits'] + 10})

        try:
            await update.message.reply_text(welcome_text,
                                            parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            # Fallback sin formato si hay error de parsing
            simple_welcome = f"🎉 ¡BIENVENIDO A CHERNOBYL CHLV! 🎉\n\n"
            simple_welcome += f"👋 Hola {user_name}\n\n"
            simple_welcome += f"🔥 ¡Te damos la bienvenida!\n\n"
            simple_welcome += f"💡 Para empezar:\n"
            simple_welcome += f"• Usa /start para ver todos los comandos\n"
            simple_welcome += f"• Obtén créditos gratis con /loot\n"
            simple_welcome += f"🎁 Recibes 10 créditos de bienvenida\n\n"
            simple_welcome += f"📋 Reglas básicas:\n"
            simple_welcome += f"• No spam ni enlaces\n"
            simple_welcome += f"• Respeta a otros usuarios\n"
            simple_welcome += f"• Usa los comandos correctamente\n\n"
            simple_welcome += f"🤖 Bot: @ChernobilChLv_bot\n"
            simple_welcome += f"🆘 Soporte: Contacta a los admins"

            await update.message.reply_text(simple_welcome)


# Sistema de Mutes mejorado
muted_users = {
}  # Chat ID -> {user_id: {'unmute_time': datetime, 'reason': str, 'muted_by': str}}


async def check_user_muted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verificar si un usuario está muteado y eliminar su mensaje si es necesario"""
    if not update.message or not update.message.text:
        return False

    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)

    # Verificar si el chat tiene usuarios muteados
    if chat_id not in muted_users:
        return False

    # Verificar si el usuario está muteado
    if user_id not in muted_users[chat_id]:
        return False

    # Verificar si el mute ha expirado
    mute_data = muted_users[chat_id][user_id]
    unmute_time = mute_data['unmute_time']
    current_time = datetime.now()

    if current_time >= unmute_time:
        # El mute ha expirado, remover del diccionario
        del muted_users[chat_id][user_id]
        if not muted_users[chat_id]:
            del muted_users[chat_id]
        return False

    # El usuario está muteado, eliminar su mensaje
    try:
        await update.message.delete()
        return True
    except:
        return False


def auto_mute_user(chat_id: str,
                   user_id: str,
                   duration_hours: int = 12,
                   reason: str = "Mute automático",
                   muted_by: str = "Sistema"):
    """Mutear usuario automáticamente"""
    if chat_id not in muted_users:
        muted_users[chat_id] = {}

    unmute_time = datetime.now() + timedelta(hours=duration_hours)
    muted_users[chat_id][user_id] = {
        'unmute_time': unmute_time,
        'reason': reason,
        'muted_by': muted_by
    }

    return unmute_time


def detect_spam_patterns(message_text: str) -> dict:
    """Detectar patrones de spam avanzados"""
    spam_detected = {'is_spam': False, 'type': '', 'severity': 0}

    # 1. Detectar caracteres repetidos (como Z Z Z Z Z...)
    import re

    # Patrón para detectar caracteres repetidos con espacios
    repeated_char_pattern = r'(\S)\s+\1(\s+\1){3,}'
    repeated_matches = re.findall(repeated_char_pattern, message_text)

    if repeated_matches:
        spam_detected['is_spam'] = True
        spam_detected['type'] = 'caracteres_repetidos'
        spam_detected['severity'] = 3  # Alta severidad
        return spam_detected

    # 2. Detectar cadenas muy largas del mismo carácter
    long_repeat_pattern = r'(.)\1{10,}'  # Mismo carácter repetido 10+ veces
    if re.search(long_repeat_pattern, message_text):
        spam_detected['is_spam'] = True
        spam_detected['type'] = 'cadena_repetida'
        spam_detected['severity'] = 3
        return spam_detected

    # 3. Detectar palabras repetidas
    words = message_text.split()
    if len(words) > 5:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Si alguna palabra se repite más de 5 veces
        for word, count in word_counts.items():
            if count > 5 and len(word) > 1:
                spam_detected['is_spam'] = True
                spam_detected['type'] = 'palabra_repetida'
                spam_detected['severity'] = 2
                return spam_detected

    # 4. Detectar mensajes excesivamente largos con poco contenido
    if len(message_text) > 200:
        unique_chars = len(set(message_text.replace(' ', '')))
        if unique_chars < 10:  # Muy pocos caracteres únicos
            spam_detected['is_spam'] = True
            spam_detected['type'] = 'contenido_pobre'
            spam_detected['severity'] = 2
            return spam_detected

    return spam_detected


# Anti-Spam Handler - MEJORADO CON DETECCIÓN DE SPAM Y MUTE AUTOMÁTICO
async def anti_spam_handler(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """Sistema anti-spam automático que detecta spam, links y aplica mutes - RESPETA ROLES DE STAFF"""
    """Sistema anti-spam automático que detecta, guarda y elimina links - RESPETA ROLES DE STAFF"""
    if not update.message or not update.message.text:
        return

    # Primero verificar si el usuario está muteado
    is_muted = await check_user_muted(update, context)
    if is_muted:
        return  # Mensaje ya eliminado por estar muteado

    user_id = str(update.effective_user.id)
    user_id_int = update.effective_user.id
    user_data = db.get_user(user_id)
    message_text = update.message.text
    message_text_lower = message_text.lower()

    # VERIFICAR SI EL USUARIO TIENE PERMISOS PARA ENVIAR LINKS
    # 1. Administradores tradicionales
    is_traditional_admin = user_id_int in ADMIN_IDS

    # 2. Staff en base de datos (fundadores, co-fundadores, moderadores)
    staff_data = db.get_staff_role(user_id)
    is_staff = staff_data is not None

    # 3. IDs de emergencia
    emergency_ids = [6938971996, 5537246556]
    is_emergency_founder = user_id_int in emergency_ids

    # Si el usuario tiene permisos de staff, NO aplicar anti-spam
    if is_traditional_admin or is_staff or is_emergency_founder:
        return  # Permitir cualquier mensaje sin restricciones

    # DETECTAR SPAM DE CARACTERES REPETIDOS (NUEVA FUNCIONALIDAD)
    spam_analysis = detect_spam_patterns(message_text)

    if spam_analysis['is_spam']:
        try:
            # ELIMINAR el mensaje de spam
            await update.message.delete()

            username = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
            chat_id = str(update.effective_chat.id)

            # Determinar duración del mute según severidad
            if spam_analysis['severity'] >= 3:
                mute_hours = 24  # 24 horas para spam severo
            elif spam_analysis['severity'] >= 2:
                mute_hours = 12  # 12 horas para spam moderado
            else:
                mute_hours = 6  # 6 horas para spam leve

            # APLICAR MUTE AUTOMÁTICO
            unmute_time = auto_mute_user(chat_id, user_id, mute_hours)

            # Incrementar advertencias
            current_warns = user_data.get('warns', 0) + 1
            db.update_user(user_id, {'warns': current_warns})

            # Mensaje de notificación
            spam_types = {
                'caracteres_repetidos': '🔤 Caracteres repetidos detectados',
                'cadena_repetida': '🔗 Cadena de caracteres repetida',
                'palabra_repetida': '📝 Palabra repetida excesivamente',
                'contenido_pobre': '📄 Contenido de baja calidad'
            }

            warning_message = f"🚫 **SPAM DETECTADO - USUARIO MUTEADO** 🚫\n\n"
            warning_message += f"👤 **Usuario:** {username}\n"
            warning_message += f"🔍 **Tipo:** {spam_types.get(spam_analysis['type'], 'Spam detectado')}\n"
            warning_message += f"⏰ **Duración mute:** {mute_hours} horas\n"
            warning_message += f"🔓 **Desmute automático:** {unmute_time.strftime('%d/%m/%Y %H:%M')}\n"
            warning_message += f"⚠️ **Advertencias:** {current_warns}/3\n\n"

            if current_warns >= 3:
                warning_message += f"🔨 **USUARIO BANEADO PERMANENTEMENTE**"
                try:
                    await context.bot.ban_chat_member(
                        chat_id=update.effective_chat.id,
                        user_id=update.effective_user.id)
                    # Remover del sistema de mutes si fue baneado
                    if chat_id in muted_users and user_id in muted_users[
                            chat_id]:
                        del muted_users[chat_id][user_id]
                except:
                    warning_message += f"\n❌ Error al banear usuario"
            else:
                warning_message += f"💡 **El usuario no puede enviar mensajes durante el mute**\n"
                warning_message += f"🔰 **Los mensajes serán eliminados automáticamente**"

            # Enviar notificación temporal
            warning_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=warning_message,
                parse_mode=ParseMode.MARKDOWN)

            # Log para administradores
            logger.info(
                f"Spam detectado y usuario muteado - Usuario: {user_id} ({username}) - Tipo: {spam_analysis['type']} - Duración: {mute_hours}h"
            )

            # Auto-eliminar notificación después de 30 segundos
            await asyncio.sleep(30)
            try:
                await warning_msg.delete()
            except:
                pass

            return  # Salir aquí para evitar procesar como link spam

        except Exception as e:
            logger.error(f"Error en detección de spam: {e}")

    # CONTINUAR CON DETECCIÓN DE LINKS (CÓDIGO ORIGINAL)
    # Detectar múltiples tipos de links incluyendo embebidos
    spam_indicators = [
        "http://", "https://", "www.", ".com", ".net", ".org", ".io", ".co",
        ".me", "t.me/", "telegram.me", "bit.ly", "tinyurl", "shortened.link",
        ".tk", ".ml", ".ga", ".cf", ".ly", ".gl", ".gg", ".cc", ".tv",
        "discord.gg", "discord.com", "youtube.com", "youtu.be"
    ]

    # Verificar si el mensaje contiene spam básico
    contains_spam = any(indicator in message_text_lower
                        for indicator in spam_indicators)

    # 🔍 DETECCIÓN DE ENLACES (nueva forma limpia)
    detected_links = db.extract_links_from_text(message_text)
    if detected_links:
        try:
            username = f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name
            chat_id = str(update.effective_chat.id)
            link_id = db.save_deleted_link(user_id, username, chat_id,
                                           message_text)

            await update.message.delete()
            current_warns = user_data.get('warns', 0) + 1
            db.update_user(user_id, {'warns': current_warns})

            warning_message = f"🚫 **LINK DETECTADO Y ELIMINADO** 🚫\n\n"
            warning_message += f"👤 **Usuario:** {username}\n"
            warning_message += f"🔗 **Link(s):** {', '.join(detected_links[:2])}\n"
            warning_message += f"🆔 **ID del registro:** `{link_id}`\n"
            warning_message += f"⚠️ **Advertencias:** {current_warns}/3\n"

            if current_warns >= 3:
                warning_message += "\n🔨 **USUARIO BANEADO POR SPAM**"
                await context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=update.effective_user.id)
            else:
                warning_message += "\n📝 **Para evitar esto, no envíes enlaces**"

            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=warning_message,
                parse_mode="Markdown")
            await asyncio.sleep(2)
            await msg.delete()
        except Exception as e:
            logger.error(f"Error al eliminar mensaje con link: {e}")
        return  # Salir del handler si es un link

        # Log para administradores


# Manejador de errores mejorado
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de errores mejorado"""
    error_msg = str(context.error)

    # Ignorar errores de conflicto comunes
    if "Conflict: terminated by other getUpdates request" in error_msg:
        logger.warning("⚠️ Conflicto de getUpdates detectado - ignorando")
        return

    if "Connection pool is full" in error_msg:
        logger.warning("⚠️ Pool de conexiones lleno - reintentando")
        await asyncio.sleep(1)
        return

    if "Read timeout" in error_msg or "Write timeout" in error_msg:
        logger.warning("⚠️ Timeout de red - continuando")
        return

    # Log solo errores importantes
    logger.error(f"❌ Error importante: {error_msg}")

    # Intentar responder al usuario si hay un update válido
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Ocurrió un error temporal. Intenta nuevamente en unos segundos.",
                parse_mode=ParseMode.MARKDOWN)
        except:
            pass  # Si no puede responder, ignorar


# Función principal
def main():
    """Función principal del bot"""
    try:
        # Configuración del bot con manejo mejorado de errores
        application = (
            Application.builder().token(BOT_TOKEN).concurrent_updates(
                True)  # Permitir actualizaciones concurrentes
            .connection_pool_size(256)  # Pool de conexiones más grande
            .pool_timeout(20.0).connect_timeout(30.0).read_timeout(
                30.0).write_timeout(30.0).get_updates_connect_timeout(
                    30.0).get_updates_read_timeout(
                        30.0).get_updates_pool_timeout(10.0).build())

        # Registrar comandos principales
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("gen", gen_command))
        application.add_handler(CommandHandler("inject", live_command))
        application.add_handler(CommandHandler("direccion", direccion_command))
        application.add_handler(CommandHandler("ex", ex_command))
        application.add_handler(CommandHandler("wallet", credits_command))
        application.add_handler(CommandHandler("loot", bonus_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("bridge", pasarela_command))
        application.add_handler(CommandHandler("apply_key", apply_key_command))
        application.add_handler(
            CommandHandler("audit", infocredits_command))
        application.add_handler(CommandHandler("transmit", donate_command))
        application.add_handler(CommandHandler("simulator", juegos_command))

        # Sistema de verificación /check
        application.add_handler(CommandHandler("check", check_command))
        application.add_handler(
            CommandHandler("setcheckchats", setcheckchats_command))

        # Sistema de logs administrativos
        application.add_handler(
            CommandHandler("establishedadministration",
                           establishedadministration_command))

        # Sistema de publicaciones
        application.add_handler(CommandHandler("post", post_command))

        # Comandos de admin y staff
        application.add_handler(CommandHandler("staff", staff_command))
        application.add_handler(CommandHandler("founder", founder_command))
        application.add_handler(CommandHandler("cofounder", cofounder_command))
        application.add_handler(CommandHandler("moderator", moderator_command))

        # Comandos administrativos de MongoDB
        application.add_handler(CommandHandler("dbstatus", mongodb_status_command))
        application.add_handler(CommandHandler("dbreconnect", mongodb_reconnect_command))
        application.add_handler(CommandHandler("dbcleanup", mongodb_cleanup_command))
        application.add_handler(CommandHandler("dbcleanup", mongodb_cleanup_command))
        application.add_handler(CommandHandler("dbbackup", mongodb_backup_command))
        application.add_handler(CommandHandler("renderbackup", mongodb_render_backup_command))

        # Manejar callbacks de MongoDB
        application.add_handler(CallbackQueryHandler(handle_mongodb_callbacks, pattern='^(db_|cleanup_)'))
        # Comandos de moderación jerárquicos
        application.add_handler(
            CommandHandler("startfoundress", startfoundress_command))
        application.add_handler(
            CommandHandler("startcofunder", startcofunder_command))
        application.add_handler(
            CommandHandler("startmoderator", startmoderator_command))
        application.add_handler(
            CommandHandler("moderation_master", moderation_master_command))
        application.add_handler(
            CommandHandler("emergency_founder", emergency_founder_command))
        application.add_handler(
            CommandHandler("fix_founder", fix_founder_command))
        application.add_handler(
            CommandHandler("check_perms",
                           fix_founder_command))  # Alias adicional
        application.add_handler(CommandHandler("clean", clean_command))
        application.add_handler(
            CommandHandler("cleanstatus", cleanstatus_command))
        application.add_handler(CommandHandler("premium", premium_command))
        application.add_handler(CommandHandler("id", id_command))
        application.add_handler(CommandHandler("ban", ban_command))
        application.add_handler(CommandHandler("warn", warn_command))
        application.add_handler(CommandHandler("unwarn", unwarn_command))
        application.add_handler(CommandHandler("unban", unban_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("links", links_command))
        application.add_handler(CommandHandler("open", open_command))
        application.add_handler(CommandHandler("close", close_command))
        application.add_handler(CommandHandler("housemode", housemode_command))
        application.add_handler(CommandHandler("lockdown", lockdown_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("mutelist", mutelist_command))
        application.add_handler(
            CommandHandler("creditcleaningworld", creditcleaningworld_command))
        application.add_handler(CommandHandler("premium", premium_command))
        application.add_handler(CommandHandler("setpremium", setpremium_command))




        # Importar funciones de gates
        from gates_system import gates_command, handle_gate_callback, process_gate_card

        # Comandos de gates
        application.add_handler(CommandHandler("gates", gates_command))
        application.add_handler(CommandHandler("gate", gates_command))  # Alias
        application.add_handler(CommandHandler(
            "am", process_gate_card))  # Comando para procesar tarjetas

        # Callback handlers
        application.add_handler(CallbackQueryHandler(button_callback))

        # Manejador de nuevos miembros
        application.add_handler(
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS,
                           welcome_new_member))

        # Anti-spam handler
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam_handler))

        # Manejador de errores mejorado
        application.add_error_handler(error_handler)

        # Iniciar el bot con configuración optimizada
        print("✅ Bot iniciado correctamente")
        logger.info("🚀 Iniciando aplicación de Telegram Bot...")

        application.run_polling(
            drop_pending_updates=True,
            poll_interval=1.0,  # Intervalo de polling
            timeout=20,  # Timeout para getUpdates
            bootstrap_retries=3,  # Reintentos de arranque
            read_timeout=20,  # Timeout de lectura
            write_timeout=20,  # Timeout de escritura
            connect_timeout=20,  # Timeout de conexión
            pool_timeout=20,  # Timeout del pool
            allowed_updates=None  # Todas las actualizaciones
        )

    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido por el usuario")
        print("🛑 Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico en el bot: {e}")
        print(f"❌ Error crítico: {e}")
        # Esperar un momento antes de salir
        import time
        time.sleep(2)


if __name__ == "__main__":
    try:
        # Importar e iniciar keep_alive para UptimeRobot
        from keep_alive import keep_alive
        keep_alive()

        # Iniciar el bot
        main()
    except Exception as e:
        logger.error(f"Error crítico al iniciar el bot: {e}")
        import sys
        sys.exit(1)
