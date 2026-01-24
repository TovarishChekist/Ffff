# -*- coding: utf-8 -*-
"""
Обработчики админ-панели для управления текстами бота
"""

import logging
import time
import os
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
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("📋 Логи", callback_data="admin_logs"),
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


def create_logs_menu() -> InlineKeyboardMarkup:
    """Создает меню управления логами"""
    from ..log_manager import log_manager

    markup = InlineKeyboardMarkup(row_width=1)

    # Кнопки для каждой категории логов
    logs_info = log_manager.get_all_logs_info()

    for log_info in logs_info:
        category = log_info['category']
        title = log_info['title']
        size_mb = log_info['size_mb']
        exists_icon = "📄" if log_info['exists'] else "⚪"

        button_text = f"{exists_icon} {title}"
        if log_info['exists']:
            button_text += f" ({size_mb} МБ)"

        markup.add(
            InlineKeyboardButton(button_text, callback_data=f"admin_log_view_{category}")
        )

    # Настройки автоочистки
    markup.add(
        InlineKeyboardButton("⚙️ Настройки автоочистки", callback_data="admin_log_autoclean_settings"),
        InlineKeyboardButton("🗑️ Очистить все логи", callback_data="admin_log_clear_all_confirm"),
        InlineKeyboardButton("🔙 В админ-меню", callback_data="admin_menu")
    )

    return markup


def create_log_actions_keyboard(category: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру действий для конкретного лога"""
    from ..log_manager import log_manager

    markup = InlineKeyboardMarkup(row_width=1)

    log_info = log_manager.get_log_info(category)

    if log_info['exists']:
        markup.add(
            InlineKeyboardButton("📥 Скачать файл", callback_data=f"admin_log_download_{category}"),
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"admin_log_delete_{category}")
        )

    markup.add(
        InlineKeyboardButton("🔙 К списку логов", callback_data="admin_logs")
    )

    return markup


def create_autoclean_settings_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру настроек автоочистки"""
    from ..log_manager import log_manager

    settings = log_manager.get_auto_cleanup_settings()
    enabled = settings['enabled']

    markup = InlineKeyboardMarkup(row_width=2)

    # Кнопка вкл/выкл
    toggle_text = "✅ Выключить" if enabled else "⚪ Включить"
    markup.add(
        InlineKeyboardButton(toggle_text, callback_data="admin_log_autoclean_toggle")
    )

    if enabled:
        # Кнопки выбора интервала
        current_interval = settings['interval_hours']

        intervals = [
            (6, "6 часов"),
            (12, "12 часов"),
            (24, "24 часа")
        ]

        for hours, label in intervals:
            icon = "✅" if hours == current_interval else "⚪"
            markup.add(
                InlineKeyboardButton(
                    f"{icon} {label}",
                    callback_data=f"admin_log_autoclean_interval_{hours}"
                )
            )

    markup.add(
        InlineKeyboardButton("🔙 К логам", callback_data="admin_logs")
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

        # Рассылка
        elif data == "admin_broadcast":
            from ..user_manager import user_manager
            user_count = user_manager.get_user_count()
            stats = user_manager.get_stats()

            text = f"""📢 <b>Рассылка сообщений</b>

<b>Статистика пользователей:</b>
• Всего пользователей: {stats['total_users']}
• Активных сегодня: {stats['active_today']}
• Всего взаимодействий: {stats['total_interactions']}

<i>Отправьте сообщение, которое хотите разослать всем пользователям.
Вы сможете предпросмотреть его перед отправкой.</i>

<b>Форматирование:</b>
• Используйте встроенное форматирование Telegram
• Или HTML-теги: &lt;b&gt;, &lt;i&gt;, &lt;a href=""&gt;, &lt;code&gt;"""

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("❌ Отмена", callback_data="admin_menu"))

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

            # Устанавливаем состояние ожидания сообщения для рассылки
            from ..states import user_states, UserState
            user_states[chat_id] = UserState.ADMIN_BROADCAST_COMPOSE

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

        # Подтверждение рассылки
        elif data == "broadcast_confirm":
            if chat_id not in user_data or 'broadcast_text' not in user_data[chat_id]:
                bot.answer_callback_query(call.id, "❌ Ошибка: текст рассылки не найден")
                return

            broadcast_text = user_data[chat_id]['broadcast_text']

            # Удаляем сообщение с предпросмотром
            delete_message_safe(bot, chat_id, message_id)

            # Отправляем уведомление о начале рассылки
            status_msg = bot.send_message(
                chat_id,
                "📢 <b>Рассылка началась...</b>\n\n<i>Пожалуйста, подождите</i>",
                parse_mode='HTML'
            )

            # Выполняем рассылку
            from ..user_manager import user_manager
            import time

            all_users = user_manager.get_all_user_ids()
            sent_count = 0
            failed_count = 0
            failed_users = []

            for user_id in all_users:
                try:
                    bot.send_message(user_id, broadcast_text, parse_mode='HTML')
                    sent_count += 1
                    # Небольшая задержка чтобы не попасть в rate limit Telegram
                    time.sleep(0.05)
                except Exception as e:
                    failed_count += 1
                    failed_users.append(user_id)
                    logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

            # Удаляем статус сообщение
            delete_message_safe(bot, chat_id, status_msg.message_id)

            # Отправляем результаты
            result_text = f"""✅ <b>Рассылка завершена!</b>

<b>Результаты:</b>
• Отправлено: {sent_count}
• Не доставлено: {failed_count}
• Всего пользователей: {len(all_users)}

<b>Успешность:</b> {round(sent_count / len(all_users) * 100, 1) if all_users else 0}%"""

            if failed_users and failed_count <= 10:
                result_text += f"\n\n<b>Не доставлено пользователям:</b>\n"
                for uid in failed_users[:10]:
                    result_text += f"• {uid}\n"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 В админ-меню", callback_data="admin_menu"))

            bot.send_message(
                chat_id,
                result_text,
                reply_markup=markup,
                parse_mode='HTML'
            )

            logger.info(f"Администратор {message.from_user.id} выполнил рассылку: {sent_count} успешно, {failed_count} ошибок")

            # Очищаем состояние
            if chat_id in user_states:
                del user_states[chat_id]
            if chat_id in user_data:
                del user_data[chat_id]

            bot.answer_callback_query(call.id)

        # Отмена рассылки
        elif data == "broadcast_cancel":
            delete_message_safe(bot, chat_id, message_id)
            bot.answer_callback_query(call.id, "❌ Рассылка отменена")

            # Очищаем состояние
            if chat_id in user_states:
                del user_states[chat_id]
            if chat_id in user_data:
                del user_data[chat_id]

            # Показываем админ-меню
            bot.send_message(
                chat_id,
                "🔧 <b>Админ-панель</b>",
                reply_markup=create_admin_menu(),
                parse_mode='HTML'
            )

        # ====================
        # УПРАВЛЕНИЕ ЛОГАМИ
        # ====================

        # Главное меню логов
        elif data == "admin_logs":
            try:
                from ..log_manager import log_manager

                logs_info = log_manager.get_all_logs_info()
                total_size = sum(log['size_mb'] for log in logs_info)

                text = f"""📋 <b>Управление логами</b>

<b>Общая информация:</b>
• Всего категорий: {len(logs_info)}
• Общий размер: {round(total_size, 2)} МБ

Выберите категорию лога для просмотра или управления:"""

                bot.edit_message_text(
                    text,
                    chat_id,
                    message_id,
                    reply_markup=create_logs_menu(),
                    parse_mode='HTML'
                )
                bot.answer_callback_query(call.id)
            except Exception as e:
                logger.error(f"Ошибка при открытии меню логов: {e}", exc_info=True)
                bot.answer_callback_query(call.id, f"❌ Ошибка: {e}", show_alert=True)

        # Просмотр конкретного лога
        elif data.startswith("admin_log_view_"):
            from ..log_manager import log_manager

            category = data.replace("admin_log_view_", "")
            log_info = log_manager.get_log_info(category)

            if log_info['exists']:
                text = f"""📄 <b>{log_info['title']}</b>

<b>Информация:</b>
• Размер: {log_info['size_mb']} МБ ({log_info['size']} байт)
• Строк: {log_info['lines']}
• Изменен: {log_info['modified'][:19].replace('T', ' ')}

<i>Что вы хотите сделать с этим логом?</i>"""
            else:
                text = f"""⚪ <b>{log_info['title']}</b>

<i>Этот лог пока пуст.</i>"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_log_actions_keyboard(category),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Скачивание лога
        elif data.startswith("admin_log_download_"):
            from ..log_manager import log_manager

            category = data.replace("admin_log_download_", "")
            log_path = log_manager.get_log_file_path(category)
            log_info = log_manager.get_log_info(category)

            if os.path.exists(log_path):
                bot.answer_callback_query(call.id, "📥 Отправляю файл...")

                try:
                    with open(log_path, 'rb') as f:
                        bot.send_document(
                            chat_id,
                            f,
                            caption=f"📄 {log_info['title']}\nРазмер: {log_info['size_mb']} МБ",
                            visible_file_name=f"{category}.log"
                        )
                    logger.info(f"Администратор {call.from_user.id} скачал лог {category}")
                except Exception as e:
                    bot.send_message(
                        chat_id,
                        f"❌ Ошибка отправки файла: {e}",
                        parse_mode='HTML'
                    )
                    logger.error(f"Ошибка отправки лога {category}: {e}")
            else:
                bot.answer_callback_query(call.id, "❌ Файл не найден", show_alert=True)

        # Удаление лога
        elif data.startswith("admin_log_delete_"):
            from ..log_manager import log_manager

            category = data.replace("admin_log_delete_", "")
            log_info = log_manager.get_log_info(category)

            text = f"""⚠️ <b>Подтверждение удаления</b>

Вы уверены, что хотите удалить лог <b>{log_info['title']}</b>?

<b>Размер:</b> {log_info['size_mb']} МБ
<b>Строк:</b> {log_info['lines']}

<i>Это действие нельзя отменить!</i>"""

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("✅ Да, удалить", callback_data=f"admin_log_delete_confirm_{category}"),
                InlineKeyboardButton("❌ Отмена", callback_data=f"admin_log_view_{category}")
            )

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Подтверждение удаления лога
        elif data.startswith("admin_log_delete_confirm_"):
            from ..log_manager import log_manager

            category = data.replace("admin_log_delete_confirm_", "")
            log_info = log_manager.get_log_info(category)

            if log_manager.delete_log(category):
                text = f"""✅ <b>Лог удален</b>

<b>{log_info['title']}</b> успешно удален.

<b>Было:</b>
• Размер: {log_info['size_mb']} МБ
• Строк: {log_info['lines']}"""

                logger.info(f"Администратор {call.from_user.id} удалил лог {category}")
            else:
                text = f"❌ Ошибка удаления лога {log_info['title']}"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 К логам", callback_data="admin_logs"))

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Очистка всех логов (подтверждение)
        elif data == "admin_log_clear_all_confirm":
            text = """⚠️ <b>Подтверждение очистки</b>

Вы уверены, что хотите удалить <b>ВСЕ логи</b>?

Это действие нельзя отменить!"""

            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("✅ Да, очистить все", callback_data="admin_log_clear_all"),
                InlineKeyboardButton("❌ Отмена", callback_data="admin_logs")
            )

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Очистка всех логов (выполнение)
        elif data == "admin_log_clear_all":
            from ..log_manager import log_manager

            results = log_manager.clear_all_logs()
            deleted_count = sum(1 for success in results.values() if success)

            text = f"""✅ <b>Логи очищены</b>

Удалено логов: {deleted_count}

<i>Все логи успешно очищены.</i>"""

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 К логам", callback_data="admin_logs"))

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id, "✅ Все логи очищены")
            logger.info(f"Администратор {call.from_user.id} очистил все логи")

        # Настройки автоочистки
        elif data == "admin_log_autoclean_settings":
            from ..log_manager import log_manager

            settings = log_manager.get_auto_cleanup_settings()

            status_icon = "✅" if settings['enabled'] else "⚪"
            status_text = "включена" if settings['enabled'] else "выключена"

            text = f"""⚙️ <b>Настройки автоочистки</b>

<b>Статус:</b> {status_icon} {status_text}"""

            if settings['enabled']:
                text += f"""
<b>Интервал:</b> {settings['interval_hours']} часов
<b>Последняя очистка:</b> {settings['last_cleanup'][:19].replace('T', ' ') if settings['last_cleanup'] else 'Не проводилась'}

<i>Автоочистка удаляет все логи через каждые {settings['interval_hours']} часов.</i>"""
            else:
                text += "\n\n<i>Включите автоочистку, чтобы логи автоматически удалялись через заданный интервал.</i>"

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_autoclean_settings_keyboard(),
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)

        # Переключение автоочистки
        elif data == "admin_log_autoclean_toggle":
            from ..log_manager import log_manager

            settings = log_manager.get_auto_cleanup_settings()
            new_status = not settings['enabled']

            log_manager.set_auto_cleanup(new_status, settings['interval_hours'])

            status_text = "включена" if new_status else "выключена"
            bot.answer_callback_query(call.id, f"Автоочистка {status_text}")

            logger.info(f"Администратор {call.from_user.id} {'включил' if new_status else 'выключил'} автоочистку логов")

            # Обновляем меню
            settings = log_manager.get_auto_cleanup_settings()
            status_icon = "✅" if settings['enabled'] else "⚪"
            status_text = "включена" if settings['enabled'] else "выключена"

            text = f"""⚙️ <b>Настройки автоочистки</b>

<b>Статус:</b> {status_icon} {status_text}"""

            if settings['enabled']:
                text += f"""
<b>Интервал:</b> {settings['interval_hours']} часов

<i>Выберите интервал автоочистки:</i>"""
            else:
                text += "\n\n<i>Включите автоочистку, чтобы логи автоматически удалялись через заданный интервал.</i>"

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_autoclean_settings_keyboard(),
                parse_mode='HTML'
            )

        # Установка интервала автоочистки
        elif data.startswith("admin_log_autoclean_interval_"):
            from ..log_manager import log_manager

            interval = int(data.replace("admin_log_autoclean_interval_", ""))
            log_manager.set_auto_cleanup(True, interval)

            bot.answer_callback_query(call.id, f"✅ Интервал изменен на {interval} часов")

            logger.info(f"Администратор {call.from_user.id} установил интервал автоочистки {interval}ч")

            # Обновляем меню
            settings = log_manager.get_auto_cleanup_settings()

            text = f"""⚙️ <b>Настройки автоочистки</b>

<b>Статус:</b> ✅ включена
<b>Интервал:</b> {settings['interval_hours']} часов
<b>Последняя очистка:</b> {settings['last_cleanup'][:19].replace('T', ' ') if settings['last_cleanup'] else 'Не проводилась'}

<i>Выберите интервал автоочистки:</i>"""

            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=create_autoclean_settings_keyboard(),
                parse_mode='HTML'
            )

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

    @bot.message_handler(func=lambda m: m.chat.id in user_states and user_states[m.chat.id] == UserState.ADMIN_BROADCAST_COMPOSE)
    def process_broadcast_message(message: Message):
        """Обрабатывает сообщение для рассылки"""
        chat_id = message.chat.id

        if not BotConfig.is_admin(message.from_user.id):
            return

        # Проверка на отмену
        if message.text == "/cancel":
            del user_states[chat_id]
            if chat_id in user_data:
                del user_data[chat_id]
            bot.reply_to(message, "❌ Рассылка отменена")
            return

        # Получаем текст с HTML-форматированием
        broadcast_text = message.html_text if message.html_text else message.text

        # Сохраняем текст рассылки
        user_data[chat_id] = {
            'broadcast_text': broadcast_text,
            'message_id': message.message_id
        }

        # Получаем статистику
        from ..user_manager import user_manager
        user_count = user_manager.get_user_count()

        # Показываем предпросмотр
        preview_text = f"""📢 <b>Предпросмотр рассылки</b>

<b>Будет отправлено {user_count} пользователям</b>

━━━━━━━━━━━━━━━━
{broadcast_text}
━━━━━━━━━━━━━━━━

<i>Проверьте сообщение перед отправкой</i>"""

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Отправить всем", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Отмена", callback_data="broadcast_cancel")
        )

        bot.send_message(
            chat_id,
            preview_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
