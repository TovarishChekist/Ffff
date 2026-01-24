# 🚀 Развертывание Telegram бота на VPS Spaceweb

Полная инструкция для запуска бота на VPS сервере Spaceweb с автозапуском.

---

## 📋 Что вам понадобится:

1. ✅ VPS сервер на Spaceweb (желательно Ubuntu 20.04/22.04)
2. ✅ SSH доступ к серверу (логин, пароль, IP адрес)
3. ✅ Токен бота от @BotFather
4. ✅ Ваш Telegram ID (от @userinfobot)
5. ✅ Chat ID совета (от @userinfobot)

---

## 🔧 Шаг 1: Подключение к VPS по SSH

### Через терминал (Linux/Mac):
```bash
ssh root@ВАШ_IP_АДРЕС
# Введите пароль когда попросит
```

### Через PuTTY (Windows):
1. Скачайте PuTTY: https://www.putty.org/
2. Откройте PuTTY
3. В поле "Host Name" введите IP адрес вашего VPS
4. Port: 22
5. Нажмите "Open"
6. Введите логин: `root`
7. Введите пароль от VPS

---

## 🐍 Шаг 2: Установка необходимого ПО

После подключения выполните команды:

```bash
# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем Python 3, pip, git
apt install python3 python3-pip python3-venv git nano -y

# Проверяем версии
python3 --version  # Должно быть Python 3.8+
git --version
```

---

## 📥 Шаг 3: Клонирование репозитория

```bash
# Переходим в домашнюю директорию
cd ~

# Клонируем репозиторий
git clone https://github.com/TovarishChekist/Ffff.git

# Переходим в папку проекта
cd Ffff

# Переключаемся на нужную ветку
git checkout claude/rewrite-telegram-bot-EEBhi
```

---

## 🔐 Шаг 4: Настройка .env файла

```bash
# Создаем .env файл
nano telegram_bot/.env
```

**Вставьте следующее содержимое** (замените на свои данные):

```env
# Токен бота от @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Ваш Telegram ID (администратор)
ADMIN_ID=123456789

# Chat ID совета (куда отправляются обращения)
COUNCIL_CHAT_ID=-1001234567890

# Режим отладки (false для продакшена)
DEBUG=false
```

**Как сохранить файл в nano:**
1. Нажмите `Ctrl + O` (сохранить)
2. Нажмите `Enter` (подтвердить имя файла)
3. Нажмите `Ctrl + X` (выйти)

---

## 📦 Шаг 5: Установка зависимостей

```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем его
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements-bot.txt

# Проверяем что все установилось
pip list | grep telebot
```

---

## 🧪 Шаг 6: Тестовый запуск

```bash
# Запускаем бота вручную для проверки
python3 telegram_bot/bot.py
```

**Проверьте:**
- Бот должен вывести: "Бот запущен! Нажмите Ctrl+C для остановки."
- Откройте Telegram и отправьте `/start` боту
- Если все работает - нажмите `Ctrl + C` чтобы остановить

---

## ⚙️ Шаг 7: Настройка автозапуска (systemd)

Чтобы бот работал 24/7 и автоматически запускался после перезагрузки:

```bash
# Создаем systemd сервис
nano /etc/systemd/system/telegram-bot.service
```

**Вставьте следующее содержимое:**

```ini
[Unit]
Description=Telegram Bot ДМОС Амурской области
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Ffff
Environment="PATH=/root/Ffff/venv/bin"
ExecStart=/root/Ffff/venv/bin/python3 /root/Ffff/telegram_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Сохраните:** `Ctrl + O`, `Enter`, `Ctrl + X`

---

## 🚀 Шаг 8: Запуск сервиса

```bash
# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable telegram-bot

# Запускаем бота
systemctl start telegram-bot

# Проверяем статус
systemctl status telegram-bot
```

**Должно быть:**
- ✅ `Active: active (running)`
- ✅ Зеленая надпись "Бот запущен!"

---

## 📊 Управление ботом

### Основные команды:

```bash
# Запустить бота
systemctl start telegram-bot

# Остановить бота
systemctl stop telegram-bot

# Перезапустить бота
systemctl restart telegram-bot

# Проверить статус
systemctl status telegram-bot

# Посмотреть логи (последние 50 строк)
journalctl -u telegram-bot -n 50

# Посмотреть логи в реальном времени
journalctl -u telegram-bot -f
```

---

## 🔄 Обновление бота

Когда выйдут обновления кода:

```bash
# Остановите бота
systemctl stop telegram-bot

# Перейдите в папку проекта
cd ~/Ffff

# Скачайте обновления
git pull origin claude/rewrite-telegram-bot-EEBhi

# Активируйте виртуальное окружение
source venv/bin/activate

# Обновите зависимости (если нужно)
pip install -r requirements-bot.txt --upgrade

# Запустите бота
systemctl start telegram-bot

# Проверьте статус
systemctl status telegram-bot
```

---

## 🛠️ Решение проблем

### Бот не запускается:

```bash
# Посмотрите подробные логи
journalctl -u telegram-bot -n 100 --no-pager

# Проверьте .env файл
cat telegram_bot/.env

# Попробуйте запустить вручную
cd ~/Ffff
source venv/bin/activate
python3 telegram_bot/bot.py
```

### Ошибка "ModuleNotFoundError":

```bash
cd ~/Ffff
source venv/bin/activate
pip install -r requirements-bot.txt --force-reinstall
```

### Бот падает после отправки сообщения:

```bash
# Проверьте правильность COUNCIL_CHAT_ID
# ID группы должен начинаться с -100
nano telegram_bot/.env
```

---

## 🔒 Безопасность (рекомендуется)

### 1. Создайте отдельного пользователя (не root):

```bash
# Создаем пользователя
adduser botuser

# Копируем проект
cp -r /root/Ffff /home/botuser/
chown -R botuser:botuser /home/botuser/Ffff

# Редактируем сервис
nano /etc/systemd/system/telegram-bot.service
```

Измените:
```ini
User=botuser
WorkingDirectory=/home/botuser/Ffff
Environment="PATH=/home/botuser/Ffff/venv/bin"
ExecStart=/home/botuser/Ffff/venv/bin/python3 /home/botuser/Ffff/telegram_bot/bot.py
```

```bash
# Перезапускаем
systemctl daemon-reload
systemctl restart telegram-bot
```

### 2. Настройте firewall:

```bash
# Устанавливаем ufw
apt install ufw -y

# Разрешаем SSH
ufw allow 22/tcp

# Включаем firewall
ufw enable

# Проверяем статус
ufw status
```

---

## ✅ Преимущества VPS перед PythonAnywhere:

- ✅ **Бот работает 24/7 без ограничений**
- ✅ **Автоматический перезапуск** при сбоях
- ✅ **Нет ограничений на внешние подключения**
- ✅ **Полный контроль** над сервером
- ✅ **Можно размещать несколько ботов**
- ✅ **Логи доступны через journalctl**

---

## 📞 Проверка работы:

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Попробуйте все кнопки
4. Проверьте админ-панель: `/admin`
5. Отправьте тестовое обращение

**Бот должен отвечать мгновенно и работать постоянно!** 🎉

---

## 📝 Полезные команды для мониторинга:

```bash
# Использование диска
df -h

# Использование памяти
free -h

# Процессы Python
ps aux | grep python

# Нагрузка на сервер
top
```

Если возникли проблемы - проверьте логи командой:
```bash
journalctl -u telegram-bot -n 100
```
