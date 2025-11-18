"""
ВРЕМЕННЫЙ СКРИПТ ДЛЯ ОТЛАДКИ
ИСПОЛЬЗУЙТЕ ТОЛЬКО ЛОКАЛЬНО!
"""
from app import app
from models import db, User

print("="*60)
print("ВРЕМЕННЫЙ РЕЖИМ ОТЛАДКИ")
print("="*60)

with app.app_context():
    # Проверяем существует ли БД
    try:
        db.create_all()
        print("✓ База данных создана/проверена")
    except Exception as e:
        print(f"✗ Ошибка БД: {e}")

    # Удаляем старого админа
    User.query.filter_by(email='admin@council.ru').delete()
    db.session.commit()

    # Создаем администратора с простым паролем
    admin = User(
        email='admin@council.ru',
        first_name='Администратор',
        last_name='Системы',
        patronymic='',
        role='admin',
        is_active=True,
        email_confirmed=True
    )
    admin.set_password('admin')  # Простой пароль!
    db.session.add(admin)
    db.session.commit()

    print("\n" + "="*60)
    print("✓ АДМИНИСТРАТОР СОЗДАН!")
    print("="*60)
    print("\nДанные для входа:")
    print("Email: admin@council.ru")
    print("Пароль: admin")
    print("\n" + "="*60)
    print("ВНИМАНИЕ: Это временный режим отладки!")
    print("Смените пароль после входа в систему!")
    print("="*60)
