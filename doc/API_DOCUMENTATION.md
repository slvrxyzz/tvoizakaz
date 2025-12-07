# TeenFreelance API Documentation

## Обзор

TeenFreelance API - это RESTful API для фриланс-платформы, предназначенной для школьников и студентов. API предоставляет полный функционал для управления пользователями, заказами, чатами, контентом и администрирования.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Аутентификация

API использует JWT токены для аутентификации. Токен должен передаваться в заголовке `Authorization`:

```
Authorization: Bearer <your_jwt_token>
```

## Модули API

### 1. Аутентификация (`/auth`)

#### POST `/auth/register`
Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "nickname": "ivan123",
  "password": "password123",
  "password_confirm": "password123",
  "specification": "Веб-разработка",
  "phone_number": "+7900123456",
  "description": "Опытный разработчик"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

#### POST `/auth/login`
Вход в систему.

**Тело запроса:**
```json
{
  "email": "ivan@example.com",
  "password": "password123"
}
```

#### GET `/auth/profile`
Получение профиля текущего пользователя.

**Ответ:**
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "nickname": "ivan123",
  "email": "ivan@example.com",
  "customer_rating": 4.5,
  "executor_rating": 4.8,
  "balance": 5000.0,
  "phone_verified": true,
  "admin_verified": false
}
```

### 2. Заказы (`/orders`)

#### POST `/orders/`
Создание нового заказа.

**Тело запроса:**
```json
{
  "title": "Создание лендинга",
  "description": "Нужен современный лендинг для стартапа",
  "price": 5000,
  "term": 7,
  "category": "Веб-разработка"
}
```

#### GET `/orders/`
Получение списка заказов с фильтрацией и пагинацией.

**Параметры запроса:**
- `category_id` (int, optional) - ID категории
- `min_price` (int, optional) - Минимальная цена
- `max_price` (int, optional) - Максимальная цена
- `sort_by` (str) - Сортировка: "date" или "price"
- `page` (int) - Номер страницы
- `page_size` (int) - Размер страницы
- `status` (str) - Статус заказа

#### GET `/orders/{order_id}`
Получение конкретного заказа.

#### POST `/orders/{order_id}/respond`
Отклик на заказ.

**Тело запроса:**
```json
{
  "message": "Готов выполнить ваш заказ",
  "price": 4500
}
```

#### POST `/orders/{order_id}/accept`
Принятие заказа заказчиком.

#### POST `/orders/{order_id}/close`
Закрытие заказа.

### 3. Чаты (`/chats`)

#### GET `/chats/`
Получение списка чатов пользователя.

#### GET `/chats/{chat_id}/messages`
Получение сообщений чата.

#### POST `/chats/{chat_id}/messages`
Отправка сообщения в чат.

**Тело запроса:**
```json
{
  "text": "Привет! Готов обсудить детали заказа"
}
```

#### POST `/chats/start/{user_id}`
Начало нового чата с пользователем.

### 4. Пользователи (`/users`)

#### GET `/users/profile`
Получение профиля текущего пользователя.

#### PUT `/users/profile`
Обновление профиля.

#### GET `/users/{nickname}`
Получение публичного профиля пользователя.

#### GET `/users/`
Получение списка пользователей с фильтрацией.

### 5. Отзывы (`/reviews`)

#### POST `/reviews/orders/{order_id}/executor`
Создание отзыва об исполнителе.

**Тело запроса:**
```json
{
  "rate": 5,
  "text": "Отличная работа, выполнил в срок!"
}
```

#### POST `/reviews/orders/{order_id}/customer`
Создание отзыва о заказчике.

#### GET `/reviews/user/{user_id}`
Получение отзывов пользователя.

#### PUT `/reviews/{review_id}`
Редактирование отзыва.

#### POST `/reviews/{review_id}/response`
Ответ на отзыв.

### 6. Администрирование (`/admin`)

#### GET `/admin/stats`
Получение статистики платформы.

#### GET `/admin/users`
Получение списка всех пользователей.

#### PUT `/admin/users/{user_id}`
Обновление данных пользователя.

#### DELETE `/admin/users/{user_id}`
Удаление пользователя.

#### GET `/admin/orders`
Получение списка всех заказов.

#### PUT `/admin/orders/{order_id}`
Обновление заказа.

#### DELETE `/admin/orders/{order_id}`
Удаление заказа.

#### GET `/admin/commission`
Получение настроек комиссий.

#### PUT `/admin/commission`
Обновление настроек комиссий.

### 7. Поиск (`/search`)

#### GET `/search/`
Поиск по заказам, пользователям и категориям.

**Параметры запроса:**
- `q` (str) - Поисковый запрос
- `limit` (int) - Лимит результатов

### 8. Контент (`/content`)

#### POST `/content/`
Создание контента (новости, статьи, тесты).

#### GET `/content/`
Получение списка контента.

#### GET `/content/{content_id}`
Получение конкретного контента.

#### PUT `/content/{content_id}`
Обновление контента.

#### DELETE `/content/{content_id}`
Удаление контента.

### 9. Рейтинги и награды (`/ratings`)

#### GET `/ratings/leaderboard/earnings`
Рейтинг по заработку.

#### GET `/ratings/leaderboard/tasks`
Рейтинг по количеству выполненных задач.

#### GET `/ratings/achievements/{user_id}`
Достижения пользователя.

#### GET `/ratings/rewards/{user_id}`
Награды пользователя.

### 10. Верификация (`/verification`)

#### POST `/verification/phone/send`
Отправка SMS с кодом верификации.

#### POST `/verification/phone/confirm`
Подтверждение номера телефона.

#### GET `/verification/status`
Статус верификации пользователя.

## Коды ошибок

- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещён
- `404` - Ресурс не найден
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

## Примеры использования

### Регистрация и создание заказа

```python
import requests

# Регистрация
response = requests.post('http://localhost:8000/api/v1/auth/register', json={
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "nickname": "ivan123",
    "password": "password123",
    "password_confirm": "password123"
})

token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Создание заказа
response = requests.post('http://localhost:8000/api/v1/orders/', 
                        json={
                            "title": "Создание лендинга",
                            "description": "Нужен современный лендинг",
                            "price": 5000,
                            "term": 7,
                            "category": "Веб-разработка"
                        },
                        headers=headers)
```

### Получение заказов с фильтрацией

```python
# Получение заказов по категории
response = requests.get('http://localhost:8000/api/v1/orders/?category_id=1&min_price=1000&max_price=10000',
                       headers=headers)

orders = response.json()['orders']
```

## Swagger UI

Интерактивная документация API доступна по адресу:
```
http://localhost:8000/docs
```

