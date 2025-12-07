Скрипт для запуска тестов с различными конфигурациями
import subprocess
def run_command(command, description):
    """Запуск команды с выводом результата"""
    print(f"\n{'='*50}")
    print(f"Запуск: {description}")
    print(f"Команда: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ УСПЕШНО")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ ОШИБКА")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
    
    return result.returncode == 0

def main():
    """Основная функция"""
    print("🧪 Запуск тестов для TeenFreelance Platform")
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists("main.py"):
        print("❌ Ошибка: main.py не найден. Запустите скрипт из корневой директории проекта.")
        sys.exit(1)
    
    # Устанавливаем зависимости для тестов
    print("\n📦 Установка зависимостей для тестов...")
    success = run_command("pip install -r tests/requirements.txt", "Установка зависимостей")
    if not success:
        print("❌ Не удалось установить зависимости для тестов")
    # Запускаем различные типы тестов
    test_commands = [
        ("pytest tests/test_basic.py -v", "Базовые тесты"),
        ("pytest tests/test_auth.py -v", "Тесты аутентификации"),
        ("pytest tests/test_orders.py -v", "Тесты заказов"),
        ("pytest tests/test_chats.py -v", "Тесты чатов"),
        ("pytest tests/test_users.py -v", "Тесты пользователей"),
        ("pytest tests/test_websocket.py -v", "Тесты WebSocket"),
        ("pytest tests/test_integration.py -v", "Интеграционные тесты"),
        ("pytest tests/test_performance.py -v -m 'not slow'", "Тесты производительности (быстрые)"),
        ("pytest tests/ -v --tb=short", "Все тесты"),
        ("pytest tests/ --cov=presentation --cov=infrastructure --cov=domain --cov-report=html", "Тесты с покрытием кода"),
    ]
    
    results = []
    
    for command, description in test_commands:
        success = run_command(command, description)
        results.append((description, success))
    
    # Выводим итоговый отчет
    print(f"\n{'='*60}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"{status:12} | {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Статистика:")
    print(f"   Прошло: {passed}")
    print(f"   Провалено: {failed}")
    print(f"   Всего: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return 0
    else:
        print(f"\n⚠️  {failed} ТЕСТОВ ПРОВАЛЕНО")
        return 1

if __name__ == "__main__":
    sys.exit(main())







