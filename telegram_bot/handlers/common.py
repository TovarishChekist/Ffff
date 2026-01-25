# -*- coding: utf-8 -*-
"""
Общие обработчики (команды, меню)
"""

import logging
from telebot import TeleBot
from telebot.types import Message

from ..states import user_states, user_data
from ..utils import send_menu, delete_message_safe, delete_last_bot_message, send_and_track, save_user_from_message
from ..messages import (
    get_council_info,
    get_leadership_info,
    get_back_to_menu
)
from ..keyboards import back_to_menu

logger = logging.getLogger(__name__)


def register_common_handlers(bot: TeleBot) -> None:
    """
    Регистрирует общие обработчики команд

    Args:
        bot: Экземпляр TeleBot
    """

    @bot.message_handler(commands=['start'])
    def cmd_start(message: Message):
        """Обработчик команды /start"""
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
        # Сохраняем пользователя в базу
        save_user_from_message(message)
        send_menu(bot, message.chat.id)

    @bot.message_handler(func=lambda m: m.text in ["🔙 Вернуться в меню", "Вернуться в меню"])
    def return_to_menu(message: Message):
        """Обработчик возврата в главное меню"""
        chat_id = message.chat.id
        logger.info(f"Пользователь {message.from_user.id} вернулся в меню")

        # Сохраняем пользователя
        save_user_from_message(message)

        # Очищаем состояние
        if chat_id in user_states:
            del user_states[chat_id]
        if chat_id in user_data:
            del user_data[chat_id]

        # Удаляем сообщение пользователя
        delete_message_safe(bot, chat_id, message.message_id)

        # Удаляем последнее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Отправляем меню
        send_menu(bot, chat_id, get_back_to_menu())

    @bot.message_handler(func=lambda m: m.text == "ℹ️ Информация о Совете")
    def handle_info(message: Message):
        """Обработчик кнопки 'Информация о Совете'"""
        chat_id = message.chat.id
        logger.info(f"Пользователь {message.from_user.id} запросил информацию о Совете")

        # Сохраняем пользователя
        save_user_from_message(message)

        # Удаляем сообщение пользователя
        delete_message_safe(bot, chat_id, message.message_id)

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Отправляем информацию
        send_and_track(bot, chat_id, get_council_info(), reply_markup=back_to_menu())

    @bot.message_handler(func=lambda m: m.text == "👥 Руководство Совета")
    def handle_leadership(message: Message):
        """Обработчик кнопки 'Руководство Совета'"""
        chat_id = message.chat.id
        logger.info(f"Пользователь {message.from_user.id} запросил информацию о руководстве")

        # Сохраняем пользователя
        save_user_from_message(message)

        # Удаляем сообщение пользователя
        delete_message_safe(bot, chat_id, message.message_id)

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Отправляем информацию
        send_and_track(bot, chat_id, get_leadership_info(), reply_markup=back_to_menu())
