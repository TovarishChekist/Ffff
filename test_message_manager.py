#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки работы MessageManager
"""

import os
import sys
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from telegram_bot.message_manager import MessageManager

def test_message_manager():
    """Тестирует сохранение и загрузку кастомных сообщений"""

    print("=" * 60)
    print("Тест MessageManager")
    print("=" * 60)

    # Создаем новый экземпляр менеджера
    mm = MessageManager()

    print(f"\n1. Путь к default_messages: {mm.default_messages_path}")
    print(f"   Существует: {mm.default_messages_path.exists()}")

    print(f"\n2. Путь к custom_messages: {mm.custom_messages_path}")
    print(f"   Существует: {mm.custom_messages_path.exists()}")

    # Получаем список всех ключей
    keys = mm.get_all_keys()
    print(f"\n3. Всего сообщений: {len(keys)}")

    if keys:
        # Берем первый ключ для теста
        test_key = keys[0]
        print(f"\n4. Тестируем с ключом: {test_key}")

        # Получаем оригинальный текст
        original_text = mm.get(test_key)
        print(f"   Оригинальный текст: {original_text[:50]}...")

        # Устанавливаем новый текст
        test_text = "🧪 ТЕСТОВОЕ СООБЩЕНИЕ 🧪\n\nЭто тестовое сообщение для проверки работы редактирования."
        print(f"\n5. Устанавливаем новый текст...")
        success = mm.set(test_key, test_text)
        print(f"   Результат: {'✓ Успешно' if success else '✗ Ошибка'}")

        # Проверяем, что файл создан
        if mm.custom_messages_path.exists():
            print(f"\n6. ✓ Файл custom_messages.json создан")

            # Читаем содержимое
            with open(mm.custom_messages_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   Содержимое: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"\n6. ✗ Файл custom_messages.json НЕ создан!")
            return False

        # Создаем новый экземпляр и проверяем загрузку
        print(f"\n7. Создаем новый экземпляр MessageManager...")
        mm2 = MessageManager()
        loaded_text = mm2.get(test_key)

        if loaded_text == test_text:
            print(f"   ✓ Текст загружен корректно!")
            print(f"   Загруженный текст: {loaded_text}")
        else:
            print(f"   ✗ Текст НЕ совпадает!")
            print(f"   Ожидалось: {test_text}")
            print(f"   Получено: {loaded_text}")
            return False

        # Сбрасываем к дефолту
        print(f"\n8. Сбрасываем к дефолту...")
        mm2.reset(test_key)
        reset_text = mm2.get(test_key)

        if reset_text == original_text:
            print(f"   ✓ Текст сброшен корректно!")
        else:
            print(f"   ✗ Ошибка сброса")
            return False

        print("\n" + "=" * 60)
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        return True

    else:
        print("\n✗ Нет сообщений для теста!")
        return False

if __name__ == '__main__':
    try:
        success = test_message_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
