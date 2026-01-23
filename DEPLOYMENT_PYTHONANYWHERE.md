# Развертывание Telegram-бота на PythonAnywhere

Пошаговая инструкция для новичков по запуску бота на бесплатном хостинге PythonAnywhere.

## Шаг 1: Регистрация на PythonAnywhere

1. Откройте [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Нажмите **"Start running Python online in less than a minute!"**
3. Выберите **"Create a Beginner account"** (бесплатный план)
4. Заполните форму регистрации:
   - Username (имя пользователя)
   - Email
   - Password
5. Подтвердите email

## Шаг 2: Загрузка кода бота

### Вариант А: Через Git (рекомендуется)

1. Откройте вкладку **"Consoles"** → **"Bash"**
2. Выполните команды:

```bash
# Клонируем репозиторий
git clone https://github.com/ВАШ_USERNAME/ВАШ_РЕПОЗИТОРИЙ.git

# Переходим в папку проекта
cd ВАШ_РЕПОЗИТОРИЙ

# Переключаемся на нужную ветку
git checkout claude/rewrite-telegram-bot-EEBhi
```

### Вариант Б: Загрузка через Files (если нет Git)

1. На своем компьютере заархивируйте папку `telegram_bot` и файлы:
   - `telegram_bot/` (вся папка)
   - `run_bot.py`
   - `requirements-bot.txt`
   - `.env.example`

2. В PythonAnywhere откройте вкладку **"Files"**
3. Нажмите **"Upload a file"**
4. Загрузите архив
5. Распакуйте через Bash консоль:
```bash
unzip archive.zip
```

## Шаг 3: Установка зависимостей

1. В Bash консоли выполните:

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements-bot.txt
```

**Важно:** PythonAnywhere использует Python 3.10 по умолчанию. Если нужна другая версия, укажите при создании консоли.

## Шаг 4: Настройка переменных окружения

1. Создайте файл `.env`:

```bash
# В Bash консоли
cp .env.example .env
nano .env
```

2. Заполните файл своими данными:

```env
# Токен бота (получить у @BotFather)
TELEGRAM_BOT_TOKEN=7710087256:AAFWHXIhrIkwL2pMLuhrvtIo8BvFCk7CebA

# ID чата для обращений
APPEAL_CHAT_ID=-1002863620257

# ID чата для заявок
APPLICATION_CHAT_ID=-1002692926810

# Таймауты
CONNECT_TIMEOUT=15.0
READ_TIMEOUT=15.0

# Уровень логирования
LOG_LEVEL=INFO

# ID администраторов (ваш Telegram ID)
# Узнать свой ID: @userinfobot
ADMIN_IDS=123456789
```

3. Сохраните файл:
   - Нажмите `Ctrl+O` (сохранить)
   - Нажмите `Enter`
   - Нажмите `Ctrl+X` (выход)

## Шаг 5: Тестовый запуск

Проверим, что бот работает:

```bash
# Убедитесь, что виртуальное окружение активно
source venv/bin/activate

# Запускаем бота
python run_bot.py
```

Если все настроено правильно, вы увидите:
```
============================================================
Запуск Telegram-бота Детского и Молодёжного Совета
============================================================
✓ Конфигурация валидна
✓ Загружено администраторов: 1
✓ API настроен
✓ Бот инициализирован
✓ Обработчики зарегистрированы
✓ Подключение успешно! Бот: @ВАШ_БОТ
============================================================
Бот запущен и готов к работе!
============================================================
```

Проверьте бота в Telegram: отправьте `/start`

**Остановите бота:** Нажмите `Ctrl+C`

## Шаг 6: Постоянный запуск бота

⚠️ **Важно:** Бесплатный аккаунт PythonAnywhere имеет ограничения:
- Консоль автоматически закрывается через несколько часов неактивности
- Для постоянной работы нужен платный аккаунт ($5/месяц) с функцией "Always-on tasks"

### Вариант 1: Always-On Task (Платный аккаунт)

Если у вас платный аккаунт:

1. Откройте вкладку **"Tasks"**
2. В разделе **"Always-on tasks"** нажмите **"Create a new always-on task"**
3. Заполните:
   - **Command:** `/home/ВАШ_USERNAME/venv/bin/python /home/ВАШ_USERNAME/путь_к_проекту/run_bot.py`
   - **Working directory:** `/home/ВАШ_USERNAME/путь_к_проекту`
4. Нажмите **"Create"**
5. Включите задачу переключателем

### Вариант 2: Запуск через tmux (Бесплатный аккаунт)

Для бесплатного аккаунта используем `tmux` (сессия сохраняется):

```bash
# Установка tmux (если нет)
pip install --user tmux

# Создаем новую сессию
tmux new -s telegram_bot

# В сессии активируем окружение и запускаем бота
source venv/bin/activate
python run_bot.py

# Отключаемся от сессии (бот продолжит работать)
# Нажмите: Ctrl+B, затем D
```

**Вернуться к сессии:**
```bash
tmux attach -t telegram_bot
```

**Остановить бота:**
```bash
# Подключитесь к сессии
tmux attach -t telegram_bot

# Остановите бота: Ctrl+C

# Закройте сессию
exit
```

⚠️ **Ограничение:** При бесплатном аккаунте сессия может закрыться, если вы не заходите на PythonAnywhere несколько дней.

### Вариант 3: Scheduled Task (Бесплатный аккаунт)

Можно настроить перезапуск бота каждый день:

1. Создайте скрипт `start_bot.sh`:

```bash
#!/bin/bash
cd /home/ВАШ_USERNAME/путь_к_проекту
source venv/bin/activate
pkill -f run_bot.py  # Останавливаем старый процесс
nohup python run_bot.py > bot.log 2>&1 &
```

2. Сделайте исполняемым:
```bash
chmod +x start_bot.sh
```

3. В PythonAnywhere:
   - Откройте вкладку **"Tasks"**
   - В разделе **"Scheduled tasks"** создайте задачу
   - **Command:** `/home/ВАШ_USERNAME/путь_к_проекту/start_bot.sh`
   - **Time:** Например, `00:00` (полночь)
   - **Frequency:** Daily

## Шаг 7: Мониторинг и логи

### Просмотр логов

```bash
# Последние 50 строк
tail -n 50 bot.log

# Следить в реальном времени
tail -f bot.log

# Очистить лог
> bot.log
```

### Проверка процесса

```bash
# Проверить, запущен ли бот
ps aux | grep run_bot.py

# Остановить бот
pkill -f run_bot.py
```

## Шаг 8: Обновление бота

Когда нужно обновить код:

```bash
# Остановите бота
pkill -f run_bot.py

# Обновите код через Git
cd путь_к_проекту
git pull origin claude/rewrite-telegram-bot-EEBhi

# Активируйте окружение
source venv/bin/activate

# Обновите зависимости (если изменились)
pip install -r requirements-bot.txt --upgrade

# Запустите бота снова
python run_bot.py
# или через tmux/скрипт
```

## Частые проблемы и решения

### Ошибка: "No module named 'telebot'"

**Решение:**
```bash
source venv/bin/activate
pip install pyTelegramBotAPI
```

### Ошибка: "TELEGRAM_BOT_TOKEN не установлен"

**Решение:** Проверьте файл `.env`:
```bash
cat .env  # Просмотреть содержимое
nano .env # Отредактировать
```

### Бот не отвечает в Telegram

**Проверьте:**
1. Запущен ли процесс: `ps aux | grep run_bot.py`
2. Логи: `tail -n 50 bot.log`
3. Интернет-соединение к Telegram API (на PythonAnywhere должно работать)

### Ошибка: "SSL: CERTIFICATE_VERIFY_FAILED"

**Решение:** Обновите certifi:
```bash
pip install --upgrade certifi
```

### Нет прав на запись в custom_messages.json

**Решение:**
```bash
chmod 644 telegram_bot/custom_messages.json
```

## Рекомендации

### Для бесплатного аккаунта:
- ✅ Используйте tmux для запуска
- ✅ Заходите на PythonAnywhere хотя бы раз в 3 дня
- ✅ Настройте Scheduled Task для ежедневного перезапуска
- ⚠️ Бот может останавливаться при долгом отсутствии

### Для стабильной работы:
- 💰 Рассмотрите платный аккаунт ($5/мес) для Always-On Task
- 🔄 Или используйте VPS (DigitalOcean, Linode от $5/мес)
- 📊 Следите за логами регулярно

## Альтернативы PythonAnywhere

Если бесплатного аккаунта недостаточно:

1. **Heroku** - бесплатный план (с ограничениями)
2. **Railway.app** - $5 кредитов/месяц бесплатно
3. **Render** - бесплатный план с ограничениями
4. **VPS** - DigitalOcean, Linode ($5-10/мес)
5. **Raspberry Pi** - если есть домашний сервер

## Полезные команды

```bash
# Показать путь к проекту
pwd

# Показать структуру папок
ls -la

# Проверить Python версию
python --version

# Показать установленные пакеты
pip list

# Проверить размер лога
du -h bot.log

# Очистить кеш Python
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -n 100 bot.log`
2. Проверьте, что все переменные в `.env` заполнены
3. Убедитесь, что виртуальное окружение активно
4. Проверьте, что токен бота корректный

---

**Готово!** Ваш бот должен работать на PythonAnywhere 🚀

Для управления текстами отправьте боту команду `/admin` (если вы добавили свой ID в ADMIN_IDS).
