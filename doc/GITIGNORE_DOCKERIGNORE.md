# 📁 .gitignore и .dockerignore

## 🎯 Обзор

Проект использует `.gitignore` и `.dockerignore` для исключения ненужных файлов из Git репозитория и Docker контекста.

## 📋 .gitignore

### 🐍 Python файлы
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
```

### 🧪 Тестирование
```gitignore
# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
```

### 🗄️ База данных
```gitignore
# Database
*.db
*.sqlite
*.sqlite3
test.db
```

### 🎨 Frontend (Node.js)
```gitignore
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js build output
.next
out/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
```

### 💻 IDE и редакторы
```gitignore
# PyCharm
.idea/

# VS Code
.vscode/

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo

# Emacs
*~
\#*\#
/.emacs.desktop
/.emacs.desktop.lock
*.elc
```

### 🖥️ Операционные системы
```gitignore
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/

# Linux
*~
```

### 🐳 Docker
```gitignore
# Docker
.dockerignore
```

### 📁 Проект-специфичные файлы
```gitignore
# Project specific
fronted_base/
fronted_old/
old_*/
backup/
```

## 🐳 .dockerignore

### 📚 Документация
```dockerignore
# Documentation
README.md
doc/
*.md
```

### 🧪 Тестирование
```dockerignore
# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
.hypothesis/
tests/
```

### 🛠️ Скрипты
```dockerignore
# Scripts
scripts/
```

### 🐳 Docker файлы
```dockerignore
# Docker
Dockerfile*
docker-compose*.yml
.dockerignore
```

### 🔧 CI/CD
```dockerignore
# CI/CD
.github/
.gitlab-ci.yml
.travis.yml
.circleci/
```

### 📁 Проект-специфичные директории
```dockerignore
# Project specific
fronted_base/
fronted_old/
old_*/
backup/
```

## 🎯 Принципы организации

### .gitignore
- **Исключает** файлы из Git репозитория
- **Включает** все необходимые для разработки файлы
- **Исключает** временные, сгенерированные и конфиденциальные файлы

### .dockerignore
- **Исключает** файлы из Docker контекста
- **Уменьшает** размер Docker образа
- **Ускоряет** сборку Docker образа
- **Исключает** ненужные для production файлы

## 📊 Результат

### Размер репозитория
- ✅ **Минимальный** - Только необходимые файлы
- ✅ **Быстрый клон** - Меньше файлов для загрузки
- ✅ **Чистая история** - Нет случайных коммитов

### Размер Docker образа
- ✅ **Оптимизированный** - Только production файлы
- ✅ **Быстрая сборка** - Меньше файлов для копирования
- ✅ **Безопасность** - Нет конфиденциальных файлов

## 🔍 Проверка

### Проверка .gitignore
```bash
# Проверка игнорируемых файлов
git status --ignored

# Проверка конкретного файла
git check-ignore filename

# Проверка всех игнорируемых файлов
git ls-files --ignored --exclude-standard
```

### Проверка .dockerignore
```bash
# Проверка Docker контекста
docker build --no-cache .

# Проверка размера контекста
docker build --no-cache . 2>&1 | grep "Sending build context"
```

## 🛠️ Добавление новых исключений

### В .gitignore
```bash
# Добавить новый паттерн
echo "new_pattern/" >> .gitignore

# Проверить
git check-ignore new_pattern/file.txt
```

### В .dockerignore
```bash
# Добавить новый паттерн
echo "new_pattern/" >> .dockerignore

# Проверить
docker build --no-cache .
```

## 📋 Чеклист

### .gitignore
- [ ] Python файлы (__pycache__, *.pyc)
- [ ] Virtual environments (.venv, venv/)
- [ ] IDE файлы (.vscode/, .idea/)
- [ ] OS файлы (.DS_Store, Thumbs.db)
- [ ] Database файлы (*.db, *.sqlite)
- [ ] Log файлы (*.log)
- [ ] Environment файлы (.env)
- [ ] Build файлы (build/, dist/)
- [ ] Test файлы (coverage, .pytest_cache)
- [ ] Node.js файлы (node_modules/, .next/)

### .dockerignore
- [ ] Documentation (README.md, doc/)
- [ ] Testing (tests/, .pytest_cache/)
- [ ] Scripts (scripts/)
- [ ] Docker файлы (Dockerfile*, docker-compose*.yml)
- [ ] CI/CD файлы (.github/, .gitlab-ci.yml)
- [ ] IDE файлы (.vscode/, .idea/)
- [ ] OS файлы (.DS_Store, Thumbs.db)
- [ ] Log файлы (*.log)
- [ ] Environment файлы (.env)
- [ ] Build файлы (build/, dist/)

---

**Оптимизированные .gitignore и .dockerignore! 🚀**







