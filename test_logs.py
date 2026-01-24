#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы логов
"""

import os
import sys

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

from telegram_bot.log_manager import log_manager

def test_logs():
    """Тестирует систему логов"""
    print("=" * 60)
    print("Тестирование системы логов")
    print("=" * 60)

    # Получаем информацию о всех логах
    logs_info = log_manager.get_all_logs_info()

    print(f"\n📋 Найдено категорий логов: {len(logs_info)}")

    for log_info in logs_info:
        print(f"\n📄 {log_info['title']} ({log_info['category']})")
        print(f"   Путь: {log_manager.get_log_file_path(log_info['category'])}")
        print(f"   Существует: {log_info['exists']}")

        if log_info['exists']:
            print(f"   Размер: {log_info['size_mb']} МБ ({log_info['size']} байт)")
            print(f"   Строк: {log_info['lines']}")
            print(f"   Изменен: {log_info['modified']}")
        else:
            print(f"   Файл не создан")

    # Проверяем настройки автоочистки
    print(f"\n⚙️ Настройки автоочистки:")
    settings = log_manager.get_auto_cleanup_settings()
    print(f"   Включена: {settings['enabled']}")
    print(f"   Интервал: {settings['interval_hours']} часов")
    print(f"   Последняя очистка: {settings['last_cleanup']}")

    print("\n" + "=" * 60)
    print("✅ Тест завершен")
    print("=" * 60)


if __name__ == '__main__':
    test_logs()
