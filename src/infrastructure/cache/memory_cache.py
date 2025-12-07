"""
In-memory кэширование с ZSTD сжатием
Высокопроизводительное кэширование популярных данных
"""
import zstandard as zstd
import json
import time
import threading
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheItem:
    """Элемент кэша с метаданными"""
    data: bytes
    compressed: bool
    created_at: float
    expires_at: Optional[float]
    access_count: int = 0
    last_accessed: float = 0.0


class MemoryCache:
    """In-memory кэш с ZSTD сжатием и TTL"""
    
    def __init__(self, 
                 max_size_mb: int = 100,
                 compression_threshold: int = 1024,
                 default_ttl: int = 3600):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression_threshold = compression_threshold
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheItem] = {}
        self.lock = threading.RLock()
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        
        # ZSTD уровень сжатия (1-22, где 1 - быстрее, 22 - лучше сжатие)
        self.compression_level = 3
        
        logger.info(f"Memory cache initialized: max_size={max_size_mb}MB, "
                   f"compression_threshold={compression_threshold}B, "
                   f"default_ttl={default_ttl}s")
    
    def _compress_data(self, data: bytes) -> bytes:
        """Сжатие данных с помощью ZSTD"""
        try:
            return zstd.compress(data, level=self.compression_level)
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Распаковка данных"""
        try:
            return zstd.decompress(data)
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            return data
    
    def _serialize_data(self, data: Any) -> bytes:
        """Сериализация данных в JSON"""
        try:
            return json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return str(data).encode('utf-8')
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Десериализация данных из JSON"""
        try:
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return data.decode('utf-8')
    
    def _calculate_size(self, item: CacheItem) -> int:
        """Расчет размера элемента кэша"""
        return len(item.data) + len(str(item))  # Примерный размер
    
    def _is_expired(self, item: CacheItem) -> bool:
        """Проверка истечения срока действия"""
        if item.expires_at is None:
            return False
        return time.time() > item.expires_at
    
    def _cleanup_expired(self):
        """Очистка истекших элементов"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.cache.items():
            if item.expires_at and current_time > item.expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_item(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired items")
    
    def _remove_item(self, key: str):
        """Удаление элемента из кэша"""
        if key in self.cache:
            item = self.cache[key]
            self.current_size -= self._calculate_size(item)
            del self.cache[key]
    
    def _evict_lru(self):
        """Удаление наименее используемых элементов"""
        if not self.cache:
            return
        
        # Сортируем по времени последнего доступа
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Удаляем 20% наименее используемых элементов
        evict_count = max(1, len(sorted_items) // 5)
        
        for i in range(evict_count):
            key, _ = sorted_items[i]
            self._remove_item(key)
        
        logger.debug(f"Evicted {evict_count} LRU items")
    
    def _ensure_space(self, required_size: int):
        """Обеспечение свободного места в кэше"""
        while (self.current_size + required_size > self.max_size_bytes and 
               self.cache):
            self._cleanup_expired()
            if self.current_size + required_size > self.max_size_bytes:
                self._evict_lru()
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            item = self.cache[key]
            
            # Проверка истечения срока
            if self._is_expired(item):
                self._remove_item(key)
                self.misses += 1
                return None
            
            # Обновление статистики доступа
            item.access_count += 1
            item.last_accessed = time.time()
            
            # Распаковка данных если нужно
            data = item.data
            if item.compressed:
                data = self._decompress_data(data)
            
            # Десериализация
            result = self._deserialize_data(data)
            
            self.hits += 1
            return result
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение данных в кэш"""
        with self.lock:
            try:
                # Сериализация данных
                serialized_data = self._serialize_data(value)
                
                # Сжатие если данные достаточно большие
                compressed = len(serialized_data) > self.compression_threshold
                if compressed:
                    serialized_data = self._compress_data(serialized_data)
                
                # Создание элемента кэша
                current_time = time.time()
                expires_at = None
                if ttl is not None:
                    expires_at = current_time + ttl
                elif self.default_ttl > 0:
                    expires_at = current_time + self.default_ttl
                
                item = CacheItem(
                    data=serialized_data,
                    compressed=compressed,
                    created_at=current_time,
                    expires_at=expires_at,
                    access_count=0,
                    last_accessed=current_time
                )
                
                # Расчет размера
                item_size = self._calculate_size(item)
                
                # Удаление существующего элемента
                if key in self.cache:
                    self._remove_item(key)
                
                # Обеспечение свободного места
                self._ensure_space(item_size)
                
                # Добавление элемента
                self.cache[key] = item
                self.current_size += item_size
                
                return True
                
            except Exception as e:
                logger.error(f"Cache set error for key '{key}': {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Удаление данных из кэша"""
        with self.lock:
            if key in self.cache:
                self._remove_item(key)
                return True
            return False
    
    def clear(self):
        """Очистка всего кэша"""
        with self.lock:
            self.cache.clear()
            self.current_size = 0
            logger.info("Cache cleared")
    
    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Получение из кэша или создание через factory функцию"""
        value = self.get(key)
        if value is not None:
            return value
        
        # Создание нового значения
        try:
            value = factory()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Factory function error for key '{key}': {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size_bytes": self.current_size,
                "size_mb": round(self.current_size / 1024 / 1024, 2),
                "max_size_mb": round(self.max_size_bytes / 1024 / 1024, 2),
                "items_count": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate_percent": round(hit_rate, 2),
                "compression_threshold": self.compression_threshold,
                "compression_level": self.compression_level
            }
    
    def cleanup(self):
        """Ручная очистка истекших элементов"""
        with self.lock:
            self._cleanup_expired()


# Глобальный экземпляр кэша
memory_cache = MemoryCache(max_size_mb=100, compression_threshold=1024, default_ttl=3600)
