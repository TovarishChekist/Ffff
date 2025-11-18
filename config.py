"""
Конфигурация приложения
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Базовая конфигурация"""

    # Secret key для сессий и CSRF защиты
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'council.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Загрузка файлов
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB максимальный размер файла
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif'}

    # Сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Пагинация
    ITEMS_PER_PAGE = 20

    # Email (если нужна отправка уведомлений)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Организация
    ORGANIZATION_NAME = 'Детский и Молодежный Общественный Совет при Уполномоченном по правам ребёнка в Амурской области'
    ORGANIZATION_SHORT_NAME = 'ДиМОС'

    # Отделы совета
    DEPARTMENTS = {
        'secretariat': 'Секретариат',
        'project_dept': 'Проектный отдел',
        'press_service': 'Пресс-служба'
    }

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
