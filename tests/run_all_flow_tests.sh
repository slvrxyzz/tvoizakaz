#!/bin/bash
# Скрипт для запуска всех flow тестов
# Использование: ./run_all_flow_tests.sh [тип_тестов]

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверяем что мы в правильной директории
if [ ! -f "main.py" ]; then
    print_error "Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Создаем директорию для логов
mkdir -p tests/logs

# Функция запуска тестов
run_tests() {
    local test_type=$1
    local description=$2
    
    print_message "Запуск $description..."
    
    if python tests/run_flow_tests.py $test_type; then
        print_success "$description завершены успешно"
        return 0
    else
        print_error "$description завершились с ошибками"
        return 1
    fi
}

# Функция проверки зависимостей
check_dependencies() {
    print_message "Проверка зависимостей..."
    
    # Проверяем Python
    if ! command -v python &> /dev/null; then
        print_error "Python не найден"
        exit 1
    fi
    
    # Проверяем pip
    if ! command -v pip &> /dev/null; then
        print_error "pip не найден"
        exit 1
    fi
    
    # Устанавливаем зависимости если нужно
    if [ ! -f "tests/requirements.txt" ]; then
        print_warning "Файл requirements.txt не найден"
    else
        print_message "Установка зависимостей для тестов..."
        pip install -r tests/requirements.txt -q
    fi
    
    print_success "Зависимости проверены"
}

# Функция очистки
cleanup() {
    print_message "Очистка временных файлов..."
    # Удаляем временные файлы тестов
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Очистка завершена"
}

# Функция генерации отчета
generate_report() {
    local test_type=$1
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local report_file="tests/logs/test_report_${test_type}_${timestamp}.txt"
    
    print_message "Генерация отчета: $report_file"
    
    {
        echo "=== Flow Tests Report ==="
        echo "Test Type: $test_type"
        echo "Timestamp: $(date)"
        echo "Python Version: $(python --version)"
        echo "========================="
        echo ""
        
        if [ -f "tests/logs/pytest.log" ]; then
            echo "=== Test Logs ==="
            cat tests/logs/pytest.log
        fi
        
    } > "$report_file"
    
    print_success "Отчет сохранен: $report_file"
}

# Основная функция
main() {
    local test_type=${1:-"all"}
    
    print_message "🚀 Запуск Flow Tests"
    print_message "Тип тестов: $test_type"
    echo ""
    
    # Проверяем зависимости
    check_dependencies
    
    # Очищаем перед запуском
    cleanup
    
    # Запускаем тесты в зависимости от типа
    case $test_type in
        "basic")
            run_tests "basic" "Базовые тесты"
            ;;
        "flow")
            run_tests "flow" "Flow тесты API"
            ;;
        "websocket")
            run_tests "websocket" "WebSocket тесты"
            ;;
        "performance")
            run_tests "performance" "Тесты производительности"
            ;;
        "stress")
            run_tests "stress" "Стресс-тесты"
            ;;
        "security")
            run_tests "security" "Тесты безопасности"
            ;;
        "integration")
            run_tests "integration" "Тесты интеграции"
            ;;
        "all")
            print_message "Запуск всех тестов..."
            
            local failed_tests=()
            
            # Базовые тесты
            if ! run_tests "basic" "Базовые тесты"; then
                failed_tests+=("basic")
            fi
            
            # Flow тесты
            if ! run_tests "flow" "Flow тесты API"; then
                failed_tests+=("flow")
            fi
            
            # WebSocket тесты
            if ! run_tests "websocket" "WebSocket тесты"; then
                failed_tests+=("websocket")
            fi
            
            # Тесты производительности
            if ! run_tests "performance" "Тесты производительности"; then
                failed_tests+=("performance")
            fi
            
            # Тесты безопасности
            if ! run_tests "security" "Тесты безопасности"; then
                failed_tests+=("security")
            fi
            
            # Тесты интеграции
            if ! run_tests "integration" "Тесты интеграции"; then
                failed_tests+=("integration")
            fi
            
            # Стресс-тесты (опционально)
            if [ "$2" = "--include-stress" ]; then
                if ! run_tests "stress" "Стресс-тесты"; then
                    failed_tests+=("stress")
                fi
            fi
            
            # Результат
            if [ ${#failed_tests[@]} -eq 0 ]; then
                print_success "🎉 Все тесты прошли успешно!"
            else
                print_error "💥 Некоторые тесты завершились с ошибками:"
                for test in "${failed_tests[@]}"; do
                    print_error "  - $test"
                done
            fi
            ;;
        "coverage")
            run_tests "coverage" "Тесты с покрытием кода"
            ;;
        "parallel")
            run_tests "parallel" "Параллельные тесты"
            ;;
        "check")
            run_tests "check" "Проверка зависимостей"
            ;;
        *)
            print_error "Неизвестный тип тестов: $test_type"
            echo "Доступные типы: basic, flow, websocket, performance, stress, security, integration, all, coverage, parallel, check"
            exit 1
            ;;
    esac
    
    # Генерируем отчет
    generate_report "$test_type"
    
    # Финальная очистка
    cleanup
    
    print_message "🏁 Тестирование завершено"
}

# Обработка сигналов
trap cleanup EXIT

# Запуск
main "$@"






