"""
Скрипт инициализации базы данных
"""
from datetime import datetime, timedelta
from app import app
from models import db, User, Event, Vote, VoteOption, News, Project

def init_database():
    """Инициализация базы данных"""
    with app.app_context():
        # Создание всех таблиц
        print("Создание таблиц базы данных...")
        db.create_all()

        # Проверка существования администратора
        admin = User.query.filter_by(email='admin@council.ru').first()
        if not admin:
            print("Создание администратора по умолчанию...")
            admin = User(
                email='admin@council.ru',
                first_name='Администратор',
                last_name='Системы',
                patronymic='',
                role='admin',
                is_active=True,
                email_confirmed=True
            )
            admin.set_password('admin123')
            db.session.add(admin)

        # Создание примеров пользователей
        if User.query.count() < 5:
            print("Создание примеров пользователей...")

            users_data = [
                {
                    'email': 'ivanov@example.com',
                    'first_name': 'Иван',
                    'last_name': 'Иванов',
                    'patronymic': 'Иванович',
                    'role': 'chairman',
                    'department': 'secretariat',
                    'password': 'password123'
                },
                {
                    'email': 'petrov@example.com',
                    'first_name': 'Петр',
                    'last_name': 'Петров',
                    'patronymic': 'Петрович',
                    'role': 'secretary',
                    'department': 'secretariat',
                    'password': 'password123'
                },
                {
                    'email': 'sidorova@example.com',
                    'first_name': 'Анна',
                    'last_name': 'Сидорова',
                    'patronymic': 'Александровна',
                    'role': 'member',
                    'department': 'press_service',
                    'password': 'password123'
                },
                {
                    'email': 'kozlov@example.com',
                    'first_name': 'Дмитрий',
                    'last_name': 'Козлов',
                    'patronymic': 'Сергеевич',
                    'role': 'member',
                    'department': 'project_dept',
                    'password': 'password123'
                }
            ]

            for user_data in users_data:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        patronymic=user_data['patronymic'],
                        role=user_data['role'],
                        department=user_data.get('department'),
                        is_active=True,
                        email_confirmed=True
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)

        # Создание примеров мероприятий
        if Event.query.count() == 0:
            print("Создание примеров мероприятий...")

            events_data = [
                {
                    'title': 'Общее собрание совета',
                    'description': 'Ежемесячное общее собрание членов совета для обсуждения текущих вопросов.',
                    'start_datetime': datetime.utcnow() + timedelta(days=7),
                    'end_datetime': datetime.utcnow() + timedelta(days=7, hours=2),
                    'location': 'Конференц-зал администрации области',
                    'event_type': 'meeting',
                    'status': 'planned'
                },
                {
                    'title': 'Тренинг по правам ребенка',
                    'description': 'Образовательный тренинг для членов совета о правах детей и молодежи.',
                    'start_datetime': datetime.utcnow() + timedelta(days=14),
                    'end_datetime': datetime.utcnow() + timedelta(days=14, hours=4),
                    'location': 'Молодежный центр',
                    'event_type': 'training',
                    'status': 'planned'
                }
            ]

            for event_data in events_data:
                event = Event(**event_data, creator_id=admin.id)
                db.session.add(event)

        # Создание примеров новостей
        if News.query.count() == 0:
            print("Создание примеров новостей...")

            news_data = [
                {
                    'title': 'Добро пожаловать в систему управления ДиМОС!',
                    'summary': 'Запущена новая система для эффективного управления деятельностью совета.',
                    'content': '''Уважаемые члены Детского и Молодежного Общественного Совета!

Мы рады представить вам новую систему управления, которая поможет нам более эффективно организовывать нашу работу.

В системе доступны следующие возможности:
- Планирование и учет мероприятий
- Электронные голосования
- Управление проектами
- Обмен документами
- Система обращений

Желаем продуктивной работы!''',
                    'is_published': True,
                    'published_at': datetime.utcnow(),
                    'is_important': True
                }
            ]

            for news_item in news_data:
                news = News(**news_item, author_id=admin.id)
                db.session.add(news)

        # Создание примера голосования
        if Vote.query.count() == 0:
            print("Создание примера голосования...")

            vote = Vote(
                title='Выбор даты следующего мероприятия',
                description='Просим проголосовать за наиболее удобную дату проведения следующего общего собрания.',
                vote_type='single',
                is_anonymous=False,
                allow_comments=True,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                status='active',
                creator_id=admin.id
            )
            db.session.add(vote)
            db.session.flush()  # Получаем ID голосования

            # Добавление вариантов ответа
            options = [
                VoteOption(vote_id=vote.id, text='15 декабря, 18:00', order=1),
                VoteOption(vote_id=vote.id, text='16 декабря, 18:00', order=2),
                VoteOption(vote_id=vote.id, text='17 декабря, 18:00', order=3)
            ]
            for option in options:
                db.session.add(option)

        # Создание примера проекта
        if Project.query.count() == 0:
            print("Создание примера проекта...")

            project = Project(
                title='Организация новогоднего мероприятия для детей',
                description='Планирование и проведение новогоднего праздника для детей из социально незащищенных семей.',
                start_date=datetime.utcnow().date(),
                end_date=(datetime.utcnow() + timedelta(days=45)).date(),
                status='active',
                progress=25,
                creator_id=admin.id
            )
            db.session.add(project)

        # Сохранение всех изменений
        db.session.commit()

        print("\n" + "="*50)
        print("База данных успешно инициализирована!")
        print("="*50)
        print("\nДанные для входа администратора:")
        print("Email: admin@council.ru")
        print("Пароль: admin123")
        print("\n⚠️  ВАЖНО: Смените пароль после первого входа!")
        print("="*50)

if __name__ == '__main__':
    init_database()
