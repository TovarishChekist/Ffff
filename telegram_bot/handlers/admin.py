# -*- coding: utf-8 -*-
"""
Обработчики для ответов администраторов из групповых чатов
"""

import logging
from telebot import TeleBot
from telebot.types import Message

from ..states import responses_map
from ..config import BotConfig
from ..messages import COUNCIL_RESPONSE, ADMIN_RESPONSE_SENT

logger = logging.getLogger(__name__)


def register_admin_handlers(bot: TeleBot) -> None:
    """
    Регистрирует обработчики для ответов администраторов

    Args:
        bot: Экземпляр TeleBot
    """

    @bot.message_handler(func=lambda m: m.chat.id in [BotConfig.APPEAL_CHAT_ID, BotConfig.APPLICATION_CHAT_ID]
                                        and m.reply_to_message is not None)
    def handle_admin_response(message: Message):
        """Обрабатывает ответы администраторов в групповых чатах"""
        key = (message.chat.id, message.reply_to_message.message_id)

        if key in responses_map:
            user_chat_id = responses_map[key]
            logger.info(f"Отправка ответа пользователю {user_chat_id} от администратора")

            try:
                # Форматируем и отправляем ответ пользователю
                formatted_response = COUNCIL_RESPONSE.format(message=message.text)
                bot.send_message(user_chat_id, formatted_response, parse_mode='HTML')

                # Подтверждаем администратору
                bot.reply_to(message, ADMIN_RESPONSE_SENT)

                logger.info(f"Ответ успешно отправлен пользователю {user_chat_id}")

            except Exception as e:
                logger.error(f"Ошибка при отправке ответа пользователю {user_chat_id}: {e}")
                bot.reply_to(message, f"❌ Ошибка при отправке ответа: {e}")
        else:
            logger.warning(f"Не найден пользователь для ответа на сообщение {message.reply_to_message.message_id}")
