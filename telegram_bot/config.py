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

    # Список ID администраторов (через запятую)
    ADMIN_IDS: list = []

    @classmethod
    def load_admin_ids(cls) -> None:
        """Загружает список ID администраторов из переменной окружения"""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            cls.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором

        Args:
            user_id: Telegram ID пользователя

        Returns:
            bool: True если пользователь - администратор
        """
        return user_id in cls.ADMIN_IDS

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
