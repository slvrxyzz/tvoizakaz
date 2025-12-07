import os
from contextlib import closing
from typing import Iterable, Optional

import pymysql
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()


def resolve(value: Optional[str], fallback: Optional[str] = None) -> Optional[str]:
    return value if value not in (None, "") else fallback


def host_candidates() -> Iterable[str]:
    env_host = resolve(os.environ.get("DB_HOST"))
    mysql_host = resolve(os.environ.get("MYSQL_HOST"))

    candidates = []
    for item in (env_host, mysql_host):
        if item and item not in candidates:
            candidates.append(item)

    for default_host in ("127.0.0.1", "localhost", "db"):
        if default_host not in candidates:
            candidates.append(default_host)

    return candidates


def resolve_port() -> int:
    env_port = resolve(os.environ.get("DB_PORT"))
    mysql_port = resolve(os.environ.get("MYSQL_PORT"))
    try_values = [env_port, mysql_port, "3306"]
    for value in try_values:
        if not value:
            continue
        try:
            return int(value)
        except ValueError:
            continue
    return 3306


def connect_with_fallback(hosts: Iterable[str], port: int, **kwargs):
    last_error = None
    for host in hosts:
        print(f"Пробуем подключиться к {host}:{port} ...")
        try:
            connection = pymysql.connect(host=host, port=port, **kwargs)
            print(f"Подключение успешно: {host}:{port}")
            return connection
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"Не удалось подключиться к {host}:{port}: {exc}")
    if last_error:
        raise last_error
    raise RuntimeError("Не удалось определить параметры подключения к БД")


DB_PORT = resolve_port()
DB_USER = resolve(os.environ.get("MYSQL_USER"), "myuser")
DB_PASSWORD = resolve(os.environ.get("MYSQL_PASSWORD"), "mypassword")
DB_NAME = resolve(os.environ.get("MYSQL_DATABASE"), "mydb")

SUPPORT_EMAIL = resolve(os.environ.get("SUPPORT_EMAIL"), "support@teenfreelance.ru")
SUPPORT_NICK = resolve(os.environ.get("SUPPORT_NICK"), "support")
SUPPORT_NAME = resolve(os.environ.get("SUPPORT_NAME"), "Service Support")
SUPPORT_PASSWORD = resolve(os.environ.get("SUPPORT_PASSWORD"), "support123")

PASSWORD_COLUMN = "hashed_password"

print("Параметры подключения к DB:")
print(f"DB_HOST candidates: {', '.join(host_candidates())}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_USER: {DB_USER}")
print(f"DB_PASSWORD: {'*' * len(DB_PASSWORD)}")
print(f"DB_NAME: {DB_NAME}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(SUPPORT_PASSWORD)

with closing(
    connect_with_fallback(
        host_candidates(),
        DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
    )
) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM users LIKE 'is_support'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN is_support BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("Added is_support column to users table")

        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='users' AND COLUMN_NAME IN ('hashed_password', 'password_hash')", (DB_NAME,))
        column_row = cursor.fetchone()
        if not column_row:
            raise RuntimeError("Не найдено поле hashed_password/password_hash в таблице users")
        password_column = column_row["COLUMN_NAME"]

        cursor.execute("SELECT id FROM users WHERE email=%s", (SUPPORT_EMAIL,))
        if cursor.fetchone() is None:
            cursor.execute(
                f"INSERT INTO users (name, nickname, email, {password_column}, is_support, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                (SUPPORT_NAME, SUPPORT_NICK, SUPPORT_EMAIL, password_hash, True)
            )
            conn.commit()
            print("Support user created.")
        else:
            print("Support user already exists.")