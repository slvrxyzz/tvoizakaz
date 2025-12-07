"""
Dependency Injection Container
Enterprise-level DI для управления зависимостями
"""
from typing import TypeVar, Type, Dict, Any, Callable, Optional
import threading
from abc import ABC, abstractmethod

T = TypeVar('T')


class DIContainer:
    """Контейнер для управления зависимостями"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = threading.RLock()
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> 'DIContainer':
        """Регистрация singleton сервиса"""
        with self._lock:
            self._services[interface] = implementation
            return self
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> 'DIContainer':
        """Регистрация transient сервиса (новый экземпляр каждый раз)"""
        with self._lock:
            self._factories[interface] = lambda: implementation()
            return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'DIContainer':
        """Регистрация factory для создания сервиса"""
        with self._lock:
            self._factories[interface] = factory
            return self
    
    def register_instance(self, interface: Type[T], instance: T) -> 'DIContainer':
        """Регистрация готового экземпляра"""
        with self._lock:
            self._singletons[interface] = instance
            return self
    
    def get(self, interface: Type[T]) -> T:
        """Получение сервиса"""
        with self._lock:
            # Проверяем готовые экземпляры
            if interface in self._singletons:
                return self._singletons[interface]
            
            # Проверяем singleton сервисы
            if interface in self._services:
                if interface not in self._singletons:
                    self._singletons[interface] = self._services[interface]()
                return self._singletons[interface]
            
            # Проверяем factory
            if interface in self._factories:
                return self._factories[interface]()
            
            raise ValueError(f"Service {interface} not registered")
    
    def get_optional(self, interface: Type[T]) -> Optional[T]:
        """Получение сервиса (может вернуть None)"""
        try:
            return self.get(interface)
        except ValueError:
            return None
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Проверка регистрации сервиса"""
        with self._lock:
            return (interface in self._services or 
                   interface in self._factories or 
                   interface in self._singletons)
    
    def clear(self):
        """Очистка контейнера"""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()


class ServiceProvider:
    """Провайдер сервисов для FastAPI"""
    
    def __init__(self, container: DIContainer):
        self.container = container
    
    def get_service(self, interface: Type[T]) -> T:
        """Получение сервиса для FastAPI dependency"""
        return self.container.get(interface)


# Глобальный контейнер
container = DIContainer()
service_provider = ServiceProvider(container)







