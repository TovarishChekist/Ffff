# -*- coding: utf-8 -*-
"""
Обработчики для обращений в Совет
"""

import logging
from telebot import TeleBot
from telebot.types import Message

from ..states import user_states, UserState, responses_map
from ..config import BotConfig
from ..utils import delete_message_safe, delete_last_bot_message, send_and_track
from ..messages import get_appeal_prompt, get_appeal_sent
from ..keyboards import back_to_menu

logger = logging.getLogger(__name__)


def register_appeal_handlers(bot: TeleBot) -> None:
    """
    Регистрирует обработчики для обращений

    Args:
        bot: Экземпляр TeleBot
    """

    @bot.message_handler(func=lambda m: m.text == "📩 Обращение в Совет")
    def start_appeal(message: Message):
        """Начинает процесс отправки обращения"""
        chat_id = message.chat.id
        logger.info(f"Пользователь {message.from_user.id} начал обращение")

        # Удаляем сообщение пользователя
        delete_message_safe(bot, chat_id, message.message_id)

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Отправляем промпт
        send_and_track(bot, chat_id, get_appeal_prompt(), reply_markup=back_to_menu())

        # Устанавливаем состояние
        user_states[chat_id] = UserState.APPEAL

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPEAL)
    def process_appeal(message: Message):
        """Обрабатывает текст обращения"""
        chat_id = message.chat.id
        logger.info(f"Получено обращение от пользователя {message.from_user.id}")

        try:
            # Пересылаем сообщение в чат для обращений
            forwarded = bot.forward_message(
                BotConfig.APPEAL_CHAT_ID,
                chat_id,
                message.message_id
            )

            # Сохраняем связь для возможности ответа
            responses_map[(BotConfig.APPEAL_CHAT_ID, forwarded.message_id)] = chat_id

            # Удаляем предыдущее сообщение бота
            delete_last_bot_message(bot, chat_id)

            # Отправляем подтверждение
            send_and_track(bot, chat_id, get_appeal_sent(), reply_markup=back_to_menu())

            # Очищаем состояние
            del user_states[chat_id]

            logger.info(f"Обращение от пользователя {message.from_user.id} успешно переслано")

        except Exception as e:
            logger.error(f"Ошибка при пересылке обращения: {e}")
            bot.send_message(
                chat_id,
                "❌ Произошла ошибка при отправке обращения. Попробуйте позже.",
                reply_markup=back_to_menu()
            )
            # Очищаем состояние
            if chat_id in user_states:
                del user_states[chat_id]
