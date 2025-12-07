"""
Репозиторий пользователей для MariaDB
Enterprise-level repository implementation
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.domain.interfaces.repositories import (
    IUserRepository, UserCreateDto, UserUpdateDto, UserLoginDto, 
    UserRole
)
from src.infrastructure.repositiry.db_models import User as UserModel
from src.infrastructure.security.auth import security_manager
from src.infrastructure.monitoring.logger import logger


class UserRepository(IUserRepository):
    """Репозиторий пользователей с кэшированием"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.cache_prefix = "user:"
    
    async def create(self, user_data: UserCreateDto) -> int:
        """Создание пользователя"""
        try:
            # Хеширование пароля
            hashed_password = security_manager.hash_password(user_data.password)
            
            # Создание модели пользователя
            user = UserModel(
                name=user_data.name,
                nickname=user_data.nickname,
                email=user_data.email,
                password_hash=hashed_password,
                role=user_data.role.value,
                phone=user_data.phone,
                description=user_data.description,
                specification=user_data.specification,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"User created: {user.id}", user_id=user.id, nickname=user.nickname)
            return user.id
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User creation failed: {e}", error=str(e))
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        try:
            # Проверка кэша
            cache_key = f"{self.cache_prefix}id:{user_id}"
            from src.infrastructure.cache.memory_cache import memory_cache
            cached_user = memory_cache.get(cache_key)
            if cached_user:
                return cached_user
            
            # Запрос к БД
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            user_dict = self._model_to_dict(user)
            
            # Кэширование на 1 час
            memory_cache.set(cache_key, user_dict, ttl=3600)
            
            return user_dict
            
        except Exception as e:
            logger.error(f"Get user by ID failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def get_by_nickname(self, nickname: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по никнейму"""
        try:
            cache_key = f"{self.cache_prefix}nickname:{nickname}"
            from src.infrastructure.cache.memory_cache import memory_cache
            cached_user = memory_cache.get(cache_key)
            if cached_user:
                return cached_user
            
            result = await self.db.execute(
                select(UserModel).where(UserModel.nickname == nickname)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            user_dict = self._model_to_dict(user)
            memory_cache.set(cache_key, user_dict, ttl=3600)
            
            return user_dict
            
        except Exception as e:
            logger.error(f"Get user by nickname failed: {e}", nickname=nickname, error=str(e))
            raise
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email"""
        try:
            cache_key = f"{self.cache_prefix}email:{email}"
            from src.infrastructure.cache.memory_cache import memory_cache
            cached_user = memory_cache.get(cache_key)
            if cached_user:
                return cached_user
            
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            user_dict = self._model_to_dict(user)
            memory_cache.set(cache_key, user_dict, ttl=3600)
            
            return user_dict
            
        except Exception as e:
            logger.error(f"Get user by email failed: {e}", email=email, error=str(e))
            raise
    
    async def get_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email или nickname"""
        try:
            cache_key = f"{self.cache_prefix}identifier:{identifier}"
            from src.infrastructure.cache.memory_cache import memory_cache
            cached_user = memory_cache.get(cache_key)
            if cached_user:
                return cached_user
            
            result = await self.db.execute(
                select(UserModel).where(
                    or_(UserModel.email == identifier, UserModel.nickname == identifier)
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            user_dict = self._model_to_dict(user)
            memory_cache.set(cache_key, user_dict, ttl=3600)
            
            return user_dict
            
        except Exception as e:
            logger.error(f"Get user by identifier failed: {e}", identifier=identifier, error=str(e))
            raise
    
    async def update(self, user_id: int, user_data: UserUpdateDto) -> bool:
        """Обновление пользователя"""
        try:
            update_data = {}
            
            if user_data.name is not None:
                update_data['name'] = user_data.name
            if user_data.email is not None:
                update_data['email'] = user_data.email
            if user_data.phone is not None:
                update_data['phone'] = user_data.phone
            if user_data.description is not None:
                update_data['description'] = user_data.description
            if user_data.specification is not None:
                update_data['specification'] = user_data.specification
            if user_data.is_active is not None:
                update_data['is_active'] = user_data.is_active
            
            if not update_data:
                return True
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = await self.db.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            if result.rowcount > 0:
                # Очистка кэша
                self._clear_user_cache(user_id)
                logger.info(f"User updated: {user_id}", user_id=user_id)
                return True
            
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User update failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def delete(self, user_id: int) -> bool:
        """Удаление пользователя (мягкое удаление)"""
        try:
            result = await self.db.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_active=False, deleted_at=datetime.utcnow())
            )
            
            await self.db.commit()
            
            if result.rowcount > 0:
                self._clear_user_cache(user_id)
                logger.info(f"User deleted: {user_id}", user_id=user_id)
                return True
            
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User delete failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def verify_password(self, user_id: int, password: str) -> bool:
        """Проверка пароля пользователя"""
        try:
            result = await self.db.execute(
                select(UserModel.password_hash).where(UserModel.id == user_id)
            )
            password_hash = result.scalar_one_or_none()
            
            if not password_hash:
                return False
            
            return security_manager.verify_password(password, password_hash)
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """Обновление пароля пользователя"""
        try:
            hashed_password = security_manager.hash_password(new_password)
            
            result = await self.db.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(
                    password_hash=hashed_password,
                    updated_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            
            if result.rowcount > 0:
                self._clear_user_cache(user_id)
                logger.info(f"Password updated: {user_id}", user_id=user_id)
                return True
            
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password update failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def get_by_role(self, role: UserRole, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение пользователей по роли"""
        try:
            result = await self.db.execute(
                select(UserModel)
                .where(and_(UserModel.role == role.value, UserModel.is_active == True))
                .limit(limit)
                .offset(offset)
            )
            users = result.scalars().all()
            
            return [self._model_to_dict(user) for user in users]
            
        except Exception as e:
            logger.error(f"Get users by role failed: {e}", role=role.value, error=str(e))
            raise
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Поиск пользователей"""
        try:
            search_term = f"%{query}%"
            result = await self.db.execute(
                select(UserModel)
                .where(
                    and_(
                        UserModel.is_active == True,
                        or_(
                            UserModel.name.ilike(search_term),
                            UserModel.nickname.ilike(search_term),
                            UserModel.email.ilike(search_term)
                        )
                    )
                )
                .limit(limit)
            )
            users = result.scalars().all()
            
            return [self._model_to_dict(user) for user in users]
            
        except Exception as e:
            logger.error(f"User search failed: {e}", query=query, error=str(e))
            raise
    
    async def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        try:
            # Здесь можно добавить запросы для получения статистики
            # Например, количество заказов, рейтинг и т.д.
            return {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "stats": {
                    "orders_count": 0,
                    "rating": 0.0,
                    "completed_orders": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Get user stats failed: {e}", user_id=user_id, error=str(e))
            raise
    
    def _model_to_dict(self, user: UserModel) -> Dict[str, Any]:
        """Преобразование модели в словарь"""
        return {
            "id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
            "description": user.description,
            "specification": user.specification,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "deleted_at": user.deleted_at.isoformat() if user.deleted_at else None
        }
    
    def _clear_user_cache(self, user_id: int):
        """Очистка кэша пользователя"""
        from src.infrastructure.cache.memory_cache import memory_cache
        
        # Получаем пользователя для очистки всех связанных ключей
        user = memory_cache.get(f"{self.cache_prefix}id:{user_id}")
        if user:
            memory_cache.delete(f"{self.cache_prefix}id:{user_id}")
            memory_cache.delete(f"{self.cache_prefix}nickname:{user['nickname']}")
            memory_cache.delete(f"{self.cache_prefix}email:{user['email']}")
            memory_cache.delete(f"{self.cache_prefix}identifier:{user['email']}")
            memory_cache.delete(f"{self.cache_prefix}identifier:{user['nickname']}")







