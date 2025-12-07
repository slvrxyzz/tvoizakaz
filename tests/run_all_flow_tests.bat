@echo off
REM Скрипт для запуска всех flow тестов в Windows
REM Использование: run_all_flow_tests.bat [тип_тестов]

setlocal enabledelayedexpansion

REM Проверяем что мы в правильной директории
if not exist "main.py" (
    echo ❌ Запустите скрипт из корневой директории проекта
    exit /b 1
)

REM Создаем директорию для логов
if not exist "tests\logs" mkdir tests\logs

REM Функция для вывода сообщений
:print_message
echo [%date% %time%] %~1
goto :eof

:print_success
echo ✅ %~1
goto :eof

:print_error
echo ❌ %~1
goto :eof

:print_warning
echo ⚠️  %~1
goto :eof

REM Функция проверки зависимостей
:check_dependencies
call :print_message "Проверка зависимостей..."

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python не найден"
    exit /b 1
)

REM Проверяем pip
pip --version >nul 2>&1
if errorlevel 1 (
    call :print_error "pip не найден"
    exit /b 1
)

REM Устанавливаем зависимости если нужно
if exist "tests\requirements.txt" (
    call :print_message "Установка зависимостей для тестов..."
    pip install -r tests\requirements.txt -q
)

call :print_success "Зависимости проверены"
goto :eof

REM Функция очистки
:cleanup
call :print_message "Очистка временных файлов..."
REM Удаляем временные файлы тестов
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
call :print_success "Очистка завершена"
goto :eof

REM Функция запуска тестов
:run_tests
set test_type=%~1
set description=%~2

call :print_message "Запуск %description%..."

python tests\run_flow_tests.py %test_type%
if errorlevel 1 (
    call :print_error "%description% завершились с ошибками"
    exit /b 1
) else (
    call :print_success "%description% завершены успешно"
)
goto :eof

REM Функция генерации отчета
:generate_report
set test_type=%~1
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
set report_file=tests\logs\test_report_%test_type%_%timestamp%.txt

call :print_message "Генерация отчета: %report_file%"

(
echo === Flow Tests Report ===
echo Test Type: %test_type%
echo Timestamp: %date% %time%
echo Python Version: 
python --version
echo =========================
echo.
) > "%report_file%"

if exist "tests\logs\pytest.log" (
    echo === Test Logs === >> "%report_file%"
    type tests\logs\pytest.log >> "%report_file%"
)

call :print_success "Отчет сохранен: %report_file%"
goto :eof

REM Основная функция
:main
set test_type=%~1
if "%test_type%"=="" set test_type=all

call :print_message "🚀 Запуск Flow Tests"
call :print_message "Тип тестов: %test_type%"
echo.

REM Проверяем зависимости
call :check_dependencies

REM Очищаем перед запуском
call :cleanup

REM Запускаем тесты в зависимости от типа
if "%test_type%"=="basic" (
    call :run_tests "basic" "Базовые тесты"
) else if "%test_type%"=="flow" (
    call :run_tests "flow" "Flow тесты API"
) else if "%test_type%"=="websocket" (
    call :run_tests "websocket" "WebSocket тесты"
) else if "%test_type%"=="performance" (
    call :run_tests "performance" "Тесты производительности"
) else if "%test_type%"=="stress" (
    call :run_tests "stress" "Стресс-тесты"
) else if "%test_type%"=="security" (
    call :run_tests "security" "Тесты безопасности"
) else if "%test_type%"=="integration" (
    call :run_tests "integration" "Тесты интеграции"
) else if "%test_type%"=="all" (
    call :print_message "Запуск всех тестов..."
    
    set failed_tests=
    
    REM Базовые тесты
    python tests\run_flow_tests.py basic
    if errorlevel 1 (
        set failed_tests=!failed_tests! basic
    ) else (
        call :print_success "Базовые тесты завершены успешно"
    )
    
    REM Flow тесты
    python tests\run_flow_tests.py flow
    if errorlevel 1 (
        set failed_tests=!failed_tests! flow
    ) else (
        call :print_success "Flow тесты API завершены успешно"
    )
    
    REM WebSocket тесты
    python tests\run_flow_tests.py websocket
    if errorlevel 1 (
        set failed_tests=!failed_tests! websocket
    ) else (
        call :print_success "WebSocket тесты завершены успешно"
    )
    
    REM Тесты производительности
    python tests\run_flow_tests.py performance
    if errorlevel 1 (
        set failed_tests=!failed_tests! performance
    ) else (
        call :print_success "Тесты производительности завершены успешно"
    )
    
    REM Тесты безопасности
    python tests\run_flow_tests.py security
    if errorlevel 1 (
        set failed_tests=!failed_tests! security
    ) else (
        call :print_success "Тесты безопасности завершены успешно"
    )
    
    REM Тесты интеграции
    python tests\run_flow_tests.py integration
    if errorlevel 1 (
        set failed_tests=!failed_tests! integration
    ) else (
        call :print_success "Тесты интеграции завершены успешно"
    )
    
    REM Стресс-тесты (опционально)
    if "%2"=="--include-stress" (
        python tests\run_flow_tests.py stress
        if errorlevel 1 (
            set failed_tests=!failed_tests! stress
        ) else (
            call :print_success "Стресс-тесты завершены успешно"
        )
    )
    
    REM Результат
    if "!failed_tests!"=="" (
        call :print_success "🎉 Все тесты прошли успешно!"
    ) else (
        call :print_error "💥 Некоторые тесты завершились с ошибками:!failed_tests!"
    )
) else if "%test_type%"=="coverage" (
    call :run_tests "coverage" "Тесты с покрытием кода"
) else if "%test_type%"=="parallel" (
    call :run_tests "parallel" "Параллельные тесты"
) else if "%test_type%"=="check" (
    call :run_tests "check" "Проверка зависимостей"
) else (
    call :print_error "Неизвестный тип тестов: %test_type%"
    echo Доступные типы: basic, flow, websocket, performance, stress, security, integration, all, coverage, parallel, check
    exit /b 1
)

REM Генерируем отчет
call :generate_report "%test_type%"

REM Финальная очистка
call :cleanup

call :print_message "🏁 Тестирование завершено"
goto :eof

REM Запуск
call :main %*






