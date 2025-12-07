"""
Сервис пользователей
Business logic layer для работы с пользователями
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.domain.interfaces.repositories import (
    IUserRepository, UserCreateDto, UserUpdateDto, UserLoginDto, 
    UserRole
)
from src.infrastructure.security.auth import security_manager
from src.infrastructure.monitoring.logger import logger


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repo = user_repository
    
    async def register_user(self, user_data: UserCreateDto) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        try:
            # Проверка существования пользователя
            existing_user = await self.user_repo.get_by_identifier(user_data.email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            existing_user = await self.user_repo.get_by_identifier(user_data.nickname)
            if existing_user:
                raise ValueError("User with this nickname already exists")
            
            # Валидация пароля
            if not security_manager.validate_password_strength(user_data.password):
                raise ValueError("Password does not meet security requirements")
            
            # Создание пользователя
            user_id = await self.user_repo.create(user_data)
            
            # Получение созданного пользователя
            user = await self.user_repo.get_by_id(user_id)
            
            logger.info(f"User registered successfully: {user_id}", user_id=user_id)
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "User registered successfully",
                "user": user
            }
            
        except Exception as e:
            logger.error(f"User registration failed: {e}", error=str(e))
            raise
    
    async def authenticate_user(self, login_data: UserLoginDto) -> Dict[str, Any]:
        """Аутентификация пользователя"""
        try:
            # Получение пользователя
            user = await self.user_repo.get_by_identifier(login_data.identifier)
            if not user:
                raise ValueError("Invalid credentials")
            
            # Проверка активности
            if not user.get('is_active', True):
                raise ValueError("Account is deactivated")
            
            # Проверка пароля
            password_valid = await self.user_repo.verify_password(user['id'], login_data.password)
            if not password_valid:
                raise ValueError("Invalid credentials")
            
            # Создание токенов
            access_token = security_manager.create_access_token({
                "user_id": user['id'],
                "email": user['email'],
                "role": user['role']
            })
            
            refresh_token = security_manager.create_refresh_token({
                "user_id": user['id']
            })
            
            logger.info(f"User authenticated: {user['id']}", user_id=user['id'])
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "nickname": user['nickname'],
                    "email": user['email'],
                    "role": user['role']
                }
            }
            
        except Exception as e:
            logger.error(f"User authentication failed: {e}", error=str(e))
            raise
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение профиля пользователя"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return None
            
            # Получение статистики
            stats = await self.user_repo.get_stats(user_id)
            
            return {
                "user": user,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Get user profile failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def update_user_profile(self, user_id: int, update_data: UserUpdateDto) -> bool:
        """Обновление профиля пользователя"""
        try:
            success = await self.user_repo.update(user_id, update_data)
            
            if success:
                logger.info(f"User profile updated: {user_id}", user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Update user profile failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Смена пароля пользователя"""
        try:
            # Проверка старого пароля
            old_password_valid = await self.user_repo.verify_password(user_id, old_password)
            if not old_password_valid:
                raise ValueError("Current password is incorrect")
            
            # Валидация нового пароля
            if not security_manager.validate_password_strength(new_password):
                raise ValueError("New password does not meet security requirements")
            
            # Обновление пароля
            success = await self.user_repo.update_password(user_id, new_password)
            
            if success:
                logger.info(f"Password changed: {user_id}", user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Change password failed: {e}", user_id=user_id, error=str(e))
            raise
    
    async def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Поиск пользователей"""
        try:
            users = await self.user_repo.search(query, limit)
            return users
            
        except Exception as e:
            logger.error(f"Search users failed: {e}", query=query, error=str(e))
            raise
    
    async def get_users_by_role(self, role: UserRole, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение пользователей по роли"""
        try:
            users = await self.user_repo.get_by_role(role, limit, offset)
            return users
            
        except Exception as e:
            logger.error(f"Get users by role failed: {e}", role=role.value, error=str(e))
            raise
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Деактивация пользователя"""
        try:
            success = await self.user_repo.delete(user_id)
            
            if success:
                logger.info(f"User deactivated: {user_id}", user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Deactivate user failed: {e}", user_id=user_id, error=str(e))
            raise







