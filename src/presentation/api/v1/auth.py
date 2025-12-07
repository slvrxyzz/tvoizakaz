import secrets
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.domain.entity.userentity import UserPrivate, UserRole
from src.infrastructure.dependencies import (
    get_auth_service,
    get_session,
    get_user_repository,
    get_user_service,
)
from src.infrastructure.repositiry.user_repository import UserRepository
from src.infrastructure.repositiry.db_models import CurrencyTypeEnum
from src.infrastructure.services.auth_service import AuthService, decode_access_token
from src.infrastructure.services.user_service import UserService
from src.infrastructure.security.reset_token_store import reset_token_store

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

# Pydantic models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    nickname: str
    password: str
    password_confirm: Optional[str] = None
    passwordConfirm: Optional[str] = None  # Для совместимости с фронтендом
    specification: str = ""
    phone_number: Optional[str] = ""
    phone: Optional[str] = ""  # Для совместимости с фронтендом
    description: str = ""
    role: Optional[str] = ""  # Для совместимости с фронтендом (customer/executor)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=6)
    password_confirm: Optional[str] = None

class UserProfile(BaseModel):
    id: str  # Соответствует UserDTO фронтенда (string)
    name: str
    nickname: str
    email: str
    customer_rating: Optional[float] = None
    executor_rating: Optional[float] = None
    balance: Optional[float] = None
    tf_balance: Optional[float] = None
    phone_verified: Optional[bool] = None
    admin_verified: Optional[bool] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserProfile] = None  # Для совместимости с фронтендом
    token: Optional[str] = None  # Для совместимости с фронтендом (alias для access_token)


ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
ACCESS_COOKIE_MAX_AGE = settings.access_token_expire_minutes * 60
REFRESH_COOKIE_MAX_AGE = settings.refresh_token_expire_days * 24 * 60 * 60


def _cookie_kwargs(max_age: int) -> dict:
    return {
        "httponly": True,
        "secure": not settings.debug,
        "samesite": "lax",
        "max_age": max_age,
    }


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    # Очистка потенциальных устаревших cookie без домена (например, вручную выставленных в тестах)
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        "",
        max_age=0,
        expires=0,
        path="/",
        domain="",
    )
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        **_cookie_kwargs(ACCESS_COOKIE_MAX_AGE),
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        path="/auth/refresh",
        **_cookie_kwargs(REFRESH_COOKIE_MAX_AGE),
    )


def _clear_auth_cookies(response: Response) -> None:
    for domain in (None, "", ".testserver.local"):
        response.delete_cookie(ACCESS_COOKIE_NAME, domain=domain)
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth/refresh")


def _build_user_profile(user) -> UserProfile:
    balance = float(getattr(user, "balance", 0.0) or getattr(user, "rub_balance", 0.0) or 0.0)
    tf_balance = float(getattr(user, "tf_balance", 0.0) or 0.0)
    is_support = bool(getattr(user, "is_support", False))
    admin_verified = bool(getattr(user, "admin_verified", False)) or is_support
    raw_role = getattr(user, "role", UserRole.CUSTOMER.value)
    try:
        role_value = raw_role.value if isinstance(raw_role, UserRole) else UserRole(str(raw_role or UserRole.CUSTOMER.value)).value
    except ValueError:
        role_value = UserRole.CUSTOMER.value
    return UserProfile(
        id=str(user.id),
        name=user.name,
        nickname=user.nickname,
        email=user.email,
        customer_rating=user.customer_rating if user.customer_rating is not None else 0.0,
        executor_rating=user.executor_rating if user.executor_rating is not None else 0.0,
        balance=balance,
        tf_balance=tf_balance,
        phone_verified=bool(user.phone_verified) if user.phone_verified is not None else False,
        admin_verified=admin_verified,
        phone_number=getattr(user, "phone_number", None),
        role=role_value,
    )

# Dependency для получения текущего пользователя
def _extract_token(
    credentials: HTTPAuthorizationCredentials | None,
    cookie_token: str | None,
) -> str | None:
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    if cookie_token:
        return cookie_token
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_cookie: str | None = Cookie(default=None, alias="access_token"),
    session: AsyncSession = Depends(get_session),
) -> UserPrivate:
    token = _extract_token(credentials, access_cookie)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_service = UserService(session)
        user = await user_service.get_user_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_admin_user(current_user: UserPrivate = Depends(get_current_user)) -> UserPrivate:
    role_value = getattr(current_user, "role", UserRole.CUSTOMER.value)
    try:
        role = role_value if isinstance(role_value, UserRole) else UserRole(str(role_value))
    except ValueError:
        role = UserRole.CUSTOMER
    if role not in {UserRole.ADMIN, UserRole.SUPPORT} and not getattr(current_user, "admin_verified", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    access_cookie: str | None = Cookie(default=None, alias="access_token"),
    session: AsyncSession = Depends(get_session),
) -> UserPrivate | None:
    """Необязательный текущий пользователь (используется в публичных эндпоинтах)."""
    token = _extract_token(credentials, access_cookie)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None

        user_service = UserService(session)
        return await user_service.get_user_by_id(int(user_id))
    except JWTError:
        return None

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    # Проверка паролей (поддержка обоих форматов)
    password_confirm = request.password_confirm or request.passwordConfirm
    if password_confirm and request.password != password_confirm:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Получаем телефон (поддержка обоих форматов)
    phone = request.phone_number or request.phone or ""
    
    try:
        user = await auth_service.register(
            name=request.name,
            email=request.email,
            nickname=request.nickname,
            password=request.password,
            specification=request.specification,
            phone=phone,
            description=request.description,
        )

        access_token = auth_service.create_access_token({"sub": str(user.id)})
        refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})
        _set_auth_cookies(response, access_token, refresh_token)

        user_profile = _build_user_profile(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_COOKIE_MAX_AGE,
            user=user_profile,
            token=access_token,
        )
    except ValueError as e:
        from src.infrastructure.monitoring.logger import logger
        logger.warning(f"registration_validation_failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback

        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"Registration error: {error_msg}")
        print(f"Traceback: {error_trace}")

        if "Duplicate entry" in error_msg and "nickname" in error_msg:
            raise HTTPException(status_code=400, detail="Пользователь с таким никнеймом уже существует")
        if "Duplicate entry" in error_msg and "email" in error_msg:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        raise HTTPException(status_code=500, detail=f"Ошибка при регистрации пользователя: {error_msg}")

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user_data = await auth_service.login(request.email, request.password)
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")

        access_token = auth_service.create_access_token({"sub": str(user_data.id)})
        refresh_token = auth_service.create_refresh_token({"sub": str(user_data.id)})
        _set_auth_cookies(response, access_token, refresh_token)

        user_profile = _build_user_profile(user_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_COOKIE_MAX_AGE,
            user=user_profile,
            token=access_token,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserProfile)
async def get_me(
    current_user: UserPrivate = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Получить текущего пользователя (для фронтенда)"""
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _build_user_profile(user)

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: UserPrivate = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Получить профиль пользователя (альтернативный эндпоинт)"""
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _build_user_profile(user)

@router.post("/logout")
async def logout(response: Response):
    _clear_auth_cookies(response)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    if not refresh_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = auth_service.decode_refresh_token(refresh_cookie)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await user_service.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = auth_service.create_access_token({"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token({"sub": str(user.id)})
    _set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_COOKIE_MAX_AGE,
        user=_build_user_profile(user),
        token=access_token,
    )

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    user = await user_repo.get_by_email(request.email)

    if not user:
        return {"success": True, "message": "Если email существует, отправлена инструкция"}

    token = secrets.token_urlsafe(32)
    await reset_token_store.set(token, user.id)

    from src.infrastructure.monitoring.logger import logger

    logger.info(f"Password reset token for {request.email}: {token}")

    response = {"success": True, "message": "Отправлена ссылка для восстановления пароля"}
    if settings.debug:
        response["token"] = token
    return response

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
):
    user_id = await reset_token_store.get_user_id(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Некорректный или просроченный токен")

    password_confirm = request.password_confirm if request.password_confirm is not None else request.password
    if request.password != password_confirm:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    hashed = auth_service.hash_password(request.password)
    await user_repo.update(user_id, hashed_password=hashed)
    await reset_token_store.delete(request.token)

    return {"success": True, "message": "Пароль успешно обновлен"}

@router.get("/reset-password/{token}/validate")
async def validate_reset_token(token: str):
    if not await reset_token_store.exists(token):
        raise HTTPException(status_code=404, detail="Токен недействителен")
    return {"valid": True}

@router.post("/balance/topup")
async def topup_balance(
    amount: float,
    currency: CurrencyTypeEnum = CurrencyTypeEnum.RUB,
    current_user: UserPrivate = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Пополнение баланса пользователя (для тестирования)"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    user_service = UserService(session)
    user = await user_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_balance = user.get_balance(currency)
    new_balance = current_balance + amount
    user.set_balance(currency, new_balance)
    await session.commit()

    return {
        "success": True,
        "message": f"Balance topped up by {amount} {currency.value}",
        "currency": currency.value,
        "new_balance": new_balance,
        "amount_added": amount,
    }
