# -*- coding: utf-8 -*-
"""
Состояния для управления диалогами с пользователем
"""

from enum import Enum


class UserState(str, Enum):
    """Состояния пользователя в боте"""

    # Обращение
    APPEAL = "appeal"

    # Заявка на вступление
    APPLICATION_FIO = "application_fio"
    APPLICATION_AGE = "application_age"
    APPLICATION_SCHOOL = "application_school"
    APPLICATION_CLASS = "application_class"
    APPLICATION_USERNAME = "application_username"
    APPLICATION_MOTIVATION = "application_motivation"
    APPLICATION_EXPERIENCE = "application_experience"
    APPLICATION_CONTACTS = "application_contacts"

    # Админ-панель - редактирование сообщений
    ADMIN_EDIT_MESSAGE = "admin_edit_message"

    # Админ-панель - рассылка
    ADMIN_BROADCAST_COMPOSE = "admin_broadcast_compose"


# Словари для хранения состояний пользователей
user_states = {}  # chat_id -> UserState
user_data = {}    # chat_id -> dict с данными заявки / данными редактирования

# Мапа для связи сообщений в групповых чатах с пользователями
# (group_chat_id, group_message_id) -> user_chat_id
responses_map = {}

# Последние сообщения бота для удаления при возврате в меню
# chat_id -> message_id
last_bot_message = {}
