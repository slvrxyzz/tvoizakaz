"""
Enterprise-level logging system
Система логирования для мониторинга и отладки
"""
import logging
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from src.config import settings


class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированного логирования"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Добавление дополнительных полей
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        
        # Добавление исключений
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class StructuredLogger:
    """Структурированный логгер для enterprise приложения"""
    
    def __init__(self, name: str = "teenfreelance"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level.upper()))
        self.logger.handlers.clear()
        
        log_dir = self._get_log_directory()
        file_handlers_enabled = self._setup_log_directory(log_dir)
        
        json_formatter = JSONFormatter()
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        if file_handlers_enabled:
            file_handler = logging.FileHandler(log_dir / "app.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)
            
            error_handler = logging.FileHandler(log_dir / "errors.log")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(json_formatter)
            self.logger.addHandler(error_handler)
            
            audit_handler = logging.FileHandler(log_dir / "audit.log")
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(json_formatter)
            self._configure_child_logger("audit", audit_handler, logging.INFO)
            
            security_handler = logging.FileHandler(log_dir / "security.log")
            security_handler.setLevel(logging.WARNING)
            security_handler.setFormatter(json_formatter)
            self._configure_child_logger("security", security_handler, logging.WARNING)
            
            performance_handler = logging.FileHandler(log_dir / "performance.log")
            performance_handler.setLevel(logging.INFO)
            performance_handler.setFormatter(json_formatter)
            self._configure_child_logger("performance", performance_handler, logging.INFO)
        
        self.logger.propagate = False
    
    @staticmethod
    def _get_log_directory() -> Path:
        log_path = os.getenv("LOG_DIR", "/app/logs")
        if not Path(log_path).is_absolute():
            return Path.cwd() / log_path
        return Path(log_path)
    
    @staticmethod
    def _setup_log_directory(log_dir: Path) -> bool:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            test_file = log_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError) as e:
            sys.stderr.write(f"Warning: Cannot create/write to log directory {log_dir}: {e}\n")
            sys.stderr.write("Falling back to console logging only.\n")
            return False
    
    @staticmethod
    def _configure_child_logger(name: str, handler: logging.Handler, level: int) -> None:
        child_logger = logging.getLogger(name)
        child_logger.handlers.clear()
        child_logger.setLevel(level)
        child_logger.addHandler(handler)
        child_logger.propagate = False
    
    def info(self, message: str, **kwargs):
        """Информационное сообщение"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Предупреждение"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Ошибка"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Критическая ошибка"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Отладочное сообщение"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def audit(self, action: str, user_id: Optional[int] = None, **kwargs):
        """Аудит действий пользователя"""
        audit_logger = logging.getLogger("audit")
        extra = dict(kwargs)
        if user_id is not None:
            extra["user_id"] = user_id
        audit_logger.info(f"Audit: {action}", extra=extra)
    
    def security(self, event: str, user_id: Optional[int] = None, ip_address: Optional[str] = None, **kwargs):
        """Логирование событий безопасности"""
        security_logger = logging.getLogger("security")
        security_logger.warning(f"Security event: {event}", 
                              user_id=user_id, 
                              ip_address=ip_address, 
                              **kwargs)
    
    def performance(self, operation: str, duration: float, **kwargs):
        """Логирование производительности"""
        perf_logger = logging.getLogger("performance")
        extra = dict(kwargs)
        extra["duration"] = duration
        perf_logger.info(f"Performance: {operation}", extra=extra)
    
    def _log(self, level: int, message: str, **kwargs):
        """Внутренний метод для логирования"""
        extra = {}
        for key, value in kwargs.items():
            if key in ['user_id', 'request_id', 'ip_address', 'endpoint']:
                extra[key] = value
        
        self.logger.log(level, message, extra=extra)


# Глобальные логгеры
logger = StructuredLogger()
audit_logger = logging.getLogger("audit")
security_logger = logging.getLogger("security")
performance_logger = logging.getLogger("performance")
