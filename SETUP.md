# Настройка и запуск TeenFreelance

## Быстрый старт

### 1. Настройка бэкенда

1. Создайте файл `.env` в корне проекта (скопируйте из `.env.example`):
```bash
cp .env.example .env
```

2. Отредактируйте `.env` и укажите:
   - `SECRET_KEY` - секретный ключ (минимум 32 символа)
   - `DATABASE_URL` - URL базы данных
   - `CORS_ORIGINS` - адреса фронтенда (по умолчанию: `http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000`)

3. Установите зависимости и запустите бэкенд:

**Windows:**
```bash
start_backend.bat
```

**Linux/Mac:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Или вручную:**
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -e .
python main.py
```

Бэкенд будет доступен на `http://localhost:8000`
- API документация: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 2. Настройка фронтенда

1. Перейдите в директорию фронтенда:
```bash
cd fronted
```

2. Создайте файл `.env.local` (скопируйте из `.env.example` если есть):
```bash
cp .env.example .env.local
```

Или создайте вручную с содержимым:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_MODE=dev
```

3. Установите зависимости и запустите фронтенд:

**Windows:**
```bash
start_frontend.bat
```

**Linux/Mac:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

**Или вручную:**
```bash
npm install
npm run dev
```

Фронтенд будет доступен на `http://localhost:3000`

## Запуск через Docker

1. Создайте `.env` файл в корне проекта
2. Запустите все сервисы:
```bash
docker-compose up -d
```

Бэкенд: `http://localhost:8000`
Фронтенд: нужно запустить отдельно (см. выше)

## Проверка работы

1. Откройте `http://localhost:3000` в браузере
2. Проверьте, что API доступен: `http://localhost:8000/health`
3. Попробуйте зарегистрироваться или войти

## Решение проблем

### CORS ошибки
Убедитесь, что в `.env` бэкенда указан правильный `CORS_ORIGINS`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

### База данных не подключается
- Проверьте `DATABASE_URL` в `.env`
- Убедитесь, что база данных запущена
- Для Docker: проверьте, что контейнер БД запущен

### Фронтенд не может подключиться к API
- Проверьте, что бэкенд запущен на порту 8000
- Проверьте `NEXT_PUBLIC_API_URL` в `.env.local` фронтенда
- Убедитесь, что нет блокировки файрволом

## Структура проекта

```
TeenFreelance-main/
├── src/                    # Бэкенд (Python/FastAPI)
│   ├── main.py            # Точка входа
│   ├── config.py          # Конфигурация
│   └── presentation/      # API endpoints
├── fronted/                # Фронтенд (Next.js/React)
│   ├── src/
│   │   ├── app/           # Страницы
│   │   ├── components/    # Компоненты
│   │   └── utils/         # Утилиты (apiClient, config)
│   └── package.json
├── docker-compose.yml      # Docker конфигурация
├── .env.example           # Пример переменных окружения
└── start_*.bat/sh         # Скрипты запуска
```

## API Endpoints

Все API endpoints доступны по префиксу `/api/v1`:
- `/api/v1/auth/*` - Аутентификация
- `/api/v1/orders/*` - Заказы
- `/api/v1/chats/*` - Чаты
- `/api/v1/users/*` - Пользователи
- `/api/v1/ws/chat` - WebSocket для чатов

Полная документация: `http://localhost:8000/docs`










