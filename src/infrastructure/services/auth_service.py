from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
from jose import JWTError, jwt

from src.config import settings
from src.domain.entity.userentity import UserPrivate
from src.infrastructure.repositiry.user_repository import UserRepository

ALGORITHM = "HS256"


def decode_access_token(token: str, *, secret_key: Optional[str] = None) -> Dict[str, Any]:
    """Decode JWT access token with the unified application secret."""
    payload = jwt.decode(
        token,
        (secret_key or settings.secret_key),
        algorithms=[ALGORITHM],
    )
    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise JWTError("Invalid token type")
    return payload

class AuthService:
    def __init__(self, secret_key: str, user_repo: UserRepository):
        self.secret_key = secret_key
        self.user_repo = user_repo

    def _create_token(self, data: dict, expires_delta: timedelta, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        return self._create_token(data, delta, token_type="access")

    def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        delta = expires_delta or timedelta(days=settings.refresh_token_expire_days)
        return self._create_token(data, delta, token_type="refresh")

    def decode_token(self, token: str):
        return jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        payload = self.decode_token(token)
        if payload.get("type") != "refresh":
            raise JWTError("Invalid refresh token")
        return payload

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    async def register(self, name: str, email: str, nickname: str, password: str, specification: str, phone: str, description: str) -> UserPrivate:
        existing_by_email = await self.user_repo.get_by_email(email)
        existing_by_nickname = await self.user_repo.get_by_nickname(nickname)

        # Разрешаем идемпотентную регистрацию с теми же данными
        if existing_by_email or existing_by_nickname:
            same_user = None
            if existing_by_email and existing_by_email.nickname == nickname:
                same_user = existing_by_email
            elif existing_by_nickname and existing_by_nickname.email == email:
                same_user = existing_by_nickname

            if same_user:
                return same_user

            raise ValueError("Пользователь с таким email или nickname уже существует")
        password_hash = self.hash_password(password)
        user = UserPrivate(
            name=name,
            nickname=nickname,
            email=email,
            specification=specification,
            description=description,
            created_at=datetime.utcnow(),
            password_hash=password_hash,
            jwt_token=None,
            email_verified=False,
            last_login=None,
            customer_rating=0.0,
            executor_rating=0.0,
            done_count=0,
            taken_count=0,
            phone_number=phone,
            phone_verified=False,
            admin_verified=False
        )
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            raise ValueError("Неверный email или пароль")
        return user
