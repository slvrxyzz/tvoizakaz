# 📦 pyproject.toml - Современное управление зависимостями

## 🎯 Обзор

Проект использует `pyproject.toml` вместо `requirements.txt` для современного управления зависимостями Python. Это стандарт PEP 518/621 для Python проектов.

## 📋 Структура pyproject.toml

### 🏗️ Build System
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

### 📦 Project Metadata
```toml
[project]
name = "teenfreelance"
version = "1.0.0"
description = "Фриланс-платформа для школьников и студентов"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
```

### 🔗 Dependencies
```toml
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "pydantic==2.5.0",
    # ... остальные зависимости
]
```

### 🛠️ Optional Dependencies
```toml
[project.optional-dependencies]
dev = ["black", "isort", "flake8", "mypy"]
test = ["pytest", "pytest-asyncio", "pytest-cov"]
docs = ["mkdocs", "mkdocs-material"]
all = ["teenfreelance[dev,test,docs]"]
```

## 🚀 Использование

### Установка
```bash
# Базовая установка
pip install -e .

# С dev зависимостями
pip install -e ".[dev]"

# С test зависимостями
pip install -e ".[test]"

# С docs зависимостями
pip install -e ".[docs]"

# Все зависимости
pip install -e ".[all]"
```

### Разработка
```bash
# Установка для разработки
pip install -e ".[dev,test]"

# Запуск приложения
cd src
python main.py

# Запуск тестов
pytest

# Форматирование кода
black src/
isort src/

# Проверка типов
mypy src/
```

## 🔧 Конфигурация инструментов

### Black (Форматирование)
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

### isort (Сортировка импортов)
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]
```

### MyPy (Проверка типов)
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Pytest (Тестирование)
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
]
testpaths = ["tests"]
```

### Coverage (Покрытие кода)
```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]
```

### Ruff (Линтер)
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```

## 📊 Группы зависимостей

### Core Dependencies
- **FastAPI** - Веб-фреймворк
- **SQLAlchemy** - ORM
- **Pydantic** - Валидация данных
- **JWT** - Аутентификация

### Development Dependencies
- **Black** - Форматирование кода
- **isort** - Сортировка импортов
- **Flake8** - Линтинг
- **MyPy** - Проверка типов

### Test Dependencies
- **pytest** - Тестирование
- **pytest-asyncio** - Асинхронные тесты
- **pytest-cov** - Покрытие кода

### Documentation Dependencies
- **mkdocs** - Генерация документации
- **mkdocs-material** - Material тема

## 🔄 Миграция с requirements.txt

### Было (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
```

### Стало (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "pydantic==2.5.0",
]
```

## 🎯 Преимущества pyproject.toml

### ✅ **Стандартизация**
- PEP 518/621 стандарт
- Единый файл для всего проекта
- Поддержка всеми современными инструментами

### ✅ **Группировка зависимостей**
- Основные зависимости
- Dev зависимости
- Test зависимости
- Docs зависимости

### ✅ **Конфигурация инструментов**
- Black, isort, MyPy в одном файле
- Pytest, coverage настройки
- Pre-commit хуки

### ✅ **Метаданные проекта**
- Версия, описание, лицензия
- Авторы, ключевые слова
- URL проекта

### ✅ **Скрипты и команды**
- Определение entry points
- CLI команды
- Удобные алиасы

## 🛠️ Команды разработки

```bash
# Установка
pip install -e ".[dev,test]"

# Форматирование
black src/
isort src/

# Линтинг
ruff check src/
flake8 src/

# Типизация
mypy src/

# Тестирование
pytest
pytest --cov=src

# Документация
mkdocs serve
mkdocs build

# Pre-commit
pre-commit install
pre-commit run --all-files
```

## 📈 Результат

- ✅ **Современный стандарт** - PEP 518/621
- ✅ **Единый файл конфигурации** - Все в одном месте
- ✅ **Группировка зависимостей** - Четкое разделение
- ✅ **Конфигурация инструментов** - Black, MyPy, Pytest
- ✅ **Удобство разработки** - Простые команды

---

**Современное управление зависимостями! 🚀**







