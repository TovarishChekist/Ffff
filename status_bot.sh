#!/bin/bash
# Скрипт проверки статуса бота

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Статус Telegram-бота${NC}"
echo "================================"

# Проверяем, запущен ли бот
if pgrep -f "python.*run_bot.py" > /dev/null; then
    BOT_PID=$(pgrep -f "python.*run_bot.py")
    echo -e "Статус: ${GREEN}✅ Запущен${NC}"
    echo "PID: $BOT_PID"

    # Время работы процесса
    START_TIME=$(ps -o lstart= -p $BOT_PID)
    echo "Запущен: $START_TIME"

    # Использование памяти
    MEM=$(ps -o rss= -p $BOT_PID)
    MEM_MB=$((MEM / 1024))
    echo "Память: ${MEM_MB} MB"

    # CPU
    CPU=$(ps -o %cpu= -p $BOT_PID)
    echo "CPU: ${CPU}%"
else
    echo -e "Статус: ${RED}❌ Остановлен${NC}"
fi

echo "================================"

# Размер лога
if [ -f "bot.log" ]; then
    LOG_SIZE=$(du -h bot.log | cut -f1)
    echo "Размер лога: $LOG_SIZE"

    # Последние ошибки
    ERROR_COUNT=$(grep -c "ERROR" bot.log 2>/dev/null || echo 0)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo -e "${YELLOW}⚠ Ошибок в логе: $ERROR_COUNT${NC}"
    fi
else
    echo "Лог-файл не найден"
fi

echo "================================"
echo ""
echo "Команды управления:"
echo "  Запустить:  ./start_bot.sh"
echo "  Остановить: ./stop_bot.sh"
echo "  Логи:       tail -f bot.log"
