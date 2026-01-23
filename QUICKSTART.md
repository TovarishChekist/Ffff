# Быстрый старт на PythonAnywhere

## За 5 минут

### 1. Подготовка (на компьютере)

```bash
# Узнайте свой Telegram ID
# Напишите боту @userinfobot
```

### 2. На PythonAnywhere

**2.1. Создайте Bash консоль:**
- Зайдите на [pythonanywhere.com](https://www.pythonanywhere.com)
- Вкладка "Consoles" → "Bash"

**2.2. Загрузите код:**

```bash
# Клонируйте репозиторий
git clone https://github.com/TovarishChekist/Ffff.git
cd Ffff
git checkout claude/rewrite-telegram-bot-EEBhi

# Создайте окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements-bot.txt
```

**2.3. Настройте .env:**

```bash
# Создайте файл конфигурации
cp .env.example .env
nano .env
```

Заполните (используйте свои данные):
```env
TELEGRAM_BOT_TOKEN=7710087256:AAFWHXIhrIkwL2pMLuhrvtIo8BvFCk7CebA
APPEAL_CHAT_ID=-1002863620257
APPLICATION_CHAT_ID=-1002692926810
ADMIN_IDS=ваш_telegram_id
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

**2.4. Запустите бота:**

```bash
# Сделайте скрипты исполняемыми
chmod +x start_bot.sh stop_bot.sh status_bot.sh

# Запустите
./start_bot.sh
```

### 3. Проверка

Откройте Telegram → найдите вашего бота → отправьте `/start`

## Управление ботом

```bash
# Проверить статус
./status_bot.sh

# Просмотреть логи
tail -f bot.log

# Остановить
./stop_bot.sh

# Запустить снова
./start_bot.sh
```

## Админ-панель

В Telegram отправьте боту: `/admin`

## Если что-то не работает

```bash
# Проверьте последние ошибки
tail -n 50 bot.log

# Убедитесь, что бот запущен
ps aux | grep run_bot.py

# Перезапустите
./stop_bot.sh
./start_bot.sh
```

## Важно для бесплатного аккаунта

⚠️ Бот может остановиться при долгом отсутствии активности.

**Решение:** Заходите на PythonAnywhere раз в 2-3 дня или используйте tmux:

```bash
# Запуск в tmux (сессия сохраняется)
tmux new -s bot
source venv/bin/activate
python run_bot.py

# Отключиться (бот продолжит работать)
# Ctrl+B, затем D

# Подключиться обратно
tmux attach -t bot
```

---

**Полная инструкция:** [DEPLOYMENT_PYTHONANYWHERE.md](DEPLOYMENT_PYTHONANYWHERE.md)
