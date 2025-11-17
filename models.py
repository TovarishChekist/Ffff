"""
Модели базы данных
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Вспомогательная таблица для связи многие-ко-многим (пользователи и мероприятия)
event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('attended', db.Boolean, default=False),
    db.Column('registered_at', db.DateTime, default=datetime.utcnow)
)

# Вспомогательная таблица для связи пользователей и проектов
project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('role', db.String(50), default='member'),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Личная информация
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))

    # Роль в совете
    role = db.Column(db.String(50), nullable=False, default='member')
    # Роли: admin, chairman, secretary, member, observer

    # Отдел в совете
    department = db.Column(db.String(50))
    # Отделы: secretariat (Секретариат), project_dept (Проектный отдел), press_service (Пресс-служба)

    # Дополнительная информация
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(255))

    # Статус
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Отношения
    created_events = db.relationship('Event', backref='creator', lazy='dynamic',
                                    foreign_keys='Event.creator_id')
    created_votes = db.relationship('Vote', backref='creator', lazy='dynamic')
    vote_responses = db.relationship('VoteResponse', backref='user', lazy='dynamic')
    documents = db.relationship('Document', backref='uploader', lazy='dynamic')
    created_projects = db.relationship('Project', backref='creator', lazy='dynamic',
                                       foreign_keys='Project.creator_id')
    news_posts = db.relationship('News', backref='author', lazy='dynamic')
    appeals = db.relationship('Appeal', backref='author', lazy='dynamic',
                             foreign_keys='Appeal.author_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password):
        """Установить пароль"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Полное имя"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def __repr__(self):
        return f'<User {self.email}>'


class Event(db.Model):
    """Модель мероприятия"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Дата и время
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)

    # Место проведения
    location = db.Column(db.String(255))
    online_link = db.Column(db.String(500))

    # Тип мероприятия
    event_type = db.Column(db.String(50), nullable=False)
    # Типы: meeting, conference, training, social, other

    # Статус
    status = db.Column(db.String(50), default='planned')
    # Статусы: planned, ongoing, completed, cancelled

    # Организатор
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Участники
    participants = db.relationship('User', secondary=event_participants,
                                  backref=db.backref('events', lazy='dynamic'))

    def __repr__(self):
        return f'<Event {self.title}>'


class Vote(db.Model):
    """Модель голосования"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Тип голосования
    vote_type = db.Column(db.String(50), nullable=False, default='single')
    # Типы: single (один вариант), multiple (несколько), rating (оценка)

    # Настройки
    is_anonymous = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)

    # Временные рамки
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    # Статус
    status = db.Column(db.String(50), default='draft')
    # Статусы: draft, active, completed, cancelled

    # Создатель
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    options = db.relationship('VoteOption', backref='vote', lazy='dynamic',
                             cascade='all, delete-orphan')
    responses = db.relationship('VoteResponse', backref='vote', lazy='dynamic',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Vote {self.title}>'


class VoteOption(db.Model):
    """Вариант ответа в голосовании"""
    __tablename__ = 'vote_options'

    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

    # Отношения
    responses = db.relationship('VoteResponse', backref='option', lazy='dynamic')

    @property
    def vote_count(self):
        """Количество голосов за этот вариант"""
        return self.responses.count()

    def __repr__(self):
        return f'<VoteOption {self.text}>'


class VoteResponse(db.Model):
    """Ответ пользователя на голосование"""
    __tablename__ = 'vote_responses'

    id = db.Column(db.Integer, primary_key=True)
    vote_id = db.Column(db.Integer, db.ForeignKey('votes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('vote_options.id'), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VoteResponse {self.id}>'


class Document(db.Model):
    """Модель документа"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))

    # Категория
    category = db.Column(db.String(100))
    # Категории: protocol, report, presentation, photo, other

    # Загрузивший пользователь
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Счетчики
    download_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Document {self.title}>'


class Project(db.Model):
    """Модель проекта"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Сроки
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    # Статус
    status = db.Column(db.String(50), default='planning')
    # Статусы: planning, active, completed, paused, cancelled

    # Прогресс (0-100)
    progress = db.Column(db.Integer, default=0)

    # Создатель
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Участники
    members = db.relationship('User', secondary=project_members,
                             backref=db.backref('projects', lazy='dynamic'))

    # Задачи
    tasks = db.relationship('Task', backref='project', lazy='dynamic',
                           cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.title}>'


class Task(db.Model):
    """Модель задачи в проекте"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Ответственный
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assignee = db.relationship('User', backref='assigned_tasks')

    # Статус
    status = db.Column(db.String(50), default='todo')
    # Статусы: todo, in_progress, review, done, cancelled

    # Приоритет
    priority = db.Column(db.String(20), default='medium')
    # Приоритеты: low, medium, high, urgent

    # Сроки
    due_date = db.Column(db.Date)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Task {self.title}>'


class News(db.Model):
    """Модель новости"""
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))

    # Изображение
    image = db.Column(db.String(255))

    # Автор
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Статус публикации
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)

    # Важность
    is_important = db.Column(db.Boolean, default=False)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Счетчики
    views_count = db.Column(db.Integer, default=0)

    # Комментарии
    comments = db.relationship('Comment', backref='news', lazy='dynamic',
                              foreign_keys='Comment.news_id',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<News {self.title}>'


class Appeal(db.Model):
    """Модель обращения"""
    __tablename__ = 'appeals'

    id = db.Column(db.Integer, primary_key=True)

    # Автор (может быть анонимным)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Контактная информация для анонимных обращений
    contact_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))

    # Содержание
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Категория
    category = db.Column(db.String(100))
    # Категории: rights, education, health, safety, other

    # Статус
    status = db.Column(db.String(50), default='new')
    # Статусы: new, in_review, in_progress, resolved, closed

    # Ответственный за рассмотрение
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id],
                                  backref='assigned_appeals')

    # Ответ
    response = db.Column(db.Text)
    responded_at = db.Column(db.DateTime)

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Приватность
    is_private = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Appeal {self.title}>'


class Comment(db.Model):
    """Модель комментария"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    # Автор
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # К чему относится комментарий
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id}>'
