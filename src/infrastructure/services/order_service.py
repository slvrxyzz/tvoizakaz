from src.infrastructure.repositiry.order_repository import OrderRepository
from src.infrastructure.repositiry.db_models import CommissionSettingsORM

class OrderService:
    def __init__(self, session):
        self.session = session
        self.order_repo = OrderRepository(session)

    async def get_order(self, order_id):
        return await self.order_repo.get_by_id(order_id)

    async def get_user_orders(self, user_id):
        return await self.order_repo.get_user_orders(user_id)

    async def increment_responses(self, order):
        await self.order_repo.increment_responses(order)

    async def add_favorite(self, user_id, order_id):
        return await self.order_repo.add_favorite(user_id, order_id)

    async def remove_favorite(self, user_id, order_id):
        return await self.order_repo.remove_favorite(user_id, order_id)

    async def get_favorites(self, user_id):
        return await self.order_repo.get_favorites(user_id)

    async def is_favorite(self, user_id, order_id):
        return await self.order_repo.is_favorite(user_id, order_id)

    async def get_commission_settings(self, session):
        settings = (await session.execute(
            CommissionSettingsORM.__table__.select().limit(1)
        )).first()
        if settings and hasattr(settings, '_mapping'):
            return settings._mapping
        return None

    async def set_commission_settings(self, session, **kwargs):
        self._validate_commission_settings(kwargs)
        settings = (await session.execute(
            CommissionSettingsORM.__table__.select().limit(1)
        )).first()
        if settings and hasattr(settings, '_mapping'):
            settings_id = settings._mapping['id']
            await session.execute(
                CommissionSettingsORM.__table__.update().where(CommissionSettingsORM.id == settings_id).values(**kwargs)
            )
        else:
            await session.execute(
                CommissionSettingsORM.__table__.insert().values(**kwargs)
            )
        await session.commit() 

    @staticmethod
    def _validate_commission_settings(values):
        percent_fields = {
            'commission_withdraw',
            'commission_customer',
            'commission_executor',
            'commission_response_percent',
        }
        non_negative_fields = {
            'commission_post_order',
            'commission_response_threshold',
        }

        for field in percent_fields:
            if field in values and values[field] is not None:
                value = float(values[field])
                if value < 0 or value > 100:
                    raise ValueError(f"{field} must be between 0 and 100")

        for field in non_negative_fields:
            if field in values and values[field] is not None:
                value = float(values[field])
                if value < 0:
                    raise ValueError(f"{field} must be non-negative")