from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.infrastructure.services.verification_service import VerificationService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.repositiry.db_models import UserORM
from sqlalchemy import select
from src.presentation.api.v1.auth import get_current_user
from src.domain.entity.userentity import UserPrivate

router = APIRouter(prefix="/verification", tags=["Verification"])

# Pydantic models
class PhoneVerificationRequest(BaseModel):
    phone: str = Field(..., pattern='^\+?[1-9]\d{1,14}$')

class PhoneVerificationConfirm(BaseModel):
    phone: str = Field(..., pattern='^\+?[1-9]\d{1,14}$')
    code: str = Field(..., min_length=4, max_length=6)

class VerificationStatus(BaseModel):
    phone_verified: bool
    admin_verified: bool
    phone_number: Optional[str]
    verification_level: str

@router.post("/phone/send")
async def send_phone_verification(
    request: PhoneVerificationRequest,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        verification_service = VerificationService(session)
        
        try:
            await verification_service.send_phone_code(request.phone)
            return {"success": True, "message": "Verification code sent"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.post("/phone/confirm")
async def confirm_phone_verification(
    request: PhoneVerificationConfirm,
    current_user: UserPrivate = Depends(get_current_user)
):
    async with AsyncSessionLocal() as session:
        verification_service = VerificationService(session)
        user_service = UserService(session)
        
        try:
            if await verification_service.verify_phone_code(request.phone, request.code):
                # Обновляем пользователя
                user = await user_service.get_user_by_id(current_user.id)
                if user:
                    user.phone_verified = True
                    user.phone_number = request.phone
                    await session.commit()
                
                return {"success": True, "message": "Phone verified successfully"}
            else:
                raise HTTPException(status_code=400, detail="Invalid verification code")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", response_model=VerificationStatus)
async def get_verification_status(current_user: UserPrivate = Depends(get_current_user)):
    verification_level = "unverified"
    
    if current_user.admin_verified:
        verification_level = "admin_verified"
    elif current_user.phone_verified:
        verification_level = "phone_verified"
    
    return VerificationStatus(
        phone_verified=current_user.phone_verified,
        admin_verified=current_user.admin_verified,
        phone_number=getattr(current_user, 'phone_number', None),
        verification_level=verification_level
    )

@router.post("/admin/{user_id}/verify")
async def admin_verify_user(
    user_id: int,
    current_user: UserPrivate = Depends(get_current_user)
):
    # Проверяем права администратора
    if current_user.nickname != "admin" and not getattr(current_user, 'is_support', False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    async with AsyncSessionLocal() as session:
        from src.infrastructure.repositiry.verification_repository import VerificationRepository
        
        verification_repo = VerificationRepository(session)
        await verification_repo.verify_by_admin(user_id)
        
        return {"success": True, "message": "User verified by admin"}
