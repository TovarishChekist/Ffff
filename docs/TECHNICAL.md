# Техническая документация

## Система управления Детским и Молодежным Общественным Советом

### Архитектура системы

Приложение построено по классической MVC-архитектуре с использованием Flask:

- **Model** - SQLAlchemy ORM модели (models.py)
- **View** - Jinja2 HTML шаблоны (templates/)
- **Controller** - Flask route handlers (app.py)

### Стек технологий

#### Backend
- **Python 3.8+** - основной язык программирования
- **Flask 3.0** - веб-фреймворк
- **Flask-SQLAlchemy** - ORM для работы с базой данных
- **Flask-Login** - управление сессиями пользователей
- **Flask-WTF** - формы и CSRF-защита
- **Werkzeug** - WSGI утилиты и безопасность
- **bcrypt** - хеширование паролей

#### Frontend
- **HTML5** - структура страниц
- **CSS3** - стилизация
- **JavaScript (Vanilla)** - клиентская логика

#### База данных
- **SQLite** (по умолчанию) - файловая БД для разработки
- Поддержка **PostgreSQL** для продакшена

### Структура проекта

```
├── app.py                 # Главный файл приложения
├── config.py              # Конфигурация
├── models.py              # Модели базы данных
├── init_db.py             # Инициализация БД
├── requirements.txt       # Зависимости Python
├── README.md              # Описание проекта
├── .gitignore            # Игнорируемые файлы
│
├── static/                # Статические файлы
│   ├── css/
│   │   └── style.css     # Основные стили
│   ├── js/
│   │   └── main.js       # Основной JavaScript
│   └── uploads/          # Загруженные файлы
│
├── templates/             # HTML шаблоны
│   ├── base.html         # Базовый шаблон
│   ├── index.html        # Главная страница
│   ├── dashboard.html    # Личный кабинет
│   │
│   ├── auth/             # Аутентификация
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── events/           # Мероприятия
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── create.html
│   │
│   ├── votes/            # Голосования
│   │   ├── list.html
│   │   └── detail.html
│   │
│   ├── projects/         # Проекты
│   │   ├── list.html
│   │   └── detail.html
│   │
│   ├── documents/        # Документы
│   │   ├── list.html
│   │   └── upload.html
│   │
│   ├── news/             # Новости
│   │   ├── list.html
│   │   └── detail.html
│   │
│   ├── appeals/          # Обращения
│   │   ├── list.html
│   │   └── create.html
│   │
│   ├── profile/          # Профиль
│   │   ├── view.html
│   │   └── edit.html
│   │
│   ├── admin/            # Администрирование
│   │   └── panel.html
│   │
│   └── errors/           # Страницы ошибок
│       ├── 404.html
│       └── 500.html
│
└── docs/                 # Документация
    ├── USER_GUIDE.md     # Руководство пользователя
    └── TECHNICAL.md      # Техническая документация
```

### Модели базы данных

#### User (Пользователь)
```python
- id: Integer (PK)
- email: String(120), unique
- password_hash: String(255)
- first_name, last_name, patronymic: String
- date_of_birth: Date
- phone: String(20)
- role: String(50) - admin, chairman, secretary, member, observer
- is_active: Boolean
- created_at, last_login: DateTime
```

#### Event (Мероприятие)
```python
- id: Integer (PK)
- title: String(200)
- description: Text
- start_datetime, end_datetime: DateTime
- location: String(255)
- online_link: String(500)
- event_type: String(50) - meeting, conference, training, social, other
- status: String(50) - planned, ongoing, completed, cancelled
- creator_id: Integer (FK -> User)
```

#### Vote (Голосование)
```python
- id: Integer (PK)
- title: String(200)
- description: Text
- vote_type: String(50) - single, multiple, rating
- is_anonymous: Boolean
- start_date, end_date: DateTime
- status: String(50) - draft, active, completed, cancelled
- creator_id: Integer (FK -> User)
```

#### VoteOption (Вариант голосования)
```python
- id: Integer (PK)
- vote_id: Integer (FK -> Vote)
- text: String(255)
- order: Integer
```

#### VoteResponse (Ответ на голосование)
```python
- id: Integer (PK)
- vote_id: Integer (FK -> Vote)
- user_id: Integer (FK -> User)
- option_id: Integer (FK -> VoteOption)
- comment: Text
- created_at: DateTime
```

#### Document (Документ)
```python
- id: Integer (PK)
- title: String(200)
- description: Text
- filename: String(255)
- file_path: String(500)
- file_size: Integer
- category: String(100) - protocol, report, presentation, photo, other
- uploader_id: Integer (FK -> User)
- download_count: Integer
```

#### Project (Проект)
```python
- id: Integer (PK)
- title: String(200)
- description: Text
- start_date, end_date: Date
- status: String(50) - planning, active, completed, paused, cancelled
- progress: Integer (0-100)
- creator_id: Integer (FK -> User)
```

#### Task (Задача)
```python
- id: Integer (PK)
- project_id: Integer (FK -> Project)
- title: String(200)
- description: Text
- assignee_id: Integer (FK -> User)
- status: String(50) - todo, in_progress, review, done, cancelled
- priority: String(20) - low, medium, high, urgent
- due_date: Date
```

#### News (Новость)
```python
- id: Integer (PK)
- title: String(200)
- content: Text
- summary: String(500)
- image: String(255)
- author_id: Integer (FK -> User)
- is_published: Boolean
- published_at: DateTime
- is_important: Boolean
- views_count: Integer
```

#### Appeal (Обращение)
```python
- id: Integer (PK)
- author_id: Integer (FK -> User, nullable)
- contact_name, contact_email, contact_phone: String
- title: String(200)
- content: Text
- category: String(100) - rights, education, health, safety, other
- status: String(50) - new, in_review, in_progress, resolved, closed
- assigned_to_id: Integer (FK -> User)
- response: Text
- is_private: Boolean
```

#### Comment (Комментарий)
```python
- id: Integer (PK)
- content: Text
- author_id: Integer (FK -> User)
- news_id: Integer (FK -> News, nullable)
- project_id: Integer (FK -> Project, nullable)
- created_at: DateTime
```

### API маршруты

#### Публичные маршруты
- `GET /` - Главная страница
- `GET /news` - Список новостей
- `GET /news/<id>` - Детали новости
- `GET /login` - Страница входа
- `POST /login` - Вход в систему
- `GET /register` - Страница регистрации
- `POST /register` - Регистрация нового пользователя
- `GET /appeals/create` - Создание обращения
- `POST /appeals/create` - Отправка обращения

#### Защищенные маршруты (требуют аутентификации)
- `GET /dashboard` - Личный кабинет
- `GET /logout` - Выход из системы
- `GET /events` - Список мероприятий
- `GET /events/<id>` - Детали мероприятия
- `GET /events/create` - Создание мероприятия (admin, chairman, secretary)
- `POST /events/create` - Сохранение мероприятия
- `GET /votes` - Список голосований
- `GET /votes/<id>` - Детали голосования
- `POST /votes/<id>/vote` - Отправка голоса
- `GET /projects` - Список проектов
- `GET /projects/<id>` - Детали проекта
- `GET /documents` - Список документов
- `GET /documents/upload` - Загрузка документа
- `POST /documents/upload` - Сохранение документа
- `GET /appeals` - Список обращений
- `GET /profile` - Профиль пользователя
- `GET /profile/edit` - Редактирование профиля
- `POST /profile/edit` - Сохранение профиля
- `GET /admin` - Административная панель (только admin)

### Безопасность

#### Аутентификация и авторизация
- Пароли хешируются с использованием bcrypt
- Сессии управляются Flask-Login
- CSRF-защита через Flask-WTF
- Контроль доступа на основе ролей

#### Валидация данных
- Валидация на стороне клиента (HTML5)
- Валидация на стороне сервера (WTForms)
- Санитизация входных данных

#### Загрузка файлов
- Проверка типов файлов
- Ограничение размера (16 МБ)
- Безопасные имена файлов (secure_filename)
- Хранение вне публичной директории

### Конфигурация

#### Переменные окружения
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///council.db  # или postgresql://...
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
```

#### Конфигурационные классы
- `Config` - базовая конфигурация
- `DevelopmentConfig` - для разработки (DEBUG=True)
- `ProductionConfig` - для продакшена (DEBUG=False)

### Развертывание

#### Разработка (локально)
```bash
# Установка зависимостей
pip install -r requirements.txt

# Инициализация БД
python init_db.py

# Запуск сервера разработки
python app.py
```

#### Продакшен

Рекомендуется использовать:
- **Gunicorn** или **uWSGI** в качестве WSGI-сервера
- **Nginx** в качестве reverse proxy
- **PostgreSQL** в качестве БД
- **Supervisor** для управления процессами

Пример запуска с Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Миграции базы данных

Для управления миграциями рекомендуется использовать Flask-Migrate (Alembic):

```bash
# Инициализация
flask db init

# Создание миграции
flask db migrate -m "Description"

# Применение миграций
flask db upgrade
```

### Тестирование

Рекомендуется использовать pytest для тестирования:

```bash
# Установка
pip install pytest pytest-flask

# Запуск тестов
pytest tests/
```

### Мониторинг и логирование

- Логирование ошибок в файл и консоль
- Мониторинг производительности
- Отслеживание активности пользователей

### Резервное копирование

Рекомендации:
- Ежедневное резервное копирование БД
- Резервное копирование загруженных файлов
- Хранение резервных копий в отдельном месте

### Масштабирование

Возможности для масштабирования:
- Использование Redis для кэширования
- Celery для асинхронных задач
- Балансировка нагрузки через Nginx
- Репликация базы данных

### Обновление системы

1. Создайте резервную копию БД и файлов
2. Загрузите новую версию кода
3. Установите новые зависимости: `pip install -r requirements.txt`
4. Выполните миграции БД: `flask db upgrade`
5. Перезапустите приложение

### Поддержка

Для получения технической поддержки:
- Создайте issue в репозитории проекта
- Обратитесь к системному администратору
- Ознакомьтесь с документацией Flask: https://flask.palletsprojects.com/
