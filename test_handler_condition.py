#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест условия обработчика редактирования
"""

import sys
sys.path.insert(0, '/home/user/Ffff')

from telegram_bot.states import user_states, user_data, UserState

# Симулируем установку состояния
chat_id = 123456789
user_states[chat_id] = UserState.ADMIN_EDIT_MESSAGE
user_data[chat_id] = {
    'key': 'test_key',
    'title': 'Test Title',
    'old_message_id': 999
}

print("=" * 60)
print("Тест условия обработчика")
print("=" * 60)

print(f"\n1. Установленное состояние:")
print(f"   user_states[{chat_id}] = {user_states[chat_id]}")
print(f"   Тип: {type(user_states[chat_id])}")
print(f"   user_data[{chat_id}] = {user_data[chat_id]}")

print(f"\n2. UserState.ADMIN_EDIT_MESSAGE:")
print(f"   Значение: {UserState.ADMIN_EDIT_MESSAGE}")
print(f"   Тип: {type(UserState.ADMIN_EDIT_MESSAGE)}")

print(f"\n3. Проверка равенства:")
print(f"   user_states[{chat_id}] == UserState.ADMIN_EDIT_MESSAGE:")
print(f"   {user_states[chat_id] == UserState.ADMIN_EDIT_MESSAGE}")

print(f"\n4. Проверка строкового значения:")
print(f"   user_states[{chat_id}] == 'admin_edit_message':")
print(f"   {user_states[chat_id] == 'admin_edit_message'}")

print(f"\n5. Проверка условия обработчика (имитация):")
# Имитируем объект сообщения
class MockMessage:
    def __init__(self, chat_id):
        self.chat.id = chat_id
        self.chat = type('obj', (object,), {'id': chat_id})

m = MockMessage(chat_id)

condition1 = m.chat.id in user_states
condition2 = user_states[m.chat.id] == UserState.ADMIN_EDIT_MESSAGE
overall = condition1 and condition2

print(f"   m.chat.id in user_states: {condition1}")
print(f"   user_states[m.chat.id] == UserState.ADMIN_EDIT_MESSAGE: {condition2}")
print(f"   Общее условие: {overall}")

print("\n" + "=" * 60)
print("✓ Тест завершен")
print("=" * 60)
