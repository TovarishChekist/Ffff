# -*- coding: utf-8 -*-
"""
Вспомогательные функции для бота
"""

import logging
from typing import Optional
from telebot import TeleBot
from telebot.types import Message

from .states import last_bot_message
from .keyboards import main_menu

logger = logging.getLogger(__name__)


def send_menu(bot: TeleBot, chat_id: int, text: Optional[str] = None) -> Message:
    """
    Отправляет главное меню пользователю

    Args:
        bot: Экземпляр TeleBot
        chat_id: ID чата пользователя
        text: Текст сообщения (если None, используется стандартный)

    Returns:
        Message: Отправленное сообщение
    """
    from .messages import get_welcome_message

    if text is None:
        text = get_welcome_message()

    sent = bot.send_message(chat_id, text, reply_markup=main_menu(), parse_mode='HTML')
    last_bot_message[chat_id] = sent.message_id
    return sent


def delete_message_safe(bot: TeleBot, chat_id: int, message_id: int) -> bool:
    """
    Безопасно удаляет сообщение (не выбрасывает исключение при ошибке)

    Args:
        bot: Экземпляр TeleBot
        chat_id: ID чата
        message_id: ID сообщения

    Returns:
        bool: True если удалено успешно, False иначе
    """
    try:
        bot.delete_message(chat_id, message_id)
        return True
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение {message_id} в чате {chat_id}: {e}")
        return False


def delete_last_bot_message(bot: TeleBot, chat_id: int) -> bool:
    """
    Удаляет последнее сообщение бота в чате

    Args:
        bot: Экземпляр TeleBot
        chat_id: ID чата

    Returns:
        bool: True если удалено успешно, False иначе
    """
    if chat_id in last_bot_message:
        result = delete_message_safe(bot, chat_id, last_bot_message[chat_id])
        if result:
            del last_bot_message[chat_id]
        return result
    return False


def send_and_track(bot: TeleBot, chat_id: int, text: str, reply_markup=None, parse_mode='HTML') -> Message:
    """
    Отправляет сообщение и сохраняет его ID для последующего удаления

    Args:
        bot: Экземпляр TeleBot
        chat_id: ID чата
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        parse_mode: Режим парсинга (по умолчанию HTML)

    Returns:
        Message: Отправленное сообщение
    """
    sent = bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    last_bot_message[chat_id] = sent.message_id
    return sent
