# 🤖 Инструкция по запуску Telegram-бота

## 📋 Содержание
1. [Быстрый старт](#быстрый-старт)
2. [Настройка переменных окружения](#настройка-переменных-окружения)
3. [Установка зависимостей](#установка-зависимостей)
4. [Запуск бота](#запуск-бота)
5. [Настройка автозапуска (systemd)](#настройка-автозапуска-systemd)
6. [Решение проблем](#решение-проблем)

---

## 🚀 Быстрый старт

```bash
# 1. Перейти в директорию проекта
cd /home/user/Ffff

# 2. Установить зависимости
pip3 install -r requirements-bot.txt --user

# 3. Отредактировать .env файл (см. ниже)
nano telegram_bot/.env

# 4. Запустить бота
python3 run_bot.py
```

---

## ⚙️ Настройка переменных окружения

Отредактируйте файл `telegram_bot/.env`:

```bash
nano telegram_bot/.env
```

### Обязательные параметры:

```bash
# Токен бота от @BotFather
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН_ЗДЕСЬ

# ID администраторов (через запятую)
ADMIN_IDS=823820673

# ID чата для обращений
APPEAL_CHAT_ID=ID_ЧАТА

# ID чата для заявлений
APPLICATION_CHAT_ID=ID_ЧАТА
```

### Как получить ID чатов:

1. **Создайте группу/канал** в Telegram (или используйте существующий)
2. **Добавьте бота** в эту группу
3. **Отправьте любое сообщение** в группу
4. **Откройте в браузере:**
   ```
   https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates
   ```
5. **Найдите** в ответе: `"chat":{"id":-1001234567890,...}`
6. **Скопируйте ID** (с минусом!) и вставьте в `.env`

### Пример готового .env:

```bash
TELEGRAM_BOT_TOKEN=7710087256:AAFWHXIhrIkwL2pMLuhrvtIo8BvFCk7CebA
ADMIN_IDS=823820673
APPEAL_CHAT_ID=-1001234567890
APPLICATION_CHAT_ID=-1009876543210
LOG_LEVEL=INFO
```

---

## 📦 Установка зависимостей

### Вариант 1: Для текущего пользователя (рекомендуется)
```bash
pip3 install -r requirements-bot.txt --user
```

### Вариант 2: В виртуальном окружении
```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install -r requirements-bot.txt
```

### Необходимые пакеты:
- `pyTelegramBotAPI` - основная библиотека для работы с Telegram Bot API
- `python-dotenv` - для загрузки переменных окружения из .env файла

---

## ▶️ Запуск бота

### Простой запуск (для тестирования)
```bash
python3 run_bot.py
```

### Запуск в фоновом режиме
```bash
nohup python3 run_bot.py > bot.log 2>&1 &
```

### Проверка работы
```bash
# Посмотреть логи
tail -f telegram_bot/bot.log

# Проверить процесс
ps aux | grep run_bot
```

### Остановка бота
```bash
# Найти PID процесса
ps aux | grep run_bot.py

# Остановить (замените <PID> на реальный номер)
kill <PID>
```

---

## 🔄 Настройка автозапуска (systemd)

### 1. Создать systemd service файл

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

### 2. Вставить конфигурацию:

```ini
[Unit]
Description=Telegram Bot - Детский и Молодёжный Совет
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/user/Ffff
ExecStart=/usr/bin/python3 /home/user/Ffff/run_bot.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 3. Активировать и запустить:

```bash
# Перезагрузить конфигурацию systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable telegram-bot

# Запустить бота
sudo systemctl start telegram-bot

# Проверить статус
sudo systemctl status telegram-bot
```

### 4. Управление сервисом:

```bash
# Остановить
sudo systemctl stop telegram-bot

# Перезапустить
sudo systemctl restart telegram-bot

# Посмотреть логи
sudo journalctl -u telegram-bot -f

# Посмотреть последние 100 строк логов
sudo journalctl -u telegram-bot -n 100
```

---

## 🔧 Решение проблем

### Проблема: Бот не отвечает

**Проверьте:**
1. Правильность токена в `.env`
2. Доступ к интернету
3. Логи бота: `tail -f telegram_bot/bot.log`

```bash
# Проверить подключение к API Telegram
curl -X GET "https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe"
```

### Проблема: Не сохраняются отредактированные тексты

**Исправлено!** Проблема была в неправильном пути к `custom_messages.json`.

**Проверьте что файл создается:**
```bash
ls -la /home/user/Ffff/telegram_bot/custom_messages.json
```

**Если файла нет, проверьте права:**
```bash
# Дать права на запись
chmod 755 /home/user/Ffff/telegram_bot/
```

### Проблема: ModuleNotFoundError

```bash
# Переустановить зависимости
pip3 install -r requirements-bot.txt --user --force-reinstall
```

### Проблема: Ошибка "APPEAL_CHAT_ID не установлен"

Убедитесь, что в `telegram_bot/.env` указаны ID чатов. Если не знаете ID - используйте временно свой личный ID:

```bash
APPEAL_CHAT_ID=823820673
APPLICATION_CHAT_ID=823820673
```

### Проблема: Бот не видит команды администратора

Проверьте что ваш Telegram ID указан в `ADMIN_IDS`:

```bash
# Узнать свой ID
# 1. Отправьте /start боту @userinfobot
# 2. Он покажет ваш ID
# 3. Добавьте в .env: ADMIN_IDS=ваш_id
```

---

## 📱 Использование админ-панели

### Доступ к админ-панели:
1. Отправьте боту команду `/admin`
2. Выберите раздел в меню

### Редактирование текстов:
1. **Админ-панель** → **📝 Редактировать тексты**
2. Выберите нужное сообщение
3. Нажмите **✏️ Редактировать**
4. Отправьте новый текст (можно использовать форматирование Telegram)
5. Текст автоматически сохранится! ✅

### Форматирование текста:
- **Жирный**: `<b>текст</b>` или выделить в Telegram
- *Курсив*: `<i>текст</i>` или выделить в Telegram
- `Моноширинный`: `<code>текст</code>`
- [Ссылка](url): `<a href="url">текст</a>`

---

## 📊 Структура проекта

```
Ffff/
├── telegram_bot/
│   ├── .env                      # Переменные окружения (СОЗДАЙТЕ!)
│   ├── bot.py                    # Главный файл бота
│   ├── config.py                 # Конфигурация
│   ├── default_messages.json     # Дефолтные тексты
│   ├── custom_messages.json      # Кастомные тексты (создается автоматически)
│   ├── handlers/
│   │   ├── admin_panel.py       # Админ-панель (ИСПРАВЛЕНО!)
│   │   ├── appeal.py            # Обращения
│   │   └── application.py       # Заявления
│   └── message_manager.py        # Менеджер сообщений (ИСПРАВЛЕНО!)
├── run_bot.py                    # Скрипт запуска
└── requirements-bot.txt          # Зависимости
```

---

## ✅ Чеклист перед запуском

- [ ] Python 3.11+ установлен
- [ ] Зависимости установлены (`pip3 install -r requirements-bot.txt --user`)
- [ ] Файл `telegram_bot/.env` создан и заполнен
- [ ] Токен бота получен от @BotFather
- [ ] ID чатов получены через getUpdates API
- [ ] ID администратора указан в ADMIN_IDS

---

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи: `tail -f telegram_bot/bot.log`
2. Проверьте системные логи: `sudo journalctl -u telegram-bot -f`
3. Запустите тест: `python3 test_message_manager.py`

---

**Версия:** 1.0
**Дата:** 13.03.2026
**Статус:** ✅ Проблема с редактированием текстов исправлена!
