# 🔄 Обновление бота на PythonAnywhere

Простая инструкция как обновить код бота после изменений в репозитории.

---

## 📋 Быстрое обновление (за 2 минуты)

### Шаг 1: Откройте консоль

1. Зайдите на [PythonAnywhere](https://www.pythonanywhere.com)
2. Вкладка **"Consoles"**
3. Нажмите **"Bash"** (или откройте существующую консоль)

### Шаг 2: Остановите бота

```bash
cd Ffff
./stop_bot.sh
```

Увидите: `✅ Бот успешно остановлен`

### Шаг 3: Обновите код

```bash
git pull origin claude/rewrite-telegram-bot-EEBhi
```

Увидите список изменённых файлов.

**Если появляется ошибка "Please commit your changes":**

```bash
# Сохраните ваши изменения
git stash

# Обновите код
git pull origin claude/rewrite-telegram-bot-EEBhi

# Верните ваши изменения
git stash pop
```

### Шаг 4: Обновите зависимости (если нужно)

```bash
source venv/bin/activate
pip install -r requirements-bot.txt --upgrade
```

**Примечание:** Этот шаг нужен только если в обновлении были изменения в `requirements-bot.txt`

### Шаг 5: Запустите бота

```bash
./start_bot.sh
```

Увидите: `✅ Бот успешно запущен`

### Шаг 6: Проверьте

Откройте бота в Telegram и отправьте `/start`

✅ **Готово!** Бот обновлён и работает с новым кодом.

---

## 🔍 Проверка изменений

### Посмотреть что изменилось

**До обновления:**
```bash
git fetch origin claude/rewrite-telegram-bot-EEBhi
git log HEAD..origin/claude/rewrite-telegram-bot-EEBhi --oneline
```

Это покажет список коммитов которые будут загружены.

**После обновления:**
```bash
git log -5 --oneline
```

Покажет последние 5 коммитов.

### Посмотреть конкретные изменения

```bash
git diff HEAD@{1} HEAD
```

Покажет все изменения в коде.

---

## 📝 Полная последовательность команд

Скопируйте и вставьте все сразу:

```bash
# Переходим в папку проекта
cd Ffff

# Останавливаем бота
./stop_bot.sh

# Обновляем код
git pull origin claude/rewrite-telegram-bot-EEBhi

# Активируем окружение
source venv/bin/activate

# Обновляем зависимости (на всякий случай)
pip install -r requirements-bot.txt --upgrade

# Запускаем бота
./start_bot.sh

# Проверяем статус
./status_bot.sh
```

---

## ⚠️ Если что-то пошло не так

### Ошибка: "Your local changes would be overwritten"

**Проблема:** Вы изменили файлы локально

**Решение:**

```bash
# Сохраните изменения
git stash

# Обновите
git pull origin claude/rewrite-telegram-bot-EEBhi

# Верните изменения
git stash pop
```

### Ошибка: "Conflicts detected"

**Проблема:** Конфликт между вашими изменениями и новым кодом

**Решение 1 - Оставить новый код:**
```bash
git checkout --theirs .
git add .
git stash drop
```

**Решение 2 - Оставить свои изменения:**
```bash
git checkout --ours .
git add .
```

### Бот не запускается после обновления

**Проверьте логи:**
```bash
tail -n 100 bot.log
```

**Переустановите зависимости:**
```bash
source venv/bin/activate
pip install -r requirements-bot.txt --force-reinstall
./start_bot.sh
```

### Нужно вернуться к предыдущей версии

```bash
# Посмотрите коммиты
git log --oneline

# Вернитесь к нужному коммиту (замените HASH на хеш коммита)
git checkout HASH

# Или вернитесь на один коммит назад
git checkout HEAD~1

# Перезапустите бота
./stop_bot.sh
./start_bot.sh
```

**Чтобы вернуться к последней версии:**
```bash
git checkout claude/rewrite-telegram-bot-EEBhi
```

---

## 🔄 Автоматическое обновление

Если хотите автоматически обновлять бота каждый день:

### Создайте скрипт auto_update.sh

```bash
nano auto_update.sh
```

Вставьте:

```bash
#!/bin/bash
cd /home/ВАШ_USERNAME/Ffff

# Останавливаем бота
./stop_bot.sh

# Обновляем код
git pull origin claude/rewrite-telegram-bot-EEBhi

# Активируем окружение
source venv/bin/activate

# Обновляем зависимости
pip install -r requirements-bot.txt --upgrade -q

# Запускаем бота
./start_bot.sh

echo "$(date): Бот обновлен" >> update.log
```

Сделайте исполняемым:
```bash
chmod +x auto_update.sh
```

### Настройте в PythonAnywhere

1. Вкладка **"Tasks"**
2. Раздел **"Scheduled tasks"**
3. **Command:** `/home/ВАШ_USERNAME/Ffff/auto_update.sh`
4. **Time:** `03:00` (3 часа ночи)
5. **Frequency:** Daily

Теперь бот будет автоматически обновляться каждый день в 3 часа ночи!

---

## 📊 Мониторинг обновлений

### Проверить когда последний раз обновлялся

```bash
git log -1 --format="%cd" --date=format:"%d.%m.%Y %H:%M"
```

### Узнать текущую версию

```bash
git rev-parse --short HEAD
```

### Посмотреть лог обновлений

```bash
cat update.log
```

---

## 💡 Полезные команды

```bash
# Текущая ветка
git branch

# Текущий коммит
git log -1 --oneline

# Статус репозитория
git status

# Проверить есть ли обновления (не скачивая их)
git fetch origin claude/rewrite-telegram-bot-EEBhi
git log HEAD..origin/claude/rewrite-telegram-bot-EEBhi --oneline

# Скачать конкретный файл без полного обновления
git checkout origin/claude/rewrite-telegram-bot-EEBhi -- путь/к/файлу
```

---

## 🆘 Экстренный сброс

Если всё сломалось и нужно начать с чистого листа:

```bash
# ВНИМАНИЕ: Это удалит ВСЕ локальные изменения!

cd Ffff

# Сохраните .env файл
cp .env .env.backup

# Сохраните custom_messages.json если есть
cp custom_messages.json custom_messages.backup 2>/dev/null

# Полный сброс
git fetch origin
git reset --hard origin/claude/rewrite-telegram-bot-EEBhi
git clean -fd

# Верните конфигурацию
cp .env.backup .env
cp custom_messages.backup custom_messages.json 2>/dev/null

# Переустановите зависимости
source venv/bin/activate
pip install -r requirements-bot.txt --force-reinstall

# Запустите
./start_bot.sh
```

---

## 📞 Нужна помощь?

- [Основная инструкция PythonAnywhere](SIMPLE_PYTHONANYWHERE.md)
- [Полная документация](DEPLOYMENT_PYTHONANYWHERE.md)
- [Быстрый старт](QUICKSTART.md)

---

**Важно:** Всегда делайте резервную копию `.env` и `custom_messages.json` перед обновлением!
