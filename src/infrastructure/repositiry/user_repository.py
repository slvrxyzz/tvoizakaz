from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from src.infrastructure.repositiry.db_models import UserORM
from src.infrastructure.repositiry.base_repository import AsyncSessionLocal
from src.domain.entity.userentity import UserPrivate

class UserRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, user_id):
        result = await self.session.execute(select(UserORM).where(UserORM.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_nickname(self, nickname):
        result = await self.session.execute(select(UserORM).where(UserORM.nickname == nickname))
        return result.scalar_one_or_none()

    async def get_by_email(self, email):
        result = await self.session.execute(select(UserORM).where(UserORM.email == email))
        return result.scalar_one_or_none()

    async def get_all(self):
        result = await self.session.execute(select(UserORM))
        return result.scalars().all()

    async def create(self, user: UserPrivate):
        from src.infrastructure.repositiry.db_models import UserORM
        user_orm = UserORM(
            name=user.name,
            nickname=user.nickname,
            email=user.email,
            hashed_password=user.password_hash,
            specification=user.specification,
            description=user.description,
            created_at=user.created_at,
            rub_balance=user.balance,
            tf_balance=user.tf_balance,
            role=user.role.value if hasattr(user, "role") else user.role,
            is_premium=False,
            phone_verified=user.phone_verified,
            admin_verified=user.admin_verified,
            phone_number=user.phone_number,
            customer_rating=user.customer_rating,
            executor_rating=user.executor_rating,
            done_count=user.done_count,
            taken_count=user.taken_count
        )
        self.session.add(user_orm)
        await self.session.commit()
        await self.session.refresh(user_orm)
        return user_orm

    async def exists(self, nickname=None, email=None):
        if nickname and await self.get_by_nickname(nickname) is not None:
            return True
        if email and await self.get_by_email(email) is not None:
            return True
        return False

    async def update(self, user_id, **kwargs):
        user = await self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        return None

    async def delete(self, user_id):
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False 