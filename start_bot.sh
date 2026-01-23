#!/bin/bash
# Скрипт автоматического запуска бота на PythonAnywhere

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Запуск Telegram-бота..."

# Получаем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Виртуальное окружение не найдено!${NC}"
    echo "Создаем виртуальное окружение..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем наличие зависимостей
if ! python -c "import telebot" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Зависимости не установлены${NC}"
    echo "Устанавливаем зависимости..."
    pip install -r requirements-bot.txt
    echo -e "${GREEN}✓ Зависимости установлены${NC}"
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo "Создайте файл .env на основе .env.example"
    exit 1
fi

# Останавливаем предыдущий экземпляр бота (если запущен)
pkill -f "python.*run_bot.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠ Остановлен предыдущий экземпляр бота${NC}"
    sleep 2
fi

# Запускаем бота в фоне
nohup python run_bot.py > bot.log 2>&1 &
BOT_PID=$!

# Ждем немного для инициализации
sleep 3

# Проверяем, запустился ли бот
if ps -p $BOT_PID > /dev/null; then
    echo -e "${GREEN}✅ Бот успешно запущен (PID: $BOT_PID)${NC}"
    echo "📋 Логи: tail -f bot.log"
    echo "🛑 Остановить: pkill -f run_bot.py"
else
    echo -e "${RED}❌ Ошибка запуска бота${NC}"
    echo "Проверьте логи: tail -n 50 bot.log"
    exit 1
fi
