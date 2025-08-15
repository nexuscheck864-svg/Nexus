import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
import json

logger = logging.getLogger(__name__)

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        self.connection_status = False
        # Obtener configuración desde variables de entorno (Secrets)
        self.connection_url = os.getenv('MONGODB_URL') or os.getenv('MONGODB_CONNECTION_STRING')
        self.db_name = os.getenv('MONGODB_DB_NAME', 'telegram_bot_db') or os.getenv('DATABASE_NAME', 'telegram_bot_db')
        self.last_connection_attempt = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        # Validar que las variables estén configuradas
        if not self.connection_url:
            logger.error("❌ MONGODB_URL no encontrado en variables de entorno")
            logger.info("💡 Configura MONGODB_URL en Secrets con tu cadena de conexión de MongoDB Atlas")
        elif not self._validate_mongodb_url(self.connection_url):
            logger.error("❌ La MONGODB_URL proporcionada no es válida.")

        self.staff_roles = {}
        self.check_chats = {}
        self.pending_checks = {}
        self.deleted_links = {}
        self.admin_log_channels = {}
        self.admin_action_logs = []

    async def connect(self) -> bool:
        """Conectar a MongoDB Atlas usando variables de entorno de Secrets"""
        try:
            # Verificar variables de entorno requeridas
            if not self.connection_url:
                logger.warning("⚠️ MONGODB_URL no configurado - usando modo local")
                return False

            if not self._validate_mongodb_url(self.connection_url):
                logger.warning("⚠️ MONGODB_URL inválida - usando modo local")
                return False

            # Ocultar información sensible en logs
            safe_url = self.connection_url.replace(self.connection_url.split('@')[0].split('//')[1], '***:***')
            logger.info(f"🔄 Conectando a MongoDB Atlas: {safe_url.split('@')[1] if '@' in safe_url else 'Atlas'}")
            self.last_connection_attempt = datetime.now()

            # Configurar cliente con timeouts optimizados
            self.client = MongoClient(
                self.connection_url,
                serverSelectionTimeoutMS=5000,  # 5 segundos timeout
                connectTimeoutMS=10000,  # 10 segundos para conectar
                socketTimeoutMS=30000,   # 30 segundos para operaciones
                maxPoolSize=10,          # Pool de conexiones
                retryWrites=True         # Reintentar escrituras
            )

            # Verificar conexión
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]

            # Configurar colecciones
            self.collections = {
                'users': self.db.users,
                'staff': self.db.staff,
                'founders': self.db.founders,
                'sessions': self.db.sessions,
                'logs': self.db.logs,
                'stats': self.db.stats
            }

            # Crear índices para optimización
            await self._create_indexes()

            self.connection_status = True
            self.reconnect_attempts = 0
            logger.info("✅ Conectado exitosamente a MongoDB Atlas")
            return True

        except Exception as e:
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "bad auth" in error_msg:
                logger.warning("⚠️ Error de autenticación MongoDB - verificar credenciales")
                logger.warning("💡 Revisa usuario/contraseña en MONGODB_URL")
            elif "network" in error_msg or "timeout" in error_msg:
                logger.warning("⚠️ Error de red MongoDB - verificar conexión")
            else:
                logger.warning(f"⚠️ Error MongoDB: {str(e)[:100]}")

            self.connection_status = False
            # Forzar fallback a archivo local cuando MongoDB falla
            logger.info("🔄 Usando modo fallback con archivo local")
            return False

    async def _create_indexes(self):
        """Crear índices para optimizar consultas"""
        try:
            # Índice para usuarios
            self.collections['users'].create_index("user_id", unique=True)
            self.collections['users'].create_index("premium_until")

            # Índice para staff
            self.collections['staff'].create_index("user_id", unique=True)

            # Índice para logs
            self.collections['logs'].create_index("timestamp")
            self.collections['logs'].create_index("user_id")

            logger.info("✅ Índices de MongoDB creados correctamente")
        except Exception as e:
            logger.error(f"Error creando índices: {e}")

    def _validate_mongodb_url(self, url: str) -> bool:
        """Validar formato básico de URL de MongoDB"""
        try:
            import re

            # Patrones válidos para MongoDB
            patterns = [
                r'^mongodb\+srv://[^:]+:[^@]+@[^/]+\.mongodb\.net/',  # Atlas SRV
                r'^mongodb://[^:]+:[^@]+@[^/]+/',  # MongoDB estándar
                r'^mongodb://[^/]+/',  # MongoDB sin credenciales
                r'^mongodb\+srv://[^/]+\.mongodb\.net/'  # Atlas SRV sin credenciales
            ]

            for pattern in patterns:
                if re.match(pattern, url):
                    logger.info("✅ Formato de URL MongoDB válido")
                    return True

            logger.error("❌ Formato de URL MongoDB inválido")
            logger.error("💡 Formatos válidos:")
            logger.error("   - mongodb+srv://user:pass@cluster.mongodb.net/dbname")
            logger.error("   - mongodb://user:pass@host:port/dbname")
            return False

        except Exception as e:
            logger.error(f"Error validando URL: {e}")
            return False

    async def ensure_connection(self) -> bool:
        """Asegurar que hay conexión activa"""
        if not self.connection_status or not self.client:
            return await self.connect()

        try:
            # Verificar conexión con ping
            self.client.admin.command('ping')
            return True
        except:
            self.connection_status = False
            return await self.auto_reconnect()

    async def auto_reconnect(self) -> bool:
        """Reconexión automática"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"❌ Máximo de intentos de reconexión alcanzado ({self.max_reconnect_attempts})")
            return False

        self.reconnect_attempts += 1
        logger.info(f"🔄 Intento de reconexión #{self.reconnect_attempts}")

        # Esperar antes de reconectar
        await asyncio.sleep(2 ** self.reconnect_attempts)  # Backoff exponencial

        return await self.connect()

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Obtener datos de usuario con fallback a archivo local"""
        try:
            if self.connection_status and self.collections:
                user = self.collections['users'].find_one({"user_id": user_id})
                if user:
                    # Remover _id de MongoDB para compatibilidad
                    user.pop('_id', None)
                    # Asegurar campos obligatorios
                    user.setdefault('total_checked', 0)
                    user.setdefault('total_generated', 0)
                    user.setdefault('credits', 10)
                    user.setdefault('warns', 0)
                    user.setdefault('premium', False)
                    return user
                else:
                    # Crear usuario nuevo en MongoDB
                    default_user = self._get_default_user(user_id)
                    try:
                        self.collections['users'].insert_one(default_user.copy())
                        return default_user
                    except Exception as insert_error:
                        logger.warning(f"Error insertando usuario en MongoDB: {insert_error}")
                        return self._get_user_from_file(user_id)
            else:
                # Fallback a archivo local
                return self._get_user_from_file(user_id)

        except Exception as e:
            logger.warning(f"Error obteniendo usuario {user_id} de MongoDB, usando fallback: {e}")
            return self._get_user_from_file(user_id)

    def _get_default_user(self, user_id: str) -> Dict[str, Any]:
        """Usuario por defecto"""
        return {
            'user_id': user_id,
            'credits': 10,
            'total_generated': 0,
            'total_checked': 0,
            'join_date': datetime.now().isoformat(),
            'premium': False,
            'premium_until': None,
            'last_bonus': None,
            'warnings': 0,
            'banned': False
        }

    def _get_user_from_file(self, user_id: str) -> Dict[str, Any]:
        """Obtener usuario desde archivo local como fallback"""
        try:
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r') as f:
                    data = json.load(f)
                    users = data.get('users', {})
                    if user_id in users:
                        return users[user_id]

            # Si no existe, crear usuario por defecto
            default_user = self._get_default_user(user_id)
            self._save_user_to_file(user_id, default_user)
            return default_user

        except Exception as e:
            logger.error(f"Error leyendo archivo local: {e}")
            return self._get_default_user(user_id)

    def _save_user_to_file(self, user_id: str, user_data: Dict[str, Any]):
        """Guardar usuario en archivo local como fallback"""
        try:
            data = {}
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r') as f:
                    data = json.load(f)

            if 'users' not in data:
                data['users'] = {}

            data['users'][user_id] = user_data

            with open('bot_data.json', 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error guardando en archivo local: {e}")

    def update_user(self, user_id: str, data: Dict[str, Any]):
        """Actualizar datos de usuario con fallback"""
        try:
            # Actualizar timestamp
            data['updated_at'] = datetime.now().isoformat()

            if self.connection_status and self.collections:
                # Intentar actualizar en MongoDB
                result = self.collections['users'].update_one(
                    {"user_id": user_id},
                    {"$set": data},
                    upsert=True
                )
                if result.modified_count == 0 and result.upserted_id is None:
                    logger.warning(f"No se actualizó ningún documento para usuario {user_id}")
            else:
                # Fallback a archivo local
                current_user = self._get_user_from_file(user_id)
                current_user.update(data)
                self._save_user_to_file(user_id, current_user)

        except Exception as e:
            logger.warning(f"Error actualizando usuario {user_id} en MongoDB, usando fallback: {e}")
            # Fallback a archivo local
            try:
                current_user = self._get_user_from_file(user_id)
                current_user.update(data)
                self._save_user_to_file(user_id, current_user)
                logger.info(f"Usuario {user_id} actualizado exitosamente en archivo local")
            except Exception as e2:
                logger.error(f"Error crítico actualizando usuario {user_id}: {e2}")
                # Crear usuario con datos mínimos como último recurso
                try:
                    default_user = self._get_default_user(user_id)
                    default_user.update(data)
                    self._save_user_to_file(user_id, default_user)
                    logger.info(f"Usuario {user_id} creado con datos por defecto")
                except Exception as e3:
                    logger.error(f"Error catastrófico creando usuario {user_id}: {e3}")

    def is_founder(self, user_id: str) -> bool:
        """Verificar si es fundador"""
        try:
            if not self.connection_status:
                return False

            founder = self.collections['founders'].find_one({"user_id": user_id})
            return founder is not None

        except Exception as e:
            logger.error(f"Error verificando fundador {user_id}: {e}")
            return False

    def add_founder(self, user_id: str, added_by: str = None):
        """Agregar fundador"""
        try:
            if not self.connection_status:
                return False

            founder_data = {
                "user_id": user_id,
                "added_at": datetime.now().isoformat(),
                "added_by": added_by,
                "level": 1
            }

            self.collections['founders'].update_one(
                {"user_id": user_id},
                {"$set": founder_data},
                upsert=True
            )
            return True

        except Exception as e:
            logger.error(f"Error agregando fundador {user_id}: {e}")
            return False

    def get_staff_role(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener rol de staff"""
        try:
            if not self.connection_status:
                return None

            staff = self.collections['staff'].find_one({"user_id": user_id})
            if staff:
                staff.pop('_id', None)
            return staff

        except Exception as e:
            logger.error(f"Error obteniendo staff {user_id}: {e}")
            return None

    def set_staff_role(self, user_id: str, role: str, assigned_by: str = None):
        """Asignar rol de staff"""
        try:
            if not self.connection_status:
                return False

            staff_data = {
                "user_id": user_id,
                "role": role,
                "assigned_at": datetime.now().isoformat(),
                "assigned_by": assigned_by
            }

            self.collections['staff'].update_one(
                {"user_id": user_id},
                {"$set": staff_data},
                upsert=True
            )
            return True

        except Exception as e:
            logger.error(f"Error asignando staff {user_id}: {e}")
            return False

    def log_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Registrar acción en logs"""
        try:
            if not self.connection_status:
                return

            log_entry = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }

            self.collections['logs'].insert_one(log_entry)

        except Exception as e:
            logger.error(f"Error registrando acción: {e}")

    def get_all_by_role(self, role: str) -> list:
        """Obtener todos los usuarios de un rol específico"""
        try:
            if not self.connection_status:
                return []

            staff_members = self.collections['staff'].find({"role": role})
            return [staff['user_id'] for staff in staff_members]

        except Exception as e:
            logger.error(f"Error obteniendo usuarios por rol {role}: {e}")
            return []

    def load_data(self):
        """Método de compatibilidad - recargar datos desde MongoDB"""
        try:
            # Este método existe para compatibilidad con el sistema anterior
            # En MongoDB, los datos ya están siempre actualizados
            if not self.connection_status:
                asyncio.create_task(self.ensure_connection())
            logger.info("🔄 Datos recargados desde MongoDB")
        except Exception as e:
            logger.error(f"Error recargando datos: {e}")

    def save_data(self):
        """Método de compatibilidad - guardar datos en MongoDB"""
        try:
            # Este método existe para compatibilidad con el sistema anterior
            # En MongoDB, los datos se guardan automáticamente
            logger.info("💾 Datos guardados en MongoDB")
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")

    def is_cofounder(self, user_id: str) -> bool:
        """Verificar si el usuario es co-fundador"""
        try:
            if not self.connection_status:
                return False

            staff = self.collections['staff'].find_one({"user_id": user_id, "role": "2"})
            return staff is not None

        except Exception as e:
            logger.error(f"Error verificando co-fundador {user_id}: {e}")
            return False

    def is_moderator(self, user_id: str) -> bool:
        """Verificar si el usuario es moderador"""
        try:
            if not self.connection_status:
                return False

            staff = self.collections['staff'].find_one({"user_id": user_id, "role": "3"})
            return staff is not None

        except Exception as e:
            logger.error(f"Error verificando moderador {user_id}: {e}")
            return False

    def increment_mod_warns(self, user_id: str) -> int:
        """Incrementar contador de warns para moderadores"""
        try:
            if not self.connection_status:
                return 0

            result = self.collections['staff'].update_one(
                {"user_id": user_id},
                {"$inc": {"warn_count": 1}},
                upsert=False
            )

            if result.modified_count > 0:
                staff = self.collections['staff'].find_one({"user_id": user_id})
                return staff.get('warn_count', 0) if staff else 0
            else:
                return 0

        except Exception as e:
            logger.error(f"Error incrementando warns de moderador {user_id}: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales"""
        try:
            if not self.connection_status:
                return {}

            stats = {
                'total_users': self.collections['users'].count_documents({}),
                'premium_users': self.collections['users'].count_documents({"premium": True}),
                'total_staff': self.collections['staff'].count_documents({}),
                'total_founders': self.collections['founders'].count_documents({}),
                'total_logs': self.collections['logs'].count_documents({}),
                'connection_status': self.connection_status,
                'last_connection': self.last_connection_attempt.isoformat() if self.last_connection_attempt else None
            }

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    async def cleanup_old_data(self, days: int = 30, deep_clean: bool = False) -> Dict[str, int]:
        """Limpiar datos antiguos con opción de limpieza profunda"""
        try:
            if not self.connection_status:
                await self.ensure_connection()

            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()

            results = {}

            # Limpiar logs antiguos
            logs_result = self.collections['logs'].delete_many({
                "timestamp": {"$lt": cutoff_iso}
            })
            results['logs_deleted'] = logs_result.deleted_count

            # Limpiar sesiones expiradas
            sessions_result = self.collections['sessions'].delete_many({
                "expires_at": {"$lt": cutoff_iso}
            })
            results['sessions_deleted'] = sessions_result.deleted_count

            if deep_clean:
                # Limpieza profunda: más criterios de eliminación

                # Limpiar todos los logs más antiguos (más agresivo)
                all_logs_result = self.collections['logs'].delete_many({
                    "timestamp": {"$lt": cutoff_iso}
                })
                results['all_logs_deleted'] = all_logs_result.deleted_count

                # Limpiar usuarios inactivos (criterios más amplios)
                inactive_users_broad = self.collections['users'].delete_many({
                    "$and": [
                        {"premium": False},
                        {"$or": [
                            {"updated_at": {"$lt": cutoff_iso}},
                            {"last_bonus": {"$lt": cutoff_iso}},
                            {"$and": [{"credits": {"$lt": 10}}, {"total_generated": {"$lt": 5}}]}
                        ]}
                    ]
                })
                results['inactive_users_deleted'] = inactive_users_broad.deleted_count

                # Limpiar datos de staff inactivos (solo si es muy antiguo)
                very_old_cutoff = datetime.now() - timedelta(days=days*3)
                old_staff_result = self.collections['staff'].delete_many({
                    "assigned_at": {"$lt": very_old_cutoff.isoformat()}
                })
                results['old_staff_deleted'] = old_staff_result.deleted_count

            else:
                # Limpieza estándar
                inactive_users = self.collections['users'].delete_many({
                    "premium": False,
                    "updated_at": {"$lt": cutoff_iso},
                    "credits": {"$lt": 5}
                })
                results['inactive_users_deleted'] = inactive_users.deleted_count

            logger.info(f"✅ Limpieza {'profunda' if deep_clean else 'estándar'} completada: {results}")
            return results

        except Exception as e:
            logger.error(f"Error en limpieza de datos: {e}")
            return {}

    async def cleanup_specific_collection(self, collection_name: str, filter_criteria: Dict = None, days: int = 30) -> Dict[str, int]:
        """Limpiar una colección específica con criterios personalizados"""
        try:
            if not self.connection_status:
                await self.ensure_connection()

            if collection_name not in self.collections:
                logger.error(f"Colección '{collection_name}' no existe")
                return {}

            collection = self.collections[collection_name]

            # Criterios por defecto basados en fecha
            if filter_criteria is None:
                cutoff_date = datetime.now() - timedelta(days=days)
                cutoff_iso = cutoff_date.isoformat()

                # Criterios por defecto según la colección
                if collection_name == 'logs':
                    filter_criteria = {"timestamp": {"$lt": cutoff_iso}}
                elif collection_name == 'sessions':
                    filter_criteria = {"expires_at": {"$lt": cutoff_iso}}
                elif collection_name == 'users':
                    filter_criteria = {
                        "premium": False,
                        "updated_at": {"$lt": cutoff_iso},
                        "credits": {"$lt": 5}
                    }
                else:
                    # Para otras colecciones, intentar usar timestamp genérico
                    filter_criteria = {"$or": [
                        {"created_at": {"$lt": cutoff_iso}},
                        {"timestamp": {"$lt": cutoff_iso}},
                        {"updated_at": {"$lt": cutoff_iso}}
                    ]}

            # Ejecutar eliminación
            result = collection.delete_many(filter_criteria)

            results = {
                'collection': collection_name,
                'deleted_count': result.deleted_count,
                'criteria_used': str(filter_criteria)
            }

            logger.info(f"✅ Limpieza específica de {collection_name}: {result.deleted_count} documentos eliminados")
            return results

        except Exception as e:
            logger.error(f"Error en limpieza específica de {collection_name}: {e}")
            return {}

    def get_connection_info(self) -> Dict[str, Any]:
        """Información de conexión"""
        return {
            'connected': self.connection_status,
            'database': self.db_name,
            'last_attempt': self.last_connection_attempt.isoformat() if self.last_connection_attempt else None,
            'reconnect_attempts': self.reconnect_attempts,
            'max_attempts': self.max_reconnect_attempts,
            'collections': list(self.collections.keys()) if self.collections else []
        }

    async def restore_from_backup(self, backup_file: str) -> Dict[str, int]:
        """Restaurar datos desde archivo de respaldo"""
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_file}")

            if not self.connection_status:
                await self.ensure_connection()

            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            results = {}

            # Restaurar usuarios
            if 'users' in backup_data:
                for user_data in backup_data['users']:
                    self.collections['users'].update_one(
                        {"user_id": user_data['user_id']},
                        {"$set": user_data},
                        upsert=True
                    )
                results['users_restored'] = len(backup_data['users'])

            # Restaurar staff
            if 'staff' in backup_data:
                for staff_data in backup_data['staff']:
                    self.collections['staff'].update_one(
                        {"user_id": staff_data['user_id']},
                        {"$set": staff_data},
                        upsert=True
                    )
                results['staff_restored'] = len(backup_data['staff'])

            # Restaurar fundadores
            if 'founders' in backup_data:
                for founder_data in backup_data['founders']:
                    self.collections['founders'].update_one(
                        {"user_id": founder_data['user_id']},
                        {"$set": founder_data},
                        upsert=True
                    )
                results['founders_restored'] = len(backup_data['founders'])

            logger.info(f"✅ Respaldo restaurado exitosamente: {results}")
            return results

        except Exception as e:
            logger.error(f"Error restaurando respaldo: {e}")
            raise e

    async def close_connection(self):
        """Cerrar conexión"""
        try:
            if self.client:
                self.client.close()
                self.connection_status = False
                logger.info("✅ Conexión a MongoDB cerrada")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")

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

    def save_deleted_link(self, user_id: str, username: str, chat_id: str, message_text: str):
        """Guardar información de link eliminado"""
        try:
            link_id = str(len(self.deleted_links) + 1).zfill(6)

            self.deleted_links[link_id] = {
                'user_id': user_id,
                'username': username,
                'chat_id': chat_id,
                'message_content': message_text,
                'deleted_at': datetime.now().isoformat(),
                'detected_links': self.extract_links_from_text(message_text)
            }
            return link_id
        except Exception as e:
            logger.error(f"Error guardando link eliminado: {e}")
            return None

    def get_deleted_links_by_user(self, user_id: str) -> list:
        """Obtener historial de links eliminados de un usuario"""
        try:
            user_links = []
            for link_id, data in self.deleted_links.items():
                if data['user_id'] == user_id:
                    user_links.append({
                        'id': link_id,
                        'deleted_at': data['deleted_at'],
                        'links': data['detected_links'],
                        'message': data['message_content'][:100] + '...' if len(data['message_content']) > 100 else data['message_content']
                    })

            # Ordenar por fecha más reciente
            user_links.sort(key=lambda x: x['deleted_at'], reverse=True)
            return user_links
        except Exception as e:
            logger.error(f"Error obteniendo links eliminados: {e}")
            return []

    # Métodos de compatibilidad con el sistema anterior
    def is_maintenance(self) -> bool:
        """Verificar si el bot está en mantenimiento"""
        try:
            if not self.connection_status:
                return False

            # Obtener configuración de mantenimiento desde MongoDB
            config = self.collections.get('config', {})
            if hasattr(config, 'find_one'):
                maintenance_config = config.find_one({"type": "maintenance"})
                return maintenance_config.get('active', False) if maintenance_config else False
            return False
        except Exception as e:
            logger.error(f"Error verificando mantenimiento: {e}")
            return False

    def set_maintenance(self, status: bool, message: str = ""):
        """Activar/desactivar modo mantenimiento"""
        try:
            if not self.connection_status:
                return

            maintenance_config = {
                "type": "maintenance",
                "active": status,
                "message": message,
                "updated_at": datetime.now().isoformat()
            }

            if 'config' not in self.collections:
                self.collections['config'] = self.db.config

            self.collections['config'].update_one(
                {"type": "maintenance"},
                {"$set": maintenance_config},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error configurando mantenimiento: {e}")

    def is_housemode(self, chat_id: str) -> bool:
        """Verificar si el chat está en modo casa"""
        try:
            if not self.connection_status:
                return False

            if 'housemode' not in self.collections:
                self.collections['housemode'] = self.db.housemode

            config = self.collections['housemode'].find_one({"chat_id": chat_id})
            return config.get('active', False) if config else False
        except Exception as e:
            logger.error(f"Error verificando housemode: {e}")
            return False

    def set_housemode(self, chat_id: str, status: bool, reason: str = ""):
        """Activar/desactivar modo casa (housemode)"""
        try:
            if not self.connection_status:
                return

            if 'housemode' not in self.collections:
                self.collections['housemode'] = self.db.housemode

            housemode_config = {
                "chat_id": chat_id,
                "active": status,
                "reason": reason,
                "activated_at": datetime.now().isoformat()
            }

            self.collections['housemode'].update_one(
                {"chat_id": chat_id},
                {"$set": housemode_config},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error configurando housemode: {e}")

    def get_housemode_reason(self, chat_id: str) -> str:
        """Obtener razón del modo casa"""
        try:
            if not self.connection_status:
                return ""

            if 'housemode' not in self.collections:
                self.collections['housemode'] = self.db.housemode

            config = self.collections['housemode'].find_one({"chat_id": chat_id})
            return config.get('reason', '') if config else ""
        except Exception as e:
            logger.error(f"Error obteniendo razón housemode: {e}")
            return ""

    def is_user_locked(self, user_id: str) -> bool:
        """Verificar si usuario está bloqueado por seguridad"""
        try:
            if not self.connection_status:
                return False

            if 'security' not in self.collections:
                self.collections['security'] = self.db.security

            security_data = self.collections['security'].find_one({"user_id": user_id})
            if not security_data:
                return False

            lock_until = security_data.get('locked_until')
            if lock_until:
                lock_time = datetime.fromisoformat(lock_until)
                if datetime.now() < lock_time:
                    return True
                else:
                    # Desbloquear automáticamente
                    self.collections['security'].update_one(
                        {"user_id": user_id},
                        {"$unset": {"locked_until": ""}}
                    )
            return False
        except Exception as e:
            logger.error(f"Error verificando bloqueo de usuario: {e}")
            return False

    def lock_user(self, user_id: str, duration_minutes: int = 30, reason: str = ""):
        """Bloquear usuario temporalmente"""
        try:
            if not self.connection_status:
                return

            if 'security' not in self.collections:
                self.collections['security'] = self.db.security

            lock_until = datetime.now() + timedelta(minutes=duration_minutes)

            security_data = {
                "user_id": user_id,
                "locked_until": lock_until.isoformat(),
                "lock_reason": reason,
                "locked_at": datetime.now().isoformat()
            }

            self.collections['security'].update_one(
                {"user_id": user_id},
                {"$set": security_data},
                upsert=True
            )

            self.log_action(user_id, 'USER_LOCKED', {
                "duration_minutes": duration_minutes,
                "reason": reason
            })
        except Exception as e:
            logger.error(f"Error bloqueando usuario: {e}")

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Verificar si usuario tiene permiso específico"""
        try:
            if not self.connection_status:
                return False

            if 'permissions' not in self.collections:
                self.collections['permissions'] = self.db.permissions

            perm_data = self.collections['permissions'].find_one({"user_id": user_id})
            if not perm_data:
                return False

            return perm_data.get('permissions', {}).get(permission, False)
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return False

    def set_user_permission(self, user_id: str, permission: str, granted: bool = True):
        """Establecer permisos específicos para usuario"""
        try:
            if not self.connection_status:
                return

            if 'permissions' not in self.collections:
                self.collections['permissions'] = self.db.permissions

            self.collections['permissions'].update_one(
                {"user_id": user_id},
                {"$set": {f"permissions.{permission}": granted}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error configurando permisos: {e}")

    def log_security_event(self, user_id: str, event_type: str, details: str):
        """Registrar evento de seguridad"""
        try:
            if not self.connection_status:
                return

            if 'security_logs' not in self.collections:
                self.collections['security_logs'] = self.db.security_logs

            log_entry = {
                "user_id": user_id,
                "event_type": event_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }

            self.collections['security_logs'].insert_one(log_entry)
        except Exception as e:
            logger.error(f"Error registrando evento de seguridad: {e}")

    def get_admin_log_channel(self, group_id: str):
        """Obtener canal de logs administrativos"""
        try:
            if not self.connection_status:
                return None

            if 'admin_channels' not in self.collections:
                self.collections['admin_channels'] = self.db.admin_channels

            config = self.collections['admin_channels'].find_one({"group_id": group_id})
            return config if config else None
        except Exception as e:
            logger.error(f"Error obteniendo canal admin: {e}")
            return None

    def set_admin_log_channel(self, group_id: str, admin_channel_id: str):
        """Configurar canal de logs administrativos"""
        try:
            if not self.connection_status:
                return

            if 'admin_channels' not in self.collections:
                self.collections['admin_channels'] = self.db.admin_channels

            config = {
                "group_id": group_id,
                "channel_id": admin_channel_id,
                "configured_at": datetime.now().isoformat(),
                "active": True
            }

            self.collections['admin_channels'].update_one(
                {"group_id": group_id},
                {"$set": config},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error configurando canal admin: {e}")

    def log_admin_action(self, action_type: str, admin_user, target_user_id: str, reason: str, group_id: str, additional_data: dict = None):
        """Registrar acción administrativa en logs"""
        try:
            if not self.connection_status:
                return None

            if 'admin_logs' not in self.collections:
                self.collections['admin_logs'] = self.db.admin_logs

            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action_type': action_type,
                'admin_id': str(admin_user.id),
                'admin_name': admin_user.first_name or "Usuario",
                'admin_username': f"@{admin_user.username}" if admin_user.username else "Sin username",
                'target_user_id': str(target_user_id),
                'reason': str(reason),
                'group_id': str(group_id),
                'additional_data': additional_data or {}
            }

            self.collections['admin_logs'].insert_one(log_entry)
            return log_entry
        except Exception as e:
            logger.error(f"Error registrando acción admin: {e}")
            return None

    def get_check_chats(self, group_id: str):
        """Obtener configuración de chats para /check"""
        try:
            if not self.connection_status:
                return None

            if 'check_config' not in self.collections:
                self.collections['check_config'] = self.db.check_config

            config = self.collections['check_config'].find_one({"group_id": group_id})
            return config if config else None
        except Exception as e:
            logger.error(f"Error obteniendo configuración check: {e}")
            return None

    def set_check_chats(self, group_id: str, verification_chat: str, publication_chat: str):
        """Configurar chats para el sistema /check"""
        try:
            if not self.connection_status:
                return

            if 'check_config' not in self.collections:
                self.collections['check_config'] = self.db.check_config

            config = {
                'group_id': group_id,
                'verification_chat': verification_chat,
                'publication_chat': publication_chat,
                'configured_at': datetime.now().isoformat()
            }

            self.collections['check_config'].update_one(
                {"group_id": group_id},
                {"$set": config},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error configurando chats check: {e}")

    def add_pending_check(self, check_id: str, user_id: str, username: str, image_file_id: str, group_id: str):
        """Agregar verificación pendiente"""
        try:
            if not self.connection_status:
                return

            if 'pending_checks' not in self.collections:
                self.collections['pending_checks'] = self.db.pending_checks

            check_data = {
                'check_id': check_id,
                'user_id': user_id,
                'username': username,
                'image_file_id': image_file_id,
                'group_id': group_id,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }

            self.collections['pending_checks'].insert_one(check_data)
        except Exception as e:
            logger.error(f"Error agregando verificación pendiente: {e}")

    def get_pending_check(self, check_id: str):
        """Obtener verificación pendiente"""
        try:
            if not self.connection_status:
                return None

            if 'pending_checks' not in self.collections:
                self.collections['pending_checks'] = self.db.pending_checks

            check = self.collections['pending_checks'].find_one({"check_id": check_id})
            return check if check else None
        except Exception as e:
            logger.error(f"Error obteniendo verificación pendiente: {e}")
            return None

    def update_check_status(self, check_id: str, status: str, admin_id: str = None):
        """Actualizar estado de verificación"""
        try:
            if not self.connection_status:
                return

            if 'pending_checks' not in self.collections:
                self.collections['pending_checks'] = self.db.pending_checks

            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }

            if admin_id:
                update_data['admin_id'] = admin_id
                update_data['processed_at'] = datetime.now().isoformat()

            self.collections['pending_checks'].update_one(
                {"check_id": check_id},
                {"$set": update_data}
            )
        except Exception as e:
            logger.error(f"Error actualizando estado de verificación: {e}")

    def remove_staff_role(self, user_id: str):
        """Remover rol de staff"""
        try:
            if not self.connection_status:
                return False

            result = self.collections['staff'].delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removiendo staff {user_id}: {e}")
            return False

    # Propiedades de compatibilidad con setter
    def _get_staff_roles_dict(self):
        """Obtener staff_roles como diccionario para compatibilidad"""
        try:
            if not self.connection_status:
                return {}

            if 'staff' not in self.collections:
                return {}

            staff_data = {}
            for staff in self.collections['staff'].find():
                user_id = staff['user_id']
                staff_data[user_id] = {
                    'role': staff['role'],
                    'assigned_date': staff.get('assigned_at', ''),
                    'warn_count': staff.get('warn_count', 0)
                }
            return staff_data
        except Exception as e:
            logger.error(f"Error obteniendo staff_roles: {e}")
            return {}

    def _get_users_dict(self):
        """Obtener users como diccionario para compatibilidad"""
        try:
            if not self.connection_status:
                return {}

            if 'users' not in self.collections:
                return {}

            users_data = {}
            for user in self.collections['users'].find():
                user_id = user['user_id']
                user.pop('_id', None)
                users_data[user_id] = user
            return users_data
        except Exception as e:
            logger.error(f"Error obteniendo users: {e}")
            return {}

    # Simular atributos como diccionarios para compatibilidad total
    def __getattr__(self, name):
        """Compatibilidad para acceso a atributos como diccionarios"""
        if name == 'staff_roles':
            return self._get_staff_roles_dict()
        elif name == 'users':
            return self._get_users_dict()
        elif name == 'bot_maintenance':
            return self.is_maintenance()
        elif name == 'maintenance_message':
            try:
                if not self.connection_status:
                    return ""
                if 'config' not in self.collections:
                    self.collections['config'] = self.db.config
                maintenance_config = self.collections['config'].find_one({"type": "maintenance"})
                return maintenance_config.get('message', '') if maintenance_config else ""
            except:
                return ""
        elif name == 'housemode_chats':
            return {}  # Placeholder para compatibilidad
        elif name == 'permissions':
            return {}  # Placeholder para compatibilidad  
        elif name == 'security_settings':
            return {}  # Placeholder para compatibilidad
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Función para migrar datos existentes
def migrate_json_to_mongodb_sync(json_file: str = 'bot_data.json'):
    """Migrar datos del archivo JSON a MongoDB (versión sincrónica)"""
    try:
        if not os.path.exists(json_file):
            logger.info("No hay archivo JSON para migrar")
            return

        with open(json_file, 'r') as f:
            data = json.load(f)

        mongo_db = MongoDatabase()

        # Conectar de forma sincrónica usando el cliente directo
        if not mongo_db.connection_url:
            logger.error("No se pudo migrar: MONGODB_URL no configurado")
            return

        try:
            # Crear cliente temporal para migración
            client = MongoClient(
                mongo_db.connection_url,
                serverSelectionTimeoutMS=5000
            )
            client.admin.command('ping')
            db = client[mongo_db.db_name]

            users_data = data.get('users', {})
            migrated_count = 0

            for user_id, user_data in users_data.items():
                user_data['user_id'] = user_id
                db.users.update_one(
                    {"user_id": user_id},
                    {"$set": user_data},
                    upsert=True
                )
                migrated_count += 1

            logger.info(f"✅ Migrados {migrated_count} usuarios a MongoDB")

            # Renombrar archivo original como backup
            backup_name = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(json_file, backup_name)
            logger.info(f"📁 Archivo original respaldado como: {backup_name}")

            client.close()

        except Exception as e:
            logger.error(f"Error conectando para migración: {e}")

    except Exception as e:
        logger.error(f"Error en migración: {e}")
async def migrate_json_to_mongodb(json_file: str = 'bot_data.json'):
    """Migrar datos del archivo JSON a MongoDB"""
    try:
        if not os.path.exists(json_file):
            logger.info("No hay archivo JSON para migrar")
            return

        with open(json_file, 'r') as f:
            data = json.load(f)

        mongo_db = MongoDatabase()
        await mongo_db.connect()

        if not mongo_db.connection_status:
            logger.error("No se pudo conectar a MongoDB para migración")
            return

        users_data = data.get('users', {})
        migrated_count = 0

        for user_id, user_data in users_data.items():
            user_data['user_id'] = user_id
            mongo_db.collections['users'].update_one(
                {"user_id": user_id},
                {"$set": user_data},
                upsert=True
            )
            migrated_count += 1

        logger.info(f"✅ Migrados {migrated_count} usuarios a MongoDB")

        # Renombrar archivo original como backup
        backup_name = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(json_file, backup_name)
        logger.info(f"📁 Archivo original respaldado como: {backup_name}")

        await mongo_db.close_connection()

    except Exception as e:
        logger.error(f"Error en migración: {e}")
