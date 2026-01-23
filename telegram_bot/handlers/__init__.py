# -*- coding: utf-8 -*-
"""
Обработчики команд и сообщений для Telegram-бота
"""

from .common import register_common_handlers
from .appeal import register_appeal_handlers
from .application import register_application_handlers
from .admin import register_admin_handlers

__all__ = [
    'register_common_handlers',
    'register_appeal_handlers',
    'register_application_handlers',
    'register_admin_handlers',
]
