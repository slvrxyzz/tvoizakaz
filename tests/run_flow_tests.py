#!/usr/bin/env python3
"""
Скрипт для запуска всех flow тестов
Поддерживает различные режимы запуска и категории тестов
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Выполняем: {' '.join(command)}")
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 минут таймаут
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Время выполнения: {duration:.2f} секунд")
        print(f"📊 Код выхода: {result.returncode}")
        
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n❌ STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Успешно выполнено!")
        else:
            print("❌ Ошибка выполнения!")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут выполнения команды!")
        return False
    except Exception as e:
        print(f"💥 Ошибка выполнения: {e}")
        return False

def run_basic_tests():
    """Запускает базовые тесты"""
    command = [
        "python", "-m", "pytest",
        "tests/test_simple_api.py",
        "tests/test_business_logic.py",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Базовые тесты API и бизнес-логики")

def run_flow_tests():
    """Запускает flow тесты"""
    command = [
        "python", "-m", "pytest",
        "tests/test_api_flows.py",
        "-v",
        "--tb=short",
        "-m", "not slow"
    ]
    return run_command(command, "Flow тесты API")

def run_websocket_tests():
    """Запускает WebSocket тесты"""
    command = [
        "python", "-m", "pytest",
        "tests/test_websocket_flows.py",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "WebSocket flow тесты")

def run_performance_tests():
    """Запускает тесты производительности"""
    command = [
        "python", "-m", "pytest",
        "tests/test_performance_flows.py",
        "-v",
        "--tb=short",
        "-m", "not stress"
    ]
    return run_command(command, "Тесты производительности")

def run_stress_tests():
    """Запускает стресс-тесты"""
    command = [
        "python", "-m", "pytest",
        "tests/test_performance_flows.py",
        "-v",
        "--tb=short",
        "-m", "stress"
    ]
    return run_command(command, "Стресс-тесты")

def run_security_tests():
    """Запускает тесты безопасности"""
    command = [
        "python", "-m", "pytest",
        "tests/test_security_flows.py",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Тесты безопасности")

def run_integration_tests():
    """Запускает тесты интеграции"""
    command = [
        "python", "-m", "pytest",
        "tests/test_integration_flows.py",
        "-v",
        "--tb=short"
    ]
    return run_command(command, "Тесты интеграции")

def run_all_tests():
    """Запускает все тесты"""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--durations=10"
    ]
    return run_command(command, "Все тесты")

def run_specific_test(test_path):
    """Запускает конкретный тест"""
    command = [
        "python", "-m", "pytest",
        test_path,
        "-v",
        "--tb=short"
    ]
    return run_command(command, f"Конкретный тест: {test_path}")

def run_tests_with_coverage():
    """Запускает тесты с покрытием кода"""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    return run_command(command, "Тесты с покрытием кода")

def run_tests_parallel():
    """Запускает тесты параллельно"""
    command = [
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-n", "auto"
    ]
    return run_command(command, "Параллельные тесты")

def check_dependencies():
    """Проверяет зависимости"""
    print("🔍 Проверяем зависимости...")
    
    required_packages = [
        "pytest",
        "httpx",
        "fastapi",
        "pytest-asyncio"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ Все зависимости установлены!")
    return True

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Запуск flow тестов")
    parser.add_argument(
        "test_type",
        choices=[
            "basic", "flow", "websocket", "performance", 
            "stress", "security", "integration", "all", 
            "coverage", "parallel", "check"
        ],
        help="Тип тестов для запуска"
    )
    parser.add_argument(
        "--test-path",
        help="Путь к конкретному тесту"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )
    
    args = parser.parse_args()
    
    print("🧪 Flow Test Runner")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Создаем директорию для логов
    log_dir = project_root / "tests" / "logs"
    log_dir.mkdir(exist_ok=True)
    
    success = False
    
    if args.test_type == "check":
        success = True
    elif args.test_type == "basic":
        success = run_basic_tests()
    elif args.test_type == "flow":
        success = run_flow_tests()
    elif args.test_type == "websocket":
        success = run_websocket_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "stress":
        success = run_stress_tests()
    elif args.test_type == "security":
        success = run_security_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "coverage":
        success = run_tests_with_coverage()
    elif args.test_type == "parallel":
        success = run_tests_parallel()
    elif args.test_path:
        success = run_specific_test(args.test_path)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("💥 Некоторые тесты завершились с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    main()
