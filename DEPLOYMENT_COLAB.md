# Запуск Telegram-бота на Google Colab

## ⚠️ ВАЖНО: Ограничения Google Colab

Google Colab **НЕ предназначен** для постоянного хостинга ботов:

- ❌ Сессия закрывается через **12 часов** максимум
- ❌ Закрывается при **90 минутах неактивности**
- ❌ Нет гарантии доступности 24/7
- ❌ Нарушение ToS Google Colab (предназначен для ML/Data Science)
- ⚠️ Может привести к бану аккаунта

**Используйте только для:**
- ✅ Тестирования бота
- ✅ Отладки
- ✅ Демонстрации
- ✅ Краткосрочного запуска

**Для постоянной работы используйте:**
- PythonAnywhere ($5/мес)
- VPS (DigitalOcean, Linode)
- Railway.app
- Render

---

## Вариант 1: Через интерфейс Colab (проще)

### Шаг 1: Создайте новый notebook

1. Откройте [Google Colab](https://colab.research.google.com)
2. Нажмите **"Новый блокнот"** или **"New Notebook"**
3. Переименуйте в "Telegram_Bot"

### Шаг 2: Загрузите код

**Ячейка 1:** Клонируйте репозиторий

```python
# Клонируем репозиторий
!git clone https://github.com/TovarishChekist/Ffff.git
%cd Ffff
!git checkout claude/rewrite-telegram-bot-EEBhi
```

**Ячейка 2:** Установите зависимости

```python
# Устанавливаем зависимости
!pip install -q -r requirements-bot.txt
```

### Шаг 3: Настройте переменные окружения

**Ячейка 3:** Создайте .env файл

```python
# ВАЖНО: Замените значения на свои!
env_content = """
TELEGRAM_BOT_TOKEN=7710087256:AAFWHXIhrIkwL2pMLuhrvtIo8BvFCk7CebA
APPEAL_CHAT_ID=-1002863620257
APPLICATION_CHAT_ID=-1002692926810
CONNECT_TIMEOUT=15.0
READ_TIMEOUT=15.0
LOG_LEVEL=INFO
ADMIN_IDS=123456789
"""

# Сохраняем в файл
with open('.env', 'w') as f:
    f.write(env_content.strip())

print("✅ Файл .env создан")
```

### Шаг 4: Запустите бота

**Ячейка 4:** Запуск

```python
# Запускаем бота
!python run_bot.py
```

**Остановка:** Нажмите кнопку ⏹️ "Stop" или `Runtime → Interrupt execution`

---

## Вариант 2: С использованием Google Drive (сохранение конфигурации)

### Шаг 1: Подключите Google Drive

**Ячейка 1:**
```python
from google.colab import drive
drive.mount('/content/drive')

# Создаем папку для бота
import os
bot_dir = '/content/drive/MyDrive/TelegramBot'
os.makedirs(bot_dir, exist_ok=True)
print(f"✅ Папка создана: {bot_dir}")
```

### Шаг 2: Клонируйте репозиторий

**Ячейка 2:**
```python
%cd /content/drive/MyDrive/TelegramBot

# Клонируем если еще не клонировали
if not os.path.exists('Ffff'):
    !git clone https://github.com/TovarishChekist/Ffff.git

%cd Ffff
!git checkout claude/rewrite-telegram-bot-EEBhi
!git pull  # Обновляем если уже клонировали
```

### Шаг 3: Создайте .env (один раз)

**Ячейка 3:**
```python
# Создаем .env если его нет
if not os.path.exists('.env'):
    env_content = """
TELEGRAM_BOT_TOKEN=ваш_токен_здесь
APPEAL_CHAT_ID=-1002863620257
APPLICATION_CHAT_ID=-1002692926810
CONNECT_TIMEOUT=15.0
READ_TIMEOUT=15.0
LOG_LEVEL=INFO
ADMIN_IDS=ваш_telegram_id
"""
    with open('.env', 'w') as f:
        f.write(env_content.strip())
    print("⚠️ ВАЖНО: Отредактируйте файл .env в Google Drive!")
    print("Путь:", os.path.abspath('.env'))
else:
    print("✅ Файл .env уже существует")
```

### Шаг 4: Установите зависимости и запустите

**Ячейка 4:**
```python
# Устанавливаем зависимости
!pip install -q -r requirements-bot.txt

# Запускаем бота
!python run_bot.py
```

---

## Вариант 3: С секретами Colab (безопаснее)

Google Colab позволяет хранить секреты безопасно.

### Шаг 1: Настройте секреты

1. В левой панели нажмите 🔑 "Secrets"
2. Добавьте секреты:
   - `TELEGRAM_BOT_TOKEN` → ваш токен
   - `APPEAL_CHAT_ID` → ID чата обращений
   - `APPLICATION_CHAT_ID` → ID чата заявок
   - `ADMIN_IDS` → ваш Telegram ID

### Шаг 2: Используйте секреты в коде

**Ячейка 1:**
```python
from google.colab import userdata
import os

# Загружаем секреты
os.environ['TELEGRAM_BOT_TOKEN'] = userdata.get('TELEGRAM_BOT_TOKEN')
os.environ['APPEAL_CHAT_ID'] = userdata.get('APPEAL_CHAT_ID')
os.environ['APPLICATION_CHAT_ID'] = userdata.get('APPLICATION_CHAT_ID')
os.environ['ADMIN_IDS'] = userdata.get('ADMIN_IDS')
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['CONNECT_TIMEOUT'] = '15.0'
os.environ['READ_TIMEOUT'] = '15.0'

print("✅ Секреты загружены")
```

**Ячейка 2:**
```python
# Клонируем репозиторий
!git clone https://github.com/TovarishChekist/Ffff.git
%cd Ffff
!git checkout claude/rewrite-telegram-bot-EEBhi

# Устанавливаем зависимости
!pip install -q -r requirements-bot.txt
```

**Ячейка 3:**
```python
# Запускаем бота (не создаем .env, используем переменные окружения)
!python run_bot.py
```

---

## Готовый Notebook

Скопируйте этот код целиком в один блокнот:

```python
# ========================================
# TELEGRAM-БОТ НА GOOGLE COLAB
# ========================================

# 1. Установка и клонирование
print("📦 Клонирование репозитория...")
!git clone -q https://github.com/TovarishChekist/Ffff.git
%cd Ffff
!git checkout -q claude/rewrite-telegram-bot-EEBhi
print("✅ Репозиторий клонирован")

# 2. Установка зависимостей
print("\n📦 Установка зависимостей...")
!pip install -q -r requirements-bot.txt
print("✅ Зависимости установлены")

# 3. Конфигурация (ЗАМЕНИТЕ НА СВОИ ДАННЫЕ!)
print("\n⚙️ Настройка конфигурации...")

# ВАЖНО: Замените эти значения на свои!
BOT_TOKEN = "7710087256:AAFWHXIhrIkwL2pMLuhrvtIo8BvFCk7CebA"
APPEAL_CHAT_ID = "-1002863620257"
APPLICATION_CHAT_ID = "-1002692926810"
ADMIN_IDS = "123456789"  # Ваш Telegram ID

# Создаем .env
import os
os.environ['TELEGRAM_BOT_TOKEN'] = BOT_TOKEN
os.environ['APPEAL_CHAT_ID'] = APPEAL_CHAT_ID
os.environ['APPLICATION_CHAT_ID'] = APPLICATION_CHAT_ID
os.environ['ADMIN_IDS'] = ADMIN_IDS
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['CONNECT_TIMEOUT'] = '15.0'
os.environ['READ_TIMEOUT'] = '15.0'

print("✅ Конфигурация установлена")

# 4. Запуск бота
print("\n" + "="*50)
print("🚀 ЗАПУСК БОТА")
print("="*50)
print("\n⚠️ Важно:")
print("- Бот будет работать пока открыт блокнот")
print("- Максимум 12 часов")
print("- Остановить: Runtime → Interrupt execution")
print("\n" + "="*50 + "\n")

!python run_bot.py
```

---

## Мониторинг и управление

### Просмотр логов

В отдельной ячейке:
```python
# Просмотр последних 50 строк лога
!tail -n 50 bot.log
```

### Проверка статуса

```python
# Проверяем, запущен ли бот
!ps aux | grep run_bot.py
```

### Остановка бота

```python
# Остановить бота
!pkill -f run_bot.py
```

---

## Автоматический перезапуск при отключении

**Не работает на Colab!** Если сессия закрывается, бот останавливается.

Можно попробовать использовать `tmux`, но это не спасет от закрытия сессии:

```python
# Запуск в tmux (все равно закроется при закрытии сессии)
!apt-get install -y tmux
!tmux new -d -s bot 'cd /content/Ffff && python run_bot.py'
```

---

## Частые проблемы

### Ошибка: "Runtime disconnected"

**Причина:** Сессия Colab закрылась
**Решение:** Запустите все ячейки заново

### Ошибка: "GPU/TPU not available"

**Решение:** Для бота не нужен GPU, игнорируйте

### Бот останавливается через 90 минут

**Причина:** Colab закрывает неактивные сессии
**Решение:**
- Держите вкладку открытой
- Периодически выполняйте какую-нибудь ячейку
- Или используйте расширение [Colab Auto Clicker](https://chrome.google.com/webstore)

### Ошибка установки зависимостей

```python
# Обновите pip
!pip install --upgrade pip
!pip install -r requirements-bot.txt --no-cache-dir
```

---

## Сохранение custom_messages.json

Если вы редактируете тексты через админ-панель, они сохраняются в `custom_messages.json`.

**С Google Drive:**
```python
# Копируем custom_messages.json в Drive для сохранения
!cp custom_messages.json /content/drive/MyDrive/TelegramBot/

# При следующем запуске восстанавливаем
!cp /content/drive/MyDrive/TelegramBot/custom_messages.json .
```

---

## Альтернативы для постоянного хостинга

### Бесплатные/дешевые варианты:

1. **PythonAnywhere** ($5/мес) - [инструкция](DEPLOYMENT_PYTHONANYWHERE.md)
2. **Railway.app** - $5 кредитов бесплатно
3. **Render** - бесплатный план с ограничениями
4. **Fly.io** - бесплатный план
5. **Heroku** - ~$5/мес после отмены бесплатного плана

### VPS (полный контроль):

1. **DigitalOcean** - от $4/мес
2. **Linode** - от $5/мес
3. **Vultr** - от $3.50/мес
4. **Hetzner** - от €4/мес

### Домашний сервер:

1. **Raspberry Pi** - одноразовая покупка ~$35
2. **Старый компьютер** - бесплатно если есть

---

## Рекомендации

✅ **Google Colab подходит для:**
- Тестирования нового кода
- Отладки
- Демонстрации функционала
- Обучения работе с ботом

❌ **Google Colab НЕ подходит для:**
- Продакшена (постоянной работы)
- Важных ботов с пользователями
- Длительной работы (>12 часов)
- Надежного хостинга

**Вывод:** Используйте Google Colab только для тестирования, а для постоянной работы переходите на PythonAnywhere или VPS.

---

## Полезные ссылки

- [PythonAnywhere инструкция](DEPLOYMENT_PYTHONANYWHERE.md)
- [Быстрый старт](QUICKSTART.md)
- [README по боту](telegram_bot/README.md)
- [Google Colab](https://colab.research.google.com)
