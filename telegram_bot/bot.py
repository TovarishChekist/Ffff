#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Главный файл Telegram-бота
Детского и Молодёжного Общественного Совета
"""

import logging
import sys
import telebot
from telebot import apihelper

from .config import BotConfig
from .handlers import (
    register_common_handlers,
    register_appeal_handlers,
    register_application_handlers,
    register_admin_handlers,
    register_admin_panel_handlers
)

# Настройка логирования
def setup_logging():
    """Настраивает логирование для бота"""
    import os

    # Определяем путь к файлу лога
    base_dir = os.path.dirname(__file__)
    log_file = os.path.join(base_dir, 'bot.log')

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=getattr(logging, BotConfig.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )


def configure_api():
    """Настраивает параметры Telegram API"""
    import os

    # Увеличиваем таймауты для обработки проблем с подключением
    apihelper.CONNECT_TIMEOUT = BotConfig.CONNECT_TIMEOUT
    apihelper.READ_TIMEOUT = BotConfig.READ_TIMEOUT

    # Настройка прокси (если указан в .env)
    proxy_dict = BotConfig.get_proxy_dict()
    if proxy_dict:
        apihelper.proxy = proxy_dict
        logging.info(f"Прокси настроен: {proxy_dict}")
    else:
        # Явно отключаем прокси, игнорируя системные переменные окружения
        apihelper.proxy = None
        # Очищаем переменные окружения прокси для requests/urllib3
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                    'GLOBAL_AGENT_HTTP_PROXY', 'GLOBAL_AGENT_HTTPS_PROXY']:
            os.environ.pop(var, None)
        logging.info("Прокси отключен")


def main():
    """Главная функция запуска бота"""
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Запуск Telegram-бота Детского и Молодёжного Совета")
    logger.info("=" * 60)

    try:
        # Валидация конфигурации
        BotConfig.validate()
        logger.info("✓ Конфигурация валидна")

        # Загрузка списка администраторов
        BotConfig.load_admin_ids()
        if BotConfig.ADMIN_IDS:
            logger.info(f"✓ Загружено администраторов: {len(BotConfig.ADMIN_IDS)}")
        else:
            logger.warning("⚠ Администраторы не настроены. Админ-панель будет недоступна.")

        # Инициализация менеджеров
        from .log_manager import log_manager
        from .user_manager import user_manager
        logger.info("✓ Менеджеры инициализированы")
        logger.info(f"  - Пользователей в базе: {user_manager.get_user_count()}")

        # Проверяем настройки автоочистки логов
        autoclean_settings = log_manager.get_auto_cleanup_settings()
        if autoclean_settings['enabled']:
            logger.info(f"  - Автоочистка логов: включена ({autoclean_settings['interval_hours']}ч)")
        else:
            logger.info(f"  - Автоочистка логов: выключена")

        # Настройка API
        configure_api()
        logger.info("✓ API настроен")

        # Создание экземпляра бота
        bot = telebot.TeleBot(BotConfig.BOT_TOKEN)
        logger.info("✓ Бот инициализирован")

        # Регистрация обработчиков
        register_common_handlers(bot)
        register_appeal_handlers(bot)
        register_application_handlers(bot)
        register_admin_handlers(bot)
        register_admin_panel_handlers(bot)
        logger.info("✓ Обработчики зарегистрированы")

        # Проверка подключения
        bot_info = bot.get_me()
        logger.info(f"✓ Подключение успешно! Бот: @{bot_info.username}")

        logger.info("=" * 60)
        logger.info("Бот запущен и готов к работе!")
        logger.info("Нажмите Ctrl+C для остановки")
        logger.info("=" * 60)

        # Запуск polling
        bot.infinity_polling(timeout=30, long_polling_timeout=30)

    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        logger.error("Проверьте файл .env и убедитесь, что все необходимые переменные установлены")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)

    finally:
        logger.info("Бот остановлен")


if __name__ == '__main__':
    main()
