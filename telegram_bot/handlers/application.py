# -*- coding: utf-8 -*-
"""
Обработчики для заявок на вступление в Совет
"""

import logging
from telebot import TeleBot
from telebot.types import Message

from ..states import user_states, user_data, UserState, responses_map
from ..config import BotConfig
from ..utils import delete_message_safe, delete_last_bot_message, send_and_track
from ..messages import (
    get_application_welcome,
    get_application_age_prompt,
    get_application_school_prompt,
    get_application_class_prompt,
    get_application_username_prompt,
    get_application_motivation_prompt,
    get_application_experience_prompt,
    get_application_contacts_prompt,
    get_application_success,
    format_application
)
from ..keyboards import back_to_menu

logger = logging.getLogger(__name__)


def register_application_handlers(bot: TeleBot) -> None:
    """
    Регистрирует обработчики для заявок на вступление

    Args:
        bot: Экземпляр TeleBot
    """

    @bot.message_handler(func=lambda m: m.text == "📝 Заявка на вступление в Совет")
    def start_application(message: Message):
        """Начинает процесс подачи заявки"""
        chat_id = message.chat.id
        logger.info(f"Пользователь {message.from_user.id} начал заявку на вступление")

        # Удаляем сообщение пользователя
        delete_message_safe(bot, chat_id, message.message_id)

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Отправляем приветствие и запрос ФИО
        send_and_track(bot, chat_id, get_application_welcome(), reply_markup=back_to_menu())

        # Устанавливаем состояние и инициализируем данные
        user_states[chat_id] = UserState.APPLICATION_FIO
        user_data[chat_id] = {}

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_FIO)
    def process_fio(message: Message):
        """Обрабатывает ввод ФИО"""
        chat_id = message.chat.id
        user_data[chat_id]['fio'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем возраст
        send_and_track(bot, chat_id, get_application_age_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_AGE

        logger.debug(f"Пользователь {message.from_user.id} указал ФИО")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_AGE)
    def process_age(message: Message):
        """Обрабатывает ввод возраста"""
        chat_id = message.chat.id
        user_data[chat_id]['age'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем школу
        send_and_track(bot, chat_id, get_application_school_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_SCHOOL

        logger.debug(f"Пользователь {message.from_user.id} указал возраст")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_SCHOOL)
    def process_school(message: Message):
        """Обрабатывает ввод школы"""
        chat_id = message.chat.id
        user_data[chat_id]['school'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем класс
        send_and_track(bot, chat_id, get_application_class_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_CLASS

        logger.debug(f"Пользователь {message.from_user.id} указал школу")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_CLASS)
    def process_class(message: Message):
        """Обрабатывает ввод класса"""
        chat_id = message.chat.id
        user_data[chat_id]['class'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем username
        send_and_track(bot, chat_id, get_application_username_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_USERNAME

        logger.debug(f"Пользователь {message.from_user.id} указал класс")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_USERNAME)
    def process_username(message: Message):
        """Обрабатывает ввод username"""
        chat_id = message.chat.id
        user_data[chat_id]['username'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем мотивацию
        send_and_track(bot, chat_id, get_application_motivation_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_MOTIVATION

        logger.debug(f"Пользователь {message.from_user.id} указал username")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_MOTIVATION)
    def process_motivation(message: Message):
        """Обрабатывает ввод мотивации"""
        chat_id = message.chat.id
        user_data[chat_id]['motivation'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем опыт
        send_and_track(bot, chat_id, get_application_experience_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_EXPERIENCE

        logger.debug(f"Пользователь {message.from_user.id} указал мотивацию")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_EXPERIENCE)
    def process_experience(message: Message):
        """Обрабатывает ввод опыта"""
        chat_id = message.chat.id
        user_data[chat_id]['experience'] = message.text

        # Удаляем предыдущее сообщение бота
        delete_last_bot_message(bot, chat_id)

        # Запрашиваем контакты
        send_and_track(bot, chat_id, get_application_contacts_prompt(), reply_markup=back_to_menu())
        user_states[chat_id] = UserState.APPLICATION_CONTACTS

        logger.debug(f"Пользователь {message.from_user.id} указал опыт")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.APPLICATION_CONTACTS)
    def process_contacts(message: Message):
        """Обрабатывает ввод контактов и отправляет заявку"""
        chat_id = message.chat.id
        user_data[chat_id]['contacts'] = message.text

        logger.info(f"Пользователь {message.from_user.id} заполнил заявку")

        try:
            # Формируем и отправляем заявку в групповой чат
            application_text = format_application(user_data[chat_id])
            sent_app = bot.send_message(
                BotConfig.APPLICATION_CHAT_ID,
                application_text,
                parse_mode='HTML'
            )

            # Сохраняем связь для возможности ответа
            responses_map[(BotConfig.APPLICATION_CHAT_ID, sent_app.message_id)] = chat_id

            # Удаляем предыдущее сообщение бота
            delete_last_bot_message(bot, chat_id)

            # Отправляем подтверждение
            send_and_track(bot, chat_id, get_application_success(), reply_markup=back_to_menu())

            # Очищаем состояние и данные
            del user_states[chat_id]
            del user_data[chat_id]

            logger.info(f"Заявка от пользователя {message.from_user.id} успешно отправлена")

        except Exception as e:
            logger.error(f"Ошибка при отправке заявки: {e}")
            bot.send_message(
                chat_id,
                "❌ Произошла ошибка при отправке заявки. Попробуйте позже.",
                reply_markup=back_to_menu()
            )
            # Очищаем состояние и данные
            if chat_id in user_states:
                del user_states[chat_id]
            if chat_id in user_data:
                del user_data[chat_id]
