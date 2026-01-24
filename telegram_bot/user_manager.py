# -*- coding: utf-8 -*-
"""
Менеджер пользователей - управление базой пользователей бота
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class UserManager:
    """Управление пользователями бота"""

    def __init__(self, db_file: str = "users.json"):
        """
        Инициализация менеджера пользователей

        Args:
            db_file: Путь к файлу базы данных пользователей
        """
        # Определяем путь к файлу относительно текущего модуля
        self.db_path = os.path.join(os.path.dirname(__file__), db_file)
        self.users: Dict[int, Dict] = {}
        self._load_users()

    def _load_users(self) -> None:
        """Загружает пользователей из файла"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Преобразуем строковые ключи обратно в int
                    self.users = {int(k): v for k, v in data.items()}
                logger.info(f"Загружено {len(self.users)} пользователей из базы")
            else:
                logger.info("База пользователей не найдена, создаем новую")
                self.users = {}
                self._save_users()
        except Exception as e:
            logger.error(f"Ошибка загрузки базы пользователей: {e}")
            self.users = {}

    def _save_users(self) -> None:
        """Сохраняет пользователей в файл"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения базы пользователей: {e}")

    def add_user(self, user_id: int, username: Optional[str] = None,
                 first_name: Optional[str] = None, last_name: Optional[str] = None) -> None:
        """
        Добавляет или обновляет пользователя

        Args:
            user_id: Telegram ID пользователя
            username: Username пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
        """
        now = datetime.now().isoformat()

        if user_id in self.users:
            # Обновляем существующего пользователя
            self.users[user_id]['last_interaction'] = now
            self.users[user_id]['interaction_count'] += 1

            # Обновляем данные если они изменились
            if username:
                self.users[user_id]['username'] = username
            if first_name:
                self.users[user_id]['first_name'] = first_name
            if last_name:
                self.users[user_id]['last_name'] = last_name
        else:
            # Добавляем нового пользователя
            self.users[user_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'first_interaction': now,
                'last_interaction': now,
                'interaction_count': 1
            }
            logger.info(f"Новый пользователь: {user_id} (@{username})")

        self._save_users()

    def get_all_user_ids(self) -> List[int]:
        """
        Возвращает список всех user_id

        Returns:
            List[int]: Список ID всех пользователей
        """
        return list(self.users.keys())

    def get_user_count(self) -> int:
        """
        Возвращает количество пользователей

        Returns:
            int: Количество пользователей в базе
        """
        return len(self.users)

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """
        Получает информацию о пользователе

        Args:
            user_id: Telegram ID пользователя

        Returns:
            Optional[Dict]: Информация о пользователе или None
        """
        return self.users.get(user_id)

    def get_stats(self) -> Dict:
        """
        Возвращает статистику по пользователям

        Returns:
            Dict: Статистика пользователей
        """
        if not self.users:
            return {
                'total_users': 0,
                'active_today': 0,
                'total_interactions': 0
            }

        today = datetime.now().date()
        active_today = 0
        total_interactions = 0

        for user_data in self.users.values():
            total_interactions += user_data.get('interaction_count', 0)

            # Проверяем активность сегодня
            last_interaction = user_data.get('last_interaction')
            if last_interaction:
                try:
                    last_date = datetime.fromisoformat(last_interaction).date()
                    if last_date == today:
                        active_today += 1
                except:
                    pass

        return {
            'total_users': len(self.users),
            'active_today': active_today,
            'total_interactions': total_interactions
        }


# Глобальный экземпляр менеджера пользователей
user_manager = UserManager()
