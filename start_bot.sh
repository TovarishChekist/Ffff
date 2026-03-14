#!/bin/bash
# Скрипт запуска бота без прокси

# Очищаем все переменные прокси
unset HTTP_PROXY
unset HTTPS_PROXY
unset http_proxy
unset https_proxy
unset GLOBAL_AGENT_HTTP_PROXY
unset GLOBAL_AGENT_HTTPS_PROXY
unset ALL_PROXY
unset all_proxy

# Переходим в директорию проекта
cd /home/user/Ffff

# Запускаем бота
exec python3 run_bot.py "$@"
