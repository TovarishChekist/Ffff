#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы логов и пользователей
"""

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_log_manager():
    """Тестирует систему логов"""
    print("=" * 60)
    print("ТЕСТ СИСТЕМЫ ЛОГОВ")
    print("=" * 60)

    try:
        from telegram_bot.log_manager import log_manager

        print("\n✓ log_manager импортирован успешно")

        # Тестируем get_all_logs_info
        print("\nПроверка get_all_logs_info():")
        logs_info = log_manager.get_all_logs_info()

        for log_info in logs_info:
            print(f"\n  📄 Категория: {log_info['category']}")

            # Проверяем наличие поля 'title'
            if 'title' in log_info:
                print(f"     ✓ Title: {log_info['title']}")
            else:
                print(f"     ❌ ОШИБКА: Поле 'title' отсутствует!")
                return False

            print(f"     Существует: {'Да' if log_info['exists'] else 'Нет'}")
            if log_info['exists']:
                print(f"     Размер: {log_info['size_mb']} МБ")
                print(f"     Строк: {log_info['lines']}")

        print("\n✅ Система логов работает корректно!")
        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_manager():
    """Тестирует систему пользователей"""
    print("\n" + "=" * 60)
    print("ТЕСТ СИСТЕМЫ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 60)

    try:
        from telegram_bot.user_manager import user_manager

        print("\n✓ user_manager импортирован успешно")

        user_count = user_manager.get_user_count()
        print(f"\nПользователей в базе: {user_count}")

        if user_count > 0:
            all_users = user_manager.get_all_user_ids()
            print(f"ID пользователей: {all_users[:5]}{'...' if len(all_users) > 5 else ''}")
        else:
            print("\n⚠️  База пользователей пуста")
            print("   Пользователи появятся когда начнут использовать бота")

        print("\n✅ Система пользователей работает корректно!")
        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Запускает все тесты"""
    print("\n🔍 ПРОВЕРКА СИСТЕМ TELEGRAM БОТА\n")

    results = []

    # Тест логов
    results.append(("Система логов", test_log_manager()))

    # Тест пользователей
    results.append(("Система пользователей", test_user_manager()))

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    for name, result in results:
        status = "✅ УСПЕШНО" if result else "❌ ОШИБКА"
        print(f"{status} - {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✅ Все тесты пройдены!")
        print("   Бот готов к работе")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        print("   Обновите код на сервере и перезапустите бота")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
