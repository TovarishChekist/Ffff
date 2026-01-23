# -*- coding: utf-8 -*-
"""
Тексты сообщений для Telegram-бота
Детского и Молодёжного Общественного Совета

Теперь тексты загружаются из MessageManager и могут быть отредактированы администраторами
"""

from .message_manager import message_manager

# Функции-геттеры для получения текстов через MessageManager
def get_welcome_message() -> str:
    return message_manager.get('welcome_message')

def get_council_info() -> str:
    return message_manager.get('council_info')

def get_leadership_info() -> str:
    return message_manager.get('leadership_info')

def get_appeal_prompt() -> str:
    return message_manager.get('appeal_prompt')

def get_appeal_sent() -> str:
    return message_manager.get('appeal_sent')

def get_application_welcome() -> str:
    return message_manager.get('application_welcome')

def get_application_age_prompt() -> str:
    return message_manager.get('application_age_prompt')

def get_application_school_prompt() -> str:
    return message_manager.get('application_school_prompt')

def get_application_class_prompt() -> str:
    return message_manager.get('application_class_prompt')

def get_application_username_prompt() -> str:
    return message_manager.get('application_username_prompt')

def get_application_motivation_prompt() -> str:
    return message_manager.get('application_motivation_prompt')

def get_application_experience_prompt() -> str:
    return message_manager.get('application_experience_prompt')

def get_application_contacts_prompt() -> str:
    return message_manager.get('application_contacts_prompt')

def get_application_success() -> str:
    return message_manager.get('application_success')

def get_back_to_menu() -> str:
    return message_manager.get('back_to_menu')

# Статические сообщения (не редактируются)
COUNCIL_RESPONSE = "<b>Пришёл ответ от Совета!</b> 📩\n\n{message}\n\n"
ADMIN_RESPONSE_SENT = "✅ Ответ отправлен пользователю."

# Обратная совместимость - оставляем константы
WELCOME_MESSAGE = get_welcome_message()
COUNCIL_INFO = get_council_info()
LEADERSHIP_INFO = get_leadership_info()
APPEAL_PROMPT = get_appeal_prompt()
APPEAL_SENT = get_appeal_sent()
APPLICATION_WELCOME = get_application_welcome()
APPLICATION_AGE_PROMPT = get_application_age_prompt()
APPLICATION_SCHOOL_PROMPT = get_application_school_prompt()
APPLICATION_CLASS_PROMPT = get_application_class_prompt()
APPLICATION_USERNAME_PROMPT = get_application_username_prompt()
APPLICATION_MOTIVATION_PROMPT = get_application_motivation_prompt()
APPLICATION_EXPERIENCE_PROMPT = get_application_experience_prompt()
APPLICATION_CONTACTS_PROMPT = get_application_contacts_prompt()
APPLICATION_SUCCESS = get_application_success()
BACK_TO_MENU = get_back_to_menu()


def format_application(data: dict) -> str:
    """Форматирует данные заявки для отправки в канал"""
    return f"""📋 <b>НОВАЯ ЗАЯВКА НА ВСТУПЛЕНИЕ В СОВЕТ</b>

👤 <b>Личные данные:</b>
• ФИО: {data['fio']}
• Возраст: {data['age']} лет
• Telegram: {data['username']}

🏫 <b>Образование:</b>
• Школа: {data['school']}
• Класс: {data['class']}

💭 <b>Мотивация:</b>
{data['motivation']}

🌟 <b>Опыт общественной деятельности:</b>
{data['experience']}

📞 <b>Контакты для связи:</b>
{data['contacts']}

✅ Заявка готова к рассмотрению"""
