# -*- coding: utf-8 -*-
"""
Конфигурация Telegram-бота
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class BotConfig:
    """Конфигурация бота"""

    # Токен бота
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # ID чатов для пересылки сообщений
    APPEAL_CHAT_ID: int = int(os.getenv("APPEAL_CHAT_ID", "0"))
    APPLICATION_CHAT_ID: int = int(os.getenv("APPLICATION_CHAT_ID", "0"))

    # Таймауты для API
    CONNECT_TIMEOUT: float = float(os.getenv("CONNECT_TIMEOUT", "15.0"))
    READ_TIMEOUT: float = float(os.getenv("READ_TIMEOUT", "15.0"))

    # Прокси (опционально)
    PROXY: Optional[str] = os.getenv("PROXY", None)

    # Уровень логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """
        Проверяет корректность конфигурации

        Raises:
            ValueError: Если конфигурация невалидна
        """
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

        if cls.APPEAL_CHAT_ID == 0:
            raise ValueError("APPEAL_CHAT_ID не установлен в переменных окружения")

        if cls.APPLICATION_CHAT_ID == 0:
            raise ValueError("APPLICATION_CHAT_ID не установлен в переменных окружения")

    @classmethod
    def get_proxy_dict(cls) -> Optional[dict]:
        """
        Возвращает словарь с настройками прокси

        Returns:
            Optional[dict]: Словарь с прокси или None
        """
        if cls.PROXY:
            return {'https': cls.PROXY}
        return None
