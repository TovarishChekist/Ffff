# -*- coding: utf-8 -*-
"""
Клавиатуры для Telegram-бота
"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    """
    Создает основное меню бота

    Returns:
        ReplyKeyboardMarkup: Главное меню с кнопками
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("📩 Обращение в Совет"))
    markup.add(KeyboardButton("📝 Заявка на вступление в Совет"))
    markup.add(KeyboardButton("ℹ️ Информация о Совете"))
    markup.add(KeyboardButton("👥 Руководство Совета"))
    return markup


def back_to_menu() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой возврата в меню

    Returns:
        ReplyKeyboardMarkup: Кнопка "Вернуться в меню"
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("🔙 Вернуться в меню"))
    return markup
