"""
Сервис заказов
Business logic layer для работы с заказами
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.domain.interfaces.repositories import (
    IOrderRepository, OrderCreateDto, OrderUpdateDto, OrderFilterDto,
    OrderStatus, OrderPriority
)
from src.infrastructure.monitoring.logger import logger


class OrderService:
    """Сервис для работы с заказами"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repo = order_repository
    
    async def create_order(self, order_data: OrderCreateDto) -> Dict[str, Any]:
        """Создание заказа"""
        try:
            # Валидация данных заказа
            if order_data.price <= 0:
                raise ValueError("Price must be positive")
            
            if order_data.deadline <= datetime.utcnow():
                raise ValueError("Deadline must be in the future")
            
            # Создание заказа
            order_id = await self.order_repo.create(order_data)
            
            # Получение созданного заказа
            order = await self.order_repo.get_by_id(order_id)
            
            logger.info(f"Order created: {order_id}", order_id=order_id, customer_id=order_data.customer_id)
            
            return {
                "success": True,
                "order_id": order_id,
                "message": "Order created successfully",
                "order": order
            }
            
        except Exception as e:
            logger.error(f"Order creation failed: {e}", error=str(e))
            raise
    
    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получение заказа по ID"""
        try:
            order = await self.order_repo.get_by_id(order_id)
            return order
            
        except Exception as e:
            logger.error(f"Get order failed: {e}", order_id=order_id, error=str(e))
            raise
    
    async def update_order(self, order_id: int, update_data: OrderUpdateDto, user_id: int) -> bool:
        """Обновление заказа"""
        try:
            # Получение заказа для проверки прав
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            # Проверка прав на обновление
            if order['customer_id'] != user_id:
                raise ValueError("No permission to update this order")
            
            # Проверка статуса заказа
            if order['status'] in [OrderStatus.CLOSE.value, OrderStatus.ARCHIVED.value]:
                raise ValueError("Cannot update closed or archived order")
            
            success = await self.order_repo.update(order_id, update_data)
            
            if success:
                logger.info(f"Order updated: {order_id}", order_id=order_id, user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Update order failed: {e}", order_id=order_id, user_id=user_id, error=str(e))
            raise
    
    async def delete_order(self, order_id: int, user_id: int) -> bool:
        """Удаление заказа"""
        try:
            # Получение заказа для проверки прав
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            # Проверка прав на удаление
            if order['customer_id'] != user_id:
                raise ValueError("No permission to delete this order")
            
            success = await self.order_repo.delete(order_id)
            
            if success:
                logger.info(f"Order deleted: {order_id}", order_id=order_id, user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Delete order failed: {e}", order_id=order_id, user_id=user_id, error=str(e))
            raise
    
    async def get_customer_orders(self, customer_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение заказов заказчика"""
        try:
            orders = await self.order_repo.get_by_customer(customer_id, limit, offset)
            return orders
            
        except Exception as e:
            logger.error(f"Get customer orders failed: {e}", customer_id=customer_id, error=str(e))
            raise
    
    async def get_executor_orders(self, executor_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение заказов исполнителя"""
        try:
            orders = await self.order_repo.get_by_executor(executor_id, limit, offset)
            return orders
            
        except Exception as e:
            logger.error(f"Get executor orders failed: {e}", executor_id=executor_id, error=str(e))
            raise
    
    async def search_orders(self, filters: OrderFilterDto, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Поиск заказов"""
        try:
            orders = await self.order_repo.search(filters, limit, offset)
            return orders
            
        except Exception as e:
            logger.error(f"Search orders failed: {e}", filters=filters.dict(), error=str(e))
            raise
    
    async def assign_executor(self, order_id: int, executor_id: int, customer_id: int) -> bool:
        """Назначение исполнителя на заказ"""
        try:
            # Получение заказа для проверки прав
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            # Проверка прав
            if order['customer_id'] != customer_id:
                raise ValueError("No permission to assign executor to this order")
            
            # Проверка статуса заказа
            if order['status'] != OrderStatus.OPEN.value:
                raise ValueError("Can only assign executor to open orders")
            
            success = await self.order_repo.assign_executor(order_id, executor_id)
            
            if success:
                logger.info(f"Executor assigned: {executor_id} to order {order_id}", 
                          order_id=order_id, executor_id=executor_id, customer_id=customer_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Assign executor failed: {e}", order_id=order_id, executor_id=executor_id, error=str(e))
            raise
    
    async def update_order_status(self, order_id: int, status: OrderStatus, user_id: int) -> bool:
        """Обновление статуса заказа"""
        try:
            # Получение заказа для проверки прав
            order = await self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Order not found")
            
            # Проверка прав
            if order['customer_id'] != user_id and order['executor_id'] != user_id:
                raise ValueError("No permission to update order status")
            
            # Валидация перехода статуса
            if not self._is_valid_status_transition(order['status'], status.value):
                raise ValueError(f"Invalid status transition from {order['status']} to {status.value}")
            
            success = await self.order_repo.update_status(order_id, status)
            
            if success:
                logger.info(f"Order status updated: {order_id} to {status.value}", 
                          order_id=order_id, status=status.value, user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Update order status failed: {e}", order_id=order_id, status=status.value, error=str(e))
            raise
    
    async def get_popular_categories(self) -> List[Dict[str, Any]]:
        """Получение популярных категорий"""
        try:
            categories = await self.order_repo.get_popular_categories()
            return categories
            
        except Exception as e:
            logger.error(f"Get popular categories failed: {e}", error=str(e))
            raise
    
    async def get_order_statistics(self) -> Dict[str, Any]:
        """Получение статистики заказов"""
        try:
            stats = await self.order_repo.get_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Get order statistics failed: {e}", error=str(e))
            raise
    
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Проверка валидности перехода статуса"""
        valid_transitions = {
            OrderStatus.OPEN.value: [OrderStatus.WORK.value, OrderStatus.ARCHIVED.value],
            OrderStatus.WORK.value: [OrderStatus.REVIEW.value, OrderStatus.ARCHIVED.value],
            OrderStatus.REVIEW.value: [OrderStatus.CLOSE.value, OrderStatus.ARCHIVED.value],
            OrderStatus.CLOSE.value: [OrderStatus.ARCHIVED.value],
            OrderStatus.ARCHIVED.value: []
        }
        
        return new_status in valid_transitions.get(current_status, [])







