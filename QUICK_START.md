## Быстрый запуск TeenFreelance

### 0. Что нужно иметь установлено

- **Python 3.10+**
- **Node.js 18+ и npm**
- **Git**

### 1. Настройка бэкенда (FastAPI)

- **Создайте `.env` в корне проекта** (рядом с `pyproject.toml`):

  - Линукс / Mac:
    ```bash
    cp .env.example .env
    ```
  - Windows: создайте файл `.env` вручную и вставьте:
    ```env
    SECRET_KEY=ваш-секретный-ключ-минимум-32-символа-длинный
    DATABASE_URL=sqlite+aiosqlite:///./teenfreelance.db
    CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
    DEBUG=true
    ENVIRONMENT=development
    ```

- **Создайте и активируйте виртуальное окружение (один раз):**

  ```bash
  python -m venv venv
  venv\Scripts\python -m pip install --upgrade pip
  venv\Scripts\pip install -e .
  ```

- **Запуск бэкенда:**

  - Через скрипт (рекомендуется):
    - **Windows:**
      ```bash
      start_backend.bat
      ```
    - **Linux/Mac:**
      ```bash
      chmod +x start_backend.sh
      ./start_backend.sh
      ```

  - Либо напрямую:
    ```bash
    venv\Scripts\python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

- **Проверка:**
  - API: `http://localhost:8000`
  - Документация: `http://localhost:8000/docs`
  - Health check: `http://localhost:8000/health`

> **Если порт 8000 занят:** используйте `--port 8001` и поменяйте URL’ы фронтенда на `http://localhost:8001` / `ws://localhost:8001`.

### 2. Настройка фронтенда (Next.js)

- **Перейдите в директорию фронтенда:**

  ```bash
  cd fronted
  ```

- **Создайте `.env.local`:**

  - На основе примера:
    ```bash
    cp env.local.example .env.local
    ```

  - Или вручную с минимальным набором:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    NEXT_PUBLIC_WS_URL=ws://localhost:8000
    NEXT_PUBLIC_MODE=dev
    NEXT_PUBLIC_ADMIN_LOGIN_DOMAIN=teenfreelance.ru
    ```

- **Установите зависимости и запустите:**

  ```bash
  npm install
  npm run dev
  ```

  Или через скрипты:

  - **Windows:**
    ```bash
    start_frontend.bat
    ```
  - **Linux/Mac:**
    ```bash
    chmod +x start_frontend.sh
    ./start_frontend.sh
    ```

- **Фронтенд доступен по адресу:** `http://localhost:3000`

### 3. Быстрый сквозной сценарий

- **Регистрация:** страница `/register`
- **Вход:** страница `/login`
- **Создание заказа:** `/orders/create` (понадобятся средства на балансе пользователя)
- **Просмотр и отклики на заказы:** `/orders`
- **Чаты по заказу:** кнопка чата из страницы заказа / списка

### 4. Полезные замечания

- **Порядок запуска:** сначала бэкенд, потом фронтенд.
- **Порты:** 3000 (фронтенд) и 8000 (бэкенд) не должны быть заняты другими процессами.
- **База данных:**
  - По умолчанию используется SQLite (`teenfreelance.db` в корне).
  - Для продакшена можно настроить MySQL/MariaDB через `DATABASE_URL` в `.env`.

Если нужны более детальные пояснения по архитектуре и структуре папок, смотри файл `doc/QUICK_START.md` и `README.md` в корне репозитория.
