from fastapi import APIRouter
from src.presentation.api.v1 import (
    admin,
    auth,
    categories,
    chats,
    career,
    content,
    favorites,
    portfolio,
    orders,
    ratings,
    reviews,
    search,
    users,
    verification,
    websocket_chats,
    rewards,
)

router = APIRouter(prefix="/api/v1")

# Подключаем все модули
router.include_router(auth.router)
router.include_router(orders.router)
router.include_router(chats.router)
router.include_router(users.router)
router.include_router(admin.router)
router.include_router(categories.router)
router.include_router(search.router)
router.include_router(reviews.router)
router.include_router(content.router)
router.include_router(ratings.router)
router.include_router(verification.router)
router.include_router(websocket_chats.router)
router.include_router(favorites.router)
router.include_router(rewards.router)
router.include_router(portfolio.router)
router.include_router(career.router)
