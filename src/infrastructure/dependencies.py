from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infrastructure.repositiry.base_repository import get_db
from src.infrastructure.repositiry.user_repository import UserRepository
from src.infrastructure.services.auth_service import AuthService
from src.infrastructure.services.order_service import OrderService
from src.infrastructure.services.portfolio_service import PortfolioService
from src.infrastructure.services.rating_service import RatingService
from src.infrastructure.services.reward_service import RewardService
from src.infrastructure.services.user_service import UserService
from src.infrastructure.services.career_guidance_service import CareerGuidanceService
from src.domain.services.career_test_service import CareerTestService
from src.domain.services.workflow_service import WorkflowService


async def get_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    return session


async def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(secret_key=settings.secret_key, user_repo=user_repo)


async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


async def get_order_service(session: AsyncSession = Depends(get_session)) -> OrderService:
    return OrderService(session)


async def get_reward_service(session: AsyncSession = Depends(get_session)) -> RewardService:
    return RewardService(session)


async def get_rating_service(session: AsyncSession = Depends(get_session)) -> RatingService:
    return RatingService(session)


async def get_portfolio_service(session: AsyncSession = Depends(get_session)) -> PortfolioService:
    return PortfolioService(session)


async def get_workflow_service(session: AsyncSession = Depends(get_session)) -> WorkflowService:
    return WorkflowService(session)


async def get_career_test_service(session: AsyncSession = Depends(get_session)) -> CareerTestService:
    return CareerTestService(session)


async def get_career_guidance_service(session: AsyncSession = Depends(get_session)) -> CareerGuidanceService:
    return CareerGuidanceService(session)

