"""
Простой Telegram-бот для приема обращений председателю.
"""
import logging
import os
from datetime import datetime
from typing import Optional, Tuple

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from app import app
from models import Appeal, db

DEFAULT_CATEGORY = "other"
DEFAULT_STATUS = "new"


def load_settings() -> Tuple[str, Optional[str]]:
    """Загрузить настройки окружения для бота."""
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chairman_chat_id = os.environ.get("TELEGRAM_CHAIRMAN_CHAT_ID")
    return token, chairman_chat_id


def build_title(message_text: str) -> str:
    """Сформировать краткий заголовок обращения."""
    clean_text = " ".join(message_text.strip().split())
    if not clean_text:
        return "Обращение из Telegram"
    return f"Telegram: {clean_text[:60]}" + ("…" if len(clean_text) > 60 else "")


def build_contact_name(user, fallback_name: Optional[str] = None) -> str:
    """Сформировать имя контакта из данных пользователя Telegram."""
    if fallback_name:
        return fallback_name
    parts = [user.first_name, user.last_name]
    name = " ".join([part for part in parts if part])
    return name or user.username or "Аноним"


def get_contact_data(context: ContextTypes.DEFAULT_TYPE) -> Tuple[Optional[str], Optional[str]]:
    """Достать сохраненные контактные данные из контекста пользователя."""
    contact_name = context.user_data.get("contact_name") if context.user_data else None
    contact_phone = context.user_data.get("contact_phone") if context.user_data else None
    return contact_name, contact_phone


def clear_contact_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очистить сохраненные контактные данные."""
    if context.user_data is not None:
        context.user_data.pop("contact_name", None)
        context.user_data.pop("contact_phone", None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартовое сообщение."""
    greeting = (
        "Здравствуйте! Это ящик обращений председателю Совета Первых.\n"
        "Отправьте ваше сообщение одним текстом, и я передам его председателю.\n\n"
        "Если хотите, можете отправить контакт (кнопка «Поделиться контактом»), "
        "чтобы мы могли связаться с вами."
    )
    if update.message:
        await update.message.reply_text(greeting)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подсказка по использованию."""
    message = (
        "Отправьте сообщение в чат, и оно будет зарегистрировано как обращение.\n"
        "Можно указать контактные данные прямо в тексте или отправить контакт отдельно.\n"
        "Команда /cancel очищает сохраненный контакт."
    )
    if update.message:
        await update.message.reply_text(message)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очистить сохраненные контактные данные."""
    clear_contact_data(context)
    if update.message:
        await update.message.reply_text("Контактные данные очищены. Можете отправить обращение текстом.")


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сохранить контакт, отправленный пользователем."""
    if not update.message or not update.message.contact:
        return

    contact = update.message.contact
    contact_name = " ".join([part for part in [contact.first_name, contact.last_name] if part]) or "Контакт"
    if context.user_data is not None:
        context.user_data["contact_name"] = contact_name
        context.user_data["contact_phone"] = contact.phone_number

    await update.message.reply_text(
        "Спасибо! Контакт сохранён. Теперь отправьте текст обращения одним сообщением."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка текстовых обращений."""
    if not update.message or not update.message.text:
        return

    message_text = update.message.text.strip()
    if not message_text:
        await update.message.reply_text("Сообщение пустое. Пожалуйста, напишите текст обращения.")
        return

    user = update.effective_user
    stored_name, stored_phone = get_contact_data(context)
    contact_name = build_contact_name(user, stored_name)
    title = build_title(message_text)

    with app.app_context():
        appeal = Appeal(
            contact_name=contact_name,
            contact_phone=stored_phone,
            title=title,
            content=message_text,
            category=DEFAULT_CATEGORY,
            status=DEFAULT_STATUS,
            is_private=True,
        )
        db.session.add(appeal)
        db.session.commit()
        appeal_id = appeal.id

    clear_contact_data(context)

    await update.message.reply_text(
        f"Спасибо! Ваше обращение зарегистрировано под номером #{appeal_id}."
    )

    chairman_chat_id = context.application.bot_data.get("chairman_chat_id")
    if chairman_chat_id:
        chairman_message = (
            "Новое обращение из Telegram:\n"
            f"Номер: #{appeal_id}\n"
            f"От: {contact_name}\n"
            f"Телефон: {stored_phone or 'не указан'}\n"
            f"Дата: {datetime.utcnow():%d.%m.%Y %H:%M UTC}\n\n"
            f"{message_text}"
        )
        await context.bot.send_message(chat_id=chairman_chat_id, text=chairman_message)


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ответ на неподдерживаемые типы сообщений."""
    if update.message:
        await update.message.reply_text("Пожалуйста, отправьте обращение текстом.")


def main() -> None:
    """Запуск бота."""
    token, chairman_chat_id = load_settings()
    if not token:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN")

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    application = ApplicationBuilder().token(token).build()
    application.bot_data["chairman_chat_id"] = chairman_chat_id

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.TEXT & ~filters.COMMAND, handle_unsupported)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
