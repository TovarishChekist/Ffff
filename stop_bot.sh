#!/bin/bash
# Скрипт остановки бота

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🛑 Остановка Telegram-бота..."

# Ищем процесс бота
if pgrep -f "python.*run_bot.py" > /dev/null; then
    # Останавливаем бота
    pkill -f "python.*run_bot.py"

    # Ждем завершения
    sleep 2

    # Проверяем, остановился ли
    if ! pgrep -f "python.*run_bot.py" > /dev/null; then
        echo -e "${GREEN}✅ Бот успешно остановлен${NC}"
    else
        echo -e "${YELLOW}⚠ Принудительная остановка...${NC}"
        pkill -9 -f "python.*run_bot.py"
        echo -e "${GREEN}✅ Бот остановлен принудительно${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Бот не запущен${NC}"
fi
