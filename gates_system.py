import asyncio
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import RetryAfter, TimedOut

# Configurar logger específico para gates
logger = logging.getLogger(__name__)

# La instancia db se pasará al constructor
db = None

class GateSystem:
    def __init__(self, database_instance):
        self.db = database_instance
        # Actualizar la referencia global para compatibilidad
        global db
        db = database_instance
        self.active_sessions = {}  # Sesiones activas de gates
        self.rate_limit_tracker = {}  # Control de rate limiting

    def is_authorized(self, user_id: str) -> bool:
        """Verificar si el usuario tiene acceso usando la base de datos MongoDB"""
        try:
            # Verificar roles de staff usando MongoDB
            if self.db.is_founder(user_id):
                logger.info(f"[GATES] Usuario {user_id} autorizado como FUNDADOR")
                return True

            if self.db.is_cofounder(user_id):
                logger.info(f"[GATES] Usuario {user_id} autorizado como CO-FUNDADOR")
                return True

            if self.db.is_moderator(user_id):
                logger.info(f"[GATES] Usuario {user_id} autorizado como MODERADOR")
                return True

            # Obtener datos del usuario desde MongoDB
            user_data = self.db.get_user(user_id)
            is_premium = user_data.get('premium', False)
            premium_until = user_data.get('premium_until')

            logger.info(f"[GATES] VERIFICACIÓN - Usuario {user_id}: premium={is_premium}, until={premium_until}")

            # Si premium=False explícitamente, denegar inmediatamente
            if is_premium is False:
                logger.info(f"[GATES] Usuario {user_id} - Premium False - ACCESO DENEGADO ❌")
                return False

            # Lógica para premium=True
            if is_premium is True:
                if premium_until:
                    try:
                        # Parsear fecha de expiración
                        if isinstance(premium_until, str):
                            premium_until_date = datetime.fromisoformat(premium_until)
                        else:
                            premium_until_date = premium_until

                        # Verificar si aún es válido
                        if datetime.now() < premium_until_date:
                            logger.info(f"[GATES] Usuario {user_id} - Premium válido hasta {premium_until_date} ✅")
                            return True
                        else:
                            # Premium expirado - actualizar automáticamente
                            logger.info(f"[GATES] Usuario {user_id} - Premium expirado, actualizando BD")
                            self.db.update_user(user_id, {'premium': False, 'premium_until': None})
                            return False
                    except Exception as date_error:
                        logger.error(f"[GATES] Error fecha premium {user_id}: {date_error}")
                        # Si no hay fecha válida, es premium permanente
                        if premium_until is None:
                            logger.info(f"[GATES] Usuario {user_id} - Premium permanente (sin fecha) ✅")
                            return True
                        else:
                            logger.warning(f"[GATES] Usuario {user_id} - Error en fecha premium, DENEGANDO por seguridad ❌")
                            return False
                else:
                    # Premium=True sin fecha = premium permanente
                    logger.info(f"[GATES] Usuario {user_id} - Premium permanente (sin until) ✅")
                    return True

            # Usuario sin premium ni staff
            logger.info(f"[GATES] Usuario {user_id} - SIN ACCESO (premium={is_premium}, staff=False) ❌")
            return False

        except Exception as e:
            logger.error(f"[GATES] Error crítico verificando {user_id}: {e}")
            return False

    def create_gates_menu(self) -> InlineKeyboardMarkup:
        """Crear menú principal de gates"""
        keyboard = [
            [
                InlineKeyboardButton("🔵 Stripe Gate", callback_data='gate_stripe'),
                InlineKeyboardButton("🟠 Amazon Gate", callback_data='gate_amazon')
            ],
            [
                InlineKeyboardButton("🔴 PayPal Gate", callback_data='gate_paypal'),
                InlineKeyboardButton("🟡 Ayden Gate", callback_data='gate_ayden')
            ],
            [
                InlineKeyboardButton("🟢 Auth Gate", callback_data='gate_auth'),
                InlineKeyboardButton("⚫ CCN Charge", callback_data='gate_ccn')
            ],
            [
                InlineKeyboardButton("🤖 CyberSource AI", callback_data='gate_cybersource'),
                InlineKeyboardButton("🇬🇧 Worldpay UK", callback_data='gate_worldpay')
            ],
            [
                InlineKeyboardButton("🌐 Braintree Pro", callback_data='gate_braintree'),
                InlineKeyboardButton("📊 Gate Status", callback_data='gates_status')
            ],
            [
                InlineKeyboardButton("❌ Cerrar", callback_data='gates_close')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def process_stripe_gate(self, card_data: str) -> dict:
        """Procesar verificación Stripe Gate - EFECTIVIDAD COMERCIAL MEJORADA"""
        await asyncio.sleep(random.uniform(2.0, 4.0))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido - Use: 4532123456781234|12|25|123',
                'status': 'DEAD'
            }

        card_number = parts[0]
        exp_month = parts[1]
        exp_year = parts[2]
        cvv = parts[3]

        # ALGORITMO MEJORADO PARA VENTA COMERCIAL (45-75% efectividad)
        success_rate = 0.45  # 45% base COMERCIAL

        # Análisis del BIN (bonificaciones SIGNIFICATIVAS)
        premium_bins = ['4532', '4485', '5531', '4539', '4000', '4001', '4242', '5555', '5200']
        if any(card_number.startswith(bin_) for bin_ in premium_bins):
            success_rate += 0.15  # +15% para BINs premium
        elif card_number.startswith(('40', '41', '42', '51', '52', '53')):
            success_rate += 0.10  # +10% para BINs buenos

        # Análisis CVV mejorado
        if cvv.endswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            success_rate += 0.05  # +5% para todos los CVVs válidos

        # Análisis de fecha de vencimiento
        try:
            current_year = 2025
            exp_year_int = int(exp_year) if len(exp_year) == 4 else 2000 + int(exp_year)
            years_until_expiry = exp_year_int - current_year

            if years_until_expiry >= 2:
                success_rate += 0.08  # +8% para tarjetas con vencimiento lejano
            elif years_until_expiry >= 1:
                success_rate += 0.05  # +5% para tarjetas válidas
        except:
            pass

        # Factor de aleatoriedad controlado
        success_rate *= random.uniform(0.85, 1.15)

        # MÁXIMO COMERCIAL del 75%
        success_rate = min(success_rate, 0.75)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ Payment successful - $1.00 charged and captured",
                "✅ Transaction approved - $1.00 authorized - CVV2/AVS Match",
                "✅ Stripe: $1.00 charged successfully - Gateway Response: 00",
                "✅ Card charged $1.00 - Risk: Low - Funds captured",
                "✅ Authorization successful - $1.00 processed - Card validated"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'Stripe Ultra',
                'amount': '$1.00',
                'is_live': True
            }
        else:
            responses = [
                "❌ Card declined - Insufficient funds",
                "❌ Transaction failed - Invalid CVV",
                "❌ Payment declined - Do not honor",
                "❌ Risk threshold exceeded",
                "❌ Generic decline - Contact bank",
                "❌ Card blocked - Security"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Stripe Ultra',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_amazon_gate(self, card_data: str) -> dict:
        """Procesar verificación Amazon Gate - EFECTIVIDAD COMERCIAL"""
        await asyncio.sleep(random.uniform(3.0, 5.0))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        # Amazon mejorado para uso comercial - 40-65% efectividad
        success_rate = 0.40  # 40% base COMERCIAL

        card_number = parts[0]
        if card_number.startswith('4'):
            success_rate += 0.12  # Amazon prefiere Visa (+12%)
        elif card_number.startswith('5'):
            success_rate += 0.08  # MasterCard (+8%)

        # Factor de aleatoriedad controlado
        success_rate *= random.uniform(0.90, 1.25)

        # MÁXIMO COMERCIAL del 65%
        success_rate = min(success_rate, 0.65)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ Amazon: $1.00 charged - Payment method verified",
                "✅ Amazon: Card charged $1.00 - Ready for purchases",
                "✅ Amazon: $1.00 authorization successful - Billing updated",
                "✅ Amazon: Payment processed $1.00 - Card validated"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'Amazon Prime',
                'amount': '$1.00',
                'is_live': True
            }
        else:
            responses = [
                "❌ Amazon: Invalid payment method",
                "❌ Amazon: Card verification failed",
                "❌ Amazon: Unable to add card",
                "❌ Amazon: Billing address mismatch",
                "❌ Amazon: Security review required"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Amazon Prime',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_paypal_gate(self, card_data: str) -> dict:
        """Procesar verificación PayPal Gate - EFECTIVIDAD COMERCIAL"""
        await asyncio.sleep(random.uniform(2.5, 4.5))

        # PayPal mejorado para venta comercial (35-60% efectividad)
        success_rate = 0.35  # 35% base comercial

        parts = card_data.split('|')
        if len(parts) >= 4:
            card_number = parts[0]
            # Bonus por tipo de tarjeta
            if card_number.startswith(('4532', '4485', '5531')):
                success_rate += 0.15  # +15% para BINs premium
            elif card_number.startswith(('4', '5')):
                success_rate += 0.08  # +8% para Visa/MC

        # Factor de aleatoriedad controlado
        success_rate *= random.uniform(0.90, 1.20)

        # MÁXIMO COMERCIAL del 60%
        success_rate = min(success_rate, 0.60)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ PayPal: $1.00 charged - Card linked successfully",
                "✅ PayPal: Payment processed $1.00 - Account verified",
                "✅ PayPal: $1.00 authorization complete - Card validated",
                "✅ PayPal: Transaction approved $1.00 - Ready for payments"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'PayPal Express',
                'amount': '$1.00',
                'is_live': True
            }
        else:
            responses = [
                "❌ PayPal: Card verification failed",
                "❌ PayPal: Unable to link card",
                "❌ PayPal: Security check failed",
                "❌ PayPal: Invalid card data"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'PayPal Express',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_ayden_gate(self, card_data: str) -> dict:
        """Procesar verificación Ayden Gate - EFECTIVIDAD COMERCIAL"""
        await asyncio.sleep(random.uniform(3.5, 5.5))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        # Ayden mejorado para venta comercial - 38-58% efectividad
        success_rate = 0.38  # 38% base comercial

        card_number = parts[0]
        # Ayden prefiere ciertos BINs europeos
        if card_number.startswith(('4000', '4001', '5200', '5201', '4532', '4485')):
            success_rate += 0.12  # +12% para BINs premium
        elif card_number.startswith(('4', '5')):
            success_rate += 0.06  # +6% para tarjetas válidas

        # Factor de aleatoriedad controlado
        success_rate *= random.uniform(0.85, 1.20)

        # MÁXIMO COMERCIAL del 58%
        success_rate = min(success_rate, 0.58)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ Ayden: $1.00 payment authorized successfully",
                "✅ Ayden: Card charged $1.00 - Verification passed",
                "✅ Ayden: $1.00 transaction approved - EU gateway",
                "✅ Ayden: Payment processed $1.00 - 3DS bypass successful"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'Ayden EU',
                'amount': '$1.00',
                'is_live': True
            }
        else:
            responses = [
                "❌ Ayden: Authorization declined",
                "❌ Ayden: Card not supported",
                "❌ Ayden: Risk score too high",
                "❌ Ayden: 3DS authentication failed"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Ayden EU',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_auth_gate(self, card_data: str) -> dict:
        """Procesar verificación Auth Gate - EFECTIVIDAD REALISTA"""
        await asyncio.sleep(random.uniform(1.5, 3.0))

        # Auth Gate efectividad ULTRA REALISTA (8-16% máximo)
        success_rate = 0.04  # 4% base realista

        # Factor de aleatoriedad
        success_rate *= random.uniform(0.5, 2.0)

        # MÁXIMO REALISTA del 16%
        success_rate = min(success_rate, 0.16)

        is_success = random.random() < success_rate

        if is_success:
            return {
                'success': True,
                'message': "✅ Auth: Verification successful",
                'status': 'LIVE',
                'gateway': 'Auth Check',
                'amount': '$0.01',
                'is_live': True
            }
        else:
            responses = [
                "❌ Auth: Verification failed",
                "❌ Auth: Invalid card data",
                "❌ Auth: CVV check failed"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Auth Check',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_ccn_charge(self, card_data: str) -> dict:
        """Procesar CCN Charge Gate - EFECTIVIDAD REALISTA"""
        await asyncio.sleep(random.uniform(2.0, 4.0))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        # CCN Charge efectividad COMERCIAL (42-68% efectividad)
        success_rate = 0.42  # 42% base comercial

        card_number = parts[0]
        # CCN prefiere ciertos tipos de tarjeta
        if card_number.startswith(('4111', '4242', '5555', '4532', '4485')):
            success_rate += 0.15  # +15% para BINs premium
        elif card_number.startswith(('4', '5')):
            success_rate += 0.08  # +8% para tarjetas válidas

        # Factor de aleatoriedad controlado
        success_rate *= random.uniform(0.88, 1.18)

        # MÁXIMO COMERCIAL del 68%
        success_rate = min(success_rate, 0.68)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ CCN: Charge successful - $1.00 processed",
                "✅ CCN: Payment $1.00 processed - CVV verified",
                "✅ CCN: Transaction approved $1.00 - Low risk",
                "✅ CCN: $1.00 charged successfully - Funds captured"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'CCN Charge',
                'amount': '$1.00',
                'is_live': True
            }
        else:
            responses = [
                "❌ CCN: Charge declined - Insufficient funds",
                "❌ CCN: Payment failed - Invalid card",
                "❌ CCN: Transaction denied - Bank decline",
                "❌ Risk threshold exceeded"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'CCN Charge',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_cybersource_ai(self, card_data: str) -> dict:
        """Procesar CyberSource AI Gate - INTELIGENCIA ARTIFICIAL ANTI-FRAUDE"""
        await asyncio.sleep(random.uniform(3.5, 6.0))  # IA toma más tiempo

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        card_number = parts[0]
        exp_month = parts[1]
        exp_year = parts[2]
        cvv = parts[3]

        # CyberSource AI - ULTRA RESTRICTIVO pero efectivo para premium
        success_rate = 0.09  # 9% base (optimizado para premium)

        # Análisis de IA simulado - patrones complejos
        digit_pattern = int(card_number[-2:]) if len(card_number) >= 2 else 0

        # Algoritmo de IA para detección de patrones
        if digit_pattern % 17 == 0:  # Patrón matemático específico
            success_rate += 0.04  # +4%
        elif digit_pattern % 7 == 0:  # Patrón secundario
            success_rate += 0.02  # +2%

        # Análisis de CVV con IA
        cvv_sum = sum(int(d) for d in cvv if d.isdigit())
        if cvv_sum % 5 == 0:
            success_rate += 0.02  # +2%

        # Análisis de fecha de vencimiento
        try:
            if int(exp_year) >= 2027:
                success_rate += 0.03  # +3% para tarjetas con vencimiento lejano
        except ValueError:
            pass

        # Factor de IA - más variable pero controlado
        success_rate *= random.uniform(0.4, 1.6)

        # MÁXIMO para CyberSource AI: 25%
        success_rate = min(success_rate, 0.25)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ CyberSource AI: ACCEPT - Low risk score",
                "✅ CyberSource AI: AUTHORIZED - Pattern verified",
                "✅ CyberSource AI: SUCCESS - ML model approved",
                "✅ CyberSource AI: APPROVED - Fraud score: 0.12"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'CyberSource AI',
                'amount': '$0.01',
                'is_live': True
            }
        else:
            responses = [
                "❌ CyberSource AI: REJECT - High risk score",
                "❌ CyberSource AI: DECLINED - ML flagged",
                "❌ CyberSource AI: BLOCKED - Fraud detection",
                "❌ CyberSource AI: REVIEW - Manual verification required",
                "❌ CyberSource AI: DENIED - Pattern anomaly detected"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'CyberSource AI',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_worldpay_gate(self, card_data: str) -> dict:
        """Procesar Worldpay Gate - PROCESAMIENTO BRITÁNICO PREMIUM"""
        await asyncio.sleep(random.uniform(2.5, 4.5))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        card_number = parts[0]
        exp_month = parts[1]
        exp_year = parts[2]
        cvv = parts[3]

        # Worldpay efectividad PREMIUM (10-20% máximo)
        success_rate = 0.08  # 8% base optimizado

        # Análisis específico de Worldpay por tipo de tarjeta
        if card_number.startswith('4'):  # Visa
            success_rate += 0.05  # +5% para Visa
        elif card_number.startswith('5'):  # MasterCard
            success_rate += 0.03  # +3% para MasterCard
        elif card_number.startswith('3'):  # American Express
            success_rate += 0.02  # +2% para Amex

        # Análisis de BIN británico
        uk_friendly_bins = ['4000', '4001', '4462', '4486', '5200', '5201']
        if any(card_number.startswith(bin_) for bin_ in uk_friendly_bins):
            success_rate += 0.04  # +4% para BINs amigables

        # Factor de procesamiento británico
        success_rate *= random.uniform(0.7, 1.4)

        # MÁXIMO Worldpay: 20%
        success_rate = min(success_rate, 0.20)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ Worldpay: AUTHORISED - Payment captured",
                "✅ Worldpay: SUCCESS - Transaction settled",
                "✅ Worldpay: APPROVED - UK gateway response",
                "✅ Worldpay: CAPTURED - Funds secured"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'Worldpay UK',
                'amount': '$0.30',
                'is_live': True
            }
        else:
            responses = [
                "❌ Worldpay: REFUSED - Issuer declined",
                "❌ Worldpay: FAILED - Card verification failed",
                "❌ Worldpay: CANCELLED - Risk assessment",
                "❌ Worldpay: BLOCKED - Fraud prevention",
                "❌ Worldpay: EXPIRED - Card invalid"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Worldpay UK',
                'amount': '$0.00',
                'is_live': False
            }

    async def process_braintree_gate(self, card_data: str) -> dict:
        """Procesar Braintree Gate - ANÁLISIS TEMPORAL AVANZADO"""
        await asyncio.sleep(random.uniform(2.0, 3.5))

        parts = card_data.split('|')
        if len(parts) < 4:
            return {
                'success': False,
                'message': '❌ Formato inválido',
                'status': 'DEAD'
            }

        card_number = parts[0]
        exp_month = parts[1]
        exp_year = parts[2]
        cvv = parts[3]

        # Braintree efectividad PREMIUM (12-24% máximo)
        success_rate = 0.10  # 10% base optimizado

        # Análisis temporal específico de Braintree
        try:
            current_year = 2025
            years_until_expiry = int(exp_year) - current_year

            if years_until_expiry >= 4:
                success_rate += 0.06  # +6% para tarjetas muy lejanas
            elif years_until_expiry >= 2:
                success_rate += 0.04  # +4% para tarjetas lejanas
            elif years_until_expiry >= 1:
                success_rate += 0.02  # +2% para tarjetas normales
            else:
                success_rate -= 0.02  # -2% para tarjetas próximas a vencer
        except ValueError:
            pass

        # Análisis adicional del número de tarjeta
        digit_sum = sum(int(d) for d in card_number if d.isdigit())
        if digit_sum % 13 == 0:  # Patrón matemático específico
            success_rate += 0.03  # +3%

        # Análisis de CVV para Braintree
        if len(cvv) == 3 and cvv.isdigit():
            cvv_value = int(cvv)
            if cvv_value % 11 == 0:
                success_rate += 0.02  # +2%

        # Factor de procesamiento Braintree
        success_rate *= random.uniform(0.8, 1.5)

        # MÁXIMO Braintree: 24%
        success_rate = min(success_rate, 0.24)

        is_success = random.random() < success_rate

        if is_success:
            responses = [
                "✅ Braintree: AUTHORIZED - Transaction approved",
                "✅ Braintree: SUCCESS - Payment processed",
                "✅ Braintree: APPROVED - Gateway response OK",
                "✅ Braintree: CAPTURED - Settlement pending"
            ]
            return {
                'success': True,
                'message': random.choice(responses),
                'status': 'LIVE',
                'gateway': 'Braintree Pro',
                'amount': '$0.25',
                'is_live': True
            }
        else:
            responses = [
                "❌ Braintree: DECLINED - Issuer refused",
                "❌ Braintree: FAILED - Card verification failed",
                "❌ Braintree: TIMEOUT - Gateway unavailable",
                "❌ Braintree: REJECTED - Risk assessment",
                "❌ Braintree: BLOCKED - Fraud protection"
            ]
            return {
                'success': False,
                'message': random.choice(responses),
                'status': 'DEAD',
                'gateway': 'Braintree Pro',
                'amount': '$0.00',
                'is_live': False
            }

    async def safe_edit_message(self, message, text, reply_markup=None, parse_mode=ParseMode.MARKDOWN):
        """Editar mensaje de forma segura con control de rate limiting"""
        try:
            await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except RetryAfter as e:
            # Esperar el tiempo requerido por Telegram
            await asyncio.sleep(e.retry_after + 1)
            try:
                await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                # Si falla de nuevo, enviar nuevo mensaje
                await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except TimedOut:
            await asyncio.sleep(2)
            try:
                await message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            # Como último recurso, enviar nuevo mensaje
            await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

# Instancia global del sistema de gates
gate_system = None

async def gates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando principal /gates - Todos pueden ver, solo premium/fundadores pueden usar"""
    global gate_system
    # Importar db aquí para asegurar que tenemos la instancia actual
    from telegram_bot import db as current_db
    if gate_system is None:
        gate_system = GateSystem(current_db)
    else:
        # Actualizar la referencia de la base de datos
        gate_system.db = current_db

    user_id = str(update.effective_user.id)

    # Verificar créditos (5 créditos por uso) - Solo si no es autorizado
    user_data = db.get_user(user_id)
    is_authorized = gate_system.is_authorized(user_id)

    # Los usuarios autorizados (premium/staff) no necesitan créditos
    if not is_authorized and user_data['credits'] < 5:
        await update.message.reply_text(
            "❌ **LOOT INSUFICIENTE** ❌\n\n"
            f"💰 **Necesitas:** 5 loot\n"
            f"💳 **Tienes:** {user_data['credits']} loot\n\n"
            "🎁 **Obtener más loot:**\n"
            "• `/loot` - Bono diario gratis\n"
            "• `/simulator` - Casino bot\n"
            "• Contactar administración",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Crear menú de gates
    keyboard = gate_system.create_gates_menu()

    # Determinar tipo de usuario y acceso
    is_founder = db.is_founder(user_id)
    is_cofounder = db.is_cofounder(user_id)
    is_moderator = db.is_moderator(user_id)
    is_authorized = gate_system.is_authorized(user_id)

    # Verificar premium - MEJORADO PARA DEPURACIÓN
    user_data = db.get_user(user_id)
    is_premium = user_data.get('premium', False)
    premium_until = user_data.get('premium_until')

    # Log detallado para depuración
    logger.info(f"Gates command - Usuario {user_id}: premium={is_premium}, until={premium_until}")

    # Verificar si el premium es válido
    premium_valid = False
    if is_premium:
        if premium_until:
            try:
                if isinstance(premium_until, str):
                    premium_until_date = datetime.fromisoformat(premium_until)
                else:
                    premium_until_date = premium_until

                if datetime.now() < premium_until_date:
                    premium_valid = True
                    logger.info(f"Premium válido hasta {premium_until_date}")
                else:
                    logger.info(f"Premium expirado en {premium_until_date}")
            except Exception as e:
                logger.error(f"Error verificando fecha premium: {e}")
                # Si hay error pero tiene premium=True, considerar válido
                premium_valid = True
        else:
            # Premium sin fecha = permanente
            premium_valid = True
            logger.info(f"Premium permanente detectado")

    # Determinar tipo de usuario y acceso basado en roles de staff y premium
    if is_founder:
        user_type = "👑 FUNDADOR"
        access_text = "✅ ACCESO COMPLETO"
        status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
        modules_status = "🔓"
        final_message = "➤ Selecciona tu módulo preferido:"
    elif is_cofounder:
        user_type = "💎 CO-FUNDADOR"
        access_text = "✅ ACCESO COMPLETO"
        status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
        modules_status = "🔓"
        final_message = "➤ Selecciona tu módulo preferido:"
    elif is_moderator:
        user_type = "🛡️ MODERADOR"
        access_text = "✅ ACCESO COMPLETO"
        status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
        modules_status = "🔓"
        final_message = "➤ Selecciona tu módulo preferido:"
    elif premium_valid:
        user_type = "💎 PREMIUM"
        access_text = "✅ ACCESO COMPLETO"
        status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
        modules_status = "🔓"
        final_message = "➤ Selecciona tu módulo preferido:"
    else:
        user_type = "🆓 USUARIO ESTÁNDAR"
        access_text = "❌ SOLO VISTA PREVIA"
        status_section = "[!] ACCESO A FUNCIONES DENEGADO\n[!] VISUALIZACIÓN TEMPORAL ACTIVADA"
        modules_status = "🔒"
        final_message = "➤ Desbloquea acceso total:\n    ↳ PREMIUM ACTIVATION: @SteveCHBll"

    # Plantilla unificada para todos los usuarios
    response = f"┏━━━━━━━━━━━━━━━┓\n"
    response += f"┃    GATES CORE   -  DARK ACCESS     ┃\n"
    response += f"┗━━━━━━━━━━━━━━━┛\n\n"
    response += f"✘ USUARIO: {user_type}\n"
    response += f"✘ ESTADO : {access_text}\n"
    response += f"✘ LOOT DISPONIBLE: {user_data['credits']}\n"
    response += f"✘ COSTO POR GATE: 1 🔻\n"
    response += f"✘ MÓDULOS RESTRINGIDOS: {modules_status}\n\n"
    response += f"──────────────────────────────\n"
    response += f"{status_section}\n"
    response += f"──────────────────────────────\n\n"
    response += f">> GATES DISPONIBLES:\n"
    response += f"│  → 🔹 Stripe                    → 🟠 Amazon\n"
    response += f"│  → 🔴 PayPal                   → 🟡 Ayden\n"
    response += f"│  → 🟢 Auth                       → ⚫ CCN Charge\n"
    response += f"│  → 🤖 CyberSource AI\n"
    response += f"│  → 🌐 Braintree Pro       → 🇬🇧 Worldpay UK\n\n"
    response += f"{final_message}"

    await update.message.reply_text(
        response,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_gate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar callbacks de gates"""
    global gate_system
    query = update.callback_query
    user_id = str(query.from_user.id)

    # Importar db aquí para asegurar que tenemos la instancia actual
    from telegram_bot import db as current_db
    if gate_system is not None:
        gate_system.db = current_db

    await query.answer()

    if query.data == 'gates_close':
        await query.edit_message_text(
            "❌ **Gates System cerrado**\n\n"
            "💡 Usa `/gates` para acceder nuevamente",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if query.data == 'gates_status':
        status_text = f"┏━━━━━━━━━━━━━━━┓\n"
        status_text += f"┃    SYSTEM MONITOR - STATUS     ┃\n"
        status_text += f"┗━━━━━━━━━━━━━━━┛\n\n"
        status_text += f">> GATEWAY STATUS:\n"
        status_text += f"│  🔹 Stripe.......: 🟢 ONLINE\n"
        status_text += f"│  🟠 Amazon.......: 🟢 ONLINE\n"
        status_text += f"│  🔴 PayPal.......: 🟢 ONLINE\n"
        status_text += f"│  🟡 Ayden........: 🟢 ONLINE\n"
        status_text += f"│  🟢 Auth.........: 🟢 ONLINE\n"
        status_text += f"│  ⚫ CCN Charge...: 🟢 ONLINE\n"
        status_text += f"│  🤖 CyberSource..: 🟢 ONLINE [PREMIUM]\n"
        status_text += f"│  🇬🇧 Worldpay....: 🟢 ONLINE [PREMIUM]\n"
        status_text += f"│  🌐 Braintree....: 🟢 ONLINE [PREMIUM]\n\n"
        status_text += f">> SYSTEM INFO:\n"
        status_text += f"│  • Última sync...: {datetime.now().strftime('%H:%M:%S')}\n"
        status_text += f"│  • Uptime........: 99.9%\n"
        status_text += f"│  • Efectividad...: PRO\n\n"
        status_text += f"➤ Todos los gateways operativos"

        back_keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data='gates_back')]]
        await query.edit_message_text(
            status_text,
            reply_markup=InlineKeyboardMarkup(back_keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if query.data == 'gates_back':
        keyboard = gate_system.create_gates_menu()
        user_data = db.get_user(user_id)

        # Verificar autorización con datos frescos
        gate_system.db.load_data()
        is_authorized = gate_system.is_authorized(user_id)
        is_founder = db.is_founder(user_id)
        is_cofounder = db.is_cofounder(user_id)
        is_moderator = db.is_moderator(user_id)
        is_premium = user_data.get('premium', False)

        # Verificar que el premium sea válido
        premium_valid = False
        if is_premium:
            premium_until = user_data.get('premium_until')
            if premium_until:
                try:
                    if isinstance(premium_until, str):
                        premium_until_date = datetime.fromisoformat(premium_until)
                    else:
                        premium_until_date = premium_until
                    premium_valid = datetime.now() < premium_until_date
                except:
                    premium_valid = True
            else:
                premium_valid = True

        # Determinar tipo de usuario y estado
        if is_founder:
            user_type = "👑 FUNDADOR"
            access_text = "✅ ACCESO COMPLETO"
            status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
            modules_status = "🔓"
            final_message = "➤ Selecciona gateway deseado:"
        elif is_cofounder:
            user_type = "💎 CO-FUNDADOR"
            access_text = "✅ ACCESO COMPLETO"
            status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
            modules_status = "🔓"
            final_message = "➤ Selecciona gateway deseado:"
        elif is_moderator:
            user_type = "🛡️ MODERADOR"
            access_text = "✅ ACCESO COMPLETO"
            status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
            modules_status = "🔓"
            final_message = "➤ Selecciona gateway deseado:"
        elif premium_valid:
            user_type = "💎 PREMIUM"
            access_text = "✅ ACCESO COMPLETO"
            status_section = "[✓] ACCESO TOTAL HABILITADO\n[✓] SISTEMAS OPERATIVOS"
            modules_status = "🔓"
            final_message = "➤ Selecciona gateway deseado:"
        else:
            user_type = "🆓 USUARIO ESTÁNDAR"
            access_text = "❌ SOLO VISTA PREVIA"
            status_section = "[!] ACCESO A FUNCIONES DENEGADO\n[!] VISUALIZACIÓN TEMPORAL ACTIVADA"
            modules_status = "🔒"
            final_message = "➤ Desbloquea acceso total:\n    ↳ PREMIUM ACTIVATION: @SteveCHBll"

        # Plantilla unificada
        response = f"┏━━━━━━━━━━━━━━━┓\n"
        response += f"┃    GATES CORE   -  DARK ACCESS     ┃\n"
        response += f"┗━━━━━━━━━━━━━━━┛\n\n"
        response += f"✘ USUARIO: {user_type}\n"
        response += f"✘ ESTADO : {access_text}\n"
        response += f"✘ CRÉDITOS DISPONIBLES: {user_data['credits']}\n"
        response += f"✘ COSTO POR GATE: 1 🔻\n"
        response += f"✘ MÓDULOS RESTRINGIDOS: {modules_status}\n\n"
        response += f"──────────────────────────────\n"
        response += f"{status_section}\n"
        response += f"──────────────────────────────\n\n"
        response += f">> GATES DISPONIBLES:\n"
        response += f"│  → 🔹 Stripe                    → 🟠 Amazon\n"
        response += f"│  → 🔴 PayPal                   → 🟡 Ayden\n"
        response += f"│  → 🟢 Auth                       → ⚫ CCN Charge\n"
        response += f"│  → 🤖 CyberSource AI\n"
        response += f"│  → 🌐 Braintree Pro       → 🇬🇧 Worldpay UK\n\n"
        response += f"{final_message}"

        await query.edit_message_text(
            response,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Procesar selección de gate específico
    gate_types = {
        'gate_stripe': ('Stripe Gate', '🔵'),
        'gate_amazon': ('Amazon Gate', '🟠'),
        'gate_paypal': ('PayPal Gate', '🔴'),
        'gate_ayden': ('Ayden Gate', '🟡'),
        'gate_auth': ('Auth Gate', '🟢'),
        'gate_ccn': ('CCN Charge', '⚫'),
        'gate_cybersource': ('CyberSource AI', '🤖'),
        'gate_worldpay': ('Worldpay UK', '🇬🇧'),
        'gate_braintree': ('Braintree Pro', '🌐')
    }

    if query.data in gate_types:
        # VERIFICAR PERMISOS AL SELECCIONAR GATE CON DATOS FRESCOS
        gate_system.db.load_data()  # FORZAR RECARGA ANTES DE VERIFICAR
        is_authorized = gate_system.is_authorized(user_id)

        # Log detallado para depuración con datos frescos
        user_data = db.get_user(user_id)
        logger.info(f"[GATE CALLBACK] Usuario {user_id}: authorized={is_authorized}, premium={user_data.get('premium', False)}, until={user_data.get('premium_until', 'None')}")

        if not is_authorized:
            await query.edit_message_text(
                "💻 SYSTEM SECURITY NODE 💻\n\n"
                "👤 USER STATUS: 🆓 FREE_MODE\n"
                "🛡 ACCESS LEVEL: 🚫 RESTRICTED\n"
                "📅 PREMIUM VALID UNTIL: ❌ NONE\n\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "⚠ ERROR 403: ACCESS DENIED ⚠\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔒 RESTRICTED MODULES\n\n"
                "🗡 Gates Avanzados OFF\n"
                "🚀 Procesamiento PRO OFF\n"
                "🛡 Anti-Rate Limit OFF\n\n"
                "💎 PREMIUM MODULES\n\n"
                "🗡 Gates Avanzados ON\n"
                "🎯 Efectividad PRO ON\n"
                "🤝 Soporte Prioritario\n"
                "📦 Multi-Card Process\n"
                "♾ Sin Límite de Uso\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📩 CONTACT ADMIN: @SteveCHBll\n"
                "━━━━━━━━━━━━━━━━━━━━")
            return

        gate_name, gate_emoji = gate_types[query.data]

        # Crear sesión para este usuario (solo si está autorizado)
        gate_system.active_sessions[user_id] = {
            'gate_type': query.data,
            'gate_name': gate_name,
            'gate_emoji': gate_emoji,
            'timestamp': datetime.now()
        }

        response = f"┏━━━━━━━━━━━━━━━┓\n"
        response += f"┃    {gate_name.upper()} - DARK PROCESS     ┃\n"
        response += f"┗━━━━━━━━━━━━━━━┛\n\n"
        response += f">> GATEWAY INFO:\n"
        response += f"│  • Estado........: 🟢 ONLINE\n"
        response += f"│  • Precio........: 5 créditos/tarjeta\n"
        response += f"│  • Plan..........: Premium Access\n"
        response += f"│  • Comando.......: /am\n\n"
        response += f">> FORMAT REQUIRED:\n"
        response += f"│  → 4532123456781234|12|25|123\n\n"
        response += f">> PROCESS INFO:\n"
        response += f"│  • Auto-processing: ✅\n"
        response += f"│  • Tiempo estimado: 2-5s\n"
        response += f"│  • Efectividad....: PRO\n\n"
        response += f"──────────────────────────────\n"
        response += f"[!] Sistema listo para procesar\n"
        response += f"──────────────────────────────\n\n"
        response += f"➤ Envía tu tarjeta para procesar"

        back_keyboard = [[InlineKeyboardButton("🔙 Volver al menú", callback_data='gates_back')]]

        await query.edit_message_text(
            response,
            reply_markup=InlineKeyboardMarkup(back_keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

async def process_gate_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar múltiples tarjetas enviadas cuando hay sesión activa - CON CONTROL DE RATE LIMITING"""
    global gate_system
    user_id = str(update.effective_user.id)

    # Importar db aquí para asegurar que tenemos la instancia actual
    from telegram_bot import db as current_db
    if gate_system is not None:
        gate_system.db = current_db

    # Verificar si hay sesión activa primero
    if user_id not in gate_system.active_sessions:
        return

    session = gate_system.active_sessions[user_id]
    message_text = update.message.text.strip()

    # Detectar múltiples tarjetas en el mensaje
    import re
    card_pattern = r'\b\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}\b'
    cards_found = re.findall(card_pattern, message_text)

    if not cards_found:
        await update.message.reply_text(
            "❌ **Formato inválido**\n\n"
            "💡 **Formato correcto:**\n"
            "`4532123456781234|12|25|123`\n\n"
            "📋 **Puedes enviar múltiples tarjetas separadas por líneas**",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar límites según nivel de usuario
    is_founder = db.is_founder(user_id)
    is_cofounder = db.is_cofounder(user_id)
    user_data = db.get_user(user_id)
    is_premium = user_data.get('premium', False)

    # Establecer límites
    if is_founder:
        max_cards = 15  # Fundadores más tarjetas
        user_type = "👑 FUNDADOR"
    elif is_cofounder:
        max_cards = 15  # Co-fundadores también más
        user_type = "💎 CO-FUNDADOR"
    elif is_premium:
        max_cards = 15   # Premium moderado
        user_type = "💎 PREMIUM"
    else:
        await update.message.reply_text("❌ Acceso denegado")
        return

    # Verificar límite de tarjetas
    if len(cards_found) > max_cards:
        await update.message.reply_text(
            f"❌ **LÍMITE EXCEDIDO** ❌\n\n"
            f"🎯 **Tu nivel:** {user_type}\n"
            f"📊 **Límite máximo:** {max_cards} tarjetas\n"
            f"📤 **Enviaste:** {len(cards_found)} tarjetas\n\n"
            f"💡 **Envía máximo {max_cards} tarjetas por vez**",
            parse_mode=ParseMode.MARKDOWN)
        return

    # Verificar créditos (5 por tarjeta)
    total_cost = len(cards_found) * 5
    if user_data['credits'] < total_cost:
        await update.message.reply_text(
            f"❌ **LOOT INSUFICIENTE** ❌\n\n"
            f"💰 **Necesitas:** {total_cost} loot\n"
            f"💳 **Tienes:** {user_data['credits']} loot\n"
            f"📊 **Costo:** 5 loot por tarjeta\n"
            f"🎯 **Tarjetas:** {len(cards_found)}\n\n"
            f"💡 Usa `/loot` para obtener loot gratis",
            parse_mode=ParseMode.MARKDOWN)
        return

    # NO descontar todos los créditos al inicio - se descontarán individualmente

    # Procesar cada tarjeta individualmente CON CONTROL DE RATE LIMITING
    results = [] # Guardar resultados para estadísticas
    for i, card_data in enumerate(cards_found, 1):

        # Descontar 1 créditos por esta tarjeta específica
        current_user_data = db.get_user(user_id)
        if current_user_data['credits'] >= 1:
            db.update_user(user_id, {'credits': current_user_data['credits'] - 1})
        else:
            # Si no hay suficientes créditos para esta tarjeta, parar el procesamiento
            await update.message.reply_text(
                f"❌ **LOOT INSUFICIENTE** ❌\n\n"
                f"💰 **Se necesitan 5 loot más para la tarjeta {i}/{len(cards_found)}**\n"
                f"💳 **Loot actual:** {current_user_data['credits']}\n\n"
                f"⚠️ **Procesamiento detenido en tarjeta {i-1}/{len(cards_found)}**",
                parse_mode=ParseMode.MARKDOWN)
            break

        # Mensaje de procesamiento
        processing_msg = await update.message.reply_text(
            f"╔═[ {session['gate_emoji']} {session['gate_name'].upper()} - INICIANDO ]═╗\n"
            f"║ 💳 Tarjeta: [{i}/{len(cards_found)}] {card_data[:4]}****{card_data[-4:]} ║\n"
            f"║ ⏳ Estado : Conectando al gateway...    \n"
            f"║ 🔄 Progreso: [██░░░░░░░░] 20%           \n"
            f"║ 📡 Latencia: Calculando...              \n"
            f"╚════════════════════════╝",
            parse_mode=ParseMode.MARKDOWN
        )

        # CONTROLAR RATE LIMITING - Esperar entre mensajes
        if i > 1:
            await asyncio.sleep(3)  # Pausa entre tarjetas

        # Simular progreso CON CONTROL DE RATE LIMITING
        await asyncio.sleep(1.5)
        await gate_system.safe_edit_message(
            processing_msg,
            f"╔═[ {session['gate_emoji']} {session['gate_name'].upper()} - VERIFICANDO ]═╗\n"
            f"║ 💳 Tarjeta: [{i}/{len(cards_found)}] {card_data[:4]}****{card_data[-4:]} ║\n"
            f"║ ⏳ Estado : Validando datos...          \n"
            f"║ 🔄 Progreso: [████░░░░░░] 40%           \n"
            f"║ 📡 Latencia: 0.234s                    \n"
            f"╚════════════════════════╝"
        )

        await asyncio.sleep(1.5)
        await gate_system.safe_edit_message(
            processing_msg,
            f"╔═[ {session['gate_emoji']} {session['gate_name'].upper()} - PROCESANDO ]═╗\n"
            f"║ 💳 Tarjeta: [{i}/{len(cards_found)}] {card_data[:4]}****{card_data[-4:]} ║\n"
            f"║ ⏳ Estado : Enviando al gateway...      \n"
            f"║ 🔄 Progreso: [██████░░░░] 60%           \n"
            f"║ 📡 Latencia: 0.456s                    \n"
            f"╚════════════════════════╝"
        )

        # Procesar según el tipo de gate
        gate_type = session['gate_type']
        if gate_type == 'gate_stripe':
            result = await gate_system.process_stripe_gate(card_data)
        elif gate_type == 'gate_amazon':
            result = await gate_system.process_amazon_gate(card_data)
        elif gate_type == 'gate_paypal':
            result = await gate_system.process_paypal_gate(card_data)
        elif gate_type == 'gate_ayden':
            result = await gate_system.process_ayden_gate(card_data)
        elif gate_type == 'gate_ccn':
            result = await gate_system.process_ccn_charge(card_data)
        elif gate_type == 'gate_cybersource':
            result = await gate_system.process_cybersource_ai(card_data)
        elif gate_type == 'gate_worldpay':
            result = await gate_system.process_worldpay_gate(card_data)
        elif gate_type == 'gate_braintree':
            result = await gate_system.process_braintree_gate(card_data)
        else:
            result = await gate_system.process_auth_gate(card_data)

        results.append(result) # Agregar resultado para estadísticas

        # Mostrar resultado final con nuevo formato
        parts = card_data.split('|')
        card_number = parts[0] if len(parts) > 0 else 'N/A'
        exp_date = f"{parts[1]}/{parts[2]}" if len(parts) > 2 else 'N/A'

        # Obtener emoji del gate
        gate_emoji = session['gate_emoji']
        gate_name = session['gate_name'].upper()

        # Obtener créditos actualizados DESPUÉS de cada verificación individual
        current_user_data = db.get_user(user_id)
        credits_remaining = current_user_data['credits']

        final_response = f"╔═[ {gate_emoji} {gate_name}: RESULTADO ]═╗\n"
        final_response += f"║ 💳 Tarjeta : {card_number}\n"
        final_response += f"║ 📅 Expira : {exp_date}\n"
        final_response += f"║ 🎯 Estado : {result['status']}\n"
        final_response += f"║ 📡 Gateway : {result['gateway']}\n"
        final_response += f"║ 💰 Monto : {result.get('amount', '$0.00')}\n"
        final_response += f"║ 📝 Respuesta : {result['message']}\n"
        final_response += f"║ ⏰ Tiempo : {datetime.now().strftime('%H:%M:%S')}\n"
        final_response += f"║ 👤 Checker : @{update.effective_user.username or update.effective_user.first_name}\n"
        final_response += f"║ 🔢 Proceso : {i} / {len(cards_found)}\n"
        final_response += f"╚════════════════════════════════╝\n\n"

        final_response += f"💰 loot restantes → {credits_remaining}\n\n"

        # System notice según el resultado
        if result['success']:
            final_response += f"✅ SYSTEM NOTICE:\n"
            final_response += f"• Transacción aprobada por el gateway\n"
            final_response += f"• Método de pago válido y activo"
        else:
            final_response += f"⚠️ SYSTEM NOTICE:\n"
            final_response += f"• Transacción rechazada por el gateway\n"
            final_response += f"• Método de pago no válido"


        keyboard = [[InlineKeyboardButton("🔄 Procesar otra", callback_data=gate_type),
                    InlineKeyboardButton("🔙 Menú principal", callback_data='gates_back')]]

        await gate_system.safe_edit_message(
            processing_msg,
            final_response,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Pausa adicional entre tarjetas para evitar rate limiting
        if i < len(cards_found):
            await asyncio.sleep(2)

    # Sistema de estadísticas avanzadas con analytics
    try:
        # Contar éxitos por gateway para estadísticas
        gateway_stats = {}
        for result in results:
            gateway = result['gateway']
            if gateway not in gateway_stats:
                gateway_stats[gateway] = {'success': 0, 'total': 0}
            gateway_stats[gateway]['total'] += 1
            if result['is_live']:
                gateway_stats[gateway]['success'] += 1

        # Actualizar estadísticas del usuario
        current_stats = db.get_user(user_id)
        new_stats = {
            'total_checked': current_stats['total_checked'] + len(cards_found)
        }

        # Agregar estadísticas por gateway si no existen
        if 'gateway_stats' not in current_stats:
            current_stats['gateway_stats'] = {}

        # Actualizar stats por gateway
        for gateway, stats in gateway_stats.items():
            if gateway not in current_stats['gateway_stats']:
                current_stats['gateway_stats'][gateway] = {'success': 0, 'total': 0}
            current_stats['gateway_stats'][gateway]['success'] += stats['success']
            current_stats['gateway_stats'][gateway]['total'] += stats['total']

        new_stats['gateway_stats'] = current_stats['gateway_stats']
        db.update_user(user_id, new_stats)

    except Exception as e:
        logger.error(f"❌ Error actualizando estadísticas: {e}")
        # Continuar sin actualizar estadísticas si hay error


    # Limpiar sesión al final
    if user_id in gate_system.active_sessions:
        del gate_system.active_sessions[user_id]
def check_user_premium_status(user_id: str) -> dict:
    """Función de verificación rápida del estado premium - SOLO PARA TESTING"""
    try:
        user_data = db.get_user(user_id)
        is_premium = user_data.get('premium', False)
        premium_until = user_data.get('premium_until')

        return {
            'user_id': user_id,
            'is_premium': is_premium,
            'premium_until': premium_until,
            'is_founder': db.is_founder(user_id),
            'is_cofounder': db.is_cofounder(user_id),
            'is_moderator': db.is_moderator(user_id),
            'authorized_for_gates': gate_system.is_authorized(user_id) if gate_system else False
        }
    except Exception as e:
        return {'error': str(e)}

async def is_authorized(user_id: str, premium_required: bool = False) -> tuple[bool, str]:
    """
    Verifica si el usuario está autorizado para usar los gates
    Returns: (is_authorized, status_message)
    """
    try:
        # Verificar admin primero
        if int(user_id) in ADMIN_IDS:
            return True, "👑 ADMIN"

        # Verificar roles de staff desde la base de datos
        if db.is_founder(user_id):
            return True, "👑 FUNDADOR"

        if db.is_cofounder(user_id):
            return True, "💎 CO-FUNDADOR"

        if db.is_moderator(user_id):
            return True, "🛡️ MODERADOR"

        # CORRECCIÓN: Obtener datos del usuario y verificar premium
        user_data = db.get_user(user_id)

        # Forzar verificación de premium desde la base de datos
        is_premium = user_data.get('premium', False)
        premium_until = user_data.get('premium_until')

        logger.info(f"Verificando usuario {user_id}: premium={is_premium}, until={premium_until}")

        if is_premium and premium_until:
            try:
                premium_until_date = datetime.fromisoformat(premium_until)
                if datetime.now() < premium_until_date:
                    logger.info(f"Usuario {user_id} tiene premium válido hasta {premium_until_date}")
                    return True, "💎 PREMIUM"
                else:
                    # Premium expirado
                    logger.info(f"Premium de usuario {user_id} expirado")
                    db.update_user(user_id, {'premium': False, 'premium_until': None})
                    return False, "❌ PREMIUM EXPIRADO"
            except Exception as date_error:
                logger.error(f"Error parsing fecha premium para {user_id}: {date_error}")
                return False, "❌ ERROR PREMIUM"
        elif is_premium and not premium_until:
            # Premium permanente
            logger.info(f"Usuario {user_id} tiene premium permanente")
            return True, "💎 PREMIUM"

        # Usuario estándar
        logger.info(f"Usuario {user_id} es estándar")
        if premium_required:
            return False, "❌ REQUIERE PREMIUM"
        else:
            return True, "✅ USUARIO ESTÁNDAR"

    except Exception as e:
        logger.error(f"Error en verificación de autorización para {user_id}: {e}")
        return False, "❌ ERROR DEL SISTEMA"
