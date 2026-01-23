# -*- coding: utf-8 -*-
"""
Обработчики админ-панели для управления текстами бота
"""

import logging
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from ..states import user_states, user_data, UserState
from ..config import BotConfig
from ..message_manager import message_manager
from ..utils import delete_message_safe

logger = logging.getLogger(__name__)


def create_admin_menu() -> InlineKeyboardMarkup:
    """Создает главное меню администратора"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📝 Редактировать тексты", callback_data="admin_edit_texts"),
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("🔄 Сбросить все тексты", callback_data="admin_reset_all"),
        InlineKeyboardButton("❌ Закрыть", callback_data="admin_close")
    )
    return markup


def create_messages_list_keyboard(page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком всех сообщений

    Args:
        page: Номер страницы
        per_page: Количество элементов на странице

    Returns:
        InlineKeyboardMarkup: Клавиатура с сообщениями
    """
    markup = InlineKeyboardMarkup(row_width=1)
    all_keys = message_manager.get_all_keys()

    # Пагинация
    start_idx = page * per_page
    end_idx = start_idx + per_page
    keys_on_page = all_keys[start_idx:end_idx]

    # Добавляем кнопки для каждого сообщения
    for key in keys_on_page:
        title = message_manager.get_title(key)
        is_custom = message_manager.is_custom(key)
        emoji = "✏️" if is_custom else "📄"
        markup.add(InlineKeyboardButton(
            f"{emoji} {title}",
            callback_data=f"admin_view_{key}"
        ))

    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"admin_list_{page-1}"))
    if end_idx < len(all_keys):
        nav_buttons.append(InlineKeyboardButton("Вперёд ▶️", callback_data=f"admin_list_{page+1}"))

    if nav_buttons:
        markup.row(*nav_buttons)

    markup.add(InlineKeyboardButton("🔙 В админ-меню", callback_data="admin_menu"))

    return markup


def create_message_actions_keyboard(key: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру с действиями для конкретного сообщения"""
    markup = InlineKeyboardMarkup(row_width=2)

    is_custom = message_manager.is_custom(key)

    markup.add(
        InlineKeyboardButton("✏️ Редактировать", callback_data=f"admin_edit_{key}")
    )

    if is_custom:
        markup.add(
            InlineKeyboardButton("🔄 Сбросить к дефолту", callback_data=f"admin_reset_{key}")
        )

    markup.add(
        InlineKeyboardButton("🔙 К списку", callback_data="admin_list_0")
    )

    return markup


def register_admin_panel_handlers(bot: TeleBot) -> None:
    """
    Регистрирует обработчики админ-панели

    Args:
        bot: Экземпляр TeleBot
    """

    @bot.message_handler(commands=['admin'])
    def cmd_admin(message: Message):
        """Обработчик команды /admin"""
        if not BotConfig.is_admin(message.from_user.id):
            bot.reply_to(message, "❌ У вас нет прав администратора.")
            logger.warning(f"Попытка доступа к админ-панели от пользователя {message.from_user.id}")
            return

        logger.info(f"Администратор {message.from_user.id} открыл админ-панель")

        text = """🔧 <b>Панель администратора</b>

Добро пожаловать в админ-панель управления ботом!

Здесь вы можете:
• Редактировать все текстовые сообщения бота
• Просматривать статистику
• Сбрасывать тексты к дефолтным значениям"""

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=create_admin_menu(),
            parse_mode='HTML'
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
    def handle_admin_callback(call: CallbackQuery):
        """Обработчик callback-запросов админ-панели"""
        if not BotConfig.is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "❌ У вас нет прав администратора.")
            return

        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # Главное меню
        if data == "admin_menu":
            text = """🔧 <b>Панель администратора</b>

Добро пожаловать в админ-панель управления ботом!

Здесь вы можете:
• Редактировать все текстовые сообщения бота
• Просматривать статистику
• Сбрасывать тексты к дефолтным значениям"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_admin_menu(),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Редактирование текстов
        elif data == "admin_edit_texts":
            stats = message_manager.get_stats()
            text = f"""📝 <b>Редактирование текстов</b>

📊 <b>Статистика:</b>
• Всего сообщений: {stats['total']}
• Кастомизировано: {stats['customized']}
• Дефолтных: {stats['default']}

<i>📄 - дефолтное сообщение
✏️ - отредактированное сообщение</i>

Выберите сообщение для просмотра или редактирования:"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_messages_list_keyboard(),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Список сообщений (пагинация)
        elif data.startswith("admin_list_"):
            page = int(data.split("_")[2])
            stats = message_manager.get_stats()
            text = f"""📝 <b>Редактирование текстов</b>

📊 <b>Статистика:</b>
• Всего сообщений: {stats['total']}
• Кастомизировано: {stats['customized']}
• Дефолтных: {stats['default']}

<i>📄 - дефолтное сообщение
✏️ - отредактированное сообщение</i>

Выберите сообщение для просмотра или редактирования:"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_messages_list_keyboard(page),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Просмотр сообщения
        elif data.startswith("admin_view_"):
            key = data.replace("admin_view_", "")
            title = message_manager.get_title(key)
            content = message_manager.get(key)
            is_custom = message_manager.is_custom(key)

            status = "✏️ Отредактировано" if is_custom else "📄 Дефолтное"

            text = f"""<b>{title}</b>

<b>Статус:</b> {status}
<b>Ключ:</b> <code>{key}</code>

<b>Текущий текст:</b>
{content}"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_message_actions_keyboard(key),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Начать редактирование
        elif data.startswith("admin_edit_"):
            key = data.replace("admin_edit_", "")
            title = message_manager.get_title(key)
            current_text = message_manager.get(key)

            # Устанавливаем состояние
            user_states[chat_id] = UserState.ADMIN_EDIT_MESSAGE
            user_data[chat_id] = {
                'key': key,
                'title': title,
                'old_message_id': message_id
            }

            text = f"""✏️ <b>Редактирование: {title}</b>

<b>Текущий текст:</b>
{current_text}

<b>Отправьте новый текст сообщения.</b>

<i>Способы форматирования:

1️⃣ <b>Используйте встроенное форматирование Telegram:</b>
   • Выделите текст → выберите жирный/курсив/ссылку
   • Бот автоматически сохранит форматирование!

2️⃣ <b>Или используйте HTML-теги:</b>
   • &lt;b&gt;жирный&lt;/b&gt;
   • &lt;i&gt;курсив&lt;/i&gt;
   • &lt;code&gt;код&lt;/code&gt;
   • &lt;a href="URL"&gt;ссылка&lt;/a&gt;

Для отмены отправьте /cancel</i>"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id, "✏️ Отправьте новый текст сообщения")
            logger.info(f"Администратор {call.from_user.id} начал редактирование '{key}'")

        # Сброс к дефолту
        elif data.startswith("admin_reset_"):
            key = data.replace("admin_reset_", "")
            title = message_manager.get_title(key)

            if message_manager.reset(key):
                new_text = message_manager.get(key)
                text = f"""🔄 <b>{title}</b>

✅ Сообщение сброшено к дефолтному значению!

<b>Текущий текст:</b>
{new_text}"""

                bot.edit_message_text(
                    text,
                    chat_id,
                    message_id,
                    reply_markup=create_message_actions_keyboard(key),
                    parse_mode='HTML'
                )
                bot.answer_callback_query(call.id, "✅ Сброшено к дефолту")
                logger.info(f"Администратор {call.from_user.id} сбросил '{key}' к дефолту")
            else:
                bot.answer_callback_query(call.id, "❌ Ошибка при сбросе")

        # Статистика
        elif data == "admin_stats":
            stats = message_manager.get_stats()
            text = f"""📊 <b>Статистика</b>

<b>Сообщения:</b>
• Всего: {stats['total']}
• Кастомизировано: {stats['customized']}
• Дефолтных: {stats['default']}

<b>Процент кастомизации:</b> {round(stats['customized'] / stats['total'] * 100, 1)}%"""

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Назад", callback_data="admin_menu"))

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Сброс всех текстов
        elif data == "admin_reset_all":
            text = """⚠️ <b>Подтверждение сброса</b>

Вы уверены, что хотите сбросить <b>ВСЕ</b> тексты к дефолтным значениям?

Это действие нельзя отменить!"""

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("✅ Да, сбросить", callback_data="admin_reset_all_confirm"),
                InlineKeyboardButton("❌ Отмена", callback_data="admin_menu")
            )

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Подтверждение сброса всех
        elif data == "admin_reset_all_confirm":
            if message_manager.reset_all():
                text = """✅ <b>Все тексты сброшены!</b>

Все сообщения вернулись к дефолтным значениям."""

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔙 В админ-меню", callback_data="admin_menu"))

                bot.edit_message_text(
                    text,
                    chat_id,
                    message_id,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
                bot.answer_callback_query(call.id, "✅ Все тексты сброшены")
                logger.warning(f"Администратор {call.from_user.id} сбросил ВСЕ тексты к дефолту")
            else:
                bot.answer_callback_query(call.id, "❌ Ошибка при сбросе")

        # Закрыть админ-панель
        elif data == "admin_close":
            delete_message_safe(bot, chat_id, message_id)
            bot.answer_callback_query(call.id, "Админ-панель закрыта")

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.ADMIN_EDIT_MESSAGE)
    def process_message_edit(message: Message):
        """Обрабатывает новый текст сообщения от администратора"""
        chat_id = message.chat.id

        if not BotConfig.is_admin(message.from_user.id):
            return

        # Проверка на отмену
        if message.text == "/cancel":
            del user_states[chat_id]
            del user_data[chat_id]
            bot.reply_to(message, "❌ Редактирование отменено")
            return

        # Получаем данные
        data = user_data[chat_id]
        key = data['key']
        title = data['title']
        old_message_id = data.get('old_message_id')

        # Получаем текст с HTML-форматированием
        # html_text сохраняет форматирование (жирный, курсив, ссылки) из Telegram
        new_text = message.html_text if message.html_text else message.text
        if message_manager.set(key, new_text):
            # Удаляем старое сообщение с инструкцией
            if old_message_id:
                delete_message_safe(bot, chat_id, old_message_id)

            text = f"""✅ <b>Сообщение обновлено!</b>

<b>{title}</b> успешно изменено.

<b>Новый текст:</b>
{new_text}"""

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📝 К списку сообщений", callback_data="admin_list_0"),
                InlineKeyboardButton("🔙 В админ-меню", callback_data="admin_menu")
            )

            bot.send_message(
                chat_id,
                text,
                reply_markup=markup,
                parse_mode='HTML'
            )

            logger.info(f"Администратор {message.from_user.id} обновил текст '{key}'")
        else:
            bot.reply_to(message, "❌ Ошибка при сохранении текста")

        # Очищаем состояние
        del user_states[chat_id]
        del user_data[chat_id]
