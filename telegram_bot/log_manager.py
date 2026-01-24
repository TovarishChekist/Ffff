# -*- coding: utf-8 -*-
"""
Менеджер логов - управление логами бота с категоризацией и автоочисткой
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LogManager:
    """Управление логами бота"""

    # Категории логов
    LOG_CATEGORIES = {
        'all': 'Все логи',
        'errors': 'Ошибки',
        'broadcast': 'Рассылки',
        'admin': 'Действия администраторов',
        'users': 'Пользователи',
    }

    def __init__(self, base_dir: str = None):
        """
        Инициализация менеджера логов

        Args:
            base_dir: Базовая директория для логов
        """
        if base_dir is None:
            base_dir = os.path.dirname(__file__)

        self.base_dir = base_dir
        self.logs_dir = os.path.join(base_dir, 'logs')
        self.settings_file = os.path.join(base_dir, 'log_settings.json')

        # Создаем директорию для логов если её нет
        os.makedirs(self.logs_dir, exist_ok=True)

        # Загружаем настройки
        self.settings = self._load_settings()

        # Запускаем автоочистку если включена
        self.auto_cleanup_thread = None
        if self.settings.get('auto_cleanup_enabled', False):
            self._start_auto_cleanup()

    def _load_settings(self) -> Dict:
        """Загружает настройки автоочистки"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек логов: {e}")

        # Настройки по умолчанию
        return {
            'auto_cleanup_enabled': False,
            'cleanup_interval_hours': 24,
            'last_cleanup': None
        }

    def _save_settings(self) -> None:
        """Сохраняет настройки автоочистки"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек логов: {e}")

    def get_log_file_path(self, category: str = 'all') -> str:
        """
        Возвращает путь к файлу лога

        Args:
            category: Категория лога

        Returns:
            str: Путь к файлу лога
        """
        if category == 'all':
            return os.path.join(self.base_dir, 'bot.log')
        else:
            return os.path.join(self.logs_dir, f'{category}.log')

    def get_log_content(self, category: str = 'all', lines: int = 100) -> Optional[str]:
        """
        Получает содержимое лога

        Args:
            category: Категория лога
            lines: Количество последних строк

        Returns:
            Optional[str]: Содержимое лога или None
        """
        log_path = self.get_log_file_path(category)

        try:
            if not os.path.exists(log_path):
                return None

            # Читаем последние N строк
            with open(log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:]) if all_lines else None
        except Exception as e:
            logger.error(f"Ошибка чтения лога {category}: {e}")
            return None

    def get_log_size(self, category: str = 'all') -> int:
        """
        Возвращает размер файла лога в байтах

        Args:
            category: Категория лога

        Returns:
            int: Размер файла в байтах
        """
        log_path = self.get_log_file_path(category)

        try:
            if os.path.exists(log_path):
                return os.path.getsize(log_path)
        except Exception as e:
            logger.error(f"Ошибка получения размера лога {category}: {e}")

        return 0

    def get_log_info(self, category: str = 'all') -> Dict:
        """
        Получает информацию о логе

        Args:
            category: Категория лога

        Returns:
            Dict: Информация о логе
        """
        log_path = self.get_log_file_path(category)

        info = {
            'category': category,
            'title': self.LOG_CATEGORIES.get(category, category),
            'exists': os.path.exists(log_path),
            'size': 0,
            'size_mb': 0,
            'lines': 0,
            'modified': None
        }

        if info['exists']:
            try:
                info['size'] = os.path.getsize(log_path)
                info['size_mb'] = round(info['size'] / 1024 / 1024, 2)
                info['modified'] = datetime.fromtimestamp(os.path.getmtime(log_path)).isoformat()

                # Подсчитываем строки
                with open(log_path, 'r', encoding='utf-8') as f:
                    info['lines'] = sum(1 for _ in f)
            except Exception as e:
                logger.error(f"Ошибка получения информации о логе {category}: {e}")

        return info

    def delete_log(self, category: str = 'all') -> bool:
        """
        Удаляет файл лога

        Args:
            category: Категория лога

        Returns:
            bool: True если удалено успешно
        """
        log_path = self.get_log_file_path(category)

        try:
            if os.path.exists(log_path):
                os.remove(log_path)
                logger.info(f"Лог {category} удален")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления лога {category}: {e}")
            return False

    def clear_all_logs(self) -> Dict[str, bool]:
        """
        Очищает все логи

        Returns:
            Dict[str, bool]: Результаты удаления для каждой категории
        """
        results = {}

        for category in self.LOG_CATEGORIES.keys():
            results[category] = self.delete_log(category)

        logger.info("Все логи очищены")
        self.settings['last_cleanup'] = datetime.now().isoformat()
        self._save_settings()

        return results

    def get_all_logs_info(self) -> List[Dict]:
        """
        Получает информацию обо всех логах

        Returns:
            List[Dict]: Список с информацией о каждом логе
        """
        logs_info = []

        for category in self.LOG_CATEGORIES.keys():
            info = self.get_log_info(category)
            logs_info.append(info)

        return logs_info

    def set_auto_cleanup(self, enabled: bool, interval_hours: int = 24) -> None:
        """
        Настраивает автоочистку логов

        Args:
            enabled: Включить/выключить автоочистку
            interval_hours: Интервал в часах (6, 12, 24)
        """
        self.settings['auto_cleanup_enabled'] = enabled
        self.settings['cleanup_interval_hours'] = interval_hours
        self._save_settings()

        # Перезапускаем поток автоочистки
        if enabled:
            self._start_auto_cleanup()
        else:
            self._stop_auto_cleanup()

        logger.info(f"Автоочистка логов: {'включена' if enabled else 'выключена'}, интервал: {interval_hours}ч")

    def get_auto_cleanup_settings(self) -> Dict:
        """
        Возвращает текущие настройки автоочистки

        Returns:
            Dict: Настройки автоочистки
        """
        return {
            'enabled': self.settings.get('auto_cleanup_enabled', False),
            'interval_hours': self.settings.get('cleanup_interval_hours', 24),
            'last_cleanup': self.settings.get('last_cleanup'),
            'next_cleanup': self._get_next_cleanup_time()
        }

    def _get_next_cleanup_time(self) -> Optional[str]:
        """Возвращает время следующей автоочистки"""
        if not self.settings.get('auto_cleanup_enabled'):
            return None

        last_cleanup = self.settings.get('last_cleanup')
        if not last_cleanup:
            return "Скоро"

        try:
            last_time = datetime.fromisoformat(last_cleanup)
            interval = timedelta(hours=self.settings.get('cleanup_interval_hours', 24))
            next_time = last_time + interval
            return next_time.isoformat()
        except:
            return None

    def _start_auto_cleanup(self) -> None:
        """Запускает поток автоочистки"""
        if self.auto_cleanup_thread and self.auto_cleanup_thread.is_alive():
            return

        self.auto_cleanup_thread = threading.Thread(
            target=self._auto_cleanup_loop,
            daemon=True
        )
        self.auto_cleanup_thread.start()
        logger.info("Поток автоочистки логов запущен")

    def _stop_auto_cleanup(self) -> None:
        """Останавливает поток автоочистки"""
        # Поток остановится сам при следующей проверке enabled
        logger.info("Автоочистка логов отключена")

    def _auto_cleanup_loop(self) -> None:
        """Основной цикл автоочистки"""
        while True:
            try:
                # Проверяем включена ли автоочистка
                if not self.settings.get('auto_cleanup_enabled'):
                    time.sleep(60)  # Проверяем каждую минуту
                    continue

                # Проверяем нужно ли очищать
                interval_hours = self.settings.get('cleanup_interval_hours', 24)
                last_cleanup = self.settings.get('last_cleanup')

                should_cleanup = False

                if not last_cleanup:
                    should_cleanup = True
                else:
                    try:
                        last_time = datetime.fromisoformat(last_cleanup)
                        if datetime.now() - last_time >= timedelta(hours=interval_hours):
                            should_cleanup = True
                    except:
                        should_cleanup = True

                if should_cleanup:
                    logger.info("Запуск автоочистки логов")
                    self.clear_all_logs()

                # Спим до следующей проверки (проверяем каждый час)
                time.sleep(3600)

            except Exception as e:
                logger.error(f"Ошибка в потоке автоочистки: {e}")
                time.sleep(60)


# Глобальный экземпляр менеджера логов
log_manager = LogManager()
