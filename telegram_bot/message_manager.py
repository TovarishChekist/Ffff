# -*- coding: utf-8 -*-
"""
Менеджер для управления текстовыми сообщениями бота
"""

import json
import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MessageManager:
    """Класс для управления текстовыми сообщениями бота"""

    def __init__(self, custom_messages_path: str = "telegram_bot/custom_messages.json"):
        """
        Инициализация менеджера сообщений

        Args:
            custom_messages_path: Путь к файлу с пользовательскими сообщениями
        """
        self.default_messages_path = Path(__file__).parent / "default_messages.json"
        self.custom_messages_path = Path(custom_messages_path)

        self.default_messages = self._load_default_messages()
        self.custom_messages = self._load_custom_messages()

    def _load_default_messages(self) -> Dict:
        """Загружает дефолтные сообщения из JSON"""
        try:
            with open(self.default_messages_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки дефолтных сообщений: {e}")
            return {}

    def _load_custom_messages(self) -> Dict:
        """Загружает пользовательские сообщения из JSON"""
        if not self.custom_messages_path.exists():
            return {}

        try:
            with open(self.custom_messages_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки пользовательских сообщений: {e}")
            return {}

    def _save_custom_messages(self) -> bool:
        """Сохраняет пользовательские сообщения в JSON"""
        try:
            # Создаем директорию если её нет
            self.custom_messages_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.custom_messages_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_messages, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения пользовательских сообщений: {e}")
            return False

    def get(self, key: str) -> str:
        """
        Получает текст сообщения по ключу

        Args:
            key: Ключ сообщения

        Returns:
            str: Текст сообщения
        """
        # Сначала ищем в пользовательских, потом в дефолтных
        if key in self.custom_messages:
            return self.custom_messages[key].get('content', '')

        if key in self.default_messages:
            return self.default_messages[key].get('content', '')

        logger.warning(f"Сообщение с ключом '{key}' не найдено")
        return f"[Сообщение '{key}' не найдено]"

    def get_title(self, key: str) -> str:
        """
        Получает заголовок сообщения по ключу

        Args:
            key: Ключ сообщения

        Returns:
            str: Заголовок сообщения
        """
        if key in self.custom_messages:
            return self.custom_messages[key].get('title', key)

        if key in self.default_messages:
            return self.default_messages[key].get('title', key)

        return key

    def set(self, key: str, content: str, title: Optional[str] = None) -> bool:
        """
        Устанавливает новый текст сообщения

        Args:
            key: Ключ сообщения
            content: Новый текст
            title: Заголовок (опционально)

        Returns:
            bool: True если успешно сохранено
        """
        if key not in self.default_messages:
            logger.warning(f"Попытка установить несуществующий ключ: {key}")
            return False

        # Используем заголовок из дефолта если не указан
        if title is None:
            title = self.default_messages[key].get('title', key)

        self.custom_messages[key] = {
            'title': title,
            'content': content
        }

        result = self._save_custom_messages()
        if result:
            logger.info(f"Сообщение '{key}' обновлено администратором")
        return result

    def reset(self, key: str) -> bool:
        """
        Сбрасывает сообщение к дефолтному значению

        Args:
            key: Ключ сообщения

        Returns:
            bool: True если успешно сброшено
        """
        if key in self.custom_messages:
            del self.custom_messages[key]
            result = self._save_custom_messages()
            if result:
                logger.info(f"Сообщение '{key}' сброшено к дефолтному значению")
            return result
        return True

    def reset_all(self) -> bool:
        """
        Сбрасывает все сообщения к дефолтным значениям

        Returns:
            bool: True если успешно сброшено
        """
        self.custom_messages = {}
        result = self._save_custom_messages()
        if result:
            logger.info("Все сообщения сброшены к дефолтным значениям")
        return result

    def get_all_keys(self) -> list:
        """
        Возвращает список всех доступных ключей сообщений

        Returns:
            list: Список ключей
        """
        return sorted(self.default_messages.keys())

    def is_custom(self, key: str) -> bool:
        """
        Проверяет, является ли сообщение кастомизированным

        Args:
            key: Ключ сообщения

        Returns:
            bool: True если сообщение кастомизировано
        """
        return key in self.custom_messages

    def get_stats(self) -> Dict:
        """
        Возвращает статистику по сообщениям

        Returns:
            dict: Статистика
        """
        return {
            'total': len(self.default_messages),
            'customized': len(self.custom_messages),
            'default': len(self.default_messages) - len(self.custom_messages)
        }


# Глобальный экземпляр менеджера
message_manager = MessageManager()
