from collections import defaultdict
from datetime import datetime, timedelta
import telebot
from telebot import types
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton,Message,ReplyKeyboardMarkup, KeyboardButton
from telebot.apihelper import ApiTelegramException
import sqlite3
import logging
import time
import requests
import random
import os
import csv
import json
from logging.handlers import RotatingFileHandler
import sys
from threading import Thread
from PIL import Image
import tempfile
from instance import (bot, photo, photo_logarithms, photo_powers, photo_fsy, photo_modules, photo_parabola,
                      photo_quadratic_equations, photo_roots, photo_direct, photo_hyperbola,
                      photo_root_function, photo_exponential_function, photo_logarithmic_function,
                      photo_contact, photo_main, photo_definition, photo_reduction_formulas,
                      photo_trigonometric_formulas, photo_task_rhombus_trapezoid, photo_task_angles,
                      photo_trigonometric_circle, photo_task45, photo_task10, photo_task2, photo_task12, photo_task3,
                      photo_task81, photo_task82, photo_task_triangle_lines, photo_task_right_triangle,
                      photo_task_isosceles_equilateral_triangle, photo_task_triangle_similarity, photo_task_triangle,
                      photo_task_circle_2, photo_task_circle_1, photo_task_parallelogram, photo_task_regular_hexagon,
                      photo_trigonometry, photo_rationalization, photo_task14, photo_task16, photo_tasks, photo_cards,
                      photo_timers,
                      photo_quize, photo_challenge, photo_quest_main, photo_quest_worlds, photo_quest_profile,
                      photo_quest_trophies, photo_quest_shop, photo_quest_coming_soon,
                      photo_quest_book, photo_quest_quests, photo_quest_ritual, photo_tangent_circle,
                      photo_world_progress_0_10, photo_world_progress_10_20, photo_world_progress_20_30,
                      photo_world_progress_30_40, photo_world_progress_40_50, photo_world_progress_50_60,
                      photo_world_progress_60_70, photo_world_progress_70_80, photo_world_progress_80_90,
                      photo_world_progress_90_100, goose_common_photo, photo_world_map_progress_0_10,
                      photo_world_map_progress_10_20, photo_world_map_progress_20_30, photo_world_map_progress_40_50,
                      photo_world_map_progress_50_60, photo_world_map_progress_60_70, photo_world_map_progress_70_80,
                      photo_world_map_progress_80_90, photo_world_map_progress_90_100, photo_world_map_progress_30_40
                      )


from screens import (tasks_screen, main_screen, contact_screen,
                     task_679_screen, task_10_screen, task_11_screen, task_12_screen,
                     task_45_screen, task_8_screen, task_1_screen, task_2_screen, task_3_screen,
                     back_to_task_679_screen, back_to_task_8_screen, back_to_task_gropCircle_screen,
                     back_to_task_11_screen, task_group_trigonometry_screen,
                     back_to_task_group_trigonometry_screen, back_to_task_1_screen, task_groupCircle_screen,
                     back_to_task_gropTriangles_screen, task_groupTriangles_screen, task_13_screen,
                     back_to_task_13_screen, task13group_trigonometry_screen, back_to_task13group_trigonometry_screen,
                     task_15_screen, back_to_task_15_screen, task_17_screen, back_to_task_17_screen,
                     task17groupTriangles_screen, back_to_task17gropTriangles_screen, back_to_task17gropCircle_screen,
                     task17groupCircle_screen, back_to_task17group_trigonometry_screen,task17group_trigonometry_screen, math_quest_screen, quest_worlds_screen, quest_profile_screen, quest_trophies_screen, quest_shop_screen, coming_soon_screen, loaded_world_screen)

# Инициализация и структура БД для избранных задач (перенесено из favorites.py)
def init_favorites_db():
    conn = sqlite3.connect('favorites.db')
    cursor = conn.cursor()
    
    # Проверяем, существует ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='favorites'")
    table_exists = cursor.fetchone() is not None
    
    # Если таблица уже существует, то просто используем её
    if not table_exists:
        # Создаем таблицу только если её еще нет
        cursor.execute('''
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            world_id TEXT,
            category_id TEXT,
            task_id TEXT,
            added_date TEXT,
            UNIQUE(user_id, world_id, category_id, task_id)
        )
        ''')
    
    conn.commit()
    conn.close()
    logging.info("✅ База данных избранных задач инициализирована. Данные сохраняются между перезапусками.")
    return True

# Добавление задачи в избранное
def add_to_favorites(user_id, world_id, category_id, task_id):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        # Проверяем есть ли уже такая задача в избранном
        cursor.execute(
            'SELECT id FROM favorites WHERE user_id=? AND world_id=? AND category_id=? AND task_id=?', 
            (user_id, world_id, category_id, task_id)
        )
        
        if cursor.fetchone():
            # Задача уже в избранном
            conn.close()
            return False
        
        # Добавляем задачу в избранное с московским временем (UTC+3)
        msk_time = datetime.now() + timedelta(hours=3)
        added_date = msk_time.isoformat()
        cursor.execute(
            'INSERT INTO favorites (user_id, world_id, category_id, task_id, added_date) VALUES (?, ?, ?, ?, ?)',
            (user_id, world_id, category_id, task_id, added_date)
        )
        
        conn.commit()
        conn.close()
        logging.info(f"Задача добавлена в избранное: user_id={user_id}, world_id={world_id}, task_id={task_id}")
        return True
    except Exception as e:
        logging.error(f"Ошибка при добавлении в избранное: {e}")
        return False

# Удаление задачи из избранного
def remove_from_favorites(user_id, world_id, category_id, task_id):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        # Удаляем задачу из избранного
        cursor.execute(
            'DELETE FROM favorites WHERE user_id=? AND world_id=? AND category_id=? AND task_id=?', 
            (user_id, world_id, category_id, task_id)
        )
        
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logging.info(f"Задача удалена из избранного: user_id={user_id}, world_id={world_id}, task_id={task_id}")
            return True
        else:
            logging.info(f"Задача не найдена в избранном: user_id={user_id}, world_id={world_id}, task_id={task_id}")
            return False
    except Exception as e:
        logging.error(f"Ошибка при удалении из избранного: {e}")
        return False

# Проверка добавлена ли задача в избранное
def is_in_favorites(user_id, world_id, category_id, task_id):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM favorites WHERE user_id=? AND world_id=? AND category_id=? AND task_id=?', 
            (user_id, world_id, category_id, task_id)
        )
        
        result = cursor.fetchone() is not None
        conn.close()
        return result
    except Exception as e:
        logging.error(f"Ошибка при проверке избранного: {e}")
        return False

# Получение списка миров с избранными задачами
def get_favorite_worlds(user_id):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT DISTINCT world_id FROM favorites WHERE user_id=?', 
            (user_id,)
        )
        
        worlds = [row[0] for row in cursor.fetchall()]
        conn.close()
        return worlds
    except Exception as e:
        logging.error(f"Ошибка при получении списка миров с избранными задачами: {e}")
        return []

# Получение списка категорий с избранными задачами в конкретном мире
def get_favorite_categories(user_id, world_id):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT DISTINCT category_id FROM favorites WHERE user_id=? AND world_id=?', 
            (user_id, world_id)
        )
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    except Exception as e:
        logging.error(f"Ошибка при получении списка категорий с избранными задачами: {e}")
        return []

# Получение всех избранных задач для конкретного пользователя и мира
def get_favorite_tasks(user_id, world_id=None, category_id=None, order_random=False):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        query = 'SELECT world_id, category_id, task_id FROM favorites WHERE user_id=?'
        params = [user_id]
        
        if world_id:
            query += ' AND world_id=?'
            params.append(world_id)
            
        if category_id:
            query += ' AND category_id=?'
            params.append(category_id)
            
        if order_random:
            query += ' ORDER BY RANDOM()'
        else:
            query += ' ORDER BY added_date'
        
        cursor.execute(query, params)
        
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    except Exception as e:
        logging.error(f"Ошибка при получении избранных задач: {e}")
        return []

# Получение количества избранных задач для пользователя
def get_favorites_count(user_id, world_id=None):
    try:
        conn = sqlite3.connect('favorites.db')
        cursor = conn.cursor()
        
        query = 'SELECT COUNT(*) FROM favorites WHERE user_id=?'
        params = [user_id]
        
        if world_id:
            query += ' AND world_id=?'
            params.append(world_id)
        
        cursor.execute(query, params)
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logging.error(f"Ошибка при подсчете избранных задач: {e}")
        return 0

# Настройка логирования с явной поддержкой UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Установка кодировки UTF-8 для вывода в консоль
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Тестовое сообщение
logging.info("✅ Логирование инициализировано с поддержкой UTF-8")

def ensure_user_data(user_id, default_data=None):
    if user_id not in user_data or not isinstance(user_data[user_id], dict):
        user_data[user_id] = default_data or {}
    return user_data[user_id]

# ================== Отслеживание активности ==================
users_db = 'users.db'
users_conn = sqlite3.connect(users_db, check_same_thread=False)
users_cursor = users_conn.cursor()

def init_users_db():
    try:
        with users_conn:
            users_cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    phone TEXT,
                    first_seen TEXT,
                    last_seen TEXT
                )''')
            users_cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS tutor_requests (
                    user_id INTEGER,
                    name TEXT,
                    school_class TEXT,
                    test_score TEXT,
                    expected_price TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, timestamp)
                )''')
            # Добавляем столбец phone, если его нет
            users_cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in users_cursor.fetchall()]
            if "phone" not in columns:
                users_cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
                logging.info("Столбец 'phone' добавлен в таблицу 'users'")
            users_conn.commit()
            logging.info("✅ Таблица 'users' и 'tutor_requests' обновлены!")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")

init_users_db()

def update_last_seen(user_id):
    """Обновляет дату последнего использования бота пользователем.
    
    Args:
        user_id: ID пользователя
    """
    user_id = str(user_id)
    # Создаем объект времени по Московскому часовому поясу (UTC+3)
    msk_time = datetime.now() + timedelta(hours=3)
    current_time = msk_time.isoformat()
    
    try:
        with users_conn:
            # Проверяем, существует ли пользователь
            users_cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
            result = users_cursor.fetchone()
            
            if result:
                # Если пользователь существует, обновляем last_seen
                users_cursor.execute('UPDATE users SET last_seen = ? WHERE user_id = ?', 
                                    (current_time, user_id))
                logging.debug(f"Обновлена дата последнего использования для пользователя {user_id}")
            else:
                # Если пользователь не существует, регистрируем его
                logging.info(f"Пользователь {user_id} не найден, выполняем регистрацию")
                users_cursor.execute('''
                    INSERT INTO users (user_id, first_seen, last_seen)
                    VALUES (?, ?, ?)
                ''', (user_id, current_time, current_time))
            
            users_conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при обновлении last_seen для пользователя {user_id}: {e}")

def register_user(user_id, username=None, phone=None):
    # Преобразуем user_id в строку для единообразия
    user_id = str(user_id)
    # Создаем объект времени по Московскому часовому поясу (UTC+3)
    msk_time = datetime.now() + timedelta(hours=3)
    current_time = msk_time.isoformat()
    
    # Сначала обновляем last_seen в любом случае
    update_last_seen(user_id)
    
    # Затем обновляем дополнительные данные, если они предоставлены
    if username or phone:
        try:
            with users_conn:
                users_cursor.execute('SELECT username, phone FROM users WHERE user_id = ?', (user_id,))
                result = users_cursor.fetchone()
                
                if not result:
                    # Если пользователь не найден (что маловероятно после update_last_seen),
                    # создаем полную запись
                    logging.info(f"Регистрация нового пользователя: {user_id}, {username}")
                    users_cursor.execute('''
                        INSERT INTO users (user_id, username, phone, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, username, phone, current_time, current_time))
                else:
                    # Обновляем только те поля, которые предоставлены
                    update_fields = []
                    update_values = []
                    
                    if username:
                        update_fields.append("username = ?")
                        update_values.append(username)
                    
                    if phone:
                        update_fields.append("phone = ?")
                        update_values.append(phone)
                    
                    # Добавляем user_id для условия WHERE
                    update_values.append(user_id)
                    
                    if update_fields:
                        query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
                        users_cursor.execute(query, update_values)
                
                users_conn.commit()
        except Exception as e:
            logging.error(f"Ошибка при регистрации/обновлении данных пользователя {user_id}: {e}")

def get_total_users():
    with users_conn:
        users_cursor.execute('SELECT COUNT(*) FROM users')
        total = users_cursor.fetchone()[0]
    return total

def get_active_users_today():
    # Используем московское время для проверки активности за сегодня
    msk_time = datetime.now() + timedelta(hours=3)
    today = msk_time.strftime('%Y-%m-%d')
    with users_conn:
        users_cursor.execute('SELECT COUNT(*) FROM users WHERE last_seen LIKE ?', (f'{today}%',))
        active = users_cursor.fetchone()[0]
    return active

# Храним данные пользователей
user_sessions = {}
user_data = {}
user_chat_history = {}
user_messages = {}
user_task_data = {}
# Храним список пользователей
users = set()

# Определяем списки тем для алгебры и геометрии
ALGEBRA_THEMES = [
    ("Теория вероятностей", "probability"),
    ("ФСУ", "fsu"),
    ("Квадратные уравнения", "quadratic"),
    ("Степени", "powers"),
    ("Корни", "roots"),
    ("Производные", "derivative"),
    ("Текстовые задачи", "wordproblem"),
    ("Тригонометрические определения", "trigonometrydefinitions"),
    ("Тригонометрические формулы", "trigonometryformulas"),
    ("Логарифмы", "logarithms"),
    ("Модули", "modules"),
    ("Функция корня", "rootfunction"),
    ("Показательная функция", "exponentialfunction"),
    ("Логарифмическая функция", "logarithmicfunction")
]
GEOMETRY_THEMES = [
    ("Окружность", "circle"),
    ("Прямоугольный треугольник", "righttriangle"),
    ("Равносторонний треугольник", "equilateraltriangle"),
    ("Равенство/Подобие", "similarity"),
    ("Ромб и Трапеция", "rhombustrapezoid"),
    ("Шестиугольник", "hexagon"),
    ("Треугольник", "triangle"),
    ("Вектор", "vector"),
    ("Стереометрия", "stereometry"),
    ("Прямая", "direct"),
    ("Парабола", "parabola"),
    ("Гипербола", "hyperbola")
]

ALGEBRA_CODES = [theme[1] for theme in ALGEBRA_THEMES]
GEOMETRY_CODES = [theme[1] for theme in GEOMETRY_THEMES]

# ================== Задачи ==================
# Функции favorites.py теперь встроены прямо в callBack.py выше

# Функция для форматирования даты из ISO-формата в читаемый вид
def format_date(timestamp, default=None):
    """
    Форматирует дату из ISO-формата в читаемый вид DD.MM.YYYY HH:MM:SS
    с учетом московского времени (UTC+3)
    
    Args:
        timestamp (str): Дата и время в ISO-формате
        default: Значение, которое возвращается при ошибке форматирования
        
    Returns:
        str: Отформатированная дата и время или default при ошибке
    """
    if not timestamp:
        return default or "Неизвестно"
        
    try:
        dt = datetime.fromisoformat(timestamp)
        # dt уже содержит МСК время (UTC+3), так как при создании его мы добавляем +3 часа
        # Не нужно прибавлять еще 3 часа
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, TypeError):
        return default or timestamp
# ================== Репетитор ==================
TUTOR_REVIEWS = [
    "https://imgur.com/zaaBUGU",
    "https://imgur.com/wdv4EAW",
    "https://imgur.com/Bj3rBZ2",
    "https://imgur.com/7ciKrv3",
    "https://imgur.com/Tu2XeFJ"
]

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"User ID: {user.id}"

def get_display_name(user_id, chat_id):
    user_id = str(user_id)  # Убедимся, что user_id — строка

    # Проверяем данные в user_data
    if user_id in user_data and "username" in user_data[user_id] and user_data[user_id]["username"]:
        return f"@{user_data[user_id]['username']}"
    elif user_id in user_data and "phone" in user_data[user_id] and user_data[user_id]["phone"]:
        return f"📞 {user_data[user_id]['phone']}"

    # Проверяем базу данных
    try:
        with users_conn:
            users_cursor.execute('SELECT username, phone FROM users WHERE user_id = ?', (user_id,))
            result = users_cursor.fetchone()
            if result:
                username, phone = result
                if username:
                    return f"@{username}"
                elif phone:
                    return f"📞 {phone}"
    except sqlite3.Error as e:
        logging.error(f"Ошибка при запросе к базе users для user_id={user_id}: {e}")

    # Пробуем получить номер телефона через API Telegram
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.user.phone_number:
            phone = chat_member.user.phone_number
            # Сохраняем номер в базу данных
            with users_conn:
                users_cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
                users_conn.commit()
            return f"📞 {phone}"
    except Exception as e:
        logging.error(f"Ошибка получения номера телефона через API для user_id={user_id}: {e}")

    # Если ничего не нашли, возвращаем ID
    return f"User ID: {user_id}"

def save_tutor_request(user_id, name, school_class, test_score, expected_price):
    try:
        with users_conn:
            # Используем московское время (UTC+3)
            msk_time = datetime.now() + timedelta(hours=3)
            timestamp = msk_time.isoformat()
            users_cursor.execute('''
                INSERT INTO tutor_requests (user_id, name, school_class, test_score, expected_price, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, school_class, test_score, expected_price, timestamp))
            users_conn.commit()
            logging.info(f"Новая заявка для user_id {user_id} сохранена.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении заявки для user_id {user_id}: {e}")

def ask_tutor_question(chat_id, user_id, message_id):
    if user_id not in user_data or "tutor_step" not in user_data[user_id]:
        logging.error(f"Нет данных для user_id={user_id} или отсутствует tutor_step")
        return

    # Сохраняем username, если он есть
    if "username" not in user_data[user_id]:
        try:
            user = bot.get_chat_member(chat_id, user_id).user
            user_data[user_id]["username"] = user.username
        except Exception as e:
            logging.error(f"Ошибка получения username для user_id={user_id}: {e}")

    # Если нет username и телефона, запрашиваем номер
    if not user_data[user_id].get("username") and "phone" not in user_data[user_id]:
        # Используем ReplyKeyboardMarkup вместо InlineKeyboardMarkup
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        contact_button = KeyboardButton(text="📞 Поделиться номером телефона", request_contact=True)
        markup.add(contact_button)
        mark = InlineKeyboardMarkup()
        mark.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
        try:
            # Отправляем сообщение с обычной клавиатурой вместо редактирования
            bot.edit_message_media(
                media=types.InputMediaPhoto(
                    photo,
                    "Мы заметили, что у вас не указан Telegram-тег. Пожалуйста, поделитесь номером телефона через кнопку ниже."
                ),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=mark  # Убираем старую клавиатуру, если была
            )
            logging.info(f"Успешно запрошен номер телефона для user_id={user_id} через ReplyKeyboardMarkup")
            # Регистрируем обработчик для контакта
            bot.register_next_step_handler_by_chat_id(chat_id, handle_contact, user_id, message_id)
        except Exception as e:
            logging.error(f"Ошибка при запросе номера телефона для user_id={user_id}: {e}")
        return

    # Остальной код с вопросами
    step = user_data[user_id]["tutor_step"]
    display_name = get_display_name(user_id, chat_id)
    questions = [
        "Как вас зовут?",
        "В каком классе вы учитесь?",
        "Писали ли вы пробники? Если да, то на какой балл?",
        "Какую цену вы ожидаете за занятие?"
    ]

    if step < len(questions):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
        try:
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, questions[step]),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            bot.register_next_step_handler_by_chat_id(chat_id, process_tutor_answer, user_id, message_id)
            logging.info(f"Вопрос '{questions[step]}' отправлен для {display_name}")
        except Exception as e:
            logging.error(f"Ошибка при отправке вопроса для user_id={user_id}: {e}")
    else:
        answers = user_data[user_id]["tutor_answers"]
        try:
            save_tutor_request(
                user_id,
                answers["name"],
                answers["school_class"],
                answers["test_score"],
                answers["expected_price"]
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, "Заявка успешно отправлена!"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            logging.info(f"Заявка успешно отправлена для {display_name}")
            del user_data[user_id]
        except Exception as e:
            logging.error(f"Ошибка при сохранении заявки для user_id={user_id}: {e}")
def handle_contact(message, user_id, message_id):
    chat_id = message.chat.id
    
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)

    if message.contact is None:
        logging.error(f"Пользователь {user_id} не поделился контактом")
        bot.send_message(chat_id, "Пожалуйста, поделитесь номером телефона через кнопку.")
        return

    if user_id not in user_data:
        user_data[user_id] = {"tutor_step": 0, "tutor_answers": {}}

    # Сохраняем номер телефона
    phone = message.contact.phone_number
    user_data[user_id]["phone"] = phone
    register_user(user_id, message.from_user.username, phone)  # Передаём номер телефона в register_user
    logging.info(f"Получен номер телефона для user_id={user_id}: {phone}")

    # Удаляем сообщение с кнопкой
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение с кнопкой для user_id={user_id}: {e}")

    # Переходим к первому вопросу
    ask_tutor_question(chat_id, user_id, message_id)

def process_tutor_answer(message, user_id, message_id):
    chat_id = message.chat.id
    
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    if user_id not in user_data or "tutor_step" not in user_data[user_id]:
        return

    if "username" not in user_data[user_id]:
        user_data[user_id]["username"] = message.from_user.username

    step = user_data[user_id]["tutor_step"]
    display_name = get_display_name(user_id, chat_id)
    user_answer = message.text.strip()

    if user_answer.startswith('/'):
        bot.send_message(chat_id, "Пожалуйста, введи корректный ответ, а не команду!")
        bot.register_next_step_handler_by_chat_id(chat_id, process_tutor_answer, user_id, message_id)
        logging.warning(f"{display_name} ввёл команду '{user_answer}' вместо ответа")
        return

    if step == 0:
        user_data[user_id]["tutor_answers"]["name"] = user_answer
    elif step == 1:
        user_data[user_id]["tutor_answers"]["school_class"] = user_answer
    elif step == 2:
        user_data[user_id]["tutor_answers"]["test_score"] = user_answer
    elif step == 3:
        user_data[user_id]["tutor_answers"]["expected_price"] = user_answer

    logging.info(f"{display_name} ответил на шаг {step}: '{user_answer}'")
    user_data[user_id]["tutor_step"] += 1

    try:
        bot.delete_message(chat_id, message.message_id)
    except telebot.apihelper.ApiTelegramException as e:
        logging.warning(f"Не удалось удалить сообщение для {display_name}: {e}")

    ask_tutor_question(chat_id, user_id, message_id)

def finish_tutor_questions(chat_id, user_id, message_id):
    if user_id not in user_data or "tutor_answers" not in user_data[user_id]:
        bot.send_message(chat_id, "Ошибка: данные не найдены.")
        logging.error(f"Данные для User ID: {user_id} не найдены в user_data")
        return

    answers = user_data[user_id]["tutor_answers"]
    display_name = get_display_name(user_id, chat_id)
    # Используем московское время (UTC+3)
    msk_time = datetime.now() + timedelta(hours=3)
    timestamp = msk_time.isoformat()

    try:
        with users_conn:
            users_cursor.execute('''
                INSERT OR REPLACE INTO tutor_requests (user_id, name, school_class, test_score, expected_price, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, answers.get("name", ""), answers.get("school_class", ""),
                  answers.get("test_score", ""), answers.get("expected_price", ""), timestamp))
            users_conn.commit()
        logging.info(f"Новая заявка для {display_name} сохранена в базе данных")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении заявки для {display_name}: {e}")
        bot.send_message(chat_id, "Ошибка при сохранении заявки. Попробуйте снова.")
        return

    text = "✅ Заявка сохранена!\n\nМы с вами свяжемся!"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Новая заявка", callback_data="tutor_call"))
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
    bot.edit_message_media(
        media=types.InputMediaPhoto(photo, text),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

    admin_chat_id = 1035828828
    notification_text = (
        f"📊 Новая заявка от {display_name}\n"
        f"Имя: {answers.get('name', 'Не указано')}\n"
        f"Класс: {answers.get('school_class', 'Не указано')}\n"
        f"Балл: {answers.get('test_score', 'Не указано')}\n"
        f"Цена: {answers.get('expected_price', 'Не указано')}\n"
        f"Время: {timestamp}"
    )

    try:
        bot.send_message(admin_chat_id, notification_text, timeout=30)
        logging.info(f"Уведомление успешно отправлено администратору для {display_name}")
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление администратору: {e}")

    # Очищаем только временные данные репетитора, сохраняя phone и username
    if user_id in user_data:
        user_data[user_id] = {
            "username": user_data[user_id].get("username"),
            "phone": user_data[user_id].get("phone")
        }

def show_review(chat_id, user_id, message_id):
    review_index = user_data[user_id]["review_index"]
    total_reviews = len(TUTOR_REVIEWS)
    photo_url = TUTOR_REVIEWS[review_index]

    # Текст для первой картинки
    if review_index == 0:
        caption = (
            "👋🏻 Привет, меня зовут Дмитрий.\n\n"
            "За последние 6 лет я выпустил более 100 учеников и 80% из них набрали более 76 баллов на ЕГЭ.\n\n"
            "P.S: Чтобы почитать отзывы — жми на кнопку «Далее»!"
        )
    else:
        caption = None  # Для остальных отзывов текст не нужен, только изображение

    markup = InlineKeyboardMarkup()

    # Первая строка: Навигационные кнопки
    nav_buttons = []
    if review_index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data="review_prev"))
    if review_index < total_reviews - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="review_next"))
    if nav_buttons:
        markup.row(*nav_buttons)

    # Вторая строка: Оставить заявку
    markup.row(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))

    # Третья строка: Назад (в "Занятие с репетитором")
    markup.row(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo_url, caption=caption if caption else ""),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка в show_review: {e}")
# ================== Метод карточек ==================
def init_cards_db():
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        # Проверяем, существует ли таблица cards, и создаём её, если нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY,
                category TEXT,
                question_image TEXT,
                answer_image TEXT
            )
        """)
        print("✅ Таблица 'cards' создана или уже существует.")

        # Проверяем, существует ли таблица user_groups, и создаём её, если нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id INTEGER,
                group_name TEXT,
                themes TEXT,
                PRIMARY KEY (user_id, group_name)
            )
        """)
        print("✅ Таблица 'user_groups' создана или уже существует.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        conn.rollback()
    finally:
        conn.close()


def add_card(id, category, question_image, answer_image):
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cards (id, category, question_image, answer_image)
            VALUES (?, ?, ?, ?)
        """, (id, category, question_image, answer_image))
        conn.commit()
        print(
            f"✅ Карточка с ID {id} добавлена: id={id}, category={category}, question={question_image}, answer={answer_image}")
    except sqlite3.IntegrityError:
        print(f"❌ Ошибка: ID {id} уже занят!")
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении карточки: {e}")
    finally:
        conn.close()


def delete_card(card_id):
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Карточка с ID {card_id} удалена!")
            return True
        else:
            print(f"❌ Карточка с ID {card_id} не найдена!")
            return False
    except sqlite3.Error as e:
        print(f"❌ Ошибка при удалении карточки: {e}")
        return False
    finally:
        conn.close()


def clear_cards_db():
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cards")
        cursor.execute("DELETE FROM user_groups")
        conn.commit()
        print("✅ Все карточки и группы удалены из базы данных!")
    except sqlite3.Error as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")
    finally:
        conn.close()


def is_image_accessible(url):
    if not url or url == "None":
        return False
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('Content-Type', '').lower()
    except Exception as e:
        print(f"Ошибка проверки ссылки {url}: {e}")
        return False


def view_all_data():
    conn = sqlite3.connect("cards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    cards_data = cursor.fetchall()
    if not cards_data:
        print("📭 Таблица 'cards' пустая!")
    else:
        print("📊 Данные из таблицы 'cards':")
        for row in cards_data:
            print(row)

    cursor.execute("SELECT * FROM user_groups")
    groups_data = cursor.fetchall()
    if not groups_data:
        print("📭 Таблица 'user_groups' пустая!")
    else:
        print("📊 Данные из таблицы 'user_groups':")
        for row in groups_data:
            print(row)
    conn.close()


def get_cards(category=None, shuffle=False):
    conn = sqlite3.connect('cards.db', check_same_thread=False)
    cursor = conn.cursor()

    if isinstance(category, list):
        placeholders = ','.join('?' for _ in category)
        query = f"SELECT * FROM cards WHERE category IN ({placeholders})"
        params = category
    else:
        query = "SELECT * FROM cards WHERE category = ?"
        params = [category]

    if shuffle:
        query += " ORDER BY RANDOM()"

    try:
        cursor.execute(query, params)
        cards = cursor.fetchall()
        print(f"Загружено карточек: {len(cards)} для категорий {category}")
        for card in cards:
            print(f"Карточка: ID={card[0]}, category={card[1]}, question={card[2]}, answer={card[3]}")
    except sqlite3.Error as e:
        print(f"Ошибка чтения базы данных: {e}")
        cards = []
    finally:
        conn.close()
    return cards


# Функции для работы с группами в базе данных
def load_card_groups():
    global user_data
    print("Попытка загрузки групп из базы данных")
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, group_name, themes FROM user_groups")
        groups = cursor.fetchall()
        user_data = {}
        for user_id, group_name, themes in groups:
            user_id = str(user_id)  # Преобразуем в строку для единообразия
            if user_id not in user_data:
                user_data[user_id] = {"selected_themes": [], "card_groups": {}}
            # Декодируем строку themes в список
            user_data[user_id]["card_groups"][group_name] = json.loads(themes)
        print(f"✅ Загружены группы: {user_data}")
    except sqlite3.Error as e:
        print(f"⚠️ Ошибка загрузки групп из базы данных: {e}")
        user_data = {}
    finally:
        conn.close()
    print(f"Текущий user_data после загрузки: {user_data}")


def save_card_groups(user_id=None):
    print("Попытка сохранить группы в базу данных")
    conn = sqlite3.connect("cards.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        # Удаляем старые записи для данного пользователя, если указан user_id
        if user_id is not None:
            cursor.execute("DELETE FROM user_groups WHERE user_id = ?", (user_id,))
        # Сохраняем новые данные
        for uid, data in user_data.items():
            if "card_groups" in data:
                for group_name, themes in data["card_groups"].items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_groups (user_id, group_name, themes)
                        VALUES (?, ?, ?)
                    """, (uid, group_name, json.dumps(themes)))
        conn.commit()
        print(f"✅ Группы сохранены для пользователей: {list(user_data.keys())}")
    except sqlite3.Error as e:
        print(f"⚠️ Ошибка сохранения групп в базу данных: {e}")
        conn.rollback()
    finally:
        conn.close()


# Инициализация базы данных и добавление карточек
# load_card_groups() вызывается в main.py через усовершенствованную функцию load_user_data()
init_cards_db()
# Алгебра
# Теория вероятностей
add_card(36, "probability", "https://i.imgur.com/H7eEwyK.jpeg", "https://i.imgur.com/b7FRGYL.jpeg")
add_card(37, "probability", "https://i.imgur.com/O4f0beM.jpeg", "https://i.imgur.com/QYMZigc.jpeg")
# ФСУ
add_card(38, "fsu", "https://i.imgur.com/HjiIqPu.jpeg", "https://i.imgur.com/Ata11FV.jpeg")
add_card(39, "fsu", "https://i.imgur.com/fJkHTm0.jpeg", "https://i.imgur.com/3fQrnZo.jpeg")
add_card(40, "fsu", "https://i.imgur.com/peVgQkO.jpeg", "https://i.imgur.com/HdCUo3s.jpeg")
add_card(41, "fsu", "https://i.imgur.com/8AHZw8n.jpeg", "https://i.imgur.com/D9ZcVLd.jpeg")
add_card(42, "fsu", "https://i.imgur.com/aa0Nuw8.jpeg", "https://i.imgur.com/NQnP8pU.jpeg")
# Квадратные уравнения
add_card(43, "quadratic", "https://i.imgur.com/OqY1Pjv.jpeg", "https://i.imgur.com/9hGF0CG.jpeg")
# Степени
add_card(47, "powers", "https://i.imgur.com/SyM1U2Z.jpeg", "https://i.imgur.com/1dXhPyb.jpeg")
add_card(48, "powers", "https://i.imgur.com/WBUhAD3.jpeg", "https://i.imgur.com/gsc25zE.jpeg")
add_card(49, "powers", "https://i.imgur.com/lFjVI60.jpeg", "https://i.imgur.com/OBlZLEd.jpeg")
add_card(50, "powers", "https://i.imgur.com/gpMLq0G.jpeg", "https://i.imgur.com/JbtwsAh.jpeg")
add_card(51, "powers", "https://i.imgur.com/vucgyxZ.jpeg", "https://i.imgur.com/YdOFXpO.jpeg")
add_card(52, "powers", "https://i.imgur.com/gofxbd5.jpeg", "https://i.imgur.com/5wgZtLS.jpeg")
add_card(53, "powers", "https://i.imgur.com/bCN1sGa.jpeg", "https://i.imgur.com/8ze2qT0.jpeg")
add_card(54, "powers", "https://i.imgur.com/Y7Vgs1S.jpeg", "https://i.imgur.com/eueiXJ1.jpeg")
# Корни
add_card(55, "roots", "https://i.imgur.com/k6gnZaw.jpeg", "https://i.imgur.com/eHs0fxg.jpeg")
add_card(56, "roots", "https://i.imgur.com/veIy6fr.jpeg", "https://i.imgur.com/WT4YTQq.jpeg")
add_card(57, "roots", "https://i.imgur.com/4gSEvla.jpeg", "https://i.imgur.com/00YYYYx.jpeg")
add_card(58, "roots", "https://i.imgur.com/biDoYma.jpeg", "https://i.imgur.com/ptpxXfk.jpeg")
add_card(59, "roots", "https://i.imgur.com/oOqDcbo.jpeg", "https://i.imgur.com/eYKlKee.jpeg")
add_card(60, "roots", "https://i.imgur.com/WIHaIDY.jpeg", "https://i.imgur.com/shijFSJ.jpeg")
# Тригонометрические определения
add_card(61, "trigonometrydefinitions", "https://i.imgur.com/OFpwGwD.jpeg", "https://i.imgur.com/7EpztRr.jpeg")
add_card(62, "trigonometrydefinitions", "https://i.imgur.com/p3U6Gyz.jpeg", "https://i.imgur.com/G2OaBV2.jpeg")
add_card(63, "trigonometrydefinitions", "https://i.imgur.com/Nky6XbH.jpeg", "https://i.imgur.com/gVMOZmH.jpeg")
add_card(64, "trigonometrydefinitions", "https://i.imgur.com/Bt0v1aE.jpeg", "https://i.imgur.com/8lW2duu.jpeg")
# Тригонометрические формулы
add_card(65, "trigonometryformulas", "https://i.imgur.com/vp3bPCp.jpeg", "https://i.imgur.com/sbcjT0L.jpeg")
add_card(66, "trigonometryformulas", "https://i.imgur.com/ssZT02P.png", "https://i.imgur.com/4wHR786.png")
add_card(67, "trigonometryformulas", "https://i.imgur.com/DHZSqmz.jpeg", "https://i.imgur.com/ylniISM.jpeg")
add_card(68, "trigonometryformulas", "https://i.imgur.com/GMClooA.png", "https://i.imgur.com/T1Sg075.png")
add_card(69, "trigonometryformulas", "https://i.imgur.com/LukvGDS.jpeg", "https://i.imgur.com/0QHpL5Z.png")
add_card(70, "trigonometryformulas", "https://i.imgur.com/RRkX3jC.jpeg", "https://i.imgur.com/5BAUlrP.png")
add_card(71, "trigonometryformulas", "https://i.imgur.com/hq2SQVk.jpeg", "https://i.imgur.com/koilgLa.jpeg")
add_card(72, "trigonometryformulas", "https://i.imgur.com/TzqU1UF.jpeg", "https://i.imgur.com/6pSFtF1.jpeg")
add_card(73, "trigonometryformulas", "https://i.imgur.com/g7ODfI7.jpeg", "https://i.imgur.com/EVYr47A.jpeg")
add_card(74, "trigonometryformulas", "https://i.imgur.com/e5bZRIi.jpeg", "https://i.imgur.com/xI4HZdR.jpeg")
add_card(75, "trigonometryformulas", "https://i.imgur.com/1lPYHhD.jpeg", "https://i.imgur.com/u7FFyC2.jpeg")
add_card(76, "trigonometryformulas", "https://i.imgur.com/OvyYJN3.jpeg", "https://i.imgur.com/vsCu8mw.jpeg")
# Логарифмы
add_card(77, "logarithms", "https://i.imgur.com/KdSLggi.jpeg", "https://i.imgur.com/e13xn5s.jpeg")
add_card(78, "logarithms", "https://i.imgur.com/tvNTnRw.jpeg", "https://i.imgur.com/dKSsia2.jpeg")
add_card(79, "logarithms", "https://i.imgur.com/vYOHJYx.jpeg", "https://i.imgur.com/SmarEaL.jpeg")
add_card(80, "logarithms", "https://i.imgur.com/Hpe9ceu.jpeg", "https://i.imgur.com/EEWMyGk.jpeg")
add_card(81, "logarithms", "https://i.imgur.com/dT5quyi.jpeg", "https://i.imgur.com/DBfUrja.jpeg")
add_card(82, "logarithms", "https://i.imgur.com/Egf8JQE.jpeg", "https://i.imgur.com/SflknHY.jpeg")
add_card(83, "logarithms", "https://i.imgur.com/LZRD2BS.jpeg", "https://i.imgur.com/mvjvRTf.jpeg")
add_card(84, "logarithms", "https://i.imgur.com/5NVY8sE.jpeg", "https://i.imgur.com/UxSWsp8.jpeg")
add_card(85, "logarithms", "https://i.imgur.com/KSFpIJJ.jpeg", "https://i.imgur.com/xeOWIUh.jpeg")
# Модули
add_card(86, "modules", "https://i.imgur.com/gFVIK86.jpeg", "https://i.imgur.com/Cer9t0c.jpeg")
add_card(87, "modules", "https://i.imgur.com/GkCpuoh.jpeg", "https://i.imgur.com/G4iST7X.jpeg")
add_card(88, "modules", "https://i.imgur.com/Uvw51TH.jpeg", "https://i.imgur.com/B8LQVOI.jpeg")
# Производные
add_card(89, "derivative", "https://i.imgur.com/9Jx0Zj1.jpeg", "https://i.imgur.com/ti38YhM.jpeg")
add_card(90, "derivative", "https://i.imgur.com/sEz4xTM.jpeg", "https://i.imgur.com/NdCSlJr.jpeg")
add_card(91, "derivative", "https://i.imgur.com/E3oQwfy.jpeg", "https://i.imgur.com/PcLyTBU.jpeg")
add_card(92, "derivative", "https://i.imgur.com/jMn3VBh.jpeg", "https://i.imgur.com/BlV5b8t.jpeg")
add_card(93, "derivative", "https://i.imgur.com/4fdzZws.jpeg", "https://i.imgur.com/0T0hleh.jpeg")
# Текстовые задачи
add_card(94, "wordproblem", "https://i.imgur.com/LrpPmiG.jpeg", "https://i.imgur.com/sgTp9NW.jpeg")
add_card(95, "wordproblem", "https://i.imgur.com/o5XKJJf.jpeg", "https://i.imgur.com/b6QuUNz.jpeg")
add_card(96, "wordproblem", "https://i.imgur.com/F7lHOiF.jpeg", "https://i.imgur.com/OjXPfON.jpeg")
add_card(97, "wordproblem", "https://i.imgur.com/S4JPG6e.jpeg", "https://i.imgur.com/PrvwNwf.jpeg")
add_card(98, "wordproblem", "https://i.imgur.com/39VHfc3.jpeg", "https://i.imgur.com/hHucJgd.jpeg")
add_card(99, "wordproblem", "https://i.imgur.com/FKd3CMf.jpeg", "https://i.imgur.com/UlyTZZb.jpeg")
# Функция корня
add_card(113, "rootfunction", "https://i.imgur.com/YhbsBdL.jpeg", "https://i.imgur.com/JInSNDw.jpeg")
# Показательная функция
add_card(114, "exponentialfunction", "https://i.imgur.com/UQHTQeA.jpeg", "https://i.imgur.com/7AyDiHc.jpeg")
add_card(115, "exponentialfunction", "https://i.imgur.com/gP9TPR9.jpeg", "https://i.imgur.com/H9LHpNs.jpeg")
add_card(116, "exponentialfunction", "https://i.imgur.com/CxbOGCV.jpeg", "https://i.imgur.com/IKKqiVN.jpeg")
add_card(117, "exponentialfunction", "https://i.imgur.com/Z01pCtC.jpeg", "https://i.imgur.com/wTjvTwo.jpeg")
add_card(118, "exponentialfunction", "https://i.imgur.com/1c3ZRTp.jpeg", "https://i.imgur.com/aAk9Ytf.jpeg")
# Логарифмическая функция
add_card(119, "logarithmicfunction", "https://i.imgur.com/sHrW0Lr.jpeg", "https://i.imgur.com/FDicEwE.jpeg")
add_card(120, "logarithmicfunction", "https://i.imgur.com/jGWCsfv.jpeg", "https://i.imgur.com/HRksM4N.jpeg")
add_card(121, "logarithmicfunction", "https://i.imgur.com/AGeMvm9.jpeg", "https://i.imgur.com/F4DDsrf.jpeg")
add_card(122, "logarithmicfunction", "https://i.imgur.com/pfqLBds.jpeg", "https://i.imgur.com/aQsGU1I.jpeg")
add_card(123, "logarithmicfunction", "https://i.imgur.com/U4XtgRX.jpeg", "https://i.imgur.com/z2LiDrG.jpeg")

# Геометрия
# Окружность
add_card(1, "circle", "https://i.imgur.com/7o21EEJ.jpeg", "https://i.imgur.com/W8DPEKb.jpeg")
add_card(2, "circle", "https://i.imgur.com/Y8NAFoa.jpeg", "https://i.imgur.com/nf7Qmd8.jpeg")
add_card(3, "circle", "https://i.imgur.com/Ov8bheW.jpeg", "https://i.imgur.com/VvzOf9o.jpeg")
add_card(4, "circle", "https://i.imgur.com/epdrfUO.jpeg", "https://i.imgur.com/VLbulJj.jpeg")
add_card(5, "circle", "https://i.imgur.com/FfkKQhm.jpeg", "https://i.imgur.com/AStLLBd.jpeg")
# Прямоугольный треугольник
add_card(9, "righttriangle", "https://i.imgur.com/jIDKP3d.jpeg", "https://i.imgur.com/SzWrTBR.jpeg")
add_card(10, "righttriangle", "https://i.imgur.com/CIzUwm5.jpeg", "https://i.imgur.com/gIjHIwp.jpeg")
add_card(11, "righttriangle", "https://i.imgur.com/d3NeDub.jpeg", "https://i.imgur.com/3j1jkwc.jpeg")
# Равносторонний треугольник
add_card(13, "equilateraltriangle", "https://i.imgur.com/GNfw2y2.jpeg", "https://i.imgur.com/GsrZKaF.jpeg")
add_card(14, "equilateraltriangle", "https://i.imgur.com/EAASCzD.jpeg", "https://i.imgur.com/ph8QUI5.jpeg")
add_card(15, "equilateraltriangle", "https://i.imgur.com/c69hlGc.jpeg", "https://i.imgur.com/B5OSyst.jpeg")
add_card(16, "equilateraltriangle", "https://i.imgur.com/i8a9jsn.jpeg", "https://i.imgur.com/Snv45Rz.jpeg")
# Равенство/Подобие
add_card(17, "similarity", "https://i.imgur.com/aTLFn8W.jpeg", "https://i.imgur.com/OF0dN15.jpeg")
add_card(18, "similarity", "https://i.imgur.com/7FfgCk6.jpeg", "https://i.imgur.com/1irQV4N.jpeg")
# Ромб и Трапеция
add_card(19, "rhombustrapezoid", "https://i.imgur.com/NWrWSD8.jpeg", "https://i.imgur.com/bHwFInE.jpeg")
add_card(20, "rhombustrapezoid", "https://i.imgur.com/w3ys1my.jpeg", "https://i.imgur.com/2s2D3xG.jpeg")
add_card(21, "rhombustrapezoid", "https://i.imgur.com/P2Xx8S2.jpeg", "https://i.imgur.com/AygQpCv.jpeg")
# Равносторонний шестиугольник
add_card(22, "hexagon", "https://i.imgur.com/hdiWXJO.jpeg", "https://i.imgur.com/ums0XaV.jpeg")
add_card(23, "hexagon", "https://i.imgur.com/GqiEjSc.jpeg", "https://i.imgur.com/ddZpzTf.jpeg")
add_card(24, "hexagon", "https://i.imgur.com/dniTMEc.jpeg", "https://i.imgur.com/jMZvTo2.jpeg")
add_card(25, "hexagon", "https://i.imgur.com/MNZXkLs.jpeg", "https://i.imgur.com/kTi7XYA.jpeg")
# Треугольник
add_card(26, "triangle", "https://i.imgur.com/3mzOeTW.jpeg", "https://i.imgur.com/lYrtISE.jpeg")
add_card(27, "triangle", "https://i.imgur.com/fwg4sTm.jpeg", "https://i.imgur.com/804kiIR.jpeg")
add_card(28, "triangle", "https://i.imgur.com/Ws9CdLG.jpeg", "https://i.imgur.com/mPOyrJx.jpeg")
add_card(29, "triangle", "https://i.imgur.com/ZhcjU8E.jpeg", "https://i.imgur.com/i6Rp4I7.jpeg")
add_card(30, "triangle", "https://i.imgur.com/rJ1kBoa.jpeg", "https://i.imgur.com/7UrsY2h.jpeg")
add_card(31, "triangle", "https://i.imgur.com/OhtEsap.jpeg", "https://i.imgur.com/Mnj31xP.jpeg")
add_card(32, "triangle", "https://i.imgur.com/GZA4J4T.jpeg", "https://i.imgur.com/13rIhlL.jpeg")
# Вектор
add_card(33, "vector", "https://i.imgur.com/CmZoeHy.jpeg", "https://i.imgur.com/jV8irGk.jpeg")
add_card(34, "vector", "https://i.imgur.com/6ao81ll.jpeg", "https://i.imgur.com/Ek9XFTi.jpeg")
add_card(35, "vector", "https://i.imgur.com/amkZPOX.jpeg", "https://i.imgur.com/NA5h4Zw.jpeg")
# Стереометрия
add_card(140, "stereometry", "https://i.imgur.com/nnjf5xb.jpeg", "https://i.imgur.com/yWw7DV5.jpeg")
add_card(141, "stereometry", "https://i.imgur.com/QmkkMuR.jpeg", "https://i.imgur.com/TIEz29u.jpeg")
add_card(142, "stereometry", "https://i.imgur.com/J0OIBvv.jpeg", "https://i.imgur.com/A4VHCMr.jpeg")
add_card(143, "stereometry", "https://i.imgur.com/47z7amI.jpeg", "https://i.imgur.com/US1mk6X.jpeg")
add_card(144, "stereometry", "https://i.imgur.com/L1Vs1qs.jpeg", "https://i.imgur.com/8AAVjUb.jpeg")
add_card(145, "stereometry", "https://i.imgur.com/wGfYadc.jpeg", "https://i.imgur.com/yCIvqcF.jpeg")
add_card(146, "stereometry", "https://i.imgur.com/hFqD8Rp.jpeg", "https://i.imgur.com/e5CjWdd.jpeg")
# Прямая
add_card(100, "direct", "https://i.imgur.com/PI1wfN3.jpeg", "https://i.imgur.com/AREIHxM.png")
add_card(101, "direct", "https://i.imgur.com/RfuQeQI.jpeg", "https://i.imgur.com/dwTKc3Y.jpeg")
# Парабола
add_card(102, "parabola", "https://i.imgur.com/y8uF2Hd.jpeg", "https://i.imgur.com/hP6NPCE.jpeg")
add_card(103, "parabola", "https://i.imgur.com/d7FejpK.jpeg", "https://i.imgur.com/0wfF32F.jpeg")
add_card(104, "parabola", "https://i.imgur.com/ijiIR7x.jpeg", "https://i.imgur.com/87lW0Nu.jpeg")
add_card(105, "parabola", "https://i.imgur.com/UZFRTMk.jpeg", "https://i.imgur.com/5itVKZd.jpeg")
add_card(106, "parabola", "https://i.imgur.com/DPcfVM9.jpeg", "https://i.imgur.com/dUv8RmI.jpeg")
add_card(107, "parabola", "https://i.imgur.com/QZAXdvA.jpeg", "https://i.imgur.com/nl4gWAd.jpeg")
# Гипербола
add_card(108, "hyperbola", "https://i.imgur.com/7fv1OFz.jpeg", "https://i.imgur.com/TUhkYne.jpeg")
add_card(109, "hyperbola", "https://i.imgur.com/TAKDnII.jpeg", "https://i.imgur.com/GCoPwfw.jpeg")
add_card(110, "hyperbola", "https://i.imgur.com/L4XrHuC.jpeg", "https://i.imgur.com/lfgKtwb.jpeg")
add_card(111, "hyperbola", "https://i.imgur.com/0hpkGYL.jpeg", "https://i.imgur.com/oLvrrU8.jpeg")
add_card(112, "hyperbola", "https://i.imgur.com/EXSjtks.jpeg", "https://i.imgur.com/m1RR74f.jpeg")


@bot.callback_query_handler(func=lambda call: call.data == "cards_method_call" or call.data == "cards_method_back")
def return_to_cards_menu(call):
    text = (
            "Способ быстро выучить и повторить материал. Здесь — удобный формат запоминания через карточки.")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    user_id = str(call.from_user.id)  # Убедимся, что user_id — строка
    
    # Просмотрим данные в базе
    try:
        conn = sqlite3.connect("cards.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, group_name, themes FROM user_groups WHERE user_id = ?", (user_id,))
        groups = cursor.fetchall()
        
        # Если у пользователя нет ключа card_groups, инициализируем его
        if user_id not in user_data:
            user_data[user_id] = {}
        if "card_groups" not in user_data[user_id]:
            user_data[user_id]["card_groups"] = {}
            
        # Добавляем группы из БД, если их нет в объекте user_data
        for _, group_name, themes in groups:
            if group_name not in user_data[user_id]["card_groups"]:
                user_data[user_id]["card_groups"][group_name] = json.loads(themes)
                print(f"Добавлена группа {group_name} из БД для пользователя {user_id}")
                
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка при получении групп из БД: {e}")
        
    print(f"Проверка групп для пользователя {user_id}: {user_data.get(user_id, {}).get('card_groups', {})}")
    if user_id in user_data and "card_groups" in user_data[user_id]:
        print(f"Найдены группы для пользователя {user_id}: {user_data[user_id]['card_groups'].keys()}")
        for group_name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы: {group_name}")
            markup.add(
                InlineKeyboardButton(group_name, callback_data=f"select_group_{group_name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{group_name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo_cards, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню карточек: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_cards")
def select_cards_menu(call):
    text = "Выбери раздел для выбора тем карточек:"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Алгебра", callback_data="select_algebra"),
        InlineKeyboardButton("Геометрия", callback_data="select_geometry")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования начального меню выбора тем: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_algebra")
def select_algebra_menu(call):
    text = "Выбери темы для карточек из раздела Алгебра (можно выбрать несколько):"
    markup = InlineKeyboardMarkup(row_width=2)

    user_id = str(call.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "selected_themes" not in user_data[user_id]:
        user_data[user_id]["selected_themes"] = []
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    selected_themes = user_data[user_id]["selected_themes"]

    for theme_name, theme_code in ALGEBRA_THEMES:
        prefix = "✅ " if theme_code in selected_themes else ""
        callback = f"toggle_theme_{theme_code}"
        print(f"Формируем кнопку: {theme_name}, callback_data={callback}")
        markup.add(InlineKeyboardButton(f"{prefix}{theme_name}", callback_data=callback))

    markup.add(InlineKeyboardButton("☑️ Готово", callback_data="finish_selection"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню алгебры: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "select_geometry")
def select_geometry_menu(call):
    text = "Выбери темы для карточек из раздела Геометрия (можно выбрать несколько):"
    markup = InlineKeyboardMarkup(row_width=2)

    user_id = str(call.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "selected_themes" not in user_data[user_id]:
        user_data[user_id]["selected_themes"] = []
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    selected_themes = user_data[user_id]["selected_themes"]

    for theme_name, theme_code in GEOMETRY_THEMES:
        prefix = "✅ " if theme_code in selected_themes else ""
        callback = f"toggle_theme_{theme_code}"
        print(f"Формируем кнопку: {theme_name}, callback_data={callback}")
        markup.add(InlineKeyboardButton(f"{prefix}{theme_name}", callback_data=callback))

    markup.add(InlineKeyboardButton("☑️ Готово", callback_data="finish_selection"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню геометрии: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_theme_"))
def toggle_theme(call):
    theme_code = call.data.split("_")[2]
    user_id = str(call.from_user.id)

    print(f"Обработка toggle_theme: theme_code={theme_code}")

    if theme_code in user_data[user_id]["selected_themes"]:
        user_data[user_id]["selected_themes"].remove(theme_code)
        print(f"Тема {theme_code} снята с выбора")
    else:
        user_data[user_id]["selected_themes"].append(theme_code)
        print(f"Тема {theme_code} выбрана")

    if theme_code in ALGEBRA_CODES:
        print(f"Тема {theme_code} относится к алгебре")
        select_algebra_menu(call)
    elif theme_code in GEOMETRY_CODES:
        print(f"Тема {theme_code} относится к геометрии")
        select_geometry_menu(call)
    else:
        print(f"Ошибка: тема {theme_code} не найдена в списках ALGEBRA_CODES или GEOMETRY_CODES")
        text = "Ошибка: неизвестная тема. Выбери раздел заново:"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Алгебра", callback_data="select_algebra"),
            InlineKeyboardButton("Геометрия", callback_data="select_geometry")
        )
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при неизвестной теме: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "finish_selection")
def finish_selection(call):
    user_id = str(call.from_user.id)
    selected_themes = user_data.get(user_id, {}).get("selected_themes", [])

    if not selected_themes:
        bot.answer_callback_query(call.id, "Выбери хотя бы одну тему!", show_alert=True)
        return

    text = "📝 Введи название для вашей группы карточек:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования ввода названия группы: {e}")

    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_group_name, user_id,
                                              call.message.message_id)


def process_group_name(message, user_id, original_message_id):
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    group_name = message.text.strip()
    if not group_name:
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, "Название не может быть пустым! Попробуйте снова."),
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="select_cards"))
            )
            bot.register_next_step_handler_by_chat_id(message.chat.id, process_group_name, user_id, original_message_id)
        except Exception as e:
            print(f"Ошибка редактирования при пустом названии: {e}")
        return

    if user_id not in user_data:
        user_data[user_id] = {"selected_themes": [], "card_groups": {}}
    elif "card_groups" not in user_data[user_id]:
        user_data[user_id]["card_groups"] = {}

    user_data[user_id]["card_groups"][group_name] = user_data[user_id]["selected_themes"].copy()
    user_data[user_id]["selected_themes"] = []

    save_card_groups(user_id)  # Сохраняем группы для конкретного пользователя

    text = ("Способ быстро выучить и повторить материал. Здесь — удобный формат запоминания через карточки.")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=message.chat.id,
            message_id=original_message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после ввода названия группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_"))
def confirm_delete_group(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    text = f"Вы точно хотите удалить группу '{group_name}'?"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Да", callback_data=f"delete_yes_{group_name}"),
        InlineKeyboardButton("Нет", callback_data=f"delete_no_{group_name}")
    )

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования подтверждения удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_yes_"))
def delete_group_yes(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    if user_id in user_data and "card_groups" in user_data[user_id] and group_name in user_data[user_id]["card_groups"]:
        del user_data[user_id]["card_groups"][group_name]
        save_card_groups(user_id)  # Сохраняем обновлённые группы для конкретного пользователя
        bot.answer_callback_query(call.id, f"Группа '{group_name}' удалена!", show_alert=True)

    text = ("Способ быстро выучить и повторить материал. Здесь — удобный формат запоминания через карточки.")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if user_id in user_data and "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню после удаления: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после подтверждения удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_no_"))
def delete_group_no(call):
    group_name = call.data.split("_", 2)[2]
    user_id = str(call.from_user.id)

    text = ("Способ быстро выучить и повторить материал. Здесь — удобный формат запоминания через карточки.")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Выбрать карточки", callback_data="select_cards"))
    if user_id in user_data and "card_groups" in user_data[user_id]:
        for name in user_data[user_id]["card_groups"]:
            print(f"Добавляем кнопку для группы в меню после отмены удаления: {name}")
            markup.add(
                InlineKeyboardButton(name, callback_data=f"select_group_{name}"),
                InlineKeyboardButton("🗑️", callback_data=f"confirm_delete_{name}")
            )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню после отмены удаления группы: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_group_"))
def select_group(call):
    group_name = call.data.split("_", 2)[2]
    text = f"Вы выбрали группу '{group_name}'. Выбери порядок выполнения:"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔢 Подряд", callback_data=f"order_sequential_group_{group_name}"),
        InlineKeyboardButton("🔁 Вперемежку", callback_data=f"order_mixed_group_{group_name}")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования выбора порядка: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_group_order(call):
    data = call.data.split("_")
    order_type = data[1]
    group_name = "_".join(data[3:])
    user_id = str(call.from_user.id)

    if user_id not in user_data or "card_groups" not in user_data[user_id] or group_name not in user_data[user_id][
        "card_groups"]:
        text = "Ошибка! Группа не найдена. Попробуйте создать новую группу."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии группы: {e}")
        return

    shuffle = (order_type == "mixed")
    categories = user_data[user_id]["card_groups"][group_name]
    cards = get_cards(category=categories, shuffle=shuffle)

    if not cards:
        text = "Ошибка! Карточки не найдены для выбранных тем."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии карточек: {e}")
        return

    user_data[user_id] = {
        "cards": cards,
        "current_index": 0,
        "wrong_cards": [],
        "last_message_id": call.message.message_id,
        "card_groups": user_data[user_id].get("card_groups", {})
    }
    send_card(call.message.chat.id)


def send_card(chat_id, message_id=None):
    session = user_data.get(str(chat_id))
    if not session:
        text = "Ошибка! Попробуйте начать заново."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=session["last_message_id"] if message_id is None and session else message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии сессии: {e}")
        return

    cards = session["cards"]
    current_index = session["current_index"]

    if current_index >= len(cards):
        show_repeat_menu(chat_id)
        return

    card = cards[current_index]
    question_image = card[2]

    if not is_image_accessible(question_image):
        print(f"Изображение недоступно: {question_image} (ID {card[0]})")
        text = f"Изображение для карточки (ID {card[0]}) недоступно. Пропускаем."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=session["last_message_id"],
                reply_markup=markup
            )
            session["current_index"] += 1
            send_card(chat_id)
        except Exception as e:
            print(f"Ошибка редактирования при недоступном изображении: {e}")
        return

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("❕ Ответил", callback_data=f"answer:{card[0]}"),
        InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back")
    )
    text = f"Вспомни формулу (карточка {current_index + 1} из {len(cards)}):"

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(question_image, text),
            chat_id=chat_id,
            message_id=session["last_message_id"],
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования карточки (ID {card[0]}): {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer"))
def process_answer(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if not session:
        return

    _, card_id = call.data.split(":")
    card = session["cards"][session["current_index"]]
    answer_image = card[3]

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Верно", callback_data=f"correct:{card[0]}"),
        InlineKeyboardButton("❌ Неверно", callback_data=f"wrong:{card[0]}")
    )
    markup.add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
    text = "Верно ли ты вспомнил?"

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(answer_image, text),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования ответа: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("correct"))
def process_correct(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session:
        session["current_index"] += 1
        send_card(chat_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("wrong"))
def process_wrong(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session:
        session["wrong_cards"].append(session["cards"][session["current_index"]])
        session["current_index"] += 1
        send_card(chat_id)


def show_repeat_menu(chat_id):
    session = user_data.get(str(chat_id))
    if not session:
        return

    if session["wrong_cards"]:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Повторить неверные", callback_data="repeat_wrong"),
            InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back")
        )
        text = "Хочешь повторить неправильные карточки?"
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
        text = "Ошибок не было или нет карточек для повторения."

    try:
        bot.edit_message_media(
            media=InputMediaPhoto(photo, text),
            chat_id=chat_id,
            message_id=session["last_message_id"],
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка редактирования меню повторения: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "repeat_wrong")
def repeat_wrong(call):
    chat_id = call.message.chat.id
    session = user_data.get(str(chat_id))
    if session and session["wrong_cards"]:
        session["cards"] = session["wrong_cards"].copy()
        session["current_index"] = 0
        session["wrong_cards"] = []
        send_card(chat_id)
    else:
        text = "Ошибок не было или нет карточек для повторения."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Выход", callback_data="cards_method_back"))
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Ошибка редактирования при отсутствии неверных карточек: {e}")


# ================== ТАЙМЕРЫ ==================
logging.basicConfig(level=logging.INFO)
user_timer_data = {}
active_timers = {}
timer_conn = sqlite3.connect('timers.db', check_same_thread=False)
timer_cursor = timer_conn.cursor()


def init_timer_db():
    # Проверяем и создаём таблицу timers с учётом возможного отсутствия старых или новых полей
    timer_cursor.execute('''
        CREATE TABLE IF NOT EXISTS timers (
            timer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            is_running BOOLEAN,
            is_paused BOOLEAN,
            start_time INTEGER,
            pause_time INTEGER,
            accumulated_time INTEGER DEFAULT 0
        )''')

    # Проверяем, существуют ли необходимые столбцы (если нет — добавляем)
    timer_cursor.execute('PRAGMA table_info(timers)')
    columns = {col[1] for col in timer_cursor.fetchall()}
    if 'start_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN start_time INTEGER')
        timer_conn.commit()
        logging.info("Столбец start_time добавлен в таблицу timers")
    if 'pause_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN pause_time INTEGER')
        timer_conn.commit()
        logging.info("Столбец pause_time добавлен в таблицу timers")
    if 'accumulated_time' not in columns:
        timer_cursor.execute('ALTER TABLE timers ADD COLUMN accumulated_time INTEGER DEFAULT 0')
        timer_conn.commit()
        logging.info("Столбец accumulated_time добавлен в таблицу timers")

    timer_cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            timer_id INTEGER,
            date TEXT,
            total_time INTEGER,
            PRIMARY KEY (timer_id, date)
        )''')
    timer_conn.commit()
    print("✅ Таблицы таймеров созданы или уже существуют!")


init_timer_db()


def get_timer_name(timer_id):
    with timer_conn:
        timer_cursor.execute("SELECT name FROM timers WHERE timer_id = ?", (timer_id,))
        result = timer_cursor.fetchone()
        return result[0] if result else None


def get_current_time(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute(
                'SELECT start_time, pause_time, is_running, is_paused, accumulated_time FROM timers WHERE timer_id = ?',
                (timer_id,))
            timer_data = cursor.fetchone()

            if not timer_data:
                logging.debug(f"Таймер {timer_id} не найден")
                return 0  # Возвращаем 0 в секундах

            start_time = timer_data[0] or 0
            pause_time = timer_data[1] or 0
            is_running = timer_data[2]
            is_paused = timer_data[3]
            accumulated_time = timer_data[4] or 0
            current_time = int(time.time())

            logging.debug(
                f"Таймер {timer_id}: start_time={start_time}, pause_time={pause_time}, is_running={is_running}, is_paused={is_paused}, accumulated_time={accumulated_time}, current_time={current_time}")

            if not is_running and not is_paused:
                logging.debug(
                    f"Таймер {timer_id} остановлен, возвращаем accumulated_time: {accumulated_time} сек для статистики")
                return accumulated_time  # Возвращаем accumulated_time для статистики при остановке
            elif is_paused:
                logging.debug(f"Таймер {timer_id} на паузе, возвращаем accumulated_time: {accumulated_time} сек")
                return accumulated_time  # Время на момент паузы
            else:
                elapsed = current_time - start_time if start_time else 0
                total_time = accumulated_time + elapsed
                logging.debug(
                    f"Таймер {timer_id} запущен, общее время: {total_time} сек (accumulated={accumulated_time}, elapsed={elapsed})")
                return total_time  # Общее время (накопленное + текущая сессия)
    except Exception as e:
        logging.error(f"Ошибка при получении текущего времени таймера {timer_id}: {e}")
        return 0


def format_timedelta_stats(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"  # Формат "ЧЧ:ММ:СС" для кнопок и статистики


def get_stats_time(timer_id, period):
    # Используем московское время (UTC+3)
    now = datetime.now() + timedelta(hours=3)
    date_query = ""
    params = ()

    if period == 'day':
        # День начинается с 00:00 по МСК
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_query = "date = ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'week':
        # Неделя начинается с понедельника 00:00 по МСК
        # now.weekday() возвращает 0 для понедельника, 1 для вторника и т.д.
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_query = "date >= ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'month':
        # Месяц начинается с 1 числа 00:00 по МСК
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        date_query = "date >= ?"
        params = (start_date.strftime('%Y-%m-%d'),)
    elif period == 'all':
        date_query = "1=1"

    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            query = f'SELECT SUM(total_time) FROM stats WHERE timer_id = ? AND {date_query}'
            cursor.execute(query, (timer_id, *params))
            stats_total_seconds = cursor.fetchone()[0] or 0
            logging.debug(f"Статистика для таймера {timer_id}, период {period}: {stats_total_seconds} сек")
            return stats_total_seconds  # Возвращаем секунды, а не timedelta
    except Exception as e:
        logging.error(f"Ошибка при получении статистики для таймера {timer_id}, период {period}: {e}")
        return 0


def show_timer_screen_1(call, timer_id, name):
    # Кнопка с временем уже убрана, оставлены только кнопки управления
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("▶️ Запустить", callback_data=f"launch_timer_{timer_id}"),
        InlineKeyboardButton("❌ Удалить", callback_data=f"delete_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton("📊 Статистика", callback_data=f"stats_menu_{timer_id}"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="timer_main"))

    caption = f"⏳ Таймер: {name}\n\n⏹ Остановлен"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_timer_screen_2(call, timer_id, name):
    current_time = get_current_time(timer_id)
    time_text = format_timedelta_stats(current_time)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("⏸ Пауза", callback_data=f"pause_timer_{timer_id}"),
        InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton(time_text, callback_data="none"))  # Кнопка с временем осталась на экране 2

    caption = f"⏳ Таймер: {name}\n\n▶️ Запущен"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_timer_screen_3(call, timer_id, name):
    current_time = get_current_time(timer_id)
    time_text = format_timedelta_stats(current_time)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("▶️ Возобновить", callback_data=f"resume_timer_{timer_id}"),
        InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
    )
    markup.row(InlineKeyboardButton(time_text, callback_data="none"))  # Кнопка с временем осталась на экране 3

    caption = f"⏳ Таймер: {name}\n\n⏸ На паузе"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана таймера {timer_id}: {e2}")


def show_stats_menu(call, timer_id):
    day_time = get_stats_time(timer_id, 'day')
    week_time = get_stats_time(timer_id, 'week')
    month_time = get_stats_time(timer_id, 'month')
    all_time = get_stats_time(timer_id, 'all')

    day_text = format_timedelta_stats(day_time)
    week_text = format_timedelta_stats(week_time)
    month_text = format_timedelta_stats(month_time)
    all_text = format_timedelta_stats(all_time)

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(f"🗓 День: {day_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 Неделя: {week_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 Месяц: {month_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton(f"🗓 За всё время: {all_text}", callback_data=f"none"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data=f"return_to_timer_{timer_id}"))  # Оставлено "Назад"

    caption = "Статистика:"
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=caption),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении меню статистики {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении меню статистики {timer_id}: {e2}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("stats_menu_"))
def handle_stats_menu(call):
    timer_id = int(call.data.split("_")[-1])
    show_stats_menu(call, timer_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("return_to_timer_"))
def handle_return_to_timer(call):
    timer_id = int(call.data.split("_")[-1])
    with timer_conn:
        timer_cursor.execute("SELECT is_running, is_paused FROM timers WHERE timer_id = ?", (timer_id,))
        status = timer_cursor.fetchone()
        if status:
            is_running, is_paused = status
            timer_name = get_timer_name(timer_id)
            if not is_running and not is_paused:
                show_timer_screen_1(call, timer_id, timer_name)
            elif is_paused:
                show_timer_screen_3(call, timer_id, timer_name)
            else:
                show_timer_screen_2(call, timer_id, timer_name)


@bot.callback_query_handler(func=lambda call: call.data == "timer_main")
def timer_main_menu(call_or_chat_id, message_id=None):
    if isinstance(call_or_chat_id, types.CallbackQuery):
        call = call_or_chat_id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.from_user.id
    else:
        chat_id = call_or_chat_id
        user_id = None

    register_user(user_id)
    markup = InlineKeyboardMarkup()
    timer_cursor.execute('SELECT name FROM timers WHERE user_id = ?', (chat_id,))
    timers = timer_cursor.fetchall()

    for timer in timers:
        markup.add(InlineKeyboardButton(timer[0], callback_data=f"select_timer_{timer[0]}"))

    markup.row(InlineKeyboardButton("Добавить таймер ➕", callback_data="add_timer"))
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    text = ("Функция для планирования учёбы. Здесь — настройка таймеров и отслеживание времени.")
    try:
        bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=InputMediaPhoto(photo_timers, caption=text),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении меню таймеров: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(photo, caption="⏳ Управление таймерами:"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении меню таймеров: {e2}")


@bot.callback_query_handler(func=lambda call: call.data == "add_timer")
def add_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    user_timer_data[user_id] = {
        "chat_id": call.message.chat.id,
        "message_id": call.message.message_id
    }

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("◀️ Назад", callback_data="timer_main"))

    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption="📝 Введи название для нового таймера:"),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при обновлении экрана добавления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption="📝 Введи название для нового таймера:"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при обновлении экрана добавления таймера: {e2}")

    bot.register_next_step_handler(call.message, process_timer_name, call.from_user.id)


def process_timer_name(message, user_id):
    name = message.text.strip()
    user_data = user_timer_data.get(user_id)
    if not user_data:
        return

    chat_id = user_data["chat_id"]
    message_id = user_data["message_id"]

    try:
        timer_cursor.execute(
            'INSERT INTO timers (user_id, name, is_running, is_paused, start_time, pause_time, accumulated_time) VALUES (?, ?, ?, ?, NULL, NULL, 0)',
            (user_id, name, False, False)
        )
        timer_conn.commit()
        # Очищаем старую статистику для нового таймера, если это новый timer_id
        timer_cursor.execute(
            'DELETE FROM stats WHERE timer_id = (SELECT timer_id FROM timers WHERE user_id = ? AND name = ?)',
            (user_id, name))
        timer_conn.commit()
        logging.info(f"Таймер создан: имя = {name}, user_id = {user_id}")

        bot.delete_message(chat_id, message.message_id)
        timer_main_menu(chat_id, message_id)
    except sqlite3.IntegrityError:
        logging.error(f"Таймер с именем {name} уже существует для другого пользователя, но это разрешено.")
        timer_cursor.execute(
            'INSERT INTO timers (user_id, name, is_running, is_paused, start_time, pause_time, accumulated_time) VALUES (?, ?, ?, ?, NULL, NULL, 0)',
            (user_id, name, False, False)
        )
        timer_conn.commit()
        # Очищаем старую статистику для нового таймера, если это новый timer_id
        timer_cursor.execute(
            'DELETE FROM stats WHERE timer_id = (SELECT timer_id FROM timers WHERE user_id = ? AND name = ?)',
            (user_id, name))
        timer_conn.commit()
        logging.info(f"Таймер создан с дублирующим именем: имя = {name}, user_id = {user_id}")

        bot.delete_message(chat_id, message.message_id)
        timer_main_menu(chat_id, message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_timer_"))
def handle_timer_selection(call):
    user_id = call.from_user.id
    register_user(user_id)
    timer_name = call.data.split("_", 2)[2]
    timer_cursor.execute("SELECT timer_id FROM timers WHERE user_id = ? AND name = ?", (call.from_user.id, timer_name))
    timer_data = timer_cursor.fetchone()

    if timer_data:
        timer_id = timer_data[0]
        show_timer_screen_1(call, timer_id, timer_name)
    else:
        try:
            bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
        except Exception as e:
            logging.error(f"Ошибка при уведомлении о таймере: {e}")
            if "ConnectionResetError" in str(e):
                time.sleep(1)
                bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление


@bot.callback_query_handler(func=lambda call: call.data.startswith("launch_timer_"))
def handle_launch_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if start_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Поток обновления запущен для таймера {timer_id}")
                # Обновляем статистику при запуске (начальное время 0)
                update_stats(timer_id, 0)
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при обработке запуска: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if start_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_2(call, timer_id, timer_name)
                        update_thread = Thread(target=update_timer_display, args=(
                        call.message.chat.id, call.message.message_id, timer_id, timer_name))
                        update_thread.daemon = True
                        update_thread.start()
                        logging.info(f"Поток обновления запущен после повторной попытки для таймера {timer_id}")
                        update_stats(timer_id, 0)
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при запуске таймера: {e2}")

def start_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            # Убедимся, что start_time всегда устанавливается корректно
            start_time = int(time.time())
            cursor.execute('''
                UPDATE timers 
                SET is_running = 1, 
                    is_paused = 0,
                    start_time = ?,
                    accumulated_time = 0,
                    pause_time = NULL
                WHERE timer_id = ?''',
                           (start_time, timer_id))
            timer_conn.commit()
            logging.debug(f"Таймер {timer_id} запущен с start_time={start_time}")
        logging.info(f"Таймер {timer_id} успешно запущен, начав с 00:00:00")
        timer_thread = Thread(target=run_timer, args=(timer_id,))
        timer_thread.daemon = True
        timer_thread.start()
        return True
    except Exception as e:
        logging.error(f"Ошибка запуска таймера: {e}")
        return False

def run_timer(timer_id):
    while True:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT is_running, is_paused FROM timers WHERE timer_id = ?', (timer_id,))
            status = cursor.fetchone()

            if not status or (not status[0] and not status[1]):
                logging.info(f"Таймер {timer_id} завершил работу")
                break

            time.sleep(1)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pause_timer_"))
def handle_pause_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if pause_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_3(call, timer_id, timer_name)
                # Обновляем статистику, используя текущее время из get_current_time
                current_time = get_current_time(timer_id)
                update_stats(timer_id, current_time)
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при паузе таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if pause_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_3(call, timer_id, timer_name)
                        current_time = get_current_time(timer_id)
                        update_stats(timer_id, current_time)
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при паузе таймера: {e2}")

def pause_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT start_time, accumulated_time, is_paused, is_running FROM timers WHERE timer_id = ?',
                           (timer_id,))
            timer_data = cursor.fetchone()
            if timer_data and timer_data[3] == 1 and timer_data[2] == 0:  # Проверяем, что таймер запущен и не на паузе
                start_time = timer_data[0]
                accumulated_time = timer_data[1] or 0
                current_time = int(time.time())
                elapsed = current_time - start_time if start_time else 0
                new_accumulated_time = accumulated_time + elapsed  # Сохраняем общее время, включая паузу

                cursor.execute('''
                    UPDATE timers 
                    SET is_paused = 1,
                        is_running = 0,
                        pause_time = ?,
                        accumulated_time = ?
                WHERE timer_id = ? AND is_running = 1''',
                               (current_time, new_accumulated_time, timer_id))
                timer_conn.commit()
                logging.debug(
                    f"Таймер {timer_id} поставлен на паузу, accumulated_time={new_accumulated_time}, elapsed={elapsed}")
            else:
                logging.warning(f"Таймер {timer_id} уже на паузе, не запущен или не найден, пропускаем обновление")
            logging.info(f"Таймер {timer_id} поставлен на паузу с временем {new_accumulated_time} секунд")
        return True
    except Exception as e:
        logging.error(f"Ошибка паузы таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_timer_"))
def handle_stop_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if stop_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_1(call, timer_id, timer_name)
                # Обновляем статистику перед сбросом, используя текущее время из get_current_time
                current_time = get_current_time(timer_id)
                # Если current_time = 0, пытаемся восстановить время, используя accumulated_time + elapsed
                if current_time == 0:
                    with timer_conn:
                        cursor = timer_conn.cursor()
                        cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?',
                                       (timer_id,))
                        timer_data = cursor.fetchone()
                        if timer_data:
                            start_time = timer_data[0] or 0
                            accumulated_time = timer_data[1] or 0
                            if start_time:
                                current_time = int(time.time()) - start_time + accumulated_time
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id}: current_time={current_time} (start_time={start_time}, accumulated_time={accumulated_time})")
                            else:
                                # Если start_time отсутствует, используем только accumulated_time
                                current_time = accumulated_time
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id} из accumulated_time: current_time={current_time}")
                            # Если всё ещё 0, используем elapsed как запасное значение
                            if current_time == 0 and start_time:
                                elapsed = int(time.time()) - start_time
                                current_time = elapsed
                                logging.debug(
                                    f"Восстановлено время для таймера {timer_id} из elapsed: current_time={current_time} (start_time={start_time})")
                # Обновляем статистику, если восстановленное время больше 0
                if current_time > 0:
                    update_stats(timer_id, current_time)
                else:
                    logging.warning(
                        f"Статистика для таймера {timer_id} не обновлена, так как восстановленное время = 0 после всех попыток")
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при остановке таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if stop_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_1(call, timer_id, timer_name)
                        current_time = get_current_time(timer_id)
                        if current_time == 0:
                            with timer_conn:
                                cursor = timer_conn.cursor()
                                cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?',
                                               (timer_id,))
                                timer_data = cursor.fetchone()
                                if timer_data:
                                    start_time = timer_data[0] or 0
                                    accumulated_time = timer_data[1] or 0
                                    if start_time:
                                        current_time = int(time.time()) - start_time + accumulated_time
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} после повторной попытки: current_time={current_time} (start_time={start_time}, accumulated_time={accumulated_time})")
                                    else:
                                        current_time = accumulated_time
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} из accumulated_time после повторной попытки: current_time={current_time}")
                                    if current_time == 0 and start_time:
                                        elapsed = int(time.time()) - start_time
                                        current_time = elapsed
                                        logging.debug(
                                            f"Восстановлено время для таймера {timer_id} из elapsed после повторной попытки: current_time={current_time} (start_time={start_time})")
                        if current_time > 0:
                            update_stats(timer_id, current_time)
                        else:
                            logging.warning(
                                f"Статистика для таймера {timer_id} не обновлена после повторной попытки, так как восстановленное время = 0")
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при остановке таймера: {e2}")

def stop_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT start_time, accumulated_time FROM timers WHERE timer_id = ?', (timer_id,))
            timer_data = cursor.fetchone()
            if timer_data:
                start_time = timer_data[0] or 0
                accumulated_time = timer_data[1] or 0
                if start_time:
                    current_time = int(time.time())
                    elapsed = current_time - start_time
                    new_accumulated_time = accumulated_time + elapsed  # Общее время для статистики
                    logging.debug(
                        f"Таймер {timer_id} остановлен, accumulated_time={new_accumulated_time}, elapsed={elapsed}")

                    # Обновляем статистику перед сбросом таймера
                    update_stats(timer_id, new_accumulated_time)

                cursor.execute('''
                    UPDATE timers 
                    SET is_running = 0,
                        is_paused = 0,
                        start_time = NULL,
                        pause_time = NULL,
                        accumulated_time = 0  -- Сбрасываем accumulated_time на 0 для отображения 00:00:00
                    WHERE timer_id = ?''',
                               (timer_id,))
                timer_conn.commit()
                logging.debug(
                    f"Таймер {timer_id} остановлен, статистика обновлена с временем {new_accumulated_time} сек")
            else:
                cursor.execute('''
                    UPDATE timers 
                    SET is_running = 0,
                        is_paused = 0,
                        start_time = NULL,
                        pause_time = NULL,
                        accumulated_time = 0  -- Сбрасываем accumulated_time на 0
                    WHERE timer_id = ?''',
                               (timer_id,))
                timer_conn.commit()
        logging.info(f"Таймер {timer_id} остановлен, время на кнопке сброшено на 00:00:00")
        return True
    except Exception as e:
        logging.error(f"Ошибка остановки таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("resume_timer_"))
def handle_resume_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if resume_timer(timer_id):
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Поток обновления запущен для таймера {timer_id} после возобновления")
                # Обновляем статистику при возобновлении (используем текущее время из get_current_time)
                update_stats(timer_id, get_current_time(timer_id))
            else:
                pass
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при возобновлении таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if resume_timer(timer_id):
                    timer_name = get_timer_name(timer_id)
                    if timer_name:
                        show_timer_screen_2(call, timer_id, timer_name)
                        update_thread = Thread(target=update_timer_display, args=(
                        call.message.chat.id, call.message.message_id, timer_id, timer_name))
                        update_thread.daemon = True
                        update_thread.start()
                        logging.info(f"Поток обновления запущен после повторной попытки для таймера {timer_id}")
                        update_stats(timer_id, get_current_time(timer_id))
                    else:
                        pass
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при возобновлении таймера: {e2}")

def resume_timer(timer_id):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            cursor.execute('SELECT accumulated_time, is_paused, is_running FROM timers WHERE timer_id = ?', (timer_id,))
            result = cursor.fetchone()
            if result and result[1] == 1 and result[2] == 0:  # Проверяем, что таймер на паузе и не запущен
                accumulated_time = result[0] or 0  # Сохраняем текущее накопленное время

                cursor.execute('''
                    UPDATE timers 
                    SET is_paused = 0,
                        pause_time = NULL,
                        start_time = ?,
                        is_running = 1,
                        accumulated_time = ?  -- Сохраняем накопленное время для продолжения
                    WHERE timer_id = ?''',
                               (int(time.time()), accumulated_time, timer_id))
                timer_conn.commit()
            else:
                logging.warning(f"Таймер {timer_id} не на паузе, запущен или не найден, пропускаем возобновление")
            logging.info(f"Таймер {timer_id} возобновлен, продолжив с {accumulated_time} секунд")
        return True
    except Exception as e:
        logging.error(f"Ошибка возобновления таймера {timer_id}: {e}")
        return False

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_timer_"))
def handle_timer_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        timer_name = get_timer_name(timer_id)
        if not timer_name:
            bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
            return
        show_delete_confirmation(call, timer_id, timer_name)
    except Exception as e:
        logging.error(f"Ошибка при удалении таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                timer_name = get_timer_name(timer_id)
                if not timer_name:
                    bot.answer_callback_query(call.id, "❌ Таймер не найден", show_alert=False)  # Убрано уведомление
                    return
                show_delete_confirmation(call, timer_id, timer_name)
            except Exception as e2:
                logging.error(f"Повторная ошибка при удалении таймера: {e2}")


def show_delete_confirmation(call, timer_id, timer_name):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Да", callback_data=f"confirm_delete_{timer_id}"),
        InlineKeyboardButton("Нет", callback_data=f"cancel_delete_{timer_id}")
    )
    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=InputMediaPhoto(photo, caption=f"❓ Вы действительно хотите удалить таймер {timer_name}?"),
            reply_markup=markup
        )
    except Exception as e:
        logging.error(f"Ошибка при отображении подтверждения удаления таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=InputMediaPhoto(photo, caption=f"❓ Вы действительно хотите удалить таймер {timer_name}?"),
                    reply_markup=markup
                )
            except Exception as e2:
                logging.error(f"Повторная ошибка при отображении подтверждения удаления таймера {timer_id}: {e2}")


def delete_timer(timer_id):
    try:
        timer_cursor.execute('DELETE FROM timers WHERE timer_id = ?', (timer_id,))
        timer_cursor.execute('DELETE FROM stats WHERE timer_id = ?', (timer_id,))
        timer_conn.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка удаления таймера: {e}")
        return False


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_"))
def handle_confirm_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if delete_timer(timer_id):
            # Убрано уведомление: bot.answer_callback_query(call.id, "🗑 Таймер удалён", show_alert=True)
            timer_main_menu(call)
        else:
            pass
    except Exception as e:
        logging.error(f"Ошибка при подтверждении удаления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                if delete_timer(timer_id):
                    # Убрано уведомление
                    timer_main_menu(call)
                else:
                    pass
            except Exception as e2:
                logging.error(f"Повторная ошибка при подтверждении удаления таймера: {e2}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_delete_"))
def handle_cancel_delete(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        timer_name = get_timer_name(timer_id)
        show_timer_screen_1(call, timer_id, timer_name)
    except Exception as e:
        logging.error(f"Ошибка при отмене удаления таймера: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                timer_id = int(call.data.split("_")[-1])
                timer_name = get_timer_name(timer_id)
                show_timer_screen_1(call, timer_id, timer_name)
            except Exception as e2:
                logging.error(f"Повторная ошибка при отмене удаления таймера: {e2}")


# Функция для автоматической остановки таймера через 3 часа с отправкой нового сообщения
def auto_stop_timer(chat_id, message_id, timer_id, name):
    try:
        stop_timer(timer_id)  # Останавливаем таймер
        # Удаляем предыдущее сообщение с таймером
        bot.delete_message(chat_id, message_id)
        # Отправляем новое сообщение
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔄 Запустить заново", callback_data=f"restart_timer_{timer_id}"),
            InlineKeyboardButton("◀️ Не запускать", callback_data="main_back_call")
        )
        caption = f"⏳ Таймер: {name}\n\n⏹ Таймер проработал 3 часа!\nПрошло времени: 03:00:00"
        bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=markup
        )
        logging.info(f"Таймер {timer_id} автоматически остановлен через 3 часа, новое сообщение отправлено")
    except Exception as e:
        logging.error(f"Ошибка при автоматической остановке таймера {timer_id}: {e}")
        # В случае ошибки попробуем отправить сообщение без удаления старого
        try:
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔄 Запустить заново", callback_data=f"restart_timer_{timer_id}"),
                InlineKeyboardButton("◀️ Не запускать", callback_data="main_back_call")
            )
            bot.send_message(
                chat_id=chat_id,
                text=f"⏳ Таймер: {name}\n\n⏹ Таймер проработал 3 часа!\nПрошло времени: 03:00:00",
                reply_markup=markup
            )
        except Exception as e2:
            logging.error(f"Ошибка при отправке нового сообщения для таймера {timer_id}: {e2}")


# Обновлённая функция update_timer_display с проверкой на 3 часа
def update_timer_display(chat_id, message_id, timer_id, name):
    local_conn = sqlite3.connect('timers.db', check_same_thread=False)
    last_caption = None
    last_time = None
    try:
        logging.info(f"Запуск потока обновления для таймера {timer_id}")
        while True:
            with local_conn:
                cursor = local_conn.cursor()
                cursor.execute('SELECT is_running, is_paused FROM timers WHERE timer_id = ?', (timer_id,))
                status = cursor.fetchone()

                if not status or (not status[0] and not status[1]):
                    logging.info(f"Таймер {timer_id} завершил работу, завершение потока обновления")
                    break

                is_running, is_paused = status
                current_time = get_current_time(timer_id)

                # Проверка на 3 часа (10800 секунд)
                if current_time >= 10800:  # 3 часа в секундах
                    auto_stop_timer(chat_id, message_id, timer_id, name)
                    break

                time_text = format_timedelta_stats(current_time)
                caption = f"⏳ Таймер: {name}\n\n{'⏸ На паузе' if is_paused else '▶️ Запущен'}"
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("▶️ Возобновить" if is_paused else "⏸ Пауза",
                                         callback_data=f"{'resume' if is_paused else 'pause'}_timer_{timer_id}"),
                    InlineKeyboardButton("⏹ Остановить", callback_data=f"stop_timer_{timer_id}")
                )
                markup.row(
                    InlineKeyboardButton(time_text, callback_data="none")
                )

                if caption != last_caption or time_text != last_time:
                    try:
                        bot.edit_message_media(
                            chat_id=chat_id,
                            message_id=message_id,
                            media=InputMediaPhoto(photo, caption=caption),
                            reply_markup=markup
                        )
                        last_caption = caption
                        last_time = time_text
                        logging.debug(f"Обновлён дисплей для таймера {timer_id}: {caption}, Время: {time_text}")
                    except Exception as e:
                        if "message is not modified" not in str(e):
                            logging.error(f"Ошибка при обновлении таймера {timer_id}: {e}")
                            if "ConnectionResetError" in str(e):
                                time.sleep(1)
                                try:
                                    bot.edit_message_media(
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        media=InputMediaPhoto(photo, caption=caption),
                                        reply_markup=markup
                                    )
                                    logging.info(f"Дисплей обновлён после повторной попытки для таймера {timer_id}")
                                except Exception as e2:
                                    logging.error(f"Повторная ошибка при обновлении таймера {timer_id}: {e2}")
                    except telebot.apihelper.ApiTelegramException as api_err:
                        if api_err.error_code == 400 and "canceled by new editMessageMedia request" in str(api_err):
                            logging.warning(f"Пропущена ошибка Telegram API для таймера {timer_id}: {api_err}")
                        else:
                            logging.error(f"Неожиданная ошибка Telegram API для таймера {timer_id}: {api_err}")
                time.sleep(0.5)
            time.sleep(0.5)
    except Exception as e:
        logging.error(f"Критическая ошибка в потоке обновления таймера {timer_id}: {e}")
    finally:
        local_conn.close()
        logging.info(f"Поток обновления для таймера {timer_id} завершён")


# Обработчик для перезапуска таймера
@bot.callback_query_handler(func=lambda call: call.data.startswith("restart_timer_"))
def handle_restart_timer(call):
    user_id = call.from_user.id
    register_user(user_id)
    try:
        timer_id = int(call.data.split("_")[-1])
        if start_timer(timer_id):  # Перезапускаем таймер
            timer_name = get_timer_name(timer_id)
            if timer_name:
                show_timer_screen_2(call, timer_id, timer_name)
                update_thread = Thread(target=update_timer_display,
                                       args=(call.message.chat.id, call.message.message_id, timer_id, timer_name))
                update_thread.daemon = True
                update_thread.start()
                logging.info(f"Таймер {timer_id} перезапущен, поток обновления запущен")
                update_stats(timer_id, 0)  # Сбрасываем статистику при перезапуске
            else:
                bot.answer_callback_query(call.id, "❌ Ошибка при перезапуске таймера")
        else:
            bot.answer_callback_query(call.id, "❌ Не удалось перезапустить таймер")
    except Exception as e:
        logging.error(f"Ошибка при перезапуске таймера: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка при перезапуске")


def update_stats(timer_id, current_time):
    try:
        with timer_conn:
            cursor = timer_conn.cursor()
            # Используем московское время (UTC+3) для сохранения статистики
            msk_time = datetime.now() + timedelta(hours=3)
            current_date = msk_time.strftime('%Y-%m-%d')
            cursor.execute('SELECT total_time FROM stats WHERE timer_id = ? AND date = ?', (timer_id, current_date))
            existing_time = cursor.fetchone()
            existing_time = existing_time[0] if existing_time else 0

            # Суммируем существующее время с текущим временем
            new_total_time = existing_time + current_time
            logging.debug(
                f"Обновление статистики для таймера {timer_id}: existing_time={existing_time}, current_time={current_time}, new_total_time={new_total_time}")

            if current_time > 0:  # Обновляем только если есть реальное время
                cursor.execute('''
                    INSERT INTO stats (timer_id, date, total_time)
                    VALUES (?, ?, ?)
                    ON CONFLICT(timer_id, date) DO UPDATE SET total_time = ?
                ''', (timer_id, current_date, new_total_time, new_total_time))
                timer_conn.commit()
                logging.info(
                    f"Статистика обновлена: timer_id={timer_id}, date={current_date}, total_time={new_total_time} сек")
            else:
                logging.warning(f"Статистика для таймера {timer_id} не обновлена, так как current_time = 0")
    except Exception as e:
        logging.error(f"Ошибка обновления статистики для таймера {timer_id}: {e}")
        if "ConnectionResetError" in str(e):
            time.sleep(1)
            try:
                with timer_conn:
                    cursor = timer_conn.cursor()
                    # Используем московское время (UTC+3) для сохранения статистики
                    msk_time = datetime.now() + timedelta(hours=3)
                    current_date = msk_time.strftime('%Y-%m-%d')
                    cursor.execute('SELECT total_time FROM stats WHERE timer_id = ? AND date = ?',
                                   (timer_id, current_date))
                    existing_time = cursor.fetchone()
                    existing_time = existing_time[0] if existing_time else 0

                    new_total_time = existing_time + current_time
                    logging.debug(
                        f"Повторное обновление статистики для таймера {timer_id}: existing_time={existing_time}, current_time={current_time}, new_total_time={new_total_time}")

                    if current_time > 0:
                        cursor.execute('''
                            INSERT INTO stats (timer_id, date, total_time)
                            VALUES (?, ?, ?)
                            ON CONFLICT(timer_id, date) DO UPDATE SET total_time = ?
                        ''', (timer_id, current_date, new_total_time, new_total_time))
                        timer_conn.commit()
                        logging.info(
                            f"Статистика обновлена после повторной попытки: timer_id={timer_id}, date={current_date}, total_time={new_total_time} сек")
                    else:
                        logging.warning(
                            f"Статистика для таймера {timer_id} не обновлена после повторной попытки, так как current_time = 0")
            except Exception as e2:
                logging.error(f"Повторная ошибка обновления статистики для таймера {timer_id}: {e2}")


def restore_active_timers():
    with timer_conn:
        timer_cursor.execute('SELECT timer_id, name, is_running FROM timers WHERE is_running = 1')
        active_timers_data = timer_cursor.fetchall()
        for timer_id, name, _ in active_timers_data:
            timer_thread = Thread(target=run_timer, args=(timer_id,))
            timer_thread.daemon = True
            timer_thread.start()
            logging.info(f"Восстановлен активный таймер: timer_id={timer_id}, name={name}")


restore_active_timers()

def view_all_data_timers():
    conn = sqlite3.connect("timers.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM timers")
    data = cursor.fetchall()

    if not data:
        print("📭 Таблица пустая!")
    else:
        print("📊 Данные из таблицы 'timers':")
        for row in data:
            print(row)
    conn.close()


def view_all_data_stats():
    conn = sqlite3.connect("timers.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM stats")
    data = cursor.fetchall()

    if not data:
        print("📭 Таблица stats пуста!")
    else:
        print("📊 Данные из таблицы 'stats':")
        for row in data:
            print(row)
    conn.close()
view_all_data_timers()
view_all_data_stats()

# ================== Обработчики команд ==================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username
    user_id = message.from_user.id
    chat_id = message.chat.id
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    register_user(user_id, username)

    # Отправляем новое приветственное сообщение
    text = (
        "Ты в умном боте для подготовки к ЕГЭ по профильной математике.\n\n"
        "Главное здесь — чёткая структура: квест от задания к заданию, теория по каждому номеру и никакой путаницы.\n\n"
        "А ещё — трекер занятий, карточки, варианты и помощь от репетитора."
    )
    msg = bot.send_photo(
        chat_id=chat_id,
        photo=photo_main,
        caption=text,
        reply_markup=main_screen()
    )
    user_messages[user_id] = msg.message_id  # Сохраняем ID нового сообщения
    logging.info(f"Отправлено приветственное сообщение для {user_id}: {msg.message_id}")

def get_username(user_id):
    try:
        with users_conn:
            users_cursor.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
            result = users_cursor.fetchone()
            if result and result[0]:
                return f"@{result[0]}"
            else:
                return f"User ID: {user_id}"
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении username для user_id={user_id}: {e}")
        return f"User ID: {user_id}"

# Список ID администраторов
ADMIN_IDS = {1035828828,932659114}  # Ваш ID

# Функции для получения статистики за разные периоды
def get_active_users_period(days=1):
    """Получает количество активных пользователей за указанный период в днях.
    
    Args:
        days (int): Количество дней для анализа
        
    Returns:
        int: Количество активных пользователей
    """
    # Вычисляем дату начала периода с учетом московского времени (UTC+3)
    msk_time = datetime.now() + timedelta(hours=3)
    period_start = (msk_time - timedelta(days=days)).strftime('%Y-%m-%d')
    
    with users_conn:
        # Запрос пользователей, активных с указанной даты
        users_cursor.execute('SELECT COUNT(*) FROM users WHERE last_seen >= ?', (period_start,))
        active = users_cursor.fetchone()[0]
    
    return active

def get_users_list(page=1, page_size=10):
    """Получает список пользователей с пагинацией.
    
    Args:
        page (int): Номер страницы (начиная с 1)
        page_size (int): Размер страницы
        
    Returns:
        tuple: (список пользователей, общее количество)
    """
    offset = (page - 1) * page_size
    
    with users_conn:
        # Получаем общее количество
        users_cursor.execute('SELECT COUNT(*) FROM users')
        total_count = users_cursor.fetchone()[0]
        
        # Получаем пользователей с пагинацией
        users_cursor.execute('''
            SELECT user_id, username, phone, first_seen, last_seen
            FROM users
            ORDER BY last_seen DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        users = users_cursor.fetchall()
    
    return users, total_count

def get_user_info(user_id):
    """Получает полную информацию о пользователе.
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        dict: Информация о пользователе
    """
    result = {}
    
    # Основная информация
    with users_conn:
        users_cursor.execute('''
            SELECT username, phone, first_seen, last_seen
            FROM users WHERE user_id = ?
        ''', (user_id,))
        user_data = users_cursor.fetchone()
        
        if user_data:
            username, phone, first_seen, last_seen = user_data
            result['username'] = username
            result['phone'] = phone
            result['first_seen'] = first_seen
            result['last_seen'] = last_seen
    
    # Проверяем наличие групп карточек
    try:
        cards_conn = sqlite3.connect("cards.db", check_same_thread=False)
        cards_cursor = cards_conn.cursor()
        cards_cursor.execute("SELECT COUNT(*) FROM user_groups WHERE user_id = ?", (user_id,))
        card_groups_count = cards_cursor.fetchone()[0]
        result['card_groups_count'] = card_groups_count
        
        if card_groups_count > 0:
            cards_cursor.execute("SELECT group_name FROM user_groups WHERE user_id = ?", (user_id,))
            groups = cards_cursor.fetchall()
            result['card_groups'] = [group[0] for group in groups]
    except Exception as e:
        logging.error(f"Ошибка при получении групп карточек: {e}")
    finally:
        if 'cards_conn' in locals():
            cards_conn.close()
    
    # Проверяем наличие избранных задач
    try:
        favorites_count = get_favorites_count(user_id)
        result['favorites_count'] = favorites_count
    except Exception as e:
        logging.error(f"Ошибка при получении избранных задач: {e}")
    
    return result

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    user_id = message.from_user.id  # Без str(), так как сравниваем с int в ADMIN_IDS
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)

    # Проверяем, что это администратор
    if user_id not in ADMIN_IDS:
        bot.send_message(chat_id, "Эта команда доступна только администратору.")
        return

    # Формируем главное меню статистики
    text = "📊 Выберите тип статистики:"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📈 Общая статистика", callback_data="stats_general"),
        InlineKeyboardButton("👥 Статистика по пользователям", callback_data="stats_users_list_1"),
        InlineKeyboardButton("🕒 По времени", callback_data="stats_time")
    )

    # Отправляем сообщение с фотографией
    bot.send_photo(chat_id, photo, caption=text, reply_markup=markup)
    logging.info(f"Меню статистики отправлено администратору {user_id}")

# Состояние для отслеживания режима администратора при рассылке
admin_update_states = {}

# Обработчик команды /update для админа
@bot.message_handler(commands=['update'])
def handle_update_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    # Проверяем, является ли пользователь администратором
    if user_id not in ADMIN_IDS:
        bot.send_message(chat_id, "⛔ У вас нет прав для использования этой команды.")
        return
    
    # Устанавливаем состояние ожидания сообщения для рассылки
    admin_update_states[user_id] = "waiting_for_broadcast_message"
    
    # Запрашиваем текст сообщения для рассылки
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_broadcast"))
    
    bot.send_message(
        chat_id, 
        "📢 Введите текст сообщения для рассылки всем пользователям:", 
        reply_markup=markup
    )
    logging.info(f"Админ {user_id} начал процесс рассылки сообщения")

# Обработчик для отмены рассылки
@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    # Проверяем, что пользователь - администратор
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ У вас нет прав для использования этой команды.")
        return
    
    # Удаляем состояние ожидания текста для рассылки
    if user_id in admin_update_states:
        del admin_update_states[user_id]
    
    # Отправляем сообщение об отмене
    bot.edit_message_text(
        "❌ Рассылка отменена.",
        chat_id=chat_id,
        message_id=call.message.message_id
    )
    logging.info(f"Админ {user_id} отменил рассылку сообщения")

# Функция для массовой рассылки сообщений
def broadcast_message_to_all_users(admin_id, message_text):
    try:
        # Получаем список всех пользователей из базы данных
        with users_conn:
            users_cursor.execute("SELECT user_id FROM users")
            all_users = users_cursor.fetchall()
        
        total_users = len(all_users)
        success_count = 0
        fail_count = 0
        
        # Отправляем администратору сообщение о начале рассылки
        bot.send_message(admin_id, f"🔄 Начинаю рассылку сообщения {total_users} пользователям...")
        
        # Отправляем сообщение каждому пользователю
        for user in all_users:
            user_id = user[0]
            try:
                # Отправляем сообщение (только текст без форматирования)
                bot.send_message(user_id, message_text)
                
                # Отправляем приветственное сообщение, как при команде /start
                username = None
                try:
                    # Пытаемся получить username пользователя
                    user_info = bot.get_chat_member(user_id, user_id).user
                    username = user_info.username
                except:
                    pass
                
                # Отправляем такое же сообщение, как при /start
                text = (
                    "Ты в умном боте для подготовки к ЕГЭ по профильной математике.\n\n"
                    "Главное здесь — чёткая структура: квест от задания к заданию, теория по каждому номеру и никакой путаницы.\n\n"
                    "А ещё — трекер занятий, карточки, варианты и помощь от репетитора."
                )
                
                # Отправляем стартовое сообщение с фото и разметкой
                bot.send_photo(
                    chat_id=user_id,
                    photo=photo_main,
                    caption=text,
                    reply_markup=main_screen()
                )
                
                success_count += 1
                logging.info(f"Рассылка: сообщения отправлены пользователю {user_id}")
            except Exception as e:
                logging.error(f"Рассылка: ошибка при отправке сообщения пользователю {user_id}: {e}")
                fail_count += 1
        
        # Отправляем отчет о результатах рассылки
        result_message = (
            f"📬 Рассылка завершена!\n\n"
            f"📊 Статистика:\n"
            f"✅ Успешно отправлено: {success_count}\n"
            f"❌ Ошибок при отправке: {fail_count}\n"
            f"📋 Всего пользователей: {total_users}"
        )
        bot.send_message(admin_id, result_message)
        
        return success_count, fail_count, total_users
    except Exception as e:
        logging.error(f"Критическая ошибка при массовой рассылке: {e}")
        bot.send_message(admin_id, f"❌ Произошла ошибка при выполнении рассылки: {e}")
        return 0, 0, 0

# Обновляем callback_query_handler для обработки статистики
@bot.callback_query_handler(func=lambda call: call.data.startswith("stats_"))
def handle_stats_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    data = call.data

    # Проверка на администратора
    if user_id not in ADMIN_IDS:
        bot.edit_message_text(
            "⛔ Доступ к этой команде есть только у администраторов!",
            chat_id=chat_id,
            message_id=message_id
        )
        return
    
    # Общая статистика
    if data == "stats_general":
        # Получаем статистику за разные периоды
        total_users = get_total_users()
        active_today = get_active_users_today()
        active_week = get_active_users_period(7)
        active_month = get_active_users_period(30)
        
        text = "📊 Общая статистика:\n\n"
        text += f"Всего пользователей: {total_users}\n"
        text += f"Активных сегодня: {active_today}\n"
        text += f"Активных за неделю: {active_week}\n"
        text += f"Активных за месяц: {active_month}\n\n"
        
        # Получаем список последних активных пользователей
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users ORDER BY last_seen DESC LIMIT 5')
            recent_users = users_cursor.fetchall()
        
        if recent_users:
            text += "📱 Недавно активные пользователи:\n"
            for i, (user_id, username) in enumerate(recent_users, 1):
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📊 За день", callback_data="stats_period_1"),
            InlineKeyboardButton("📊 За неделю", callback_data="stats_period_7"),
            InlineKeyboardButton("📊 За месяц", callback_data="stats_period_30"),
            InlineKeyboardButton("📊 За всё время", callback_data="stats_period_all")
        )
        markup.add(InlineKeyboardButton("📋 Заявки", callback_data="stats_requests"))
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Статистика за период
    elif data.startswith("stats_period_"):
        from datetime import datetime, timedelta  # Локальный импорт для избежания конфликтов имен
        period = data.split("_")[2]
        
        if period == "all":
            # Статистика за всё время
            total_users = get_total_users()
            
            # Получаем список всех пользователей
            with users_conn:
                users_cursor.execute('SELECT user_id, username FROM users ORDER BY last_seen DESC')
                users_list = users_cursor.fetchall()
            
            text = f"📊 Статистика за всё время:\n\nВсего пользователей: {total_users}\n\n"
            
            # Добавляем теги пользователей
            if users_list:
                text += "📋 Список пользователей:\n"
                for i, (user_id, username) in enumerate(users_list[:15], 1):  # Ограничиваем 15 пользователями
                    display_name = f"@{username}" if username else f"ID: {user_id}"
                    text += f"{i}. {display_name}\n"
                
                if len(users_list) > 15:
                    text += f"\n... и ещё {len(users_list) - 15} пользователей"
        else:
            # Статистика за конкретный период
            days = int(period)
            # Используем московское время (UTC+3) для вычисления начала периода
            from datetime import datetime, timedelta  # Локальный импорт для избежания конфликтов имен
            msk_time = datetime.now() + timedelta(hours=3)
            period_start = (msk_time - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Получаем список активных пользователей за период
            with users_conn:
                users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? ORDER BY last_seen DESC', (period_start,))
                active_users_list = users_cursor.fetchall()
            
            active_users_count = len(active_users_list)
            period_text = "день" if days == 1 else ("неделю" if days == 7 else "месяц")
            text = f"📊 Статистика за {period_text}:\n\nАктивных пользователей: {active_users_count}\n\n"
            
            # Добавляем теги активных пользователей
            if active_users_list:
                text += "📋 Список активных пользователей:\n"
                for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                    display_name = f"@{username}" if username else f"ID: {user_id}"
                    text += f"{i}. {display_name}\n"
                
                if len(active_users_list) > 15:
                    text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_general"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Статистика по пользователям - список пользователей
    elif data.startswith("stats_users_list_"):
        page = int(data.split("_")[3])
        users, total_count = get_users_list(page)
        
        if not users:
            text = "Пользователи не найдены."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            return
        
        text = "👥 Пользователи:\n\n"
        markup = InlineKeyboardMarkup(row_width=2)
        
        for user in users:
            user_id_str, username, phone, first_seen, last_seen = user
            display_name = f"@{username}" if username else f"ID: {user_id_str}"
            # Добавляем кнопку для каждого пользователя
            markup.add(InlineKeyboardButton(display_name, callback_data=f"stats_user_{user_id_str}"))
        
        # Пагинация
        pagination_row = []
        max_pages = (total_count + 9) // 10  # Округление вверх до целого
        
        if page > 1:
            pagination_row.append(InlineKeyboardButton("⬅️", callback_data=f"stats_users_list_{page-1}"))
        
        pagination_row.append(InlineKeyboardButton(f"{page}/{max_pages}", callback_data="stats_nothing"))
        
        if page < max_pages:
            pagination_row.append(InlineKeyboardButton("➡️", callback_data=f"stats_users_list_{page+1}"))
        
        markup.row(*pagination_row)
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Информация о конкретном пользователе - для обработки только stats_user_ID
    elif data.startswith("stats_user_") and len(data.split("_")) == 3:
        parts = data.split("_")
        # Проверяем, что после "stats_user_" следует ID пользователя
        if parts[2].isdigit():
            user_id_str = parts[2]
            user_info = get_user_info(int(user_id_str))
            
            if not user_info:
                text = f"Информация о пользователе {user_id_str} не найдена."
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_users_list_1"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                return
        else:
            # Обработка ошибочного формата ID
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption="Неверный формат ID пользователя"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        
        # Форматируем даты и время в более читаемый вид используя функцию format_date
        first_seen = format_date(user_info.get('first_seen'), 'Неизвестно')
        last_seen = format_date(user_info.get('last_seen'), 'Неизвестно')
            
        # Формируем текст с информацией о пользователе
        text = f"👤 Информация о пользователе:\n\n"
        text += f"ID: {user_id_str}\n"
        username_value = user_info.get('username')
        text += f"Тег: {'@' + username_value if username_value else 'Нет'}\n"
        text += f"Телефон: {user_info.get('phone', 'Нет')}\n"
        text += f"Первое использование: {first_seen}\n"
        text += f"Последнее использование: {last_seen}\n"
        
        # Формируем меню действий для пользователя
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем основные разделы статистики
        
        # Study Counter - таймеры пользователя
        markup.add(InlineKeyboardButton("⏱ Study Counter", callback_data=f"stats_user_timers_{user_id_str}"))
        
        # Метод карточек
        markup.add(InlineKeyboardButton("📚 Метод карточек", callback_data=f"stats_user_cards_{user_id_str}"))
        
        # Варианты
        markup.add(InlineKeyboardButton("📝 Варианты", callback_data=f"stats_user_variants_{user_id_str}"))
        
        # Математический квест
        markup.add(InlineKeyboardButton("🎮 Математический квест", callback_data=f"stats_user_quest_{user_id_str}"))
        
        # Если у пользователя есть избранные задачи
        if user_info.get('favorites_count', 0) > 0:
            text += f"\nИзбранных задач: {user_info.get('favorites_count')}\n"
            markup.add(InlineKeyboardButton("⭐ Избранные задачи", callback_data=f"stats_user_favorites_{user_id_str}"))
        
        # Кнопка назад
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_users_list_1"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Информация о таймерах пользователя (Study Counter)
    elif data.startswith("stats_user_timers_"):
        user_id_str = data.split("_")[3]
        
        try:
            # Подключаемся к базе данных timers.db
            timers_conn = sqlite3.connect("timers.db", check_same_thread=False)
            timers_cursor = timers_conn.cursor()
            
            # Получаем таймеры пользователя
            timers_cursor.execute(
                "SELECT timer_id, name, accumulated_time, CASE WHEN is_running = 1 THEN 'running' WHEN is_paused = 1 THEN 'paused' ELSE 'stopped' END as state FROM timers WHERE user_id = ?", 
                (user_id_str,)
            )
            timers = timers_cursor.fetchall()
            
            # Получаем статистику таймеров - используем существующую структуру таблицы
            timers_cursor.execute(
                "SELECT timer_id, date, total_time FROM stats WHERE timer_id IN (SELECT timer_id FROM timers WHERE user_id = ?)", 
                (user_id_str,)
            )
            stats_rows = timers_cursor.fetchall()
            
            # Преобразуем в структуру для отображения
            stats = {}
            for row in stats_rows:
                timer_id, date, total_time = row
                if timer_id not in stats:
                    stats[timer_id] = [0, 0, 0, 0]  # day_time, week_time, month_time, all_time
                
                # Добавляем время к соответствующему периоду
                # Используем московское время (UTC+3)
                from datetime import datetime, timedelta  # Локальный импорт для избежания конфликтов имен
                msk_time = datetime.now() + timedelta(hours=3)
                today = msk_time.strftime('%Y-%m-%d')
                week_ago = (msk_time - timedelta(days=7)).strftime('%Y-%m-%d')
                month_ago = (msk_time - timedelta(days=30)).strftime('%Y-%m-%d')
                
                # Все записи идут в общее время
                stats[timer_id][3] += total_time
                
                # Фильтруем по датам для более коротких периодов
                if date == today:
                    stats[timer_id][0] += total_time
                if date >= week_ago:
                    stats[timer_id][1] += total_time
                if date >= month_ago:
                    stats[timer_id][2] += total_time
            
            if not timers:
                text = f"⏱ Study Counter пользователя {user_id_str}:\n\nУ пользователя нет таймеров."
            else:
                text = f"⏱ Study Counter пользователя {user_id_str}:\n\n"
                
                for timer_id, name, current_time, state in timers:
                    # Преобразуем секунды в человекочитаемый вид (чч:мм:сс)
                    current_time_str = format_timedelta_stats(current_time)
                    
                    # Определяем статус таймера
                    status = "⏸️ На паузе" if state == "paused" else "▶️ Активен" if state == "running" else "⏹️ Остановлен"
                    
                    text += f"📌 {name}: {current_time_str} {status}\n"
                    
                    # Если есть статистика по этому таймеру, добавляем её
                    if timer_id in stats:
                        day_time, week_time, month_time, all_time = stats[timer_id]
                        
                        text += f"   За день: {format_timedelta_stats(day_time)}\n"
                        text += f"   За неделю: {format_timedelta_stats(week_time)}\n"
                        text += f"   За месяц: {format_timedelta_stats(month_time)}\n"
                        text += f"   За всё время: {format_timedelta_stats(all_time)}\n\n"
                    else:
                        text += "   Нет статистики\n\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            logging.error(f"Ошибка при получении таймеров: {e}")
            text = f"Ошибка при получении таймеров пользователя {user_id_str}."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        finally:
            if 'timers_conn' in locals():
                timers_conn.close()
                
    # Информация о вариантах (тестах) пользователя
    elif data.startswith("stats_user_variants_"):
        user_id_str = data.split("_")[3]
        
        try:
            # Подключаемся к базе данных quiz.db
            variants_conn = sqlite3.connect("quiz.db", check_same_thread=False)
            variants_cursor = variants_conn.cursor()
            
            # Получаем информацию о вариантах пользователя
            variants_cursor.execute('''
                SELECT day, option, primary_score, secondary_score, timestamp, completed
                FROM user_quiz_state
                WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (user_id_str,))
            variants = variants_cursor.fetchall()
            
            if not variants:
                text = f"📝 Варианты пользователя {user_id_str}:\n\nПользователь не решал варианты."
            else:
                text = f"📝 Варианты пользователя {user_id_str}:\n\n"
                
                for day, option, primary_score, secondary_score, timestamp, completed in variants:
                    # Форматируем дату прохождения
                    date_str = format_date(timestamp, "Неизвестно")
                    
                    # Статус варианта
                    status = "✅ Завершен" if completed else "🔄 В процессе"
                    
                    text += f"Вариант {option}, день {day}: {status}\n"
                    
                    if completed:
                        text += f"   Первичный балл: {primary_score}\n"
                        text += f"   Вторичный балл: {secondary_score}\n"
                    
                    text += f"   Дата: {date_str}\n\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            logging.error(f"Ошибка при получении вариантов: {e}")
            text = f"Ошибка при получении вариантов пользователя {user_id_str}."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        finally:
            if 'variants_conn' in locals():
                variants_conn.close()
    
    # Информация о прогрессе в математическом квесте
    elif data.startswith("stats_user_quest_"):
        user_id_str = data.split("_")[3]
        
        try:
            # Подключаемся к базе данных quest.db
            quest_conn = sqlite3.connect("quest.db", check_same_thread=False)
            quest_cursor = quest_conn.cursor()
            
            # Получаем информацию о прогрессе в мирах
            quest_cursor.execute('''
                SELECT world_id, completed_tasks, total_tasks
                FROM world_progress
                WHERE user_id = ?
            ''', (user_id_str,))
            worlds_progress = quest_cursor.fetchall()
            
            # Получаем информацию о заданиях с верными ответами
            task_progress_conn = sqlite3.connect("task_progress.db", check_same_thread=False)
            task_cursor = task_progress_conn.cursor()
            
            task_cursor.execute('''
                SELECT COUNT(*) FROM task_progress
                WHERE user_id = ? AND status = 'correct'
            ''', (user_id_str,))
            correct_tasks = task_cursor.fetchone()[0]
            
            # Получаем информацию о просмотренных подсказках
            task_cursor.execute('''
                SELECT COUNT(*) FROM hint_usage
                WHERE user_id = ?
            ''', (user_id_str,))
            hints_used = task_cursor.fetchone()[0]
            
            # Получаем общее количество заданий
            task_cursor.execute('''
                SELECT COUNT(*) FROM task_progress
                WHERE user_id = ?
            ''', (user_id_str,))
            total_attempted_tasks = task_cursor.fetchone()[0]
            
            # Получаем информацию о домашних заданиях
            task_cursor.execute('''
                SELECT COUNT(*) FROM task_progress
                WHERE user_id = ? AND type = 'homework'
            ''', (user_id_str,))
            homework_tasks = task_cursor.fetchone()[0]
            
            # Получаем информацию об избранных задачах
            favorites_conn = sqlite3.connect("favorites.db", check_same_thread=False)
            favorites_cursor = favorites_conn.cursor()
            
            favorites_cursor.execute('''
                SELECT COUNT(*) FROM favorites
                WHERE user_id = ?
            ''', (user_id_str,))
            favorites_count = favorites_cursor.fetchone()[0]
            
            if not worlds_progress:
                text = f"🎮 Математический квест - пользователь {user_id_str}:\n\nПользователь не начинал квест."
            else:
                text = f"🎮 Математический квест - пользователь {user_id_str}:\n\n"
                
                # Только прогресс по мирам и избранные задачи согласно новым требованиям
                text += f"1. Прогресс по мирам:\n"
                text += f"2. Избранные задачи: {favorites_count}\n\n"
                
                total_completed = 0
                total_tasks = 0
                
                for world_id, completed, total in worlds_progress:
                    if completed > 0 or total > 0:  # Показываем только те миры, где есть прогресс
                        progress_percent = int(completed / total * 100) if total > 0 else 0
                        text += f"   Мир {world_id}: {completed}/{total} задач ({progress_percent}%)\n"
                        total_completed += completed
                        total_tasks += total
                
                # Общий прогресс
                if total_tasks > 0:
                    overall_percent = int(total_completed / total_tasks * 100)
                    text += f"\n   Общий прогресс: {total_completed}/{total_tasks} ({overall_percent}%)\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            logging.error(f"Ошибка при получении прогресса в квесте: {e}")
            text = f"Ошибка при получении прогресса в квесте пользователя {user_id_str}."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        finally:
            if 'quest_conn' in locals():
                quest_conn.close()
            if 'task_progress_conn' in locals():
                task_progress_conn.close()
            if 'favorites_conn' in locals():
                favorites_conn.close()
            
    # Информация о карточках пользователя
    elif data.startswith("stats_user_cards_"):
        user_id_str = data.split("_")[3]
        
        try:
            # Подключаемся к базе данных cards.db
            cards_conn = sqlite3.connect("cards.db", check_same_thread=False)
            cards_cursor = cards_conn.cursor()
            
            # Получаем группы карточек пользователя
            cards_cursor.execute(
                "SELECT group_name, themes FROM user_groups WHERE user_id = ?", 
                (user_id_str,)
            )
            groups = cards_cursor.fetchall()
            
            if not groups:
                text = "У пользователя нет групп карточек."
            else:
                text = f"📚 Группы карточек пользователя {user_id_str}:\n\n"
                for i, (group_name, themes_json) in enumerate(groups, 1):
                    themes = json.loads(themes_json)
                    text += f"{i}. {group_name} - {len(themes)} тем\n"
                    # Ограничиваем длину сообщения
                    if i <= 10:  # Показываем максимум 10 групп для краткости
                        text += f"   Темы: {', '.join(themes)}\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            logging.error(f"Ошибка при получении групп карточек: {e}")
            text = f"Ошибка при получении групп карточек пользователя {user_id_str}."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        finally:
            if 'cards_conn' in locals():
                cards_conn.close()
    
    # Информация об избранных задачах пользователя
    elif data.startswith("stats_user_favorites_"):
        user_id_str = data.split("_")[3]
        
        try:
            # Получаем избранные задачи
            favorite_tasks = get_favorite_tasks(user_id_str)
            
            if not favorite_tasks:
                text = "У пользователя нет избранных задач."
            else:
                text = f"⭐ Избранные задачи пользователя {user_id_str}:\n\n"
                text += f"Всего избранных задач: {len(favorite_tasks)}\n\n"
                
                # Группируем задачи по мирам
                worlds = {}
                for task in favorite_tasks:
                    world_id = task[1]
                    if world_id not in worlds:
                        worlds[world_id] = 0
                    worlds[world_id] += 1
                
                for world_id, count in worlds.items():
                    text += f"Мир {world_id}: {count} задач\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
        except Exception as e:
            logging.error(f"Ошибка при получении избранных задач: {e}")
            text = f"Ошибка при получении избранных задач пользователя {user_id_str}."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"stats_user_{user_id_str}"))
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
    
    # Статистика по времени
    elif data == "stats_time":
        # Импортируем datetime и timedelta для правильной работы
        from datetime import datetime, timedelta
        
        # Получаем текущую дату (МСК)
        msk_time = datetime.now() + timedelta(hours=3)
        # Список месяцев для выбора (12 месяцев, начиная с текущего)
        months = []
        current_month = msk_time.replace(day=1)
        
        for i in range(12):
            if i == 0:
                month_date = current_month
            else:
                # Получаем предыдущий месяц
                prev_month = current_month.replace(day=1) - timedelta(days=1)
                month_date = prev_month.replace(day=1)
                current_month = month_date
                
            month_id = month_date.strftime('%Y-%m')  # ГГГГ-ММ
            month_name = month_date.strftime('%B %Y')  # название месяца и год
            months.append((month_id, month_name))
            
        # Текущий месяц
        current_month_id = msk_time.strftime('%Y-%m')
        current_year = msk_time.year
        current_month_num = msk_time.month
        
        # Показываем статистику за текущий месяц
        import calendar
        month_days = calendar.monthrange(current_year, current_month_num)[1]
        month_start = datetime(current_year, current_month_num, 1)
        month_end = datetime(current_year, current_month_num, month_days)
        
        # Получаем активных пользователей за текущий месяц
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? AND last_seen <= ? ORDER BY last_seen DESC', 
                             (month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
            active_users_list = users_cursor.fetchall()
        
        active_users_count = len(active_users_list)
        
        # Названия месяцев на русском
        month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                       "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        current_month_name = month_names[current_month_num-1]
        
        # Формируем текст сообщения со статистикой
        text = f"📊 Статистика активности за {current_month_name} {current_year}:\n\n"
        text += f"Всего активных пользователей: {active_users_count}\n\n"
        
        # Добавляем список активных пользователей
        if active_users_list:
            text += "📋 Список активных пользователей:\n"
            for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
            
            if len(active_users_list) > 15:
                text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        else:
            text += "За этот месяц не было активных пользователей."
        
        text += "\n\n🕒 Выберите другой месяц для просмотра статистики:"
        
        # Формируем клавиатуру с кнопками выбора месяца
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для текущего месяца по дням и неделям
        markup.add(
            InlineKeyboardButton(f"📅 Просмотр по дням ({current_month_name})", 
                               callback_data=f"stats_time_month_select_{current_month_id}")
        )
        
        markup.add(
            InlineKeyboardButton(f"📆 Просмотр по неделям ({current_month_name})",
                               callback_data=f"stats_time_month_weeks_{current_month_id}")
        )
        
        # Добавляем кнопки выбора месяца
        for month_id, month_name in months:
            if month_id != current_month_id:  # Не показываем текущий месяц в списке
                # Название месяца на русском
                month_ru = month_name.replace("January", "Январь").replace("February", "Февраль").replace("March", "Март") \
                                    .replace("April", "Апрель").replace("May", "Май").replace("June", "Июнь") \
                                    .replace("July", "Июль").replace("August", "Август").replace("September", "Сентябрь") \
                                    .replace("October", "Октябрь").replace("November", "Ноябрь").replace("December", "Декабрь")
                markup.add(InlineKeyboardButton(month_ru, callback_data=f"stats_time_month_specific_{month_id}"))
        
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Выбор конкретного дня
    elif data == "stats_time_select_day":
        # Получаем текущую дату (МСК)
        msk_time = datetime.now() + timedelta(hours=3)
        # Текущий месяц и 3 предыдущих
        months = []
        for i in range(4):
            month_date = msk_time - timedelta(days=30*i)
            month_name = month_date.strftime('%B %Y')  # название месяца и год
            month_id = month_date.strftime('%Y-%m')  # ГГГГ-ММ
            months.append((month_id, month_name))
            
        text = "📅 Выберите месяц для просмотра статистики по дням:"
        markup = InlineKeyboardMarkup(row_width=1)
        for month_id, month_name in months:
            # Название месяца на русском
            month_ru = month_name.replace("January", "Январь").replace("February", "Февраль").replace("March", "Март") \
                                .replace("April", "Апрель").replace("May", "Май").replace("June", "Июнь") \
                                .replace("July", "Июль").replace("August", "Август").replace("September", "Сентябрь") \
                                .replace("October", "Октябрь").replace("November", "Ноябрь").replace("December", "Декабрь")
            markup.add(InlineKeyboardButton(month_ru, callback_data=f"stats_time_month_select_{month_id}"))
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Выбор конкретного месяца для отображения дней
    elif data.startswith("stats_time_month_select_"):
        month_id = data.split("_")[4]  # ГГГГ-ММ
        year, month = month_id.split("-")
        year = int(year)
        month = int(month)
        
        # Получаем все дни месяца
        import calendar
        month_days = calendar.monthrange(year, month)[1]
        
        text = f"📅 Выберите день для просмотра статистики:"
        markup = InlineKeyboardMarkup(row_width=7)  # 7 дней в неделе
        
        # Добавляем кнопки для дней месяца
        buttons = []
        for day in range(1, month_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"  # ГГГГ-ММ-ДД
            day_btn = InlineKeyboardButton(f"{day}", callback_data=f"stats_time_day_specific_{date_str}")
            buttons.append(day_btn)
            
            # Добавляем ряд после 7 кнопок или в конце месяца
            if len(buttons) == 7 or day == month_days:
                markup.row(*buttons)
                buttons = []
        
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_main"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Выбор конкретной недели
    elif data == "stats_time_select_week":
        # Получаем текущую дату (МСК)
        msk_time = datetime.now() + timedelta(hours=3)
        # Текущая неделя и несколько предыдущих (8 недель)
        weeks = []
        for i in range(8):
            # Вычисляем начало недели (понедельник)
            week_start = msk_time - timedelta(days=msk_time.weekday() + 7*i)
            week_end = week_start + timedelta(days=6)  # воскресенье
            week_id = week_start.strftime('%Y-%m-%d')  # ГГГГ-ММ-ДД начала недели
            week_name = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}"
            weeks.append((week_id, week_name))
            
        text = "📆 Выберите неделю для просмотра статистики:"
        markup = InlineKeyboardMarkup(row_width=1)
        for week_id, week_name in weeks:
            markup.add(InlineKeyboardButton(week_name, callback_data=f"stats_time_week_specific_{week_id}"))
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Выбор конкретного месяца
    elif data == "stats_time_select_month":
        # Получаем текущую дату (МСК)
        msk_time = datetime.now() + timedelta(hours=3)
        # Текущий месяц и 11 предыдущих (1 год)
        months = []
        for i in range(12):
            month_date = msk_time.replace(day=1) - timedelta(days=1)  # последний день предыдущего месяца
            month_date = month_date.replace(day=1)  # первый день предыдущего месяца
            for _ in range(i-1):
                month_date = month_date.replace(day=1) - timedelta(days=1)  # последний день предыдущего месяца
                month_date = month_date.replace(day=1)  # первый день предыдущего месяца
                
            month_id = month_date.strftime('%Y-%m')  # ГГГГ-ММ
            month_name = month_date.strftime('%B %Y')  # название месяца и год
            months.append((month_id, month_name))
            
        text = "📆 Выберите месяц для просмотра статистики:"
        markup = InlineKeyboardMarkup(row_width=1)
        for month_id, month_name in months:
            # Название месяца на русском
            month_ru = month_name.replace("January", "Январь").replace("February", "Февраль").replace("March", "Март") \
                                .replace("April", "Апрель").replace("May", "Май").replace("June", "Июнь") \
                                .replace("July", "Июль").replace("August", "Август").replace("September", "Сентябрь") \
                                .replace("October", "Октябрь").replace("November", "Ноябрь").replace("December", "Декабрь")
            markup.add(InlineKeyboardButton(month_ru, callback_data=f"stats_time_month_specific_{month_id}"))
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Обработка статистики за конкретный день
    elif data.startswith("stats_time_day_specific_"):
        from datetime import datetime, timedelta
        
        date_str = data.split("_")[4]  # ГГГГ-ММ-ДД
        year, month, day = date_str.split("-")
        
        # Создаем объект даты
        date_obj = datetime(int(year), int(month), int(day))
        next_day = date_obj + timedelta(days=1)
        
        # Форматируем дату для отображения
        display_date = date_obj.strftime("%d.%m.%Y")
        
        # Получаем активных пользователей за выбранный день
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? AND last_seen < ? ORDER BY last_seen DESC', 
                             (date_str, next_day.strftime('%Y-%m-%d')))
            active_users_list = users_cursor.fetchall()
        
        active_users_count = len(active_users_list)
        
        text = f"📊 Статистика активности за {display_date}:\n\n"
        text += f"Всего активных пользователей: {active_users_count}\n\n"
        
        # Добавляем список активных пользователей
        if active_users_list:
            text += "📋 Список активных пользователей:\n"
            for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
            
            if len(active_users_list) > 15:
                text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        else:
            text += "За этот день не было активных пользователей."
        
        # Получаем месяц для возврата
        back_month_id = f"{year}-{month}"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад к дням", callback_data=f"stats_time_month_select_{back_month_id}"))
        markup.add(InlineKeyboardButton("◀️ Назад к выбору периода", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Обработка статистики за конкретную неделю
    elif data.startswith("stats_time_week_specific_"):
        from datetime import datetime, timedelta
        
        week_start_str = data.split("_")[4]  # ГГГГ-ММ-ДД
        week_start = datetime.strptime(week_start_str, '%Y-%m-%d')
        week_end = week_start + timedelta(days=6)
        
        # Форматируем даты для отображения
        display_week = f"{week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}"
        
        # Проверяем месяц недели для кнопки возврата
        month_id = week_start.strftime('%Y-%m')
        
        # Получаем активных пользователей за выбранную неделю
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? AND last_seen <= ? ORDER BY last_seen DESC', 
                             (week_start_str, week_end.strftime('%Y-%m-%d')))
            active_users_list = users_cursor.fetchall()
        
        active_users_count = len(active_users_list)
        
        text = f"📊 Статистика активности за неделю {display_week}:\n\n"
        text += f"Всего активных пользователей: {active_users_count}\n\n"
        
        # Добавляем список активных пользователей
        if active_users_list:
            text += "📋 Список активных пользователей:\n"
            for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
            
            if len(active_users_list) > 15:
                text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        else:
            text += "За эту неделю не было активных пользователей."
        
        markup = InlineKeyboardMarkup()
        
        # Проверяем, пришли ли из списка недель месяца
        if data.split("_")[3] == "month":
            # Возврат к неделям текущего месяца
            markup.add(InlineKeyboardButton("◀️ Назад к неделям", callback_data=f"stats_time_month_weeks_{month_id}"))
        else:
            # Возврат к общему списку недель
            markup.add(InlineKeyboardButton("◀️ Назад к неделям", callback_data="stats_time_select_week"))
            
        markup.add(InlineKeyboardButton("◀️ Назад к выбору периода", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Просмотр недель конкретного месяца
    elif data.startswith("stats_time_month_weeks_"):
        from datetime import datetime, timedelta
        import calendar
        
        month_id = data.split("_")[4]  # ГГГГ-ММ
        year, month = month_id.split("-")
        year = int(year)
        month = int(month)
        
        # Названия месяцев на русском
        month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        month_name = month_names[month-1]
        
        # Получаем все дни месяца
        month_days = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        
        # Получаем недели месяца
        weeks = []
        current_date = month_start
        
        while current_date.month == month:
            # Находим начало недели (понедельник)
            week_start = current_date - timedelta(days=current_date.weekday())
            
            # Если начало недели в предыдущем месяце, устанавливаем на 1 число текущего
            if week_start.month != month:
                week_start = month_start
                
            # Находим конец недели (воскресенье)
            week_end = week_start + timedelta(days=6)
            
            # Если конец недели в следующем месяце, устанавливаем на последний день текущего
            if week_end.month != month:
                week_end = datetime(year, month, month_days)
                
            week_id = week_start.strftime('%Y-%m-%d')
            week_name = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')}"
            weeks.append((week_id, week_name))
            
            # Переходим к следующей неделе
            current_date = week_end + timedelta(days=1)
            
            # Проверяем, не вышли ли за пределы месяца
            if current_date.month != month:
                break
        
        text = f"📆 Недели {month_name} {year}:\n\nВыберите неделю для просмотра статистики:"
        
        markup = InlineKeyboardMarkup(row_width=1)
        for week_id, week_name in weeks:
            markup.add(InlineKeyboardButton(week_name, callback_data=f"stats_time_week_specific_{week_id}"))
            
        # Добавляем кнопки навигации
        markup.add(
            InlineKeyboardButton(f"📅 Просмотр по дням ({month_name})", 
                               callback_data=f"stats_time_month_select_{month_id}")
        )
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Обработка статистики за конкретный месяц
    elif data.startswith("stats_time_month_specific_"):
        from datetime import datetime, timedelta
        import calendar
        
        month_id = data.split("_")[4]  # ГГГГ-ММ
        year, month = month_id.split("-")
        year = int(year)
        month = int(month)
        
        # Создаем объекты даты для начала и конца месяца
        month_days = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, month_days)
        
        # Форматируем даты для отображения
        month_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                       "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        month_name = month_names[month-1]
        display_month = f"{month_name} {year}"
        
        # Получаем активных пользователей за выбранный месяц
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? AND last_seen <= ? ORDER BY last_seen DESC', 
                             (month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
            active_users_list = users_cursor.fetchall()
        
        active_users_count = len(active_users_list)
        
        text = f"📊 Статистика активности за {display_month}:\n\n"
        text += f"Всего активных пользователей: {active_users_count}\n\n"
        
        # Добавляем список активных пользователей
        if active_users_list:
            text += "📋 Список активных пользователей:\n"
            for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
            
            if len(active_users_list) > 15:
                text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        else:
            text += "За этот месяц не было активных пользователей."
        
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для просмотра по дням и неделям текущего месяца
        markup.add(
            InlineKeyboardButton(f"📅 Просмотр по дням ({month_name})", 
                               callback_data=f"stats_time_month_select_{month_id}")
        )
        
        markup.add(
            InlineKeyboardButton(f"📆 Просмотр по неделям ({month_name})",
                               callback_data=f"stats_time_month_weeks_{month_id}")
        )
        
        markup.add(InlineKeyboardButton("◀️ Назад к выбору месяца", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Обработка быстрой статистики (текущий день, неделя, месяц)
    elif data.startswith("stats_time_day_current") or data.startswith("stats_time_week_current") or data.startswith("stats_time_month_current"):
        from datetime import datetime, timedelta
        
        period_type = data.split("_")[2]  # day, week, month
        
        # Получаем текущую дату (МСК)
        msk_time = datetime.now() + timedelta(hours=3)
        
        if period_type == "day":
            days = 1
            period_text = "текущий день"
            period_start = msk_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "week":
            days = 7
            period_text = "текущую неделю"
            # Вычисляем начало недели (понедельник)
            period_start = msk_time - timedelta(days=msk_time.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period_type == "month":
            days = 30
            period_text = "текущий месяц"
            # Вычисляем начало месяца
            period_start = msk_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            days = 1
            period_text = "день"
            period_start = msk_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Форматируем дату начала периода
        display_date = period_start.strftime('%d.%m.%Y')
        
        # Получаем активных пользователей за указанный период
        with users_conn:
            users_cursor.execute('SELECT user_id, username FROM users WHERE last_seen >= ? ORDER BY last_seen DESC', 
                             (period_start.strftime('%Y-%m-%d'),))
            active_users_list = users_cursor.fetchall()
        
        active_users_count = len(active_users_list)
        
        text = f"📊 Статистика активности за {period_text} (с {display_date}):\n\n"
        text += f"Всего активных пользователей: {active_users_count}\n\n"
        
        # Добавляем список активных пользователей
        if active_users_list:
            text += "📋 Список активных пользователей:\n"
            for i, (user_id, username) in enumerate(active_users_list[:15], 1):  # Ограничиваем 15 пользователями
                display_name = f"@{username}" if username else f"ID: {user_id}"
                text += f"{i}. {display_name}\n"
            
            if len(active_users_list) > 15:
                text += f"\n... и ещё {len(active_users_list) - 15} пользователей"
        else:
            text += "За этот период не было активных пользователей."
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="stats_time"))
        
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Возврат в главное меню статистики
    elif data == "stats_main":
        text = "📊 Выберите тип статистики:"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📈 Общая статистика", callback_data="stats_general"),
            InlineKeyboardButton("👥 Статистика по пользователям", callback_data="stats_users_list_1"),
            InlineKeyboardButton("🕒 По времени", callback_data="stats_time")
        )
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    
    # Заглушка для нерабочих кнопок (номер страницы)
    elif data == "stats_nothing":
        bot.answer_callback_query(call.id)
        
    # Обработка заявок на репетитора
    elif data == "stats_requests":
        # Показываем список пользователей с заявками
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT DISTINCT tr.user_id, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                ''')
                users = users_cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке пользователей с заявками: {e}")
            bot.edit_message_text("Ошибка при загрузке статистики заявок.", chat_id, message_id)
            return

        if not users:
            text = "📋 Заявки на репетитора:\n\nПока нет заявок."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_main"))
        else:
            text = "📋 Заявки на репетитора:\n\nВыберите пользователя:"
            markup = InlineKeyboardMarkup(row_width=1)
            for user in users:
                user_id, username = user
                display_name = f"@{username}" if username else f"User ID: {user_id}"
                markup.add(InlineKeyboardButton(display_name, callback_data=f"stats_request_user_{user_id}"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_main"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data.startswith("stats_user_"):
        # Показываем все заявки выбранного пользователя
        selected_user_id = data.split("_")[2]
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT tr.user_id, tr.name, tr.school_class, tr.test_score, tr.expected_price, tr.timestamp, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                    WHERE tr.user_id = ?
                    ORDER BY tr.timestamp DESC
                ''', (selected_user_id,))
                requests = users_cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке заявок для user_id {selected_user_id}: {e}")
            bot.edit_message_text("Ошибка при загрузке заявок.", chat_id, message_id)
            return

        if not requests:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nЗаявок не найдено."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))
        else:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nВыберите заявку:"
            markup = InlineKeyboardMarkup(row_width=1)
            for req in requests:
                user_id, _, _, _, _, timestamp, username = req
                display_name = get_display_name(user_id, chat_id)
                markup.add(InlineKeyboardButton(
                    f"{display_name} | {timestamp[:19]}",
                    callback_data=f"stats_request_{user_id}_{timestamp}"
                ))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data.startswith("stats_request_user_"):
        # Просмотр всех заявок выбранного пользователя
        selected_user_id = data.split("_")[3]  # Извлекаем ID пользователя из callback_data
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT tr.user_id, tr.name, tr.school_class, tr.test_score, tr.expected_price, tr.timestamp, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                    WHERE tr.user_id = ?
                    ORDER BY tr.timestamp DESC
                ''', (selected_user_id,))
                requests = users_cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке заявок для user_id {selected_user_id}: {e}")
            bot.edit_message_text("Ошибка при загрузке заявок.", chat_id, message_id)
            return

        if not requests:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nЗаявок не найдено."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))
        else:
            text = f"📋 Заявки от {get_display_name(selected_user_id, chat_id)}\n\nВыберите заявку:"
            markup = InlineKeyboardMarkup(row_width=1)
            for req in requests:
                user_id, _, _, _, _, timestamp, username = req
                display_name = get_display_name(user_id, chat_id)
                markup.add(InlineKeyboardButton(
                    f"{display_name} | {timestamp[:19]}",
                    callback_data=f"stats_request_{user_id}_{timestamp}"
                ))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="stats_requests"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
    elif data.startswith("stats_request_"):
        # Просмотр конкретной заявки
        parts = data.split("_")
        req_user_id = parts[2]
        req_timestamp = "_".join(parts[3:])
        try:
            with users_conn:
                users_cursor.execute('''
                    SELECT tr.user_id, tr.name, tr.school_class, tr.test_score, tr.expected_price, tr.timestamp, u.username
                    FROM tutor_requests tr
                    LEFT JOIN users u ON tr.user_id = u.user_id
                    WHERE tr.user_id = ? AND tr.timestamp = ?
                ''', (req_user_id, req_timestamp))
                request = users_cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при загрузке заявки для user_id {req_user_id}: {e}")
            bot.edit_message_text("Ошибка при загрузке данных заявки.", chat_id, message_id)
            return

        if not request:
            text = f"📋 Заявка от User ID: {req_user_id}\n\nЗаявка не найдена."
        else:
            user_id, name, school_class, test_score, expected_price, timestamp, username = request
            display_name = f"@{username}" if username else f"User ID: {user_id}"
            
            # Форматируем дату и время в более читаемый вид используя функцию format_date
            formatted_date = format_date(timestamp)
                
            text = (
                f"📋 Заявка от {display_name}\n\n"
                f"👤 Имя: {name}\n"
                f"🏫 Класс: {school_class}\n"
                f"📈 Пробный балл: {test_score}\n"
                f"💰 Ожидаемая цена: {expected_price}\n"
                f"⏰ Дата: {formatted_date}"
            )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"stats_request_user_{req_user_id}"))

        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

    elif data == "stats_back":
        # Возврат к общей статистике
        total_users = get_total_users()
        active_today = get_active_users_today()
        text = f"📊 Общая статистика:\nВсего пользователей: {total_users}\nАктивных сегодня: {active_today}"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📋 Заявки", callback_data="stats_requests"))
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
# ================== Теория по темам ==================

def theory_screen():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔢 по заданиям", callback_data="tasks_call"),
        InlineKeyboardButton("📘 по темам", callback_data="tasks_by_topic_call")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    return markup
# Создаёт экран "Теория по темам"
def tasks_by_topic_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Алгебра", callback_data="topics_algebra_call"),
        InlineKeyboardButton("Геометрия", callback_data="topics_geometry_call")
    )
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="theory_call"))
    return markup
# Создаёт экран со списком тем Алгебры для выбора пользователем
def algebra_topics_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    algebra_topics = [
        ("Теория вероятностей", "probability"),
        ("ФСУ", "fsu"),
        ("Квадратные уравнения", "quadratic"),
        ("Степени", "powers"),
        ("Корни", "roots"),
        ("Тригонометрическая окружность", "trigonometric_circle"),
        ("Окружность для тангенса", "tangent_circle"),
        ("Тригонометрические определения", "definitions"),
        ("Тригонометрические формулы", "trigonometric_formulas"),
        ("Формулы приведения", "reduction_formulas"),
        ("Логарифмы", "logarithms"),
        ("Модули", "modules"),
        ("Обычная функция и производная", "usual_function_and_derivative"),
        ("Производная", "derivative"),
        ("Функция корня", "root_function"),
        ("Показательная функция", "exponential_function"),
        ("Логарифмическая функция", "logarithmic_function"),
        ("Метод рационализации", "rationalization")
    ]
    for theme_name, theme_code in algebra_topics:
        markup.add(InlineKeyboardButton(theme_name, callback_data=f"topic_{theme_code}_call"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="tasks_by_topic_call"))
    return markup
# Создаёт экран со списком тем Геометрии для выбора пользователем
def geometry_topics_screen():
    markup = InlineKeyboardMarkup(row_width=2)
    geometry_topics = [
        ("Биссектриса, медиана", "triangle_lines"),
        ("Прямоугольный треугольник", "right_triangle"),
        ("Равнобедренный/Равносторонний треугольник", "isosceles_equilateral_triangle"),
        ("Равенство/Подобие треугольников", "triangle_similarity"),
        ("Треугольник", "triangle"),
        ("Окружность", "circle"),
        ("Параллелограмм", "parallelogram"),
        ("Равносторонний шестиугольник", "regular_hexagon"),
        ("Ромб и Трапеция", "rhombus_trapezoid"),
        ("Углы", "angles"),
        ("Вектор", "vector"),
        ("Стереометрия", "stereometry"),
        ("Прямая", "direct"),
        ("Парабола", "parabola"),
        ("Гипербола", "hyperbola")
    ]
    for theme_name, theme_code in geometry_topics:
        markup.add(InlineKeyboardButton(theme_name, callback_data=f"topic_{theme_code}_call"))
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="tasks_by_topic_call"))
    return markup

# ================== Quiz ==================
quiz_conn = sqlite3.connect('quiz.db', check_same_thread=False)
quiz_cursor = quiz_conn.cursor()

# Словарь для преобразования первичных баллов во вторичные
primary_to_secondary = {
    1: 6,
    2: 11,
    3: 17,
    4: 22,
    5: 27,
    6: 34,
    7: 40,
    8: 46,
    9: 52,
    10: 58,
    11: 64,
    12: 70
}
# Функция для получения вторичных баллов
def get_secondary_score(primary_score):
    return primary_to_secondary.get(primary_score, 0)

# Инициализация базы данных для Quize
def init_quiz_db():
    global quiz_conn, quiz_cursor
    try:
        logging.info("Инициализация базы данных quiz.db")
        quiz_conn = sqlite3.connect("quiz.db", check_same_thread=False)
        quiz_cursor = quiz_conn.cursor()

        # Удаляем только таблицу quiz_tasks, чтобы задачи могли быть загружены заново
        quiz_cursor.execute('DROP TABLE IF EXISTS quiz_tasks')
        quiz_conn.commit()
        logging.info("Таблица quiz_tasks сброшена")

        # Создаём таблицу quiz_tasks, если её нет
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                option INTEGER,
                day INTEGER,
                task_number INTEGER,
                image_url TEXT,
                correct_answer TEXT
            )''')
        logging.info("Таблица quiz_tasks создана")

        # Удаляем старую таблицу user_quiz_progress, чтобы пересоздать с правильной схемой
        quiz_cursor.execute('DROP TABLE IF EXISTS user_quiz_progress')
        quiz_conn.commit()

        # Создаём таблицу user_quiz_progress с правильной схемой
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_progress (
                user_id INTEGER,
                quiz_id INTEGER,
                task_number INTEGER,
                user_answer TEXT,
                attempt_id INTEGER,  -- Добавляем столбец attempt_id
                option INTEGER,
                timestamp TEXT,
                PRIMARY KEY (user_id, quiz_id, task_number, attempt_id, option)
            )''')

        # Создаём таблицу user_quiz_state, если её нет
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_state (
                user_id INTEGER,
                option INTEGER,
                day INTEGER,
                task_number INTEGER,
                attempt_id INTEGER,
                primary_score INTEGER DEFAULT 0,
                secondary_score INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                timestamp TEXT,
                username TEXT,
                PRIMARY KEY (user_id, option, day, attempt_id)
            )''')

        # Создаём таблицу user_data_temp для хранения состояния user_data
        quiz_cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data_temp (
                user_id INTEGER PRIMARY KEY,
                data TEXT
            )''')

        # Проверяем, существует ли столбец username, и добавляем его, если отсутствует
        quiz_cursor.execute('PRAGMA table_info(user_quiz_state)')
        columns = {col[1] for col in quiz_cursor.fetchall()}
        if 'username' not in columns:
            quiz_cursor.execute('ALTER TABLE user_quiz_state ADD COLUMN username TEXT')
            quiz_conn.commit()
            logging.info("Столбец username добавлен в таблицу user_quiz_state")

        quiz_conn.commit()
        logging.info("✅ База данных quiz.db успешно инициализирована")
    except sqlite3.Error as e:
        logging.error(f"❌ Ошибка при инициализации базы данных quiz.db: {e}")
        raise

# Проверяем, что таблица существует и задачи загружены
try:
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM quiz_tasks')
    task_count = cursor.fetchone()[0]
    cursor.close()
    if task_count == 0:
        logging.error("Критическая ошибка: задачи не загружены в таблицу quiz_tasks!")
    else:
        logging.info(f"Успешно загружено {task_count} задач в таблицу quiz_tasks.")
except sqlite3.OperationalError as e:
    logging.error(f"Ошибка при проверке таблицы quiz_tasks: {e}")
    logging.info("Таблица quiz_tasks еще не создана или недоступна. Продолжаем выполнение.")

# Функция для очистки задач (больше не удаляем старые варианты)
def clear_quiz_tasks():
    try:
        quiz_cursor.execute('DELETE FROM quiz_tasks')  # Очищаем все задачи перед загрузкой новых
        quiz_conn.commit()
        logging.info("Очищены все задачи перед загрузкой новых")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при очистке задач: {e}")

# Функция для загрузки задач из CSV
def load_quiz_from_csv(filename):
    try:
        # Очищаем старые задачи
        logging.info("Очищены все задачи перед загрузкой новых")
        clear_quiz_tasks()
        
        # Если файл не в текущем каталоге, ищем его в родительском и корневом
        if not os.path.exists(filename):
            parent_path = os.path.join('..', filename)
            root_path = os.path.join('/', filename)
            
            if os.path.exists(parent_path):
                filename = parent_path
                logging.info(f"Найден файл {filename} в родительском каталоге")
            elif os.path.exists(root_path):
                filename = root_path
                logging.info(f"Найден файл {filename} в корневом каталоге")
            else:
                logging.error(f"Файл {filename} не найден ни в одном из каталогов!")
                return False

        # Открываем файл и загружаем задачи
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)  # Загружаем все строки в список для проверки
            if not rows:
                logging.error(f"Файл {filename} пуст или не содержит данных!")
                return False

            # Загружаем задачи в базу данных
            cursor = quiz_conn.cursor()
            for row in rows:
                option = int(row['option'])  # Номер варианта
                day = option  # Вариант и день совпадают (1 вариант = 1 день)
                task_number = int(row['task_number'])
                image_url = row['image_url']  # URL фото задания
                correct_answer = row['correct_answer']
                cursor.execute('''
                    INSERT INTO quiz_tasks (option, day, task_number, image_url, correct_answer)
                    VALUES (?, ?, ?, ?, ?)
                ''', (option, day, task_number, image_url, correct_answer))
            quiz_conn.commit()
            cursor.close()
            logging.info(f"Загружено {len(rows)} задач из {filename}")

            # Проверяем, что задачи загружены
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM quiz_tasks')
            task_count = cursor.fetchone()[0]
            cursor.close()
            if task_count == 0:
                logging.error("Критическая ошибка: задачи не загружены в таблицу quiz_tasks!")
                return False
            else:
                logging.info(f"Успешно загружено {task_count} задач в таблицу quiz_tasks.")
                return True
    except Exception as e:
        logging.error(f"Ошибка при загрузке задач из {filename}: {e}")
        return False
# Инициализация базы данных и загрузка задач
try:
    init_quiz_db()
    # Загружаем задачи только один раз
    if not load_quiz_from_csv('week.csv'):
        logging.error("Не удалось загрузить задачи из week.csv. Бот может работать некорректно.")
    else:
        logging.info("Все задачи успешно загружены.")
except Exception as e:
    logging.error(f"Ошибка при инициализации quiz: {e}")

# Экран "Quize" с выбором варианта
def quiz_screen(page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все доступные варианты
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT DISTINCT option FROM quiz_tasks')
    options = sorted([int(row[0]) for row in cursor.fetchall()])
    cursor.close()
    
    # Проверка на пустой список вариантов
    if not options:
        # Если вариантов нет, просто покажем вариант 1 из week.csv
        options = [1]
    
    total_variants = len(options)

    # Пагинация: показываем до 10 вариантов на странице
    variants_per_page = 10
    start_idx = (page - 1) * variants_per_page
    end_idx = min(start_idx + variants_per_page, total_variants)
    visible_variants = options[start_idx:end_idx]

    # Добавляем кнопки для видимых вариантов
    for option in visible_variants:
        markup.add(types.InlineKeyboardButton(f"Вариант {option}", callback_data=f"start_quiz_{option}"))

    # Добавляем кнопки пагинации, если нужно
    if total_variants > variants_per_page:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=f"quiz_page_{page - 1}"))
        if end_idx < total_variants:
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=f"quiz_page_{page + 1}"))
        markup.add(*pagination_buttons)
    # Кнопка "Статистика" и "Назад"
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="quiz_stats"))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="main_back_call"))
    return markup
# Экран статистики с выбором варианта
def stats_screen(user_id, page=1):  # Добавляем user_id как параметр
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все завершённые варианты для конкретного пользователя
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT DISTINCT option FROM user_quiz_state WHERE user_id = ? AND completed = 1', (user_id,))
    variants = sorted([row[0] for row in cursor.fetchall()])
    cursor.close()
    total_variants = len(variants)

    # Пагинация: показываем до 10 вариантов на странице
    variants_per_page = 10
    start_idx = (page - 1) * variants_per_page
    end_idx = min(start_idx + variants_per_page, total_variants)
    visible_variants = variants[start_idx:end_idx]

    # Добавляем кнопки для видимых вариантов
    for variant in visible_variants:
        markup.add(types.InlineKeyboardButton(f"Вариант {variant}", callback_data=f"stats_variant_{variant}"))

    # Добавляем кнопки пагинации, если нужно
    if total_variants > variants_per_page:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=f"stats_page_{page - 1}"))
        if end_idx < total_variants:
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=f"stats_page_{page + 1}"))
        markup.add(*pagination_buttons)

    # Кнопка "Назад"
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_call"))
    return markup
# Экран статистики с выбором попытки для варианта
def stats_attempts_screen(user_id, variant, page=1):
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Получаем все завершённые попытки для данного варианта (отсортированы по времени, от старых к новым)
    cursor = quiz_conn.cursor()
    cursor.execute('''
        SELECT attempt_id, timestamp 
        FROM user_quiz_state 
        WHERE user_id = ? AND option = ? AND completed = 1 
        ORDER BY timestamp ASC
    ''', (user_id, variant))
    attempts = cursor.fetchall()
    cursor.close()
    total_attempts = len(attempts)

    logging.info(f"Найдено {total_attempts} попыток для пользователя {user_id}, вариант {variant}")

    # Пагинация: показываем до 10 попыток на странице
    attempts_per_page = 10
    start_idx = (page - 1) * attempts_per_page
    end_idx = min(start_idx + attempts_per_page, total_attempts)
    visible_attempts = attempts[start_idx:end_idx]

    # Нумерация попыток: самая старая попытка — "Попытка 1"
    for index, (attempt_id, timestamp) in enumerate(visible_attempts, start=start_idx + 1):
        try:
            attempt_id = int(attempt_id)
        except ValueError:
            logging.error(f"Некорректный attempt_id: {attempt_id}, пропускаем попытку")
            continue
        callback_data = f"stats_attempt_{variant}_{attempt_id}"  # Изменили на подчёркивание
        logging.info(f"Формирование callback_data для попытки: {callback_data}")
        markup.add(types.InlineKeyboardButton(f"Попытка {index}", callback_data=callback_data))

    # Добавляем кнопки пагинации, если нужно
    if total_attempts > attempts_per_page:
        pagination_buttons = []
        if page > 1:
            callback_prev = f"stats_attempts_page_{variant}_{page - 1}"  # Используем подчёркивание
            pagination_buttons.append(types.InlineKeyboardButton("◀️", callback_data=callback_prev))
            logging.info(f"Добавлена кнопка '◀️' с callback_data: {callback_prev}")
        if end_idx < total_attempts:
            callback_next = f"stats_attempts_page_{variant}_{page + 1}"  # Используем подчёркивание
            pagination_buttons.append(types.InlineKeyboardButton("▶️", callback_data=callback_next))
            logging.info(f"Добавлена кнопка '▶️' с callback_data: {callback_next}")
        markup.add(*pagination_buttons)

    # Кнопка "Назад"
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_stats"))
    return markup

# ================== Математический квест  ==================
challenge ={
    "6": {
        "lin": {
            "name": "Линейные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/4NQpUhK",
                    "hint": ["https://imgur.com/L4cZoLE", "https://imgur.com/gE2YTd6", "https://imgur.com/pQaYooP", "https://imgur.com/ZrIUaUf", "https://imgur.com/kc0sFah", "https://imgur.com/L4yDIHX", "https://imgur.com/K7blD33"],
                    "answer": "-17",
                    "analog": {"photo": "https://imgur.com/cNfMQA1", "answer": "-18"},
                    "homework": {"photo": "https://imgur.com/775gKq1", "answer": "6,3"}
                },
                {
                    "photo": "https://imgur.com/0JQujsF",
                    "hint": ["https://imgur.com/BDZSIEF", "https://imgur.com/2CRzthQ", "https://imgur.com/saPamdV", "https://imgur.com/DomEXt8", "https://imgur.com/h7hUDg0", "https://imgur.com/8TTg6B1"],
                    "answer": "3.5",
                    "analog": {"photo": "https://imgur.com/T5POcl8", "answer": "7"},
                    "homework": {"photo": "https://imgur.com/7Pbxuw2", "answer": "3"}
                },
                {
                    "photo": "https://imgur.com/ZhFvCpw",
                    "hint": ["https://imgur.com/Ghb9naw", "https://imgur.com/jFau90k", "https://imgur.com/ngqLbFu", "https://imgur.com/3ezX1DC", "https://imgur.com/PtSyN35"],
                    "answer": "3",
                    "analog": {"photo": "https://imgur.com/YbyWm33", "answer": "1.9"},
                    "homework": {"photo": "https://imgur.com/dCHjOe1", "answer": "1"}
                }
            ]
        },
        "quad": {
            "name": "Квадратные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/Rzfc7L2",
                    "hint": ["https://imgur.com/eEhPowi", "https://imgur.com/1JXFcGN", "https://imgur.com/B8RogGN", "https://imgur.com/5lNqfbF"],
                    "answer": "9",
                    "analog": {"photo": "https://imgur.com/yRYV33Q", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/7yDbs2t", "answer": "-3"}
                },
                {
                    "photo": "https://imgur.com/fnYsNWZ",
                    "hint": ["https://imgur.com/c2rhW30", "https://imgur.com/LkIsKKr", "https://imgur.com/6lJai7G", "https://imgur.com/wXKj0Wz", "https://imgur.com/76cu2zF"],
                    "answer": "7",
                    "analog": {"photo": "https://imgur.com/c8osUfW", "answer": "12"},
                    "homework": {"photo": "https://imgur.com/y1LAAK8", "answer": "18"}
                },
                {
                    "photo": "https://imgur.com/DhRaVsd",
                    "hint": ["https://imgur.com/OVRBMJT", "https://imgur.com/JtMSN10", "https://imgur.com/8ZwH9rA", "https://imgur.com/upsse3b", "https://imgur.com/fdPVe8r"],
                    "answer": "-4",
                    "analog": {"photo": "https://imgur.com/xoG9YsP", "answer": "-4"},
                    "homework": {"photo": "https://imgur.com/yww27op", "answer": "-2"}
                }
            ]
        },
        "odd": {
            "name": "Уравнения нечётных степеней",
            "tasks": [
                {
                    "photo": "https://imgur.com/wHOWnt5",
                    "hint": ["https://imgur.com/h0jJ1Ew", "https://imgur.com/4uHDGBb", "https://imgur.com/BRxwuEi"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/myTyMdj", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/BngCzDi", "answer": "-4"}
                }
            ]
        },
        "frac": {
            "name": "Дробно-рациональные урав-я",
            "tasks": [
                {
                    "photo": "https://imgur.com/9q8GbH3",
                    "hint": ["https://imgur.com/hFjIgRS", "https://imgur.com/Erb50IQ", "https://imgur.com/oLwZt6U", "https://imgur.com/aZaR4WL", "https://imgur.com/rDgsCKY"],
                    "answer": "0.45",
                    "analog": {"photo": "https://imgur.com/CF8cD5a", "answer": "0.875"},
                    "homework": {"photo": "https://imgur.com/ZlDIypW", "answer": "-0.6875"}
                },
                {
                    "photo": "https://imgur.com/sNUY4tV",
                    "hint": ["https://imgur.com/5HFweRZ", "https://imgur.com/TWSptG4", "https://imgur.com/2MNOcYR", "https://imgur.com/g1rCj6K", "https://imgur.com/cALRPwV"],
                    "answer": "4",
                    "analog": {"photo": "https://imgur.com/K8KuJRo", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/P9KQhVI", "answer": "2,4"}
                },
                {
                    "photo": "https://imgur.com/onm5Kmd",
                    "hint": ["https://imgur.com/3sgncXW", "https://imgur.com/M9lOT6K", "https://imgur.com/LkFp2Pk", "https://imgur.com/zlYkjAY", "https://imgur.com/p8bPGHB"],
                    "answer": "15",
                    "analog": {"photo": "https://imgur.com/7NTpN7f", "answer": "29"},
                    "homework": {"photo": "https://imgur.com/XJKug8M", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/hH7qdVl",
                    "hint": ["https://imgur.com/60AYjuN", "https://imgur.com/WwYf2V4", "https://imgur.com/miopmey", "https://imgur.com/6eX76I4", "https://imgur.com/fBVeCbz", "https://imgur.com/U18Isdr"],
                    "answer": "4",
                    "analog": {"photo": "https://imgur.com/LaH0csS", "answer": "4"},
                    "homework": {"photo": "https://imgur.com/aeDV8iD", "answer": "10"}
                },
                {
                    "photo": "https://imgur.com/sRQnt6K",
                    "hint": ["https://imgur.com/ZjJWEzb", "https://imgur.com/NzOSjBe", "https://imgur.com/6Ng8vIp", "https://imgur.com/neUC8qw", "https://imgur.com/OXmCdrg", "https://imgur.com/rrf2URv", "https://imgur.com/Tze5uqC", "https://imgur.com/y1jc1wY"],
                    "answer": "-8",
                    "analog": {"photo": "https://imgur.com/IenzECq", "answer": "-5"},
                    "homework": {"photo": "https://imgur.com/OtPX1ia", "answer": "-3,5"}
                }
            ]
        },
        "irr": {
            "name": "Иррациональные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/Ip0TUQC",
                    "hint": ["https://imgur.com/3MU4mFu", "https://imgur.com/XkUMRf4", "https://imgur.com/Z4M94Tj", "https://imgur.com/6aMGDOV"],
                    "answer": "12",
                    "analog": {"photo": "https://imgur.com/35MK172", "answer": "4"},
                    "homework": {"photo": "https://imgur.com/xDOtDdW", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/5ZdpMIi",
                    "hint": ["https://imgur.com/N4IGBvC", "https://imgur.com/yfxlbvm"],
                    "answer": "19",
                    "analog": {"photo": "https://imgur.com/cNTIHp0", "answer": "28"},
                    "homework": {"photo": "https://imgur.com/wkHEBve", "answer": "62"}
                },
                {
                    "photo": "https://imgur.com/QmQGLYj",
                    "hint": ["https://imgur.com/3rxVmIN", "https://imgur.com/nx07HS1", "https://imgur.com/2bW7SG7", "https://imgur.com/q6yjjcB", "https://imgur.com/ERo0BoR", "https://imgur.com/5c39Lb6"],
                    "answer": "20",
                    "analog": {"photo": "https://imgur.com/J0OhUv3", "answer": "5"},
                    "homework": {"photo": "https://imgur.com/YnOT1um", "answer": "9"}
                },
                {
                    "photo": "https://imgur.com/M5LMPbe",
                    "hint": ["https://imgur.com/PiS29MY", "https://imgur.com/gHAMKaz", "https://imgur.com/vKMqLx2", "https://imgur.com/jVO313F", "https://imgur.com/h7fBPjo", "https://imgur.com/ybYtEkV"],
                    "answer": "-8",
                    "analog": {"photo": "https://imgur.com/Wgp1vQh", "answer": "-12"},
                    "homework": {"photo": "https://imgur.com/hreMMUh", "answer": "-8,5"}
                }
            ]
        },
        "log": {
            "name": "Логарифмические уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/NZqLSwp",
                    "hint": ["https://imgur.com/6OsYCxE", "https://imgur.com/PBZ1IYp", "https://imgur.com/a33ByAX"],
                    "answer": "-6",
                    "analog": {"photo": "https://imgur.com/nWH5CMb", "answer": "-5"},
                    "homework": {"photo": "https://imgur.com/AOhuKPi", "answer": "1"}
                },
                {
                    "photo": "https://imgur.com/2RcdQTf",
                    "hint": ["https://imgur.com/WMElPaz", "https://imgur.com/6mPePlu", "https://imgur.com/a4zhJvO", "https://imgur.com/doel9Ro"],
                    "answer": "-7",
                    "analog": {"photo": "https://imgur.com/NEVciY8", "answer": "-6"},
                    "homework": {"photo": "https://imgur.com/4hWyrM6", "answer": "-71"}
                },
                {
                    "photo": "https://imgur.com/CspBO7d",
                    "hint": ["https://imgur.com/p9Y9Ylp", "https://imgur.com/Wqfb4jW", "https://imgur.com/3beIbAP", "https://imgur.com/7XM0fz8", "https://imgur.com/vGvQ4Pv"],
                    "answer": "85",
                    "analog": {"photo": "https://imgur.com/XwnbO6A", "answer": "-4"},
                    "homework": {"photo": "https://imgur.com/ZdUwBQA", "answer": "93"}
                },
                {
                    "photo": "https://imgur.com/MRWlYjO",
                    "hint": ["https://imgur.com/5nSBDtH", "https://imgur.com/knHiJZQ", "https://imgur.com/1yByr0h", "https://imgur.com/des8TR3"],
                    "answer": "3",
                    "analog": {"photo": "https://imgur.com/Flz6mly", "answer": "3"},
                    "homework": {"photo": "https://imgur.com/Sj8S3aX", "answer": "3"}
                },
                {
                    "photo": "https://imgur.com/m0SmA8I",
                    "hint": ["https://imgur.com/apJZ3cU", "https://imgur.com/XAPCGbE", "https://imgur.com/yA1GPHV", "https://imgur.com/vfzRgtb", "https://imgur.com/zrTw5PD"],
                    "answer": "-20",
                    "analog": {"photo": "https://imgur.com/VFy0H17", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/NuD7q1J", "answer": "-8"}
                },
                {
                    "photo": "https://imgur.com/r7YIn94",
                    "hint": ["https://imgur.com/GPYe9hW", "https://imgur.com/wR4AU0r", "https://imgur.com/wJQ2PyP", "https://imgur.com/7ODxTzb"],
                    "answer": "2",
                    "analog": {"photo": "https://imgur.com/dhSDJfV", "answer": "-0.2"},
                    "homework": {"photo": "https://imgur.com/OMtU0qV", "answer": "-2"}
                },
                {
                    "photo": "https://imgur.com/SnBlk8t",
                    "hint": ["https://imgur.com/LGAt5ta", "https://imgur.com/9v8idFn", "https://imgur.com/MvEII24", "https://imgur.com/tSxpSXr", "https://imgur.com/ahL3sQx"],
                    "answer": "0",
                    "analog": {"photo": "https://imgur.com/lkKpvIZ", "answer": "0"},
                    "homework": {"photo": "https://imgur.com/PIHrPYO", "answer": "1,25"}
                },
                {
                    "photo": "https://imgur.com/cZ1WfqQ",
                    "hint": ["https://imgur.com/NN6FCjF", "https://imgur.com/BVDxE0j", "https://imgur.com/zhMuMUl", "https://imgur.com/QE4lDKZ", "https://imgur.com/JWxPvy3", "https://imgur.com/9qdbs5a"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/Xb2Vjc0", "answer": "1"},
                    "homework": {"photo": "https://imgur.com/cYljXWg", "answer": "1"}
                },
                {
                    "photo": "https://imgur.com/RZW1y8X",
                    "hint": ["https://imgur.com/UgTz0U5", "https://imgur.com/q0VTSjH", "https://imgur.com/zplCbbp", "https://imgur.com/YssB1LG", "https://imgur.com/XN5LlE7"],
                    "answer": "6",
                    "analog": {"photo": "https://imgur.com/q26bYlk", "answer": "6"},
                    "homework": {"photo": "https://imgur.com/U18Zoie", "answer": "7"}
                }
            ]
        },
        "exp": {
            "name": "Показательные уравнения",
            "tasks": [
                {
                    "photo": "https://imgur.com/2OkH42p",
                    "hint": ["https://imgur.com/h2aIuOz", "https://imgur.com/kf0a3fk", "https://imgur.com/WWaxPu5"],
                    "answer": "-5",
                    "analog": {"photo": "https://imgur.com/Ho28Hqu", "answer": "-6"},
                    "homework": {"photo": "https://imgur.com/JZeBEnO", "answer": "-3,5"}
                },
                {
                    "photo": "https://imgur.com/5MgRIzz",
                    "hint": ["https://imgur.com/PXNCQPU", "https://imgur.com/dEp50cS", "https://imgur.com/ufEp8E6", "https://imgur.com/uuoKfhR", "https://imgur.com/ZN3qvph"],
                    "answer": "1.25",
                    "analog": {"photo": "https://imgur.com/jXGrttf", "answer": "7"},
                    "homework": {"photo": "https://imgur.com/tyMsyig", "answer": "0,8"}
                },
                {
                    "photo": "https://imgur.com/JrwTbFI",
                    "hint": ["https://imgur.com/c8NtG0y", "https://imgur.com/xBBtmI1", "https://imgur.com/smKETZx", "https://imgur.com/EiNUHwP", "https://imgur.com/f4eBHlU"],
                    "answer": "2.5",
                    "analog": {"photo": "https://imgur.com/44ZZq5n", "answer": "2.5"},
                    "homework": {"photo": "https://imgur.com/ZmkKkI2", "answer": "0,3"}
                },
                {
                    "photo": "https://imgur.com/ln93w42",
                    "hint": ["https://imgur.com/dTmFSmJ", "https://imgur.com/1mPXuOm", "https://imgur.com/Q9ZdDTJ", "https://imgur.com/IpH0mbj", "https://imgur.com/bTBCrhM", "https://imgur.com/2gyD7mb"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/839oweU", "answer": "0.6"},
                    "homework": {"photo": "https://imgur.com/rxofpvz", "answer": "0,8"}
                },
                {
                    "photo": "https://imgur.com/AGH84E0",
                    "hint": ["https://imgur.com/JIBGx9g", "https://imgur.com/B9o3fjv", "https://imgur.com/DGsLTUG", "https://imgur.com/WB6G1dq", "https://imgur.com/nEvgEAC", "https://imgur.com/ZAGHL6b"],
                    "answer": "31",
                    "analog": {"photo": "https://imgur.com/RevlHe5", "answer": "125.5"},
                    "homework": {"photo": "https://imgur.com/lmVkhcT", "answer": "16,75"}
                },
                {
                    "photo": "https://imgur.com/m9Po1PX",
                    "hint": ["https://imgur.com/hhVzHo5", "https://imgur.com/2LmRxJH", "https://imgur.com/JBIn95G", "https://imgur.com/eaHrCe6", "https://imgur.com/tzjIf6Z", "https://imgur.com/aaldMwO", "https://imgur.com/6miJi10", "https://imgur.com/nb55pIT", "https://imgur.com/aqm0zx1"],
                    "answer": "3.25",
                    "analog": {"photo": "https://imgur.com/2NXP3IY", "answer": "8"},
                    "homework": {"photo": "https://imgur.com/Rn1GIj1", "answer": "2"}
                },
                {
                    "photo": "https://imgur.com/d9fQTX7",
                    "hint": ["https://imgur.com/ci1nc88", "https://imgur.com/Ue4Y4ca", "https://imgur.com/PDEsmwM", "https://imgur.com/MwrnAtO", "https://imgur.com/4v2V1vs"],
                    "answer": "1",
                    "analog": {"photo": "https://imgur.com/5OVse3v", "answer": "0.2"},
                    "homework": {"photo": "https://imgur.com/l9arGB5", "answer": "0,6"}
                }
            ]
        }
    }
}

# Определение миров для квеста
QUEST_WORLDS = [
    {
        "id": 6,
        "name": "Мир Простейших Уравнений",
        "description": "Мир Простейших Уравнений",
        "image": "https://i.imgur.com/Z0Io2Jf.jpg",
        "loaded_image": "https://i.imgur.com/Z0Io2Jf.jpg",
        "unlocked": True
    },
    {
        "id": 1,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 2,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 3,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 4,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 5,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 7,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 8,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 9,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 10,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 11,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    },
    {
        "id": 12,
        "name": "Мир находится в разработке...",
        "description": "🔧 Этот мир сейчас находится в разработке. Следите за обновлениями — скоро здесь появится нечто интересное!\n\n⚠️ Этот мир пока недоступен, но когда он откроется, вас ждут новые захватывающие математические приключения и еще более сложные головоломки.\n\n🔮 Возвращайтесь позже, чтобы проверить, доступен ли этот мир!",
        "image": "https://imgur.com/dOEwecR.jpg",
        "loaded_image": "https://imgur.com/dOEwecR.jpg",
        "unlocked": False
    }
]

def init_quest_db():
    """Инициализация базы данных для квеста"""
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    
    # Таблица для хранения прогресса пользователей в квесте
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        world_id INTEGER NOT NULL,
        completed_tasks INTEGER DEFAULT 0,
        total_tasks INTEGER DEFAULT 0,
        date_updated TEXT NOT NULL,
        UNIQUE(user_id, world_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("✅ Таблица 'world_progress' создана или уже существует!")
    
    # Функциональность избранного удалена

def get_world_progress(user_id, world_id, force_recount=False):
    """Получение прогресса пользователя в конкретном мире
    
    Параметры:
        user_id (str): ID пользователя
        world_id (str|int): ID мира
        force_recount (bool): Принудительно пересчитать количество выполненных задач
    """
    # Подсчитываем общее количество заданий в мире (всегда актуальное)
    total_tasks = 0
    world_challenges = challenge.get(str(world_id), {})
    for category in world_challenges.values():
        total_tasks += len(category['tasks'])
    
    # Минимальное количество стандартных заданий в мире
    if total_tasks < 32:
        total_tasks = 32

    homework_count = 0
    try:
        # Используем task_progress.db для подсчета домашних заданий
        conn_task = sqlite3.connect('task_progress.db')
        cursor_task = conn_task.cursor()
        
        # Запрос на получение количества домашних заданий для конкретного пользователя и мира
        cursor_task.execute("""
            SELECT COUNT(*) FROM task_progress 
            WHERE user_id = ? AND challenge_num = ? AND type = 'homework'
        """, (user_id, str(world_id)))
        
        result = cursor_task.fetchone()
        if result and result[0] > 0:
            homework_count = result[0]
            logging.info(f"Найдено {homework_count} домашних заданий для пользователя {user_id} в мире {world_id}")
        
        conn_task.close()
    except Exception as e:
        logging.error(f"Ошибка при подсчете домашних заданий: {e}")
    
    # Добавляем домашние задания к общему количеству
    # Домашние задания отдельно учитываются в общем числе
    total_tasks += homework_count
    
    # Получаем информацию о завершенных заданиях
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    
    # Здесь измененный код для подсчета прогресса
    completed_tasks = 0
    
    if force_recount:
        try:
            # Подсчитываем количество задач со статусом "correct" в базе task_progress.db
            conn_task = sqlite3.connect('task_progress.db')
            cursor_task = conn_task.cursor()
            
            # Запрос на получение количества правильно решенных основных задач
            cursor_task.execute("""
                SELECT COUNT(DISTINCT cat_code || '_' || task_idx) FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND status = 'correct' AND type = 'main'
            """, (user_id, str(world_id)))
            
            result = cursor_task.fetchone()
            if result:
                main_completed_tasks = result[0]
                logging.info(f"✅✅✅ Пересчет прогресса: найдено {main_completed_tasks} правильно решенных основных задач для пользователя {user_id} в мире {world_id}")
            else:
                main_completed_tasks = 0
                
            # Запрос на получение количества правильно решенных домашних заданий
            cursor_task.execute("""
                SELECT COUNT(DISTINCT cat_code || '_' || task_idx) FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND status = 'correct' AND type = 'homework'
            """, (user_id, str(world_id)))
            
            result = cursor_task.fetchone()
            if result:
                homework_completed_tasks = result[0]
                logging.info(f"✅✅✅ Пересчет прогресса: найдено {homework_completed_tasks} правильно решенных домашних заданий для пользователя {user_id} в мире {world_id}")
            else:
                homework_completed_tasks = 0
                
            # Суммируем количество правильно решенных задач
            completed_tasks = main_completed_tasks + homework_completed_tasks
            logging.info(f"✅✅✅ Общее количество правильно решенных задач: {completed_tasks} для пользователя {user_id} в мире {world_id}")
            
            conn_task.close()
        except Exception as e:
            logging.error(f"❌❌❌ Ошибка при пересчете правильно решенных задач: {e}")
    
    # Создаем переменную msk_time сразу, чтобы избежать ошибки UnboundLocalError
    msk_time = datetime.now() + timedelta(hours=3)
    
    cursor.execute("SELECT completed_tasks, total_tasks FROM world_progress WHERE user_id = ? AND world_id = ?", 
                  (user_id, world_id))
    row = cursor.fetchone()
    
    if row:
        # Если force_recount=False, используем значение из базы
        if not force_recount:
            completed_tasks = row[0]
        
        # Обновляем данные в базе с московским временем (UTC+3)
        cursor.execute(
            "UPDATE world_progress SET completed_tasks = ?, total_tasks = ?, date_updated = ? WHERE user_id = ? AND world_id = ?",
            (completed_tasks, total_tasks, msk_time.strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
        )
    else:
        # Если записи нет, создаем запись в базе данных с московским временем (UTC+3)
        cursor.execute(
            "INSERT INTO world_progress (user_id, world_id, completed_tasks, total_tasks, date_updated) VALUES (?, ?, ?, ?, ?)",
            (user_id, world_id, completed_tasks, total_tasks, msk_time.strftime("%Y-%m-%d %H:%M:%S"))
        )
    
    conn.commit()
    conn.close()
    
    # Включаем названия ключей как в коде handle_quest_progress_map
    return {"completed_tasks": completed_tasks, "total_tasks": total_tasks}

def update_world_progress(user_id, world_id, completed=None):
    """Обновление прогресса пользователя в конкретном мире"""
    conn = sqlite3.connect('quest.db')
    cursor = conn.cursor()
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если completed задан явно, используем его,
    # иначе пересчитываем количество выполненных задач на основе базы данных
    if completed is not None:
        # Используем московское время (UTC+3)
        msk_time = datetime.now() + timedelta(hours=3)
        cursor.execute(
            "UPDATE world_progress SET completed_tasks = ?, date_updated = ? WHERE user_id = ? AND world_id = ?",
            (completed, msk_time.strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
        )
    else:
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновляем только дату и 
        # принудительно пересчитываем выполненные задачи для точного отображения прогресса
        try:
            # Получаем прогресс с принудительным пересчетом количества задач
            progress_data = get_world_progress(user_id, world_id, force_recount=True)
            logging.info(f"🔄 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Пересчитан прогресс для пользователя {user_id} в мире {world_id}: {progress_data}")
            
            # Используем московское время (UTC+3)
            msk_time = datetime.now() + timedelta(hours=3)
            
            # Обновляем таблицу прогресса с новыми данными
            cursor.execute(
                "UPDATE world_progress SET completed_tasks = ?, date_updated = ? WHERE user_id = ? AND world_id = ?",
                (progress_data['completed_tasks'], msk_time.strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
            )
            logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновлен прогресс для пользователя {user_id} в мире {world_id}")
        except Exception as e:
            # В случае ошибки просто обновляем дату
            logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Ошибка при пересчете прогресса: {e}")
            # Убеждаемся, что msk_time инициализировано в блоке catch
            msk_time = datetime.now() + timedelta(hours=3)
            cursor.execute(
                "UPDATE world_progress SET date_updated = ? WHERE user_id = ? AND world_id = ?",
                (msk_time.strftime("%Y-%m-%d %H:%M:%S"), user_id, world_id)
            )
    
    conn.commit()
    conn.close()

def handle_mathquest_call(call):
    """Обработчик для математического квеста"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Отправляем главный экран математического квеста
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Ты — герой, который проходит ЕГЭ как фэнтези-приключение.\n"
                                                            "Выбирай мир и решай задания."),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=math_quest_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл математический квест")
    except Exception as e:
        logging.error(f"Ошибка при открытии математического квеста: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки математического квеста.")

def handle_quest_select_world(call):
    """Обработчик выбора мира в квесте"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем текущий индекс или устанавливаем 0, если это первый вызов
    data_parts = call.data.split('_')
    
    # Проверяем, не является ли вызов из кнопки "Назад"
    if data_parts[-1] == "worlds":
        current_index = 0  # По умолчанию показываем первый мир
    else:
        # Получаем индекс из параметра, если он есть
        current_index = int(data_parts[-1]) if len(data_parts) > 3 else 0
    
    try:
        # Получаем текущий мир для отображения
        world = QUEST_WORLDS[current_index]
        
        # Отображаем список миров с изображением текущего мира
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выбери мир для исследования:\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(current_index, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {call.from_user.id} просматривает список миров")
    except Exception as e:
        logging.error(f"Ошибка при отображении списка миров: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки списка миров.")

def handle_quest_profile(call):
    """Обработчик просмотра профиля героя"""
    from instance import photo_quest_profile
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text=(
          "Здесь появится всё, что ты накопил в квесте: твой скин, уровень, шкала опыта и количество заработанной голды.\n\n"
          "Следи за прогрессом, развивай персонажа — и стань легендой этого мира. Скоро.")

    try:
        # Временная заглушка для профиля
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_profile, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_profile_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл профиль героя")
    except Exception as e:
        logging.error(f"Ошибка при отображении профиля героя: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки профиля героя.")

def handle_quest_trophies(call):
    """Обработчик просмотра хранилища трофеев"""
    from instance import photo_quest_trophies
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = ("Каждый трофей — это память о победе.\n\n "
            "Здесь будут храниться артефакты и находки, которые ты получил, проходя миры и сражаясь с боссами.Пока пусто. Но ненадолго."
            )
    try:
        # Временная заглушка для трофеев
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_trophies, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_trophies_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл хранилище трофеев")
    except Exception as e:
        logging.error(f"Ошибка при отображении хранилища трофеев: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки хранилища трофеев.")

def handle_quest_shop(call):
    """Обработчик просмотра лавки скинов"""
    from instance import photo_quest_shop
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    text = ("Здесь можно будет переодеть героя: выбрать стиль, купить скин, собрать уникальный образ.\n\n"
            "Боевой доспех, плащ мага или что-то совсем неожиданное — всё будет.\n"
            "Лавка пока закрыта, но готовится к открытию."
    )
    try:
        # Временная заглушка для магазина
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_shop, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_shop_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} открыл лавку скинов")
    except Exception as e:
        logging.error(f"Ошибка при отображении лавки скинов: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки лавки скинов.")

def handle_quest_navigation(call):
    """Обработчик навигации по списку миров"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    try:
        # Определяем направление и текущий индекс
        data_parts = call.data.split('_')
        direction = data_parts[-2]
        current_index = int(data_parts[-1])
        
        # Вычисляем новый индекс в зависимости от направления
        if direction == "next":
            new_index = current_index + 1
            if new_index >= len(QUEST_WORLDS):
                new_index = 0
        else:  # "prev"
            new_index = current_index - 1
            if new_index < 0:
                new_index = len(QUEST_WORLDS) - 1
        
        # Получаем новый мир для отображения
        world = QUEST_WORLDS[new_index]
        
        # Обновляем экран выбора мира
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выбери мир для исследования:\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(new_index, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {call.from_user.id} навигирует по списку миров ({direction}, индекс: {new_index})")
    except Exception as e:
        logging.error(f"Ошибка при навигации по списку миров: {e}")
        bot.answer_callback_query(call.id, "Ошибка при навигации по списку миров.")

def handle_quest_enter_world(call):
    """Обработчик входа в выбранный мир"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Получаем ID выбранного мира из колбэка (текущий индекс в списке)
    world_index = int(call.data.split('_')[-1])
    
    # Найти соответствующий мир по индексу из общего массива
    if world_index >= 0 and world_index < len(QUEST_WORLDS):
        world = QUEST_WORLDS[world_index]
    else:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return
    
    # Проверяем доступность мира
    if not world["unlocked"]:
        bot.answer_callback_query(call.id, "⚠️ Этот мир пока недоступен")
        return
    
    # Анимация загрузки мира
    # Согласно требованиям должна быть первая строка "Загрузка мира..." и 
    # вторая строка с прогресс-баром и тематическим сообщением
    
    loading_bars = [
        "[███░░░░░░░░░░░░░░░] 17%",
        "[█████░░░░░░░░░░░░] 33%",
        "[████████░░░░░░░░░] 51%",
        "[███████████░░░░░░] 68%",
        "[██████████████░░] 85%",
        "[████████████████] 100%"
    ]
    
    loading_messages = [
        "Всё делится. Даже ты.",
        "Скидка на здравый смысл: -50%.",
        "Числа растут. Ценность — нет.",
        "Контракт подписан. Шрифт — неясен",
        "Проценты сложились. Ты — нет.",
        "Добро пожаловать. Всё уже не твоё."
    ]
    # Отправляем серию сообщений с анимацией загрузки
    for i in range(6):
        caption = f"Загрузка мира...\n\n{loading_bars[i]}\n{loading_messages[i]}"
        
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None
        )
        
        # Задержка для анимации (0.5 секунд между кадрами)
        time.sleep(0.5)
    
    # Загрузка завершена, показываем мир
    world_id = world["id"]  # Получаем ID мира для БД
    
    # Логируем описание мира, чтобы увидеть, что передается боту
    logging.info(f"Вход в мир, загрузка описания: '{world['description']}'")
    
    # Получаем изображение в зависимости от прогресса пользователя
    world_image = get_world_progress_image(user_id, world_id)
    
    # Проверяем, является ли путь локальным файлом или URL
    import os
    
    try:
        if os.path.isfile(world_image):
            # Если это локальный файл, открываем его и отправляем
            with open(world_image, 'rb') as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo, caption=world['description']),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=loaded_world_screen(world_id)
                )
                logging.info(f"Отправлено локальное изображение карты прогресса: {world_image}")
        else:
            # Если это URL, отправляем как обычно
            bot.edit_message_media(
                media=InputMediaPhoto(world_image, caption=world['description']),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=loaded_world_screen(world_id)
            )
            logging.info(f"Отправлен URL изображения карты прогресса: {world_image}")
    except Exception as e:
        # В случае ошибки используем резервное изображение
        logging.error(f"Ошибка при отправке изображения карты: {e}")
        fallback_url = f"https://imgur.com/qc6fZ6S.jpg?t={int(time.time())}"
        bot.edit_message_media(
            media=InputMediaPhoto(fallback_url, caption=world['description']),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=loaded_world_screen(world_id)
        )
        logging.info(f"Отправлен резервный URL изображения")
    
    # Обновляем прогресс пользователя с принудительным пересчётом
    get_world_progress(user_id, world_id, force_recount=True)  # Это создаст запись, если её нет и обновит прогресс

# Глобальные переменные для генерации карт с гусем
MAP_IMAGES = {
    '0_10': photo_world_progress_0_10,
    '10_20': photo_world_progress_10_20,
    '20_30': photo_world_progress_20_30,
    '30_40': photo_world_progress_30_40,
    '40_50': photo_world_progress_40_50,
    '50_60': photo_world_progress_50_60,
    '60_70': photo_world_progress_60_70,
    '70_80': photo_world_progress_70_80,
    '80_90': photo_world_progress_80_90,
    '90_100': photo_world_progress_90_100,
}
# Координаты для размещения гуся на разных картах в зависимости от прогресса
GOOSE_MAP_POSITIONS = {
    '0_10': {
        'start': (900, 450),    # 0-3%
        'middle': (500, 515),   # 4-6%
        'end': (405, 910)       # 7-9%
    },
    '10_20': {
        'start': (100, 445),    # 10-13%
        'middle': (445, 575),   # 14-16%
        'end': (840, 805)       # 17-19%
    },
    '20_30': {
        'start': (155, 205),    # 20-23%
        'middle': (500, 530),   # 24-26%
        'end': (440, 910)       # 27-29%
    },
    '30_40': {
        'start': (365, 185),    # 30-33%
        'middle': (545, 530),   # 34-36%
        'end': (650, 915)       # 37-39%
    },
    '40_50': {
        'start': (290, 900),    # 40-43%
        'middle': (640, 560),   # 44-46%
        'end': (455, 155)       # 47-49%
    },
    '50_60': {
        'start': (500, 905),    # 50-53%
        'middle': (420, 590),   # 54-56%
        'end': (500, 190)       # 57-59%
    },
    '60_70': {
        'start': (320, 745),    # 60-63%
        'middle': (620, 545),   # 64-66%
        'end': (890, 345)       # 67-69%
    },
    '70_80': {
        'start': (160, 270),    # 70-73%
        'middle': (465, 445),   # 74-76%
        'end': (590, 875)       # 77-79%
    },
    '80_90': {
        'start': (400, 810),    # 80-83%
        'middle': (565, 480),   # 84-86%
        'end': (910, 255)       # 87-89%
    },
    '90_100': {
        'start': (470, 940),    # 90-93%
        'middle': (570, 680),   # 94-96%
        'end': (500, 485)       # 97-100%
    }
}

PROGRESS_MAP_IMAGES = {
    '0_10': photo_world_map_progress_0_10,
    '10_20': photo_world_map_progress_10_20,
    '20_30': photo_world_map_progress_20_30,
    '30_40': photo_world_map_progress_30_40,
    '40_50': photo_world_map_progress_40_50,
    '50_60': photo_world_map_progress_50_60,
    '60_70': photo_world_map_progress_60_70,
    '70_80': photo_world_map_progress_70_80,
    '80_90': photo_world_map_progress_80_90,
    '90_100': photo_world_map_progress_90_100,
}

GOOSE_PROGRESS_MAP_POSITIONS = {
    '0_10': {},  # Гуся нету
    '10_20': {
        'start': (45, 180),     # 10-13%
        'middle': (170, 235),   # 14-16%
        'end': (345, 335),      # 17-19%
    },
    '20_30': {
        'start': (355, 515),    # 20-23%
        'middle': (215, 640),   # 24-26%
        'end': (240, 805),      # 27-29%
    },
    '30_40': {
        'start': (135, 900),    # 30-33%
        'middle': (235, 1080),  # 34-36%
        'end': (270, 1230),     # 37-39%
    },
    '40_50': {
        'start': (550, 1230),   # 40-43%
        'middle': (690, 1090),  # 44-46%
        'end': (620, 900),      # 47-49%
    },
    '50_60': {
        'start': (630, 810),    # 50-53%
        'middle': (620, 630),   # 54-56%
        'end': (640, 480),      # 57-59%
    },
    '60_70': {
        'start': (610, 370),    # 60-63%
        'middle': (670, 225),   # 64-66%
        'end': (810, 135),      # 67-69%
    },
    '70_80': {
        'start': (1030, 1215),  # 70-73%
        'middle': (1070, 1050), # 74-76%
        'end': (1235, 940),     # 77-79%
    },
    '80_90': {
        'start': (1115, 770),   # 80-83%
        'middle': (1045, 625),  # 84-86%
        'end': (900, 560),      # 87-89%
    },
    '90_100': {
        'start': (1050, 390),   # 90-93%
        'middle': (1090, 285),  # 94-96%
        'end': (1065, 200),     # 97-100%
    }
}

def generate_progress_map(progress_percent, fallback_url=None):
    """
    Генерирует карту прогресса с гусем, расположенным в зависимости от процента прогресса.
    
    Args:
        progress_percent (float): Процент выполнения от 0 до 100
        fallback_url (str, optional): URL для возврата в случае ошибки
        
    Returns:
        str: Путь к сгенерированному изображению или fallback_url в случае ошибки
    """
    try:
        # Определяем диапазон прогресса и позицию
        image_range = get_progress_range(progress_percent)
        position = get_position_in_range(progress_percent, image_range)
        
        # Получаем путь к карте для текущего диапазона
        map_path = get_map_path(image_range)
        if not map_path:
            logging.error(f"Карта для диапазона {image_range} не найдена")
            return fallback_url
        
        # Загружаем изображение карты
        try:
            map_image = Image.open(map_path)
            logging.info(f"Загружена карта: {map_path}")
        except Exception as e:
            logging.error(f"Ошибка при загрузке карты {map_path}: {e}")
            return fallback_url
        
        # Загружаем изображение гуся
        try:
            if os.path.exists(goose_common_photo):
                goose_image = Image.open(goose_common_photo)
                logging.info(f"Загружен гусь: {goose_common_photo}")
        except Exception as e:
            logging.error(f"Ошибка при загрузке гуся {goose_common_photo}: {e}")
            return fallback_url
        
        # Получаем координаты для гуся
        try:
            goose_x, goose_y = GOOSE_MAP_POSITIONS[image_range][position]
            logging.info(f"Выбраны координаты для гуся: ({goose_x}, {goose_y})")
        except KeyError:
            logging.error(f"Не найдены координаты для диапазона {image_range} и позиции {position}")
            return fallback_url
        
        # Изменяем размер гуся в зависимости от карты
        goose_width, goose_height = goose_image.size
        map_width, map_height = map_image.size

        goose_scale = 0.30  # Масштаб гуся (30% от оригинала)
        
        # Увеличиваем масштаб, если карта больше стандартной
        if map_width > 1024 or map_height > 1024:
            goose_scale *= (max(map_width, map_height) / 1024)
        
        new_width = int(goose_width * goose_scale)
        new_height = int(goose_height * goose_scale)
        goose_image = goose_image.resize((new_width, new_height), Image.LANCZOS)

        # Подготавливаем координаты вставки гуся (центрируем относительно заданной точки)
        paste_x = int(goose_x - new_width / 2)
        paste_y = int(goose_y - new_height / 1.2)
        
        # Копируем изображение карты для обработки
        result_image = map_image.copy()
        
        # Вставляем гуся на карту с учетом прозрачности
        if goose_image.mode == 'RGBA':
            # Вставляем изображение с альфа-каналом
            result_image.paste(goose_image, (paste_x, paste_y), goose_image)
        else:
            # Если у изображения нет альфа-канала, просто вставляем его
            result_image.paste(goose_image, (paste_x, paste_y))
        
        # Создаем временный файл для сохранения результата
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_path = temp_file.name
            result_image.save(temp_path, format='PNG')
        
        # Возвращаем путь к временному файлу с результатом
        logging.info(f"Сгенерировано изображение прогресса {progress_percent:.2f}% с гусем в позиции {position}")
        return temp_path
        
    except Exception as e:
        logging.error(f"Ошибка при создании изображения с гусем: {e}")
        # В случае ошибки возвращаем исходный URL
        return fallback_url

def get_progress_range(progress_percent):
    """Определяет диапазон прогресса"""
    if progress_percent < 10:
        return '0_10'
    elif progress_percent < 20:
        return '10_20'
    elif progress_percent < 30:
        return '20_30'
    elif progress_percent < 40:
        return '30_40'
    elif progress_percent < 50:
        return '40_50'
    elif progress_percent < 60:
        return '50_60'
    elif progress_percent < 70:
        return '60_70'
    elif progress_percent < 80:
        return '70_80'
    elif progress_percent < 90:
        return '80_90'
    else:
        return '90_100'

def get_position_in_range(progress_percent, image_range):
    """Определяет позицию в пределах диапазона"""
    range_min = int(image_range.split('_')[0])
    range_max = int(image_range.split('_')[1])
    range_size = range_max - range_min

    # Вычисляем положение в пределах текущего диапазона (0-100%)
    position_in_range = (progress_percent - range_min) / range_size if range_size > 0 else 0

    # Распределяем на три подкатегории: начало, середина, конец
    if position_in_range < 0.33:
        return 'start'
    elif position_in_range < 0.66:
        return 'middle'
    else:
        return 'end'

def get_map_path(image_range):
    """Возвращает путь к карте для заданного диапазона"""
    if image_range in MAP_IMAGES:
        return MAP_IMAGES[image_range]
    else:
        # Если карта для диапазона не определена, используем первую карту
        logging.warning(f"Карта для диапазона {image_range} не найдена. Используем карту по умолчанию.")
        return MAP_IMAGES.get('0_10')

def get_world_progress_image(user_id, world_id):
    """Получить URL изображения в зависимости от прогресса пользователя в мире"""
    # Используем URL-адреса напрямую вместо импорта переменных
    # Добавляем параметр timestamp к URL, чтобы избежать кеширования на стороне клиента
    timestamp = int(time.time())

    # URL для карт (используются если генерация изображения не удалась)
    photo_world_progress_0_10 = f"https://imgur.com/qc6fZ6S.jpg?t={timestamp}"
    photo_world_progress_10_20 = f"https://imgur.com/ia6KPHj.jpg?t={timestamp}"
    photo_world_progress_20_30 = f"https://imgur.com/a3ZZywI.jpg?t={timestamp}"
    photo_world_progress_30_40 = f"https://imgur.com/1yrJXCg.jpg?t={timestamp}"
    photo_world_progress_40_50 = f"https://imgur.com/HldobcV.jpg?t={timestamp}"
    photo_world_progress_50_60 = f"https://imgur.com/WWSrTwz.jpg?t={timestamp}"
    photo_world_progress_60_70 = f"https://imgur.com/LBKfVro.jpg?t={timestamp}"
    photo_world_progress_70_80 = f"https://imgur.com/YX7bQYv.jpg?t={timestamp}"
    photo_world_progress_80_90 = f"https://imgur.com/K1NzLR3.jpg?t={timestamp}"
    photo_world_progress_90_100 = f"https://imgur.com/5juAYva.jpg?t={timestamp}"

    # Получаем прогресс пользователя с принудительным пересчётом
    progress_data = get_world_progress(user_id, world_id, force_recount=True)
    completed_tasks = progress_data["completed_tasks"]
    total_tasks = progress_data["total_tasks"]

    # Избегаем деления на ноль
    if total_tasks == 0:
        progress_percent = 0
    else:
        progress_percent = (completed_tasks / total_tasks) * 100

    # Логируем процент прогресса для отладки
    logging.info(f"Прогресс пользователя {user_id} в мире {world_id}: {progress_percent:.2f}% ({completed_tasks}/{total_tasks})")

    # Выбираем fallback URL в зависимости от процента прогресса
    if progress_percent < 10:
        fallback_url = photo_world_progress_0_10
    elif progress_percent < 20:
        fallback_url = photo_world_progress_10_20
    elif progress_percent < 30:
        fallback_url = photo_world_progress_20_30
    elif progress_percent < 40:
        fallback_url = photo_world_progress_30_40
    elif progress_percent < 50:
        fallback_url = photo_world_progress_40_50
    elif progress_percent < 60:
        fallback_url = photo_world_progress_50_60
    elif progress_percent < 70:
        fallback_url = photo_world_progress_60_70
    elif progress_percent < 80:
        fallback_url = photo_world_progress_70_80
    elif progress_percent < 90:
        fallback_url = photo_world_progress_80_90
    else:
        fallback_url = photo_world_progress_90_100

    # Используем функцию генерации карты с гусем
    try:
        # Генерируем карту с гусем
        image_path = generate_progress_map(
            progress_percent=progress_percent,
            fallback_url=fallback_url
        )

        # Возвращаем путь к сгенерированному изображению
        return image_path
    except Exception as e:
        logging.error(f"Ошибка при генерации карты прогресса: {e}")
        # В случае ошибки возвращаем fallback URL
        return fallback_url

def handle_quest_loaded_world(call):
    """Обработчик загруженного мира"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    # Получаем ID мира из колбэка
    world_id = int(call.data.split('_')[-1])
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)

    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return

    # Сохраняем ID текущего мира в данных пользователя для использования в домашних заданиях и т.д.
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["current_world_id"] = world_id

    # Обновляем экран мира
    # Загружаем мир с правильным оформлением и логируем
    logging.info(f"Загрузка описания мира: '{world['description']}'")

    # Получаем изображение на основе прогресса пользователя
    world_image = get_world_progress_image(user_id, world_id)

    # Проверяем, является ли путь локальным файлом или URL
    import os

    try:
        if os.path.isfile(world_image):
            # Если это локальный файл, открываем его и отправляем
            with open(world_image, 'rb') as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo, caption=f"{world['name'].replace('🌍 ', '')}"),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=loaded_world_screen(world_id)
                )
                logging.info(f"Отправлено локальное изображение карты прогресса: {world_image}")
        else:
            # Если это URL, отправляем как обычно
            bot.edit_message_media(
                media=InputMediaPhoto(world_image, caption=f"{world['name'].replace('🌍 ', '')}"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=loaded_world_screen(world_id)
            )
            logging.info(f"Отправлен URL изображения карты прогресса: {world_image}")
    except Exception as e:
        # В случае ошибки используем резервное изображение
        logging.error(f"Ошибка при отправке изображения карты: {e}")
        fallback_url = f"https://imgur.com/qc6fZ6S.jpg?t={int(time.time())}"
        bot.edit_message_media(
            media=InputMediaPhoto(fallback_url, caption=f"{world['name'].replace('🌍 ', '')}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=loaded_world_screen(world_id)
        )
        logging.info(f"Отправлен резервный URL изображения")
    logging.info(f"Пользователь {user_id} вошел в мир {world_id} с названием: '{world['name']}'")

def handle_quest_back_to_worlds(call):
    """Обработчик возврата к списку миров из загруженного мира - без анимации загрузки"""
    from telebot.types import InputMediaPhoto

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем первый мир для отображения
        world = QUEST_WORLDS[0]

        # Отображаем список миров с изображением первого мира без анимации
        bot.edit_message_media(
            media=InputMediaPhoto(world["image"], caption=f"Выбери мир для исследования:\n{world['name']}"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_worlds_screen(0, len(QUEST_WORLDS))
        )
        logging.info(f"Пользователь {user_id} вернулся к списку миров")
    except Exception as e:
        logging.error(f"Ошибка при возврате к списку миров: {e}")
        # В случае ошибки, просто вызываем обычную функцию
        handle_quest_select_world(call)

def handle_mathquest_back(call):
    """Обработчик возврата в главное меню из квеста"""
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Очищаем данные пользователя, как это делается в main_back_call
    if user_id in user_data:
        del user_data[user_id]

    # Текст приветствия такой же, как в main_back_call
    text = (
        "Ты в умном боте для подготовки к ЕГЭ по профильной математике.\n\n"
        "Главное здесь — чёткая структура: квест от задания к заданию, теория по каждому номеру и никакой путаницы.\n\n"
        "А ещё — трекер занятий, карточки, варианты и помощь от репетитора.\n\n"
        "Всё, чтобы подготовка была по шагам и без стресса."
    )

    try:
        # Возвращаемся в главное меню с нужным текстом
        from instance import photo_main
        from telebot.types import InputMediaPhoto

        bot.edit_message_media(
            media=InputMediaPhoto(photo_main, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=main_screen()
        )
        logging.info(f"Пользователь {call.from_user.id} вернулся в главное меню из квеста")
    except Exception as e:
        logging.error(f"Ошибка при возвращении в главное меню: {e}")
        bot.answer_callback_query(call.id, "Ошибка при возвращении в главное меню.")

def handle_quest_theory(call):
    """Обработчик просмотра теории в мире (Книга знаний)"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Получаем ID мира из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-1])
    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)

    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return

    # Отображаем экран книги знаний с разделами
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("ФСУ", callback_data=f"theory_fsu_{world_id}"),
        InlineKeyboardButton("Квадратные уравнения", callback_data=f"theory_quadratic_{world_id}"),
        InlineKeyboardButton("Степени", callback_data=f"theory_powers_{world_id}"),
        InlineKeyboardButton("Корни", callback_data=f"theory_roots_{world_id}"),
        InlineKeyboardButton("Тригонометрия", callback_data=f"theory_trigonometry_{world_id}"),
        InlineKeyboardButton("Логарифмы", callback_data=f"theory_logarithms_{world_id}"),
        InlineKeyboardButton("Модули", callback_data=f"theory_modules_{world_id}"),
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )

    bot.edit_message_media(
        media=InputMediaPhoto(photo_quest_book, caption="Выбери раздел для изучения:"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

def handle_quest_task_list(call):
    """Обработчик просмотра списка заданий в мире"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    # Логируем информацию
    logging.info(f"Открытие списка заданий, пользователь {user_id}")

    # Инициализируем данные пользователя
    ensure_user_data(user_id)

    # Сохраняем текущую категорию перед переходом в список заданий
    if "current_task" in user_data[user_id]:
        current_task = user_data[user_id]["current_task"]
        if 'world_id' in current_task and 'cat_code' in current_task:
            # Сохраняем информацию о последней просмотренной категории
            user_data[user_id]["last_category"] = {
                "world_id": current_task["world_id"],
                "cat_code": current_task["cat_code"]
            }
            logging.info(f"Сохранена информация о категории {current_task['world_id']}_{current_task['cat_code']} для пользователя {user_id}")

        # Важно: НЕ удаляем текущую задачу, чтобы сохранить целостность навигации
        # Это позволит вернуться к той же категории после выхода в меню и обратно
        # del user_data[user_id]["current_task"]
        # logging.info(f"Удалена информация о текущей задаче для пользователя {user_id}")

    # Получаем ID мира из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-1])

    # Сохраняем текущее положение пользователя
    user_data[user_id]["current_screen"] = "task_list"
    user_data[user_id]["current_world_id"] = world_id

    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)

    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return

    # Экран выбора категорий
    photo = photo_quest_quests  # Используем изображение для квестов
    caption = "Выбери этап:"

    # Создаем клавиатуру для выбора категории
    markup = InlineKeyboardMarkup(row_width=1)

    # Получаем доступные категории для этого мира из challenge
    world_challenges = challenge.get(str(world_id), {})

    if world_challenges:
        # Добавляем кнопки для категорий из challenge с информацией о прогрессе
        for cat_code, category in world_challenges.items():
            # Подсчитываем количество правильно решенных задач для данной категории
            try:
                conn_task = sqlite3.connect('task_progress.db')
                cursor_task = conn_task.cursor()

                # Подсчитываем ТОЛЬКО правильно решенные основные задачи
                # Для отображения прогресса в категориях используем только основные задачи type = 'main'
                cursor_task.execute("""
                    SELECT COUNT(*) FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND status = 'correct' AND type = 'main'
                """, (user_id, str(world_id), cat_code))
                main_correct_count = cursor_task.fetchone()[0]

                # Для отображения прогресса в категориях НЕ учитываем домашние задания
                # Оставляем закомментированным для справки
                # cursor_task.execute("""
                #     SELECT COUNT(*) FROM task_progress
                #     WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND status = 'correct' AND type = 'homework'
                # """, (user_id, str(world_id), cat_code))
                # homework_correct_count = cursor_task.fetchone()[0]

                # Общее количество правильно решенных задач (только основные)
                correct_count = main_correct_count

                # Общее количество задач в категории
                total_count = len(category['tasks'])

                conn_task.close()

                # Добавляем кнопку с информацией о прогрессе (решенных верно/всего)
                markup.add(
                    InlineKeyboardButton(f"{category['name']} ({correct_count}/{total_count})",
                                         callback_data=f"quest_category_{world_id}_{cat_code}")
                )
                logging.info(f"Прогресс в категории {cat_code}: {correct_count}/{total_count}")
            except Exception as e:
                logging.error(f"Ошибка при подсчете прогресса для категории {cat_code}: {e}")
                # В случае ошибки просто отображаем название категории без прогресса
                markup.add(
                    InlineKeyboardButton(f"{category['name']}",
                                         callback_data=f"quest_category_{world_id}_{cat_code}")
                )
    else:
        # Если категории для мира не найдены, показываем сообщение
        markup.add(
            InlineKeyboardButton("📝 Категории в разработке", callback_data=f"quest_loaded_world_{world_id}")
        )

    # Кнопка назад
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )

    try:
        # Отображаем экран задач с категориями
        bot.edit_message_media(
            media=InputMediaPhoto(photo, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Ошибка при отображении списка задач: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при загрузке заданий")

def handle_quest_category(call):
    """Обработчик просмотра заданий категории"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    # Получаем параметры из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-2])
    cat_code = parts[-1]

    # Логируем информацию для отладки
    logging.info(f"Обработка категории: world_id={world_id}, cat_code={cat_code}, user_id={user_id}")

    # Сначала убедимся, что данные пользователя инициализированы
    ensure_user_data(user_id)

    # Сохраняем информацию о последней посещенной категории
    user_data[user_id]["last_category"] = {
        "world_id": world_id,
        "cat_code": cat_code
    }

    # НЕ очищаем информацию о текущей задаче, чтобы сохранить возможность навигации
    # if "current_task" in user_data[user_id]:
    #     del user_data[user_id]["current_task"]

    world = next((w for w in QUEST_WORLDS if w["id"] == world_id), None)
    if not world:
        bot.answer_callback_query(call.id, "Ошибка: мир не найден")
        return

    # Если это опция "Все задания", показываем оригинальную кнопку с task_1_call и категории из challenge
    if cat_code == "all":
        # Экран всех задач
        photo = "https://i.imgur.com/aZ5tK3Q.jpg"  # Изображение экрана с задачами
        caption = "Задачи\n\nВыбери задание:"

        # Создаем клавиатуру для выбора задания (как на скриншоте)
        markup = InlineKeyboardMarkup(row_width=1)

        # Кнопка "Все задания" с оригинальным callback_data
        markup.add(
            InlineKeyboardButton("📚 Все задания", callback_data="task_1_call")
        )

        # Получаем доступные категории для этого мира из challenge и добавляем их
        world_challenges = challenge.get(str(world_id), {})

        if world_challenges:
            # Добавляем заголовок для категорий из challenge
            markup.add(
                InlineKeyboardButton("📋 Категории задач:", callback_data=f"quest_task_list_{world_id}")
            )
            # Добавляем кнопки для каждой категории из challenge
            for category_code, category in world_challenges.items():
                markup.add(
                    InlineKeyboardButton(f"📘 {category['name']}",
                                         callback_data=f"quest_category_{world_id}_{category_code}")
                )

        # Кнопка домашка
        markup.add(
            InlineKeyboardButton("📝 Домашка", callback_data="quest_homework")
        )

        # Кнопка избранное удалена

        # Кнопка назад
        markup.add(
            InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
        )

        # Отображаем экран задач
        bot.edit_message_media(
            media=InputMediaPhoto(photo, caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        return

    # Стандартная обработка категории
    # Получаем категорию
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)

    if not category:
        bot.answer_callback_query(call.id, "Ошибка: категория не найдена")
        return

    # Всегда показываем первое задание из категории, а не проверяем уже выбрана ли эта категория
    # Этот подход делает навигацию проще для пользователя - категория всегда загружается,
    # даже если пользователь повторно нажимает на неё

    # Убираем проверку already_selected, которая мешала повторному открытию категории
    logging.info(f"Загружаем категорию {world_id}_{cat_code} для пользователя {user_id}")

    # Сохраняем информацию о текущей категории для дальнейшего использования
    user_data[user_id]["current_category"] = {
        "world_id": world_id,
        "cat_code": cat_code
    }

    # Всегда показываем первое задание
    task_idx = 0

    # Создаем новый call с правильными параметрами
    import copy
    new_call = copy.deepcopy(call)
    new_call.data = f"quest_task_{world_id}_{cat_code}_{task_idx}"
    handle_quest_task(new_call)
    return

def handle_quest_task(call):
    """Обработчик просмотра конкретного задания"""
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = str(call.from_user.id)

        # Получаем параметры из колбэка
        parts = call.data.split('_')
        world_id = int(parts[-3])
        cat_code = parts[-2]
        task_idx = int(parts[-1])

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 2.0: Используем унифицированный метод проверки подсказок
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 2.0: Проверка использования подсказки через ЕДИНЫЙ МЕТОД при открытии задания")
        logging.info(f"Проверка использования подсказки при открытии задания: user_id={user_id}, task_key={task_key}")

        # Используем унифицированную функцию для проверки использования подсказки
        used_hint = check_hint_usage(user_id, str(world_id), cat_code, task_idx)

        logging.info(f"При открытии задания {task_key}, состояние использования подсказки: {used_hint}")

        # Проверяем, не дублируется ли запрос с одинаковыми message_id
        if (user_id in user_data and
                'last_task_request' in user_data[user_id] and
                message_id is not None):
            last_request = user_data[user_id]['last_task_request']
            if (last_request['world_id'] == world_id and
                    last_request['cat_code'] == cat_code and
                    last_request['task_idx'] == task_idx and
                    last_request['message_id'] == message_id and
                    (datetime.now().timestamp() - last_request['timestamp']) < 1.0):  # Защита от повторных запросов в течение 1 секунды (не требует МСК)
                # Это повторный запрос того же задания с тем же message_id - отменяем
                bot.answer_callback_query(
                    call.id,
                    "Задание уже отображается"
                )
                return

        # Сохраняем текущий запрос
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['last_task_request'] = {
            'world_id': world_id,
            'cat_code': cat_code,
            'task_idx': task_idx,
            'message_id': message_id,
            'timestamp': datetime.now().timestamp()  # Timestamp для сравнения, не требует МСК
        }

        # Получаем информацию о задании
        world_challenges = challenge.get(str(world_id), {})
        category = world_challenges.get(cat_code)

        if not category or task_idx >= len(category['tasks']):
            bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
            return

        task = category['tasks'][task_idx]

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Улучшенная обработка URL изображений задач
        # Получаем ссылку на изображение задания
        photo_url = task['photo']
        if not photo_url.startswith("http"):
            photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur

        # Добавляем параметр для предотвращения кеширования и логотипа Imgur
        if "?" not in photo_url:
            # Добавляем случайный параметр и размер изображения
            import random
            random_param = random.randint(10000, 99999)
            photo_url = f"{photo_url}?cache={random_param}&size=l"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Добавлен параметр против кеширования для задачи: {photo_url}")

        # Создаем клавиатуру
        markup = InlineKeyboardMarkup(row_width=2)

        # Кнопки навигации
        # Получаем общее количество задач в категории
        total_tasks = len(category['tasks'])

        # Добавляем кнопки навигации
        navigation_buttons = []
        if task_idx > 0:
            navigation_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx-1}"))
        else:
            navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))

        navigation_buttons.append(InlineKeyboardButton(f"{task_idx+1}/{total_tasks}", callback_data="no_action"))

        if task_idx < total_tasks - 1:
            navigation_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx+1}"))
        else:
            navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))

        markup.row(*navigation_buttons)

        # Кнопка для просмотра решения/подсказки
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_solution_{world_id}_{cat_code}_{task_idx}"))

        # Код получения избранных заданий пользователя
        from main import is_in_favorites
        # Проверяем, есть ли задача в избранном
        is_favorite = is_in_favorites(call.from_user.id, str(world_id), cat_code, task_idx)
        # Текст кнопки зависит от статуса избранного
        favorite_text = "🗑 Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное"
        # Добавляем кнопку для добавления/удаления из избранного
        markup.add(InlineKeyboardButton(favorite_text, callback_data=f"quest_favorite_{world_id}_{cat_code}_{task_idx}"))

        # Кнопка возврата в меню выбора тем
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_list_{world_id}"))

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Улучшена проверка статуса задачи
        # Проверяем, решал ли пользователь эту задачу
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()

        # ВАЖНО: Сначала проверяем наличие записи с type='main'
        cursor.execute(
            "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'",
            (user_id, str(world_id), cat_code, task_idx)
        )
        result = cursor.fetchone()

        # Добавляем логирование для отслеживания
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Проверка статуса задачи {world_id}_{cat_code}_{task_idx} для пользователя {user_id}")
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Результат запроса к базе данных: {result}")

        conn.close()

        status_text = "❔ Не решено"
        answer_text = ""
        if result:
            status = result[0]
            # ВАЖНО: используем оба возможных формата статуса (текстовый и числовой)
            if status == "correct" or status == 1 or status == "1":
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Найден статус ВЕРНО ({status}) для задачи {world_id}_{cat_code}_{task_idx}")
                status_text = "✅ Верно"
                # Всегда добавляем правильный ответ, если задача решена правильно и ответ известен
                if 'answer' in task:
                    answer_text = f"\n\nПравильный ответ: {task['answer']}"

                # Обязательно сохраняем в информации для пользователя, что задача уже решена верно
                # это предотвратит случайное изменение статуса при последующих ответах
                if 'user_solutions' not in user_data[user_id]:
                    user_data[user_id]['user_solutions'] = {}
                user_data[user_id]['user_solutions'][f"{world_id}_{cat_code}_{task_idx}"] = "correct"
            elif status == "wrong":
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Найден статус НЕВЕРНО (wrong) для задачи {world_id}_{cat_code}_{task_idx}")
                status_text = "❌ Неверно"
            else:
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Найден НЕОПРЕДЕЛЕННЫЙ статус ({status}) для задачи {world_id}_{cat_code}_{task_idx}")
                status_text = "❌ Неверно"

        # Отображаем задание
        # Добавляем текст "введи ответ в чат:" для нерешенных заданий
        # Используем "№6" вместо "Задача N"
        caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}"
        if status_text == "❔ Не решено" or status_text == "❌ Неверно":
            caption += "\n\nВведи ответ в чат:"

        # Сохраняем ID сообщения для последующего обновления при ответе
        if user_id not in user_data:
            user_data[user_id] = {}

        try:
            # Пытаемся редактировать существующее сообщение
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            # Если редактирование прошло успешно, сохраняем ID сообщения
            user_data[user_id]['quest_message_id'] = message_id
        except Exception as e:
            # Если не удалось отредактировать сообщение, отправляем новое
            if "message to edit not found" in str(e) or "message to be edited" in str(e):
                try:
                    # Отправляем новое сообщение
                    new_message = bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_url,
                        caption=caption,
                        reply_markup=markup
                    )
                    # Сохраняем ID нового сообщения
                    user_data[user_id]['quest_message_id'] = new_message.message_id
                    logging.info(f"Отправлено новое сообщение с заданием (message_id={new_message.message_id}) вместо редактирования старого (message_id={message_id})")
                except Exception as send_err:
                    logging.error(f"Не удалось отправить новое сообщение с заданием: {send_err}")
            elif "message is not modified" not in str(e):
                # Логируем ошибку только если это не предупреждение о том, что сообщение не изменилось
                logging.error(f"Ошибка при редактировании сообщения с заданием: {e}")

        # Сохраняем информацию о текущем задании пользователя для обработки ответа
        user_data[user_id]['current_task'] = {
            'world_id': world_id,
            'cat_code': cat_code,
            'task_idx': task_idx,
            'answer': task.get('answer')
        }
    except Exception as e:
        logging.error(f"Критическая ошибка в handle_quest_task: {e}")
        try:
            bot.answer_callback_query(call.id, "Произошла ошибка при обработке задания.")
        except:
            pass

def handle_quest_answer(call):
    """Обработчик для ввода ответа на задание"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    # Получаем параметры из колбэка
    parts = call.data.split('_')
    world_id = int(parts[-3])
    cat_code = parts[-2]
    task_idx = int(parts[-1])

    logging.info(f"===== НАЧАЛО ВВОДА ОТВЕТА =====")
    logging.info(f"Запрос на ввод ответа: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")

    # Проверяем, решено ли уже задание
    conn = sqlite3.connect('task_progress.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
        (user_id, str(world_id), cat_code, task_idx)
    )
    result = cursor.fetchone()
    conn.close()

    if result and result[0] == 1:
        # Если задание уже решено, просто тихо отвечаем на колбэк без изменения сообщения
        logging.info(f"Пользователь повторно запросил ввод ответа для уже решенного задания")
        bot.answer_callback_query(call.id, "Вы уже решили это задание", show_alert=False)
        return

    # Сохраняем состояние пользователя для обработки ответа
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['state'] = 'quest_answer'
    user_data[user_id]['quest_world_id'] = world_id
    user_data[user_id]['quest_cat_code'] = cat_code
    user_data[user_id]['quest_task_idx'] = task_idx
    user_data[user_id]['quest_message_id'] = message_id
    user_data[user_id]['current_screen'] = 'quest_task'  # Установка current_screen для обработки ответа

    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)

    if not category or task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return

    task = category['tasks'][task_idx]

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Улучшенная обработка URL изображений для вопросов
    # Получаем ссылку на изображение задания
    photo_url = task['photo']
    if not photo_url.startswith("http"):
        photo_url = f"https://i.imgur.com/{photo_url}.jpeg"  # Формируем URL для imgur

    # Добавляем параметр для предотвращения кеширования и логотипа Imgur
    if "?" not in photo_url:
        # Добавляем случайный параметр и размер изображения
        import random
        random_param = random.randint(10000, 99999)
        photo_url = f"{photo_url}?cache={random_param}&size=l"
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Добавлен параметр против кеширования для вопроса: {photo_url}")

    # Отправляем сообщение с запросом ввода ответа
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↩️ Отмена", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))

    logging.info(f"Отправка формы для ввода ответа на задание")

    bot.edit_message_media(
        media=InputMediaPhoto(photo_url, caption=f"📝 {category['name']} - {task.get('title', f'Задание {task_idx+1}')}\n\n✏️ Введи ответ в чат:"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

def handle_quest_solution(call):
    """Обработчик для просмотра решения задания"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    logging.info(f"===== ВЫЗОВ ПРОСМОТРА РЕШЕНИЯ: {call.data} =====")
    logging.info(f"Тип данных call.data: {type(call.data)}")

    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"Части callback data для решения: {parts}")

        # Проверяем формат данных
        if len(parts) < 4:
            logging.error(f"Неверный формат callback data для просмотра решения: {call.data}")
            bot.answer_callback_query(call.id, "Ошибка при загрузке решения")
            return

        world_id = int(parts[-3])
        cat_code = parts[-2]
        task_idx = int(parts[-1])
        logging.info(f"Параметры решения: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 2.0: Используем унифицированный метод для работы с подсказками
        # Это гарантирует, что при "верном ответе + использована подсказка" задание будет добавлено в Ритуал повторения
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 2.0: Открыта первая страница подсказки, используем единую систему для отметки")
        logging.info(f"Используем единую функцию mark_hint_as_used для задачи {task_key}")

        # Отмечаем использование подсказки с помощью единой функции
        mark_hint_as_used(user_id, str(world_id), cat_code, task_idx)

        # Проверяем правильность маркировки для отладки
        used_hint = check_hint_usage(user_id, str(world_id), cat_code, task_idx)
        logging.info(f"✅ ПРОВЕРКА: После маркировки подсказки для задачи {task_key}, состояние: {used_hint}")

        # Сохраняем состояние в долговременную память
        save_user_data(user_id)

        # Дополнительное логирование для отладки
        logging.info(f"⚠️ Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 2.0: Сохранен флаг использования подсказки для задачи {task_key} с помощью единой функции")
    except Exception as e:
        logging.error(f"Ошибка при разборе callback data для решения: {e}, данные: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке решения")
        return

    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code)

    if not category or task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return

    task = category['tasks'][task_idx]

    # Проверяем наличие подсказок/решения
    if not task.get('hint'):
        bot.answer_callback_query(call.id, "Решение для этого задания недоступно")
        return

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Улучшенная обработка URL изображений для подсказок
    # Получаем первую подсказку (шаг решения)
    hint_url = task['hint'][0]
    if not hint_url.startswith("http"):
        hint_url = f"https://i.imgur.com/{hint_url}.jpeg"  # Формируем URL для imgur

    # Добавляем параметр для предотвращения кеширования и проблем с Imgur
    if "?" not in hint_url:
        # Добавляем случайный параметр и размер изображения
        import random
        random_param = random.randint(10000, 99999)
        hint_url = f"{hint_url}?cache={random_param}&size=l"
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Добавлен параметр против кеширования для подсказки: {hint_url}")

    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=2)

    # Кнопки навигации по шагам решения
    if len(task['hint']) > 1:
        # Первая кнопка будет пустой, т.к. это первый шаг
        prev_button = InlineKeyboardButton(" ", callback_data=f"quest_empty")

        # Важная модификация: используем строковый формат для всех компонентов,
        # включая числовые значения. Это необходимо для корректной обработки.
        step = "0"  # Используем строку вместо числа
        next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{step}"

        # Отладочная информация для контроля правильности данных
        logging.info(f"ПОДСКАЗКИ: создаем кнопки навигации. Всего шагов: {len(task['hint'])}")
        logging.info(f"ПАРАМЕТРЫ КНОПКИ: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, step={step}")
        logging.info(f"КНОПКА ВПЕРЕД: {next_callback}")
        logging.info(f"ДЛИНА: длина callback_data = {len(next_callback)}")
        logging.info(f"СОСТАВ: {next_callback.split('_')}")

        # Создаем кнопку с правильно сформированным callback_data
        next_button = InlineKeyboardButton("▶️", callback_data=next_callback)
        markup.add(prev_button, next_button)

    # Кнопка возврата - проверяем, открыта ли задача из избранного
    if 'from_favorites' in user_data.get(user_id, {}) and user_data[user_id].get('from_favorites', False):
        # Если открыта из избранного, возвращаемся к избранной задаче с нужным флагом
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorite_category_{world_id}_{cat_code}_{task_idx}"))
    else:
        # Обычный режим
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))

    try:
        # Пытаемся редактировать существующее сообщение
        bot.edit_message_media(
            media=InputMediaPhoto(hint_url, caption=f"💡Подсказка 1/{len(task['hint'])}\nВернись к заданию, чтобы ввести ответ"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        # Если редактирование прошло успешно, сохраняем ID сообщения
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['quest_message_id'] = message_id
    except Exception as e:
        # Если не удалось отредактировать сообщение, отправляем новое
        if "message to edit not found" in str(e) or "message to be edited" in str(e):
            try:
                # Отправляем новое сообщение с подсказкой
                new_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=hint_url,
                    caption=f"💡Подсказка 1/{len(task['hint'])}\nВернись к заданию, чтобы ввести ответ",
                    reply_markup=markup
                )
                # Сохраняем ID нового сообщения для последующих обновлений
                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['quest_message_id'] = new_message.message_id
                logging.info(f"Отправлено новое сообщение с решением (message_id={new_message.message_id}) вместо редактирования старого (message_id={message_id})")
            except Exception as send_err:
                logging.error(f"Не удалось отправить новое сообщение с решением: {send_err}")
                bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте вернуться к списку заданий и начать заново.")
        elif "message is not modified" not in str(e):
            # Логируем ошибку только если это не предупреждение о том, что сообщение не изменилось
            logging.error(f"Ошибка при отображении решения: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка при загрузке решения.")

def handle_hint_direct(call):
    """Обработчик прямого перехода к шагу решения/подсказки"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    logging.info(f"++++ ОБРАБОТКА ПРЯМОГО ПЕРЕХОДА: {call.data} ++++")

    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"Части callback data прямого перехода: {parts}")

        # Проверка формата данных
        if len(parts) < 7:
            logging.error(f"ОШИБКА: Неверный формат callback data для прямого перехода: {call.data}")
            bot.answer_callback_query(call.id, "Ошибка формата данных для навигации")
            return

        # Извлекаем параметры
        world_id = int(parts[3])
        cat_code = parts[4]
        task_idx = int(parts[5])
        target_step = int(parts[6])

        logging.info(f"ПАРАМЕТРЫ: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, target_step={target_step}")

        # Получаем данные задания
        world_challenges = challenge.get(str(world_id), {})
        category = world_challenges.get(cat_code, {})

        if not category or 'tasks' not in category:
            logging.error(f"ОШИБКА: Категория не найдена: {cat_code} в мире {world_id}")
            bot.answer_callback_query(call.id, "Категория задания не найдена")
            return

        if task_idx >= len(category['tasks']):
            logging.error(f"ОШИБКА: Индекс задания вне диапазона: {task_idx} >= {len(category['tasks'])}")
            bot.answer_callback_query(call.id, "Задание не найдено")
            return

        # Получаем задание
        task = category['tasks'][task_idx]

        # Проверяем наличие подсказок
        if not task.get('hint'):
            logging.error(f"ОШИБКА: У задания нет подсказок")
            bot.answer_callback_query(call.id, "У задания нет подсказок")
            return

        total_steps = len(task['hint'])

        if target_step >= total_steps:
            logging.error(f"ОШИБКА: Шаг подсказки вне диапазона: {target_step} >= {total_steps}")
            bot.answer_callback_query(call.id, "Шаг подсказки не найден")
            return

        logging.info(f"ПЕРЕХОД: на шаг {target_step} из {total_steps} шагов")

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Улучшенная обработка URL изображений для подсказок
        # Получаем URL изображения
        hint_url = task['hint'][target_step]
        if not hint_url.startswith("http"):
            hint_url = f"https://i.imgur.com/{hint_url}.jpeg"

        # Добавляем параметр для предотвращения кеширования и проблем с Imgur
        if "?" not in hint_url:
            # Добавляем случайный параметр и размер изображения
            import random
            random_param = random.randint(10000, 99999)
            hint_url = f"{hint_url}?cache={random_param}&size=l"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Добавлен параметр против кеширования для подсказки: {hint_url}")

        logging.info(f"URL подсказки: {hint_url}")

        # Создаем клавиатуру
        markup = InlineKeyboardMarkup(row_width=2)

        # Кнопки навигации
        prev_callback = f"quest_hint_prev_{world_id}_{cat_code}_{task_idx}_{target_step}"
        next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{target_step}"

        # Если первый шаг - кнопка "назад" пустая
        if target_step == 0:
            prev_button = InlineKeyboardButton(" ", callback_data="quest_empty")
            logging.info("Первый шаг - кнопка назад пустая")
        else:
            prev_button = InlineKeyboardButton("◀️", callback_data=prev_callback)

        # Если последний шаг - кнопка "вперед" пустая
        if target_step == total_steps - 1:
            next_button = InlineKeyboardButton(" ", callback_data="quest_empty")
            logging.info("Последний шаг - кнопка вперед пустая")
        else:
            next_button = InlineKeyboardButton("▶️", callback_data=next_callback)

        # Добавляем кнопки
        markup.add(prev_button, next_button)

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Определяем, с какого экрана пришел пользователь
        # Чтобы вернуть его туда же после просмотра подсказки
        is_homework_mode = False
        is_favorites_mode = False

        if user_id in user_data:
            # Проверяем режим домашнего задания
            current_screen = user_data[user_id].get("current_screen", "")
            if current_screen == "homework_task":
                is_homework_mode = True
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Обнаружен режим домашнего задания у пользователя {user_id}")

            # Проверяем режим избранного
            if 'from_favorites' in user_data[user_id] and user_data[user_id].get('from_favorites', False):
                is_favorites_mode = True
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обнаружен режим избранного у пользователя {user_id}")

        # Выбираем правильную кнопку возврата в зависимости от режима
        if is_homework_mode and "current_homework" in user_data[user_id]:
            # Используем данные текущего домашнего задания для возврата
            hw_data = user_data[user_id]["current_homework"]
            hw_world_id = hw_data.get("world_id")
            hw_cat_code = hw_data.get("cat_code")
            hw_task_idx = hw_data.get("task_idx")

            # Возвращаем в то же домашнее задание
            markup.add(InlineKeyboardButton("↩️ Назад",
                                            callback_data=f"quest_homework_task_{hw_world_id}_{hw_cat_code}_{hw_task_idx}"))
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Добавлена кнопка возврата в домашнее задание {hw_world_id}_{hw_cat_code}_{hw_task_idx}")
        elif is_favorites_mode:
            # Возвращаем в избранное задание
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorite_category_{world_id}_{cat_code}_{task_idx}"))
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавлена кнопка возврата в избранное задание {world_id}_{cat_code}_{task_idx}")
        else:
            # Стандартное поведение - возврат в обычное задание
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))

        # Отправляем сообщение
        try:
            logging.info(f"Отправляем изображение: {hint_url} с caption: 💡 Подсказка - Шаг {target_step+1}/{total_steps}")

            bot.edit_message_media(
                media=InputMediaPhoto(hint_url, caption=f"💡Подсказка {target_step+1}/{total_steps}\nВернись к заданию, чтобы ввести ответ"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['quest_message_id'] = message_id

            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Отмечаем использование подсказки с помощью унифицированной функции
            try:
                # Создаем ключ для отслеживания использования подсказки
                task_key = f"{world_id}_{cat_code}_{task_idx}"

                # Используем единую функцию для отметки использования подсказки
                mark_hint_as_used(user_id, str(world_id), cat_code, task_idx)
                logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Использование подсказки помечено единым способом для задачи {task_key}")

                # Проверяем состояние после маркировки
                is_hint_used = check_hint_usage(user_id, str(world_id), cat_code, task_idx)
                logging.info(f"✅ ПРОВЕРКА ПОСЛЕ МАРКИРОВКИ: Состояние использования подсказки для задачи {task_key}: {is_hint_used}")

                # Сохраняем состояние подсказок в долговременной памяти (сериализация)
                # Это дополнительная гарантия для корректной работы "Ритуала повторения"
                save_user_data(user_id)

                logging.info(f"Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
                if user_id in user_data and 'viewed_hints' in user_data[user_id]:
                    logging.info(f"ОТЛАДКА ПОДСКАЗОК: текущие подсказки для пользователя {user_id}: {user_data[user_id]['viewed_hints']}")

                # Дополнительное сообщение для отладки
                logging.info(f"✅✅✅ Сохранен флаг использования подсказки для задачи {task_key} в памяти и в БД")

                # Теперь не добавляем задачу в домашнюю работу сразу.
                # Это будет сделано только при ответе на задачу в handle_task_answer
                # согласно новым правилам: верно+подсказка, неверно+подсказка, неверно без подсказки
            except Exception as err:
                logging.error(f"Ошибка при отметке использования подсказки: {err}")

            logging.info(f"УСПЕХ: Сообщение обновлено, показан шаг {target_step+1}")

        except Exception as e:
            logging.error(f"ОШИБКА редактирования сообщения: {e}")

            # Если сообщение не найдено, отправляем новое
            if "message to edit not found" in str(e) or "message to be edited" in str(e):
                try:
                    new_message = bot.send_photo(
                        chat_id=chat_id,
                        photo=hint_url,
                        caption=f"💡Подсказка {target_step+1}/{total_steps}\nВернись к заданию, чтобы ввести ответ",
                        reply_markup=markup
                    )

                    if user_id not in user_data:
                        user_data[user_id] = {}
                    user_data[user_id]['quest_message_id'] = new_message.message_id

                    logging.info(f"УСПЕХ: Отправлено новое сообщение, показан шаг {target_step+1}")

                except Exception as send_err:
                    logging.error(f"ОШИБКА отправки нового сообщения: {send_err}")
                    bot.answer_callback_query(call.id, "Ошибка отправки сообщения")
            elif "message is not modified" not in str(e):
                logging.error(f"ОШИБКА обновления сообщения: {e}")
                bot.answer_callback_query(call.id, "Ошибка обновления сообщения")

    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА обработки перехода: {e}")
        import traceback
        logging.error(traceback.format_exc())
        bot.answer_callback_query(call.id, "Произошла ошибка при обработке")

def handle_quest_hint_navigation(call):
    """Обработчик навигации по шагам решения/подсказкам"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    logging.info(f"======== НАВИГАЦИЯ ПО ПОДСКАЗКАМ =======")
    logging.info(f"ДАННЫЕ: {call.data}")
    logging.info(f"ТИП: {type(call.data)}")
    logging.info(f"ДЛИНА: {len(call.data)}")
    
    try:
        # Получаем параметры из колбэка
        parts = call.data.split('_')
        logging.info(f"РАЗБОР: {parts}")
        
        # Проверяем достаточно ли частей в колбэке
        if len(parts) < 7:
            logging.error(f"ОШИБКА ФОРМАТА: {call.data} - недостаточно частей")
            bot.answer_callback_query(call.id, "Ошибка формата данных")
            return
        
        # Извлекаем параметры
        action = parts[2]  # next или prev
        world_id = int(parts[3])
        cat_code = parts[4]
        task_idx = int(parts[5])
        
        # Важно: преобразуем текущий шаг в целое число 
        # и проверяем корректность преобразования
        try:
            current_step = int(parts[6])
            logging.info(f"ТЕКУЩИЙ ШАГ: {current_step} (успешно преобразован)")
        except ValueError:
            logging.error(f"ОШИБКА ПРЕОБРАЗОВАНИЯ: {parts[6]} не является числом")
            bot.answer_callback_query(call.id, "Ошибка формата шага")
            return

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Отмечаем использование подсказки с помощью унифицированной функции
        # Эта метка будет использоваться при проверке ответа для добавления в "Ритуал повторения"

        # Формируем ключ для отслеживания использования подсказки
        task_key = f"{world_id}_{cat_code}_{task_idx}"

        # Используем унифицированную функцию для отметки использования подсказки
        mark_hint_as_used(user_id, str(world_id), cat_code, task_idx)

        # Проверяем состояние после маркировки для отладки
        is_hint_used = check_hint_usage(user_id, str(world_id), cat_code, task_idx)

        # Сохраняем состояние в долговременную память - дополнительная гарантия для работы "Ритуала повторения"
        save_user_data(user_id)

        logging.info(f"⚠️ Отмечено использование подсказки для задачи {task_key} пользователем {user_id}")
        logging.info(f"✅ ПРОВЕРКА ПОСЛЕ МАРКИРОВКИ: Состояние использования подсказки для задачи {task_key}: {is_hint_used}")
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Использование подсказки помечено единым способом для задачи {task_key}")

        # Уведомляем пользователя только при первом просмотре подсказки
        # чтобы не спамить сообщениями при переходе между шагами
        # Убрано уведомление о добавлении задачи в "Ритуал повторения"
        # Пользователь видит только подсказку, без дополнительных сообщений
        # Сохраняем информацию о текущей задаче для корректного возврата
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['current_task'] = {
            "challenge_num": str(world_id),
            "cat_code": cat_code,
            "task_idx": task_idx,
            "screen": "quest_task"
        }
        logging.info(f"Сохранен текущий контекст задачи для пользователя {user_id}")

        logging.info(f"ПАРАМЕТРЫ: action={action}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}, current_step={current_step}")
    except Exception as e:
        logging.error(f"ОШИБКА при разборе данных: {e}, данные: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка разбора данных")
        return

    # Получаем информацию о задании
    world_challenges = challenge.get(str(world_id), {})
    category = world_challenges.get(cat_code, {})

    if not category or 'tasks' not in category:
        logging.error(f"ОШИБКА: Категория не найдена: {cat_code} в мире {world_id}")
        bot.answer_callback_query(call.id, "Категория не найдена")
        return

    if task_idx >= len(category['tasks']):
        logging.error(f"ОШИБКА: Индекс задания вне диапазона: {task_idx} >= {len(category['tasks'])}")
        bot.answer_callback_query(call.id, "Задание не найдено")
        return

    task = category['tasks'][task_idx]

    # Проверяем наличие подсказок
    if not task.get('hint'):
        logging.error(f"ОШИБКА: У задания нет подсказок")
        bot.answer_callback_query(call.id, "У задания нет подсказок")
        return

    total_steps = len(task['hint'])

    if total_steps <= 1:
        logging.error(f"ОШИБКА: У задания только одна подсказка")
        bot.answer_callback_query(call.id, "Нет дополнительных шагов")
        return

    # Вычисляем новый шаг
    new_step = current_step

    # Добавим подробное логирование для отладки
    logging.info(f"ТЕКУЩИЙ ШАГ: {current_step}, ВСЕГО ШАГОВ: {total_steps}")

    # Проверяем возможность перехода
    if action == "next":
        if current_step < total_steps - 1:
            new_step = current_step + 1
            logging.info(f"ПЕРЕХОД: Вперед с шага {current_step} на {new_step}")
            # Пишем подробную информацию о шагах
            logging.info(f"ПОДСКАЗКИ: {len(task['hint'])} шт, текущий шаг: {current_step}, новый шаг: {new_step}")

            # ИСПРАВЛЕНИЕ: При переходе к следующему шагу подсказки НЕ добавляем задачу в домашнюю работу
            # Теперь задачи добавляются в домашнюю работу только при ответе пользователя
            # согласно правилам: 
            # 1. Верный ответ + подсказка -> Добавить в домашние задания
            # 2. Неверный ответ (с подсказкой или без) -> Добавить в домашние задания
            # 3. Верный ответ без подсказки -> НЕ добавлять в домашние задания

            # Проверяем текущий статус задачи для логирования
            try:
                conn = sqlite3.connect('task_progress.db')
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
                """, (user_id, str(world_id), cat_code, task_idx))
                result = cursor.fetchone()

                # Только логирование для отладки
                main_status = result[0] if result else None
                logging.info(f"ВАЖНО: При навигации подсказок - текущий статус задачи {world_id}_{cat_code}_{task_idx}: {main_status}")

                conn.close()
                logging.info(f"✅ Просмотр подсказки для задачи {world_id}_{cat_code}_{task_idx} отмечен в профиле пользователя {user_id}")
            except Exception as e:
                logging.error(f"Ошибка при логировании использования подсказки: {e}")
        else:
            logging.error(f"ОШИБКА: Невозможно перейти вперед, уже последний шаг ({current_step}/{total_steps-1})")
            bot.answer_callback_query(call.id, "Это последний шаг")
            return
    elif action == "prev":
        if current_step > 0:
            new_step = current_step - 1
            logging.info(f"ПЕРЕХОД: Назад с шага {current_step} на {new_step}")
        else:
            logging.error(f"ОШИБКА: Невозможно перейти назад, уже первый шаг")
            bot.answer_callback_query(call.id, "Это первый шаг")
            return
    else:
        logging.error(f"ОШИБКА: Неизвестное действие: {action}")
        bot.answer_callback_query(call.id, "Неизвестное действие")
        return

    logging.info(f"РЕЗУЛЬТАТ: Переход с шага {current_step} на шаг {new_step} из {total_steps} шагов")

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Улучшенная обработка URL изображений для подсказок
    # Получаем URL изображения для нового шага
    hint_url = task['hint'][new_step]
    if not hint_url.startswith("http"):
        hint_url = f"https://i.imgur.com/{hint_url}.jpeg"

    # Добавляем параметр для предотвращения кеширования и проблем с Imgur
    if "?" not in hint_url:
        # Добавляем случайный параметр и размер изображения
        import random
        random_param = random.randint(10000, 99999)
        hint_url = f"{hint_url}?cache={random_param}&size=l"
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 7.0: Добавлен параметр против кеширования для навигации по подсказкам: {hint_url}")

    logging.info(f"URL подсказки: {hint_url}")

    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=2)

    # Кнопки навигации
    # Используем строковый формат для шага
    str_step = str(new_step)
    logging.info(f"ШАГ КАК СТРОКА: {str_step}")

    prev_callback = f"quest_hint_prev_{world_id}_{cat_code}_{task_idx}_{str_step}"
    next_callback = f"quest_hint_next_{world_id}_{cat_code}_{task_idx}_{str_step}"

    # Добавление задачи в домашнюю работу выполнено ранее в коде, не нужно делать это повторно

    logging.info(f"CALLBACK PREV: {prev_callback}, ДЛИНА: {len(prev_callback)}")
    logging.info(f"CALLBACK NEXT: {next_callback}, ДЛИНА: {len(next_callback)}")

    # Если первый шаг - кнопка "назад" пустая
    if new_step == 0:
        prev_button = InlineKeyboardButton(" ", callback_data="quest_empty")
        logging.info("Первый шаг - кнопка назад пустая")
    else:
        prev_button = InlineKeyboardButton("◀️", callback_data=prev_callback)
        logging.info(f"Кнопка НАЗАД: {prev_callback}")

    # Если последний шаг - кнопка "вперед" пустая
    if new_step == total_steps - 1:
        next_button = InlineKeyboardButton(" ", callback_data="quest_empty")
        logging.info("Последний шаг - кнопка вперед пустая")
    else:
        next_button = InlineKeyboardButton("▶️", callback_data=next_callback)
        logging.info(f"Кнопка ВПЕРЕД: {next_callback}")

    # Добавляем кнопки
    markup.add(prev_button, next_button)

    # Проверяем, открыта ли задача из избранного
    if user_id in user_data and 'from_favorites' in user_data[user_id] and user_data[user_id].get('from_favorites', False):
        # Если открыта из избранного, возвращаемся к избранной задаче с нужным флагом
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"favorite_category_{world_id}_{cat_code}_{task_idx}"))
        logging.info(f"Добавлена кнопка возврата в избранное задание {world_id}_{cat_code}_{task_idx}")
    else:
        # Обычный режим
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx}"))

    try:
        logging.info(f"Отправляем изображение: {hint_url} с caption: 💡 Подсказка - Шаг {new_step+1}/{total_steps}")

        bot.edit_message_media(
            media=InputMediaPhoto(hint_url, caption=f"💡Подсказка {new_step+1}/{total_steps}\nВернись к заданию, чтобы ввести ответ"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['quest_message_id'] = message_id

        logging.info(f"УСПЕХ: Сообщение обновлено, показан шаг {new_step+1}")

    except Exception as e:
        logging.error(f"ОШИБКА редактирования сообщения: {e}")

        # Если сообщение не найдено, отправляем новое
        if "message to edit not found" in str(e) or "message to be edited" in str(e):
            try:
                new_message = bot.send_photo(
                    chat_id=chat_id,
                    photo=hint_url,
                    caption=f"💡Подсказка {new_step+1}/{total_steps}\n Вернись к заданию, чтобы ввести ответ",
                    reply_markup=markup
                )

                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['quest_message_id'] = new_message.message_id

                logging.info(f"УСПЕХ: Отправлено новое сообщение с шагом {new_step+1}")

            except Exception as send_err:
                logging.error(f"ОШИБКА отправки нового сообщения: {send_err}")
                bot.answer_callback_query(call.id, "Ошибка отправки сообщения")
        elif "message is not modified" not in str(e):
            logging.error(f"ОШИБКА обновления сообщения: {e}")
            bot.answer_callback_query(call.id, "Ошибка обновления сообщения")

@bot.callback_query_handler(func=lambda call: call.data.startswith("favorite_category_random_"))
def handle_favorite_category_random(call):
    """Обработчик для навигации по избранным заданиям в режиме случайного порядка"""

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Парсим данные из callback
        # Формат: favorite_category_random_<world_id>_<category_code>_<task_idx>_<position>
        parts = call.data.split("_")
        world_id = parts[3]
        category_code = parts[4]
        task_idx = int(parts[5])
        position = int(parts[6])  # Позиция в списке перемешанных задач

        logging.info(f"Обработка навигации по избранным заданиям в режиме случайного порядка: world_id={world_id}, category={category_code}, task_idx={task_idx}, position={position}")

        # Проверяем, есть ли сохраненный перемешанный список
        if user_id not in user_data or 'random_favorites' not in user_data[user_id]:
            # Если нет сохраненного списка, получаем его из БД
            from main import get_favorite_tasks
            favorites = get_favorite_tasks(user_id, world_id=world_id, order_random=True)

            # Сохраняем для будущего использования
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['random_favorites'] = favorites
            logging.info(f"Создан новый перемешанный список для навигации: {len(favorites)} заданий")
        else:
            logging.info(f"Использован существующий перемешанный список: {len(user_data[user_id]['random_favorites'])} заданий")

        # Отображаем задачу с указанием, что это избранное, в режиме random_order и с правильной позицией
        display_task(chat_id, message_id, world_id, category_code, task_idx, from_favorites=True, random_order=True, current_position=position)

    except Exception as e:
        logging.error(f"Ошибка при обработке навигации по избранным заданиям в режиме случайного порядка: {e}")
        bot.answer_callback_query(call.id, "Ошибка при навигации по избранным")

@bot.callback_query_handler(func=lambda call: call.data.startswith("favorite_category_") and not call.data.startswith("favorite_category_random_"))
def handle_favorite_category(call):
    """Обработчик для навигации по избранным заданиям"""
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = str(call.from_user.id)

        # Получаем параметры из колбэка
        parts = call.data.split('_')
        world_id = parts[2]
        cat_code = parts[3]
        task_idx = int(parts[4])

        logging.info(f"Запрос на отображение избранной задачи: world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")

        # Отображаем задачу с флагом from_favorites=True
        display_task(chat_id, message_id, world_id, cat_code, task_idx, from_favorites=True)

    except Exception as e:
        logging.error(f"Ошибка в handle_favorite_category: {e}")
        bot.answer_callback_query(
            call.id,
            "Ошибка при отображении задачи из избранного"
        )

def handle_quest_favorite(call):
    """Обработчик кнопки "Добавить в избранное"/"Удалить из избранного" для конкретной задачи"""
    # Используем функции определенные в callBack.py, а не импортируем их из main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    # Получаем параметры из колбэка (quest_favorite_world_id_category_id_task_id)
    parts = call.data.split('_')

    if len(parts) >= 5:
        world_id = parts[2]
        cat_code = parts[3]
        task_idx = parts[4]

        logging.info(f"Обработка избранного: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")

        # Проверяем, находится ли задача в избранном
        if is_in_favorites(user_id, world_id, cat_code, task_idx):
            # Если задача в избранном - удаляем
            remove_from_favorites(user_id, world_id, cat_code, task_idx)
            bot.answer_callback_query(call.id, "✅ Задача удалена из избранного")
            logging.info(f"Задача удалена из избранного: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")
        else:
            # Если задачи нет в избранном - добавляем
            add_to_favorites(user_id, world_id, cat_code, task_idx)
            bot.answer_callback_query(call.id, "⭐️ Задача добавлена в избранное")
            logging.info(f"Задача добавлена в избранное: user_id={user_id}, world_id={world_id}, cat_code={cat_code}, task_idx={task_idx}")

        # Обновляем ТОЛЬКО кнопку избранного, а не всю задачу
        try:
            # Сначала пробуем получить текущую разметку сообщения
            message = call.message
            current_markup = message.reply_markup

            if current_markup and current_markup.keyboard:
                # Найдем нашу кнопку с "избранным" и обновим её текст
                in_favorites = is_in_favorites(user_id, world_id, cat_code, task_idx)
                favorite_text = "🗑 Удалить из избранного" if in_favorites else "⭐️ Добавить в избранное"
                favorite_data = f"quest_favorite_{world_id}_{cat_code}_{task_idx}"

                # Ищем кнопку избранного по callback_data и обновляем её текст
                updated = False
                new_keyboard = []

                # Проходим по всем кнопкам и обновляем только кнопку избранного
                for row in current_markup.keyboard:
                    new_row = []
                    for button in row:
                        if button.callback_data and button.callback_data.startswith("quest_favorite_"):
                            # Это кнопка избранного - обновляем текст
                            new_row.append(InlineKeyboardButton(favorite_text, callback_data=favorite_data))
                            updated = True
                        else:
                            # Остальные кнопки оставляем без изменений
                            new_row.append(button)
                    new_keyboard.append(new_row)

                # Создаем новую клавиатуру с обновленными кнопками
                if updated:
                    new_markup = InlineKeyboardMarkup()
                    new_markup.keyboard = new_keyboard

                    # Обновляем только клавиатуру без изменения содержимого сообщения
                    bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=new_markup
                    )
                    logging.info(f"Обновлена кнопка избранного в сообщении, избранное: {in_favorites}")
                    return

            # Если не удалось обновить только кнопку, используем запасной вариант с полным обновлением
            logging.info(f"Не удалось обновить только кнопку, обновляем всю задачу")
            display_task(chat_id, message_id, world_id, cat_code, int(task_idx))

        except Exception as e:
            logging.error(f"Ошибка при обновлении кнопки избранного: {e}")
            # В случае ошибки используем запасной вариант с полным обновлением задачи
            display_task(chat_id, message_id, world_id, cat_code, int(task_idx))
    else:
        logging.error(f"Неверный формат callback_data для обработки избранного: {call.data}")
        bot.answer_callback_query(call.id, "Произошла ошибка при обработке избранного")

    return

def handle_quest_favorites_with_simple_animation(call):
    """Обработчик просмотра избранных заданий в квесте с простой анимацией загрузки"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    import time

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Сначала отображаем анимацию загрузки
        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n0%\nПодготовка данных..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)

        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n25%\nПолучение списка заданий..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)

        # Фото для экрана избранного
        favorites_image = "https://imgur.com/b9u6HER.jpg"

        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n50%\nОбработка избранных заданий..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)

        # Получаем избранные задания пользователя
        favorites = get_user_favorites(user_id)
        logging.info(f"Получено избранное для user_id={user_id}: {len(favorites)} задач")

        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n75%\nФормирование интерфейса..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)

        bot.edit_message_media(
            media=InputMediaPhoto(photo_quest_main, caption="Загрузка избранного...\n\n100%\nЗавершение..."),
            chat_id=chat_id,
            message_id=message_id
        )
        time.sleep(0.3)

        if not favorites:
            # Если у пользователя нет избранных заданий
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nУ вас пока нет избранных заданий.\nДобавьте задания в избранное, нажав на звёздочку в задачах квеста."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
            return

        # Группируем задания по мирам
        grouped = {}
        for item in favorites:
            world_id = item['challenge_num']
            if world_id not in grouped:
                grouped[world_id] = []
            grouped[world_id].append(item)

        logging.info(f"Обработка избранного для пользователя {user_id}. Найдено {len(favorites)} заданий")
        logging.info(f"Сгруппировано по мирам: {list(grouped.keys())}")

        # Создаем клавиатуру для выбора мира
        markup = InlineKeyboardMarkup(row_width=1)

        # Добавляем кнопки для каждого мира
        for world_id in sorted(grouped.keys()):
            # Находим информацию о мире в списке миров
            try:
                world_id_int = int(world_id)
                world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
            except ValueError:
                world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id), None)

            if world:
                # Используем имя мира из списка
                world_name = world["name"]
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_name} ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.info(f"Добавлена кнопка для мира {world_id}: {world_name} ({count})")
            else:
                # Если мир не найден, используем ID как имя
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"🌍 {world_id}. Мир ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.warning(f"Мир с ID {world_id} не найден в списке миров")

        # Кнопка возврата
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call"))

        # Отображаем окончательный экран с избранными заданиями
        bot.edit_message_media(
            media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nВыберите мир для просмотра избранных заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список избранных заданий для пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий: {e}")
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo_quest_main, caption="Произошла ошибка при загрузке избранных заданий. Пожалуйста, попробуйте позже."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="mathQuest_back_call")
                )
            )
        except Exception as e2:
            logging.error(f"Не удалось отобразить сообщение об ошибке: {e2}")

# Сохраняем старую функцию для обратной совместимости
def handle_quest_favorites_no_animation(call):
    """Обработчик просмотра избранных заданий в квесте без анимации загрузки"""
    from instance import photo_quest_main
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)  # Приведение к строковому типу для совместимости с БД

    try:
        # Фото для экрана избранного
        favorites_image = "https://imgur.com/b9u6HER.jpg"

        # Получаем избранные задания пользователя
        favorites = get_user_favorites(user_id)
        logging.info(f"Получено избранное для user_id={user_id}: {len(favorites)} задач")

        if not favorites:
            # Если у пользователя нет избранных заданий
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nУ вас пока нет избранных заданий.\nДобавьте задания в избранное, нажав на звёздочку в задачах квеста."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="quest_select_world")
                )
            )
            return

        # Группируем задания по мирам
        grouped = {}
        for item in favorites:
            world_id = item['challenge_num']
            if world_id not in grouped:
                grouped[world_id] = []
            grouped[world_id].append(item)

        logging.info(f"Обработка избранного для пользователя {user_id}. Найдено {len(favorites)} заданий")
        logging.info(f"Сгруппировано по мирам: {list(grouped.keys())}")

        # Создаем клавиатуру для выбора мира
        markup = InlineKeyboardMarkup(row_width=1)

        # Добавляем кнопки для каждого мира
        for world_id in sorted(grouped.keys()):
            # Находим информацию о мире в списке миров
            try:
                world_id_int = int(world_id)
                world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
            except ValueError:
                world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id), None)

            if world:
                # Используем имя мира из списка без добавления дополнительной иконки 🌍
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 25.0: Исправлено дублирование эмодзи в имени мира
                world_name = world["name"]
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"{world_name} ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.info(f"Добавлена кнопка для мира {world_id}: {world_name} ({count})")
            else:
                # Если мир не найден, используем ID как имя
                count = len(grouped[world_id])
                markup.add(InlineKeyboardButton(
                    f"Мир {world_id} ({count})",
                    callback_data=f"quest_favorite_world_{world_id}"
                ))
                logging.warning(f"Мир с ID {world_id} не найден в списке миров")

        # Кнопка возврата к списку миров
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 25.0: Изменен callback кнопки назад, 
        # чтобы она вела к выбору мира, а не в главное меню
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_select_world"))

        # Отображаем окончательный экран с избранными заданиями
        bot.edit_message_media(
            media=InputMediaPhoto(favorites_image, caption="⭐ Избранные задания\n\nВыберите мир для просмотра избранных заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображен список избранных заданий для пользователя {user_id}")

    except Exception as e:
        # Обработка ошибок
        logging.error(f"Ошибка при отображении избранного без анимации: {e}")
        try:
            bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте позже.")
            bot.edit_message_media(
                media=InputMediaPhoto("https://imgur.com/N9LBWJJ.jpg", caption="⚠️ Ошибка\n\nПроизошла ошибка при загрузке избранного.\nПопробуйте позже."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="quest_select_world")
                )
            )
        except Exception as e2:
            logging.error(f"Не удалось отобразить сообщение об ошибке: {e2}")

# Обработчик для просмотра избранных заданий с красивой анимацией загрузки
def handle_quest_favorites(call):
    """Обработчик просмотра избранных заданий в квесте с красивой анимацией загрузки"""
    from main import get_favorite_worlds, get_favorites_count
    from screens import quest_favorites_screen
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)  # Приведение к строковому типу для совместимости с БД

    try:
        # Фото для экрана избранного из требований
        favorites_image = "https://imgur.com/Z2Zay6H"
        import time

        # Анимация загрузки избранного
        loading_bars = [
            "[███░░░░░░░░░░░░░░░] 17%",
            "[█████░░░░░░░░░░░░] 33%",
            "[████████░░░░░░░░░] 51%",
            "[███████████░░░░░░] 68%",
            "[██████████████░░] 85%",
            "[████████████████] 100%"
        ]

        loading_messages = [
            "Поиск сокровищ...",
            "Перебираем драгоценности...",
            "Проверяем качество камней...",
            "Восстанавливаем блеск...",
            "Сортируем по значимости...",
            "Доступ к коллекции открыт!"
        ]

        # Отправляем серию сообщений с анимацией загрузки
        for i in range(6):
            caption = f"Загрузка избранного...\n\n{loading_bars[i]}\n{loading_messages[i]}"

            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=None
            )

            # Задержка для анимации (0.5 секунд между кадрами)
            time.sleep(0.5)

        # После загрузки показываем экран избранного
        # Получаем список миров, в которых есть избранные задачи
        favorite_worlds = get_favorite_worlds(user_id)

        # Получаем общее количество избранных задач
        total_favorites = get_favorites_count(user_id)

        # Формируем описание для экрана избранного
        if total_favorites > 0:
            # Если есть избранные задачи, сразу показываем список миров
            # Вызываем функцию отображения миров с избранным напрямую
            return handle_quest_favorites_by_world(call)
        else:
            caption = "Ваша коллекция избранных задач пуста\n\nДобавляйте интересные задачи в избранное с помощью кнопки \"⭐️ Добавить в избранное\" при просмотре задач."

            # Показываем экран с сообщением о пустой коллекции
            bot.edit_message_media(
                media=InputMediaPhoto(favorites_image, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="quest_back_to_worlds")
                )
            )

        logging.info(f"Пользователь {user_id} открыл экран избранного. Найдено {total_favorites} избранных задач в {len(favorite_worlds)} мирах")
    except Exception as e:
        logging.error(f"Ошибка при отображении избранных заданий: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий.")

@bot.callback_query_handler(func=lambda call: call.data == "quest_favorites_sequential")
def handle_quest_favorites_sequential(call):
    """Обработчик просмотра избранных задач подряд"""
    from main import get_favorite_tasks

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)  # Приведение к строковому типу для совместимости с БД

    # Получаем список всех избранных задач по порядку
    favorites = get_favorite_tasks(user_id, order_random=False)

    if not favorites:
        bot.answer_callback_query(call.id, "⚠️ У вас нет избранных задач")
        return

    # Берем первую задачу из списка
    first_task = favorites[0]
    world_id = first_task[0]
    cat_code = first_task[1]
    task_idx = first_task[2]

    # Отображаем первую задачу
    display_task(chat_id, message_id, world_id, cat_code, int(task_idx), from_favorites=True)
    logging.info(f"Пользователь {user_id} начал просмотр избранных задач по порядку")

@bot.callback_query_handler(func=lambda call: call.data == "quest_favorites_random")
def handle_quest_favorites_random(call):
    """Обработчик просмотра избранных задач вперемешку"""
    from main import get_favorite_tasks

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)  # Приведение к строковому типу для совместимости с БД

    # Получаем список избранных задач в случайном порядке
    favorites = get_favorite_tasks(user_id, order_random=True)

    if not favorites:
        bot.answer_callback_query(call.id, "⚠️ У вас нет избранных задач")
        return

    # Берем первую задачу из перемешанного списка
    first_task = favorites[0]
    world_id = first_task[0]
    cat_code = first_task[1]
    task_idx = first_task[2]

    # Отображаем первую задачу
    display_task(chat_id, message_id, world_id, cat_code, int(task_idx), from_favorites=True)
    logging.info(f"Пользователь {user_id} начал просмотр избранных задач в случайном порядке")

@bot.callback_query_handler(func=lambda call: call.data == "quest_favorites_by_world")
def handle_quest_favorites_by_world(call):
    """Обработчик просмотра избранных заданий по мирам"""
    from main import get_favorite_worlds, get_favorites_count
    from screens import quest_favorites_worlds_screen
    from telebot.types import InputMediaPhoto

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)  # Приведение к строковому типу для совместимости с БД

    # Получаем список миров, в которых есть избранные задачи
    favorite_worlds = get_favorite_worlds(user_id)

    if not favorite_worlds:
        bot.answer_callback_query(call.id, "⚠️ У вас нет избранных задач")
        return

    # Формируем список миров с названиями и количеством задач
    caption = "⭐️ Избранные задания\n\nВыберите мир для просмотра избранных заданий:"

    # Создаем словарь с количеством задач для каждого мира
    world_counts = {}
    for world_id in favorite_worlds:
        world_counts[world_id] = get_favorites_count(user_id, world_id)
        logging.info(f"ДИАГНОСТИКА: Мир {world_id}, количество задач: {world_counts[world_id]}")

    # Показываем экран выбора мира
    favorites_image = "https://imgur.com/Z2Zay6H"  # URL из требований

    # Создаем объект разметки из telebot.types
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(row_width=1)

    # Список миров с количеством задач
    for world_id in favorite_worlds:
        # Получаем название мира
        world_name = f"Мир {world_id}"  # По умолчанию название с номером мира

        # Ищем имя мира в списке миров
        for world in QUEST_WORLDS:
            if str(world["id"]) == str(world_id):
                world_name = world["name"]
                break

        # Получаем количество задач в этом мире
        count = world_counts[world_id]

        # Добавляем кнопку с названием мира и количеством задач
        markup.add(
            InlineKeyboardButton(f"{world_name} ({count})", callback_data=f"quest_favorite_world_{world_id}")
        )

    # Кнопка возврата
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data="quest_back_to_worlds")
    )

    bot.edit_message_media(
        media=InputMediaPhoto(favorites_image, caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )

    logging.info(f"Пользователь {user_id} открыл список миров с избранными задачами. Найдено {len(favorite_worlds)} миров")

def handle_quest_favorite_world(call):
    """Обработчик просмотра избранных заданий конкретного мира"""
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем ID мира из колбэка
        world_id_str = call.data.split("_")[-1]

        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)

        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return

        # Используем строковое представление world_id для сравнения с challenge_num из БД
        world_id_for_db = str(world["id"])

        # Получаем избранные задания для этого мира
        all_favorites = get_user_favorites(user_id)
        logging.info(f"Получены все избранные задания для пользователя {user_id}: {len(all_favorites)}")

        # Фильтруем задания для текущего мира, с преобразованием типов
        world_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db]
        logging.info(f"Отфильтрованы задания для мира {world_id_for_db}: {len(world_favorites)}")

        if not world_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этом мире")
            return

        # Сохраняем избранные задания для этого мира в user_data
        if user_id not in user_data:
            user_data[user_id] = {}

        # Подготавливаем данные для просмотра заданий
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in world_favorites]
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_screen"] = "favorite_view"

        # Создаем клавиатуру с кнопками просмотра
        markup = InlineKeyboardMarkup(row_width=1)

        # Добавляем кнопки для разных режимов просмотра без индикации количества заданий
        markup.add(InlineKeyboardButton(
            "🔢 Подряд",
            callback_data=f"quest_favorite_view_ordered_{world['id']}"
        ))

        # Добавляем кнопку "Вперемежку" всегда, она просто будет показывать задачи в том же порядке для одной задачи
        markup.add(InlineKeyboardButton(
            "🔁 Вперемежку",
            callback_data=f"quest_favorite_view_random_{world['id']}"
        ))

        # Добавляем кнопку "По темам" для просмотра по категориям
        markup.add(InlineKeyboardButton(
            "📚 По темам",
            callback_data=f"quest_favorite_world_categories_{world['id']}"
        ))

        # Кнопка возврата - используем специальный callback для возврата без анимации
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_favorites_no_animation"))

        # Отображаем меню выбора способа просмотра
        bot.edit_message_media(
            media=InputMediaPhoto(world["loaded_image"], caption=f"⭐ Избранные задания - {world['name']}\n\nВыберите способ просмотра заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображено меню просмотра избранных заданий для мира {world['name']}")
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий для мира: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")

@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_view_ordered_"))
def handle_quest_favorite_view_ordered(call):
    """Обработчик для просмотра избранных заданий конкретного мира по порядку"""
    from main import get_favorite_tasks

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем ID мира из callback_data
        world_id_str = call.data.split("_")[-1]

        # Приводим к нужному формату для БД
        world_id_for_db = str(world_id_str)

        # Получаем избранные задачи для этого мира по порядку
        favorites = get_favorite_tasks(user_id, world_id=world_id_for_db, order_random=False)

        if not favorites:
            bot.answer_callback_query(call.id, "⚠️ Не найдены избранные задачи в этом мире")
            return

        # Берем первую задачу из списка
        first_task = favorites[0]
        challenge_num = first_task[0]
        cat_code = first_task[1]
        task_idx = first_task[2]

        # Отображаем первую задачу
        display_task(chat_id, message_id, challenge_num, cat_code, int(task_idx), from_favorites=True)
        logging.info(f"Пользователь {user_id} начал просмотр избранных задач мира {world_id_str} по порядку")

    except Exception as e:
        logging.error(f"Ошибка при отображении избранных задач по порядку: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий")


@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_view_random_") and not call.data.startswith("quest_favorite_view_random_category_"))
def handle_quest_favorite_view_random(call):
    """Обработчик для просмотра избранных заданий конкретного мира в случайном порядке"""
    from main import get_favorite_tasks

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем ID мира из callback_data
        world_id_str = call.data.split("_")[-1]

        # Приводим к нужному формату для БД
        world_id_for_db = str(world_id_str)

        # Получаем избранные задачи для этого мира в случайном порядке
        favorites = get_favorite_tasks(user_id, world_id=world_id_for_db, order_random=True)

        if not favorites:
            bot.answer_callback_query(call.id, "⚠️ Не найдены избранные задачи в этом мире")
            return

        # Сохраняем перемешанный список в user_data для использования в навигации
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['random_favorites'] = favorites
        logging.info(f"Сохранен перемешанный список избранных задач для {user_id}: {len(favorites)} заданий")

        # Берем первую задачу из перемешанного списка
        first_task = favorites[0]
        challenge_num = first_task[0]
        cat_code = first_task[1]
        task_idx = first_task[2]

        # Отображаем первую задачу с указанием случайного порядка и позицией 0
        display_task(chat_id, message_id, challenge_num, cat_code, int(task_idx), from_favorites=True, random_order=True, current_position=0)
        logging.info(f"Пользователь {user_id} начал просмотр избранных задач мира {world_id_str} в случайном порядке")

    except Exception as e:
        logging.error(f"Ошибка при отображении избранных задач в случайном порядке: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий")


@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_world_categories_"))
def handle_quest_favorite_world_categories(call):
    """Обработчик для отображения категорий с избранными заданиями в конкретном мире"""
    from main import get_favorite_categories
    from screens import quest_favorites_categories_screen
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем ID мира из callback_data
        world_id_str = call.data.split("_")[-1]

        # Приводим к нужному формату для БД
        world_id_for_db = str(world_id_str)

        # Находим информацию о мире
        try:
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)

        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            return

        # Получаем категории с избранными задачами для этого мира
        categories = get_favorite_categories(user_id, world_id_for_db)

        if not categories:
            bot.answer_callback_query(call.id, "⚠️ Не найдены категории с избранными задачами")
            return

        # Устанавливаем ID пользователя в переменную окружения для использования в screens.py
        import os
        os.environ["CURRENT_USER_ID"] = user_id

        # Отображаем экран выбора категории
        bot.edit_message_media(
            media=InputMediaPhoto(
                world["loaded_image"],
                caption=f"📚 Избранные задания - {world['name']}\n\nВыберите категорию:"
            ),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=quest_favorites_categories_screen(world_id_for_db, categories)
        )

        logging.info(f"Пользователь {user_id} открыл список категорий для мира {world['name']}. Найдено {len(categories)} категорий")

    except Exception as e:
        logging.error(f"Ошибка при отображении категорий с избранными заданиями: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки категорий")


@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_view_by_category_") and not call.data.startswith("quest_favorite_view_by_category_random_"))
def handle_quest_favorite_view_by_category(call):
    """Обработчик для просмотра избранных заданий конкретной категории по порядку"""
    from main import get_favorite_tasks

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Парсим callback_data для получения параметров
        parts = call.data.split("_")
        world_id_str = parts[-2]
        category_code = parts[-1]

        # Приводим к нужному формату для БД
        world_id_for_db = str(world_id_str)

        # Получаем избранные задачи для этой категории
        favorites = get_favorite_tasks(user_id, world_id=world_id_for_db, category_id=category_code)

        if not favorites:
            bot.answer_callback_query(call.id, "⚠️ Не найдены избранные задачи в этой категории")
            return

        # Берем первую задачу из списка
        first_task = favorites[0]
        challenge_num = first_task[0]
        cat_code = first_task[1]
        task_idx = first_task[2]

        # Устанавливаем маркер текущего экрана для правильной фильтрации задач в категории
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['current_screen'] = "favorite_category_view"
        logging.info(f"Установлен current_screen = favorite_category_view для пользователя {user_id}")

        # Отображаем первую задачу
        display_task(chat_id, message_id, challenge_num, cat_code, int(task_idx), from_favorites=True)
        logging.info(f"Пользователь {user_id} начал просмотр избранных задач категории {category_code} мира {world_id_str}")

    except Exception as e:
        logging.error(f"Ошибка при отображении избранных задач категории: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий")


@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_category_"))
def handle_quest_favorite_category(call):
    """Обработчик просмотра избранных заданий конкретной категории"""
    # Import тут, чтобы избежать циклических импортов
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    try:
        # Получаем параметры из колбэка
        parts = call.data.split("_")
        world_id_str = parts[-2]
        cat_code = parts[-1]

        logging.info(f"Обработка избранных заданий категории для пользователя {user_id}, мир: {world_id_str}, категория: {cat_code}")

        try:
            # Пробуем преобразовать в число, так как в QUEST_WORLDS id хранятся как числа
            world_id_int = int(world_id_str)
            world = next((w for w in QUEST_WORLDS if w["id"] == world_id_int), None)
        except ValueError:
            # Если не удалось преобразовать в число, пытаемся найти мир с id в строковом формате
            logging.warning(f"Не удалось преобразовать world_id {world_id_str} в число")
            world = next((w for w in QUEST_WORLDS if str(w["id"]) == world_id_str), None)

        if not world:
            bot.answer_callback_query(call.id, "Ошибка: мир не найден")
            logging.error(f"Мир с ID {world_id_str} не найден в QUEST_WORLDS")
            return

        # Используем строковое представление world_id для сравнения с challenge_num из БД
        world_id_for_db = str(world["id"])
        
        # Получаем информацию о категориях в этом мире
        world_challenges = challenge.get(world_id_for_db, {})
        category = world_challenges.get(cat_code)
        
        if not category:
            bot.answer_callback_query(call.id, "Ошибка: категория не найдена")
            logging.error(f"Категория с кодом {cat_code} не найдена в мире {world_id_for_db}")
            return
        
        # Получаем избранные задания для этой категории
        all_favorites = get_user_favorites(user_id)
        logging.info(f"Получены все избранные задания для пользователя {user_id}: {len(all_favorites)}")
        
        # Фильтруем задания для текущей категории, с преобразованием типов
        category_favorites = [f for f in all_favorites if f['challenge_num'] == world_id_for_db and f['cat_code'] == cat_code]
        logging.info(f"Отфильтрованы задания для категории {cat_code} в мире {world_id_for_db}: {len(category_favorites)}")
        
        if not category_favorites:
            bot.answer_callback_query(call.id, "Нет избранных заданий в этой категории")
            return
        
        # Сохраняем избранные задания для этой категории в user_data
        if user_id not in user_data:
            user_data[user_id] = {}
        
        # Подготавливаем данные для просмотра заданий
        favorite_tasks = [(fav["challenge_num"], fav["cat_code"], fav["task_idx"]) for fav in category_favorites]
        user_data[user_id]["favorite_tasks"] = favorite_tasks
        user_data[user_id]["current_index"] = 0
        user_data[user_id]["current_world_id"] = world["id"]
        user_data[user_id]["current_screen"] = "favorite_category_view"
        
        # Создаем клавиатуру с кнопками просмотра
        markup = InlineKeyboardMarkup(row_width=1)
        
        # Добавляем кнопки для разных режимов просмотра с указанием количества заданий
        markup.add(InlineKeyboardButton(
            f"🔢 Подряд ({len(category_favorites)} заданий)", 
            callback_data=f"quest_favorite_view_by_category_{world['id']}_{cat_code}"
        ))
        
        # Добавляем кнопку "Вперемежку" всегда, она просто будет показывать задачи в том же порядке для одной задачи
        # Создаем новую callback ссылку для случайного порядка с ID категории
        random_callback = f"quest_favorite_view_by_category_random_{world['id']}_{cat_code}"
        markup.add(InlineKeyboardButton(
            f"🔁 Вперемежку ({len(category_favorites)} заданий)", 
            callback_data=random_callback
        ))
        
        # Кнопка возврата - используем специальный callback для возврата к списку категорий текущего мира
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_categories_{world_id_for_db}"))
        
        # Отображаем меню выбора способа просмотра
        bot.edit_message_media(
            media=InputMediaPhoto(world["loaded_image"], caption=f"⭐ Избранные задания - {world['name']}\nКатегория: {category['name']}\n\nВыберите способ просмотра заданий:"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        logging.info(f"Отображено меню просмотра избранных заданий категории {category['name']} для пользователя {user_id}")
    
    except Exception as e:
        logging.error(f"Ошибка при обработке избранных заданий категории: {e}")
        bot.answer_callback_query(call.id, "Ошибка при загрузке избранных заданий")
        
@bot.callback_query_handler(func=lambda call: call.data.startswith("quest_favorite_view_by_category_random_"))
def handle_quest_favorite_view_by_category_random(call):
    """Обработчик для просмотра избранных заданий конкретной категории в случайном порядке"""
    from main import get_favorite_tasks
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Парсим callback_data для получения параметров
        parts = call.data.split("_")
        world_id_str = parts[-2]
        category_code = parts[-1]
        
        # Приводим к нужному формату для БД
        world_id_for_db = str(world_id_str)
        
        # Получаем избранные задачи только для этой категории в случайном порядке
        favorites = get_favorite_tasks(user_id, world_id=world_id_for_db, category_id=category_code, order_random=True)
        
        if not favorites:
            bot.answer_callback_query(call.id, "⚠️ Не найдены избранные задачи в этой категории")
            return
        
        # Сохраняем перемешанный список в user_data для использования в навигации
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['random_favorites'] = favorites
        user_data[user_id]['current_screen'] = "favorite_category_view"
        logging.info(f"Сохранен перемешанный список избранных задач категории для {user_id}: {len(favorites)} заданий")
        
        # Берем первую задачу из перемешанного списка
        first_task = favorites[0]
        challenge_num = first_task[0]
        cat_code = first_task[1]
        task_idx = first_task[2]
        
        # Отображаем первую задачу с указанием случайного порядка и позицией 0
        display_task(chat_id, message_id, challenge_num, cat_code, int(task_idx), from_favorites=True, random_order=True, current_position=0)
        logging.info(f"Пользователь {user_id} начал просмотр избранных задач категории {category_code} мира {world_id_str} в случайном порядке")
    
    except Exception as e:
        logging.error(f"Ошибка при отображении избранных задач категории в случайном порядке: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки избранных заданий")


@bot.callback_query_handler(func=lambda call: call.data.startswith("favorite_category_random_by_category_"))
def handle_favorite_category_random_by_category(call):
    """Обработчик для навигации по избранным заданиям категории в режиме случайного порядка"""
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Парсим данные из callback
        # Формат: favorite_category_random_by_category_<world_id>_<category_code>_<task_idx>_<position>
        parts = call.data.split("_")
        world_id = parts[4]
        category_code = parts[5]
        task_idx = int(parts[6])
        position = int(parts[7])  # Позиция в списке перемешанных задач
        
        logging.info(f"Обработка навигации по избранным заданиям категории в режиме случайного порядка: world_id={world_id}, category={category_code}, task_idx={task_idx}, position={position}")
        
        # Проверяем, есть ли сохраненный перемешанный список
        if user_id not in user_data or 'random_favorites' not in user_data[user_id]:
            # Если нет сохраненного списка, получаем его из БД
            from main import get_favorite_tasks
            favorites = get_favorite_tasks(user_id, world_id=world_id, category_id=category_code, order_random=True)
            
            # Сохраняем для будущего использования
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['random_favorites'] = favorites
            user_data[user_id]['current_screen'] = "favorite_category_view"
            logging.info(f"Создан новый перемешанный список категории для навигации: {len(favorites)} заданий")
        else:
            logging.info(f"Использован существующий перемешанный список: {len(user_data[user_id]['random_favorites'])} заданий")
        
        # Отображаем задачу с указанием, что это избранное, в режиме random_order и с правильной позицией
        display_task(chat_id, message_id, world_id, category_code, task_idx, from_favorites=True, random_order=True, current_position=position)
        
    except Exception as e:
        logging.error(f"Ошибка при обработке навигации по избранным заданиям категории в режиме случайного порядка: {e}")
        bot.answer_callback_query(call.id, "Ошибка при навигации по избранным категории")

    # Здесь был дублирующийся блок except - код должен работать корректно после удаления дублирования
        
def handle_quest_homework(call):
    """Обработчик просмотра домашних заданий в квесте (Ритуал повторения)"""
    from instance import photo_quest_ritual
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Всегда запускаем синхронизацию при открытии домашних заданий
    # чтобы гарантировать актуальность списка
    logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Принудительная синхронизация при открытии ДЗ")
    force_sync_homework_tasks()
    logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Синхронизация завершена")
    
    # Инициализируем данные пользователя при необходимости
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # Извлекаем ID мира из callback-данных
    data = call.data.split('_')
    if len(data) > 3:
        world_id = data[3]
        logging.info(f"Получен мир из callback: {world_id}")
    else:
        # Используем мир 6 (Мир Простейших Уравнений) по умолчанию
        world_id = '6'
        logging.info(f"Используем мир по умолчанию: {world_id}")
    
    user_data[user_id]['current_world_id'] = world_id
    
    # Получаем все категории для этого мира
    world_categories = challenge.get(world_id, {})
    
    # Получаем список домашних заданий для пользователя
    homework_tasks = []
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info(f"Подключение к базе данных task_progress.db для Ритуала повторения")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Перед загрузкой списка заданий, сделаем принудительный
        # вызов VACUUM для оптимизации базы данных 
        cursor.execute("PRAGMA journal_mode = WAL")
        conn.commit()
        
        # Получаем все домашние задания
        # Удалена сортировка, чтобы позиция заданий не менялась в зависимости от статуса
        cursor.execute("""
            SELECT cat_code, task_idx FROM task_progress 
            WHERE user_id = ? AND type = 'homework'
        """, (user_id,))
        
        homework_tasks = cursor.fetchall()
        
        # Выводим отладочную информацию
        print(f"Найдено {len(homework_tasks)} домашних заданий для пользователя {user_id}")
        print(f"Все домашние задания: {homework_tasks}")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Выводим подробную информацию в лог
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Загружено {len(homework_tasks)} ДЗ для пользователя {user_id}")
        
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении домашних заданий: {e}")
    
    # Если нет домашних заданий
    if not homework_tasks:
        # Дополнительно проверяем наличие заданий с неверными ответами
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            logging.info(f"Подключение к базе данных task_progress.db для проверки заданий с неверными ответами")
            
            # Получаем все задания с неверными ответами
            # Удалена сортировка, чтобы позиция заданий не менялась в зависимости от статуса
            cursor.execute("""
                SELECT challenge_num, cat_code, task_idx FROM task_progress 
                WHERE (user_id = ? AND status = 'wrong')
                OR (user_id = ? AND type = 'main' AND status = '0')
            """, (user_id, user_id))
            
            wrong_tasks = cursor.fetchall()
            
            # Если есть задания с неверными ответами, добавляем их в домашнюю работу
            if wrong_tasks:
                logging.info(f"Найдено {len(wrong_tasks)} заданий с неверными ответами для пользователя {user_id}")
                for task in wrong_tasks:
                    challenge_num, cat_code, task_idx = task
                    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.1: Используем статус "unresolved" вместо "wrong"
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, challenge_num, cat_code, task_idx, "homework", "unresolved"))
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.1: Задача с неверным ответом добавлена в ДЗ со статусом 'unresolved': {user_id}_{challenge_num}_{cat_code}_{task_idx}")
                
                conn.commit()
                homework_tasks = wrong_tasks
                
            conn.close()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при проверке заданий с неверными ответами: {e}")
            
    # Если все еще нет домашних заданий
    if not homework_tasks:
        bot.edit_message_media(
            media=InputMediaPhoto(
                photo_quest_ritual,
                caption="У тебя пока нет домашнего задания.\n\nЗадания появятся здесь, если ответишь неверно или воспользуешься подсказкой при решении задач."
            ),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
            )
        )
        bot.answer_callback_query(call.id)
        return
    
    # Группируем домашние задания по категориям
    categories_dict = {}
    for task in homework_tasks:
        # Если это кортеж с двумя элементами (cat_code, task_idx)
        if len(task) == 2:
            cat_code, task_idx = task
            if cat_code not in categories_dict:
                categories_dict[cat_code] = []
            categories_dict[cat_code].append(task_idx)
        # Если это кортеж с тремя элементами (challenge_num, cat_code, task_idx)
        elif len(task) == 3:
            challenge_num, cat_code, task_idx = task
            if cat_code not in categories_dict:
                categories_dict[cat_code] = []
            categories_dict[cat_code].append(task_idx)
        
    # Выводим отладочную информацию
    logging.info(f"Сгруппированные категории: {categories_dict}")
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Определяем порядок категорий как в квесте 
    # (соответствует порядку в словаре challenge)
    ordered_categories = []
    
    # Добавляем категории в том же порядке, что и в словаре challenge
    for world_id_str in challenge:
        for cat_code in challenge[world_id_str]:
            if cat_code in categories_dict and cat_code not in [c for c, _ in ordered_categories]:
                ordered_categories.append((cat_code, challenge[world_id_str][cat_code]['name']))
    
    # Добавляем оставшиеся категории, которые могут быть не в списке challenge
    for cat_code in categories_dict:
        if cat_code not in [c for c, _ in ordered_categories]:
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Улучшаем обработку неизвестных категорий
            # Если категория не найдена, используем специализированные имена
            if cat_code == 'quad':
                name = "Квадратичная функция"
            elif cat_code == 'frac':
                name = "Дробно-рациональные выражения"
            elif cat_code == 'log':
                name = "Логарифмические выражения"
            elif cat_code == 'exp':
                name = "Показательные функции"
            elif cat_code == 'odd':
                name = "Разные задания"
            elif cat_code == 'lin':
                name = "Линейные функции"
            else:
                name = world_categories.get(cat_code, {}).get('name', f"Тип: {cat_code}")
            
            logging.info(f"⚠️ КАТЕГОРИЯ НЕ НАЙДЕНА В МИРЕ: {cat_code}, используем имя: {name}")
            ordered_categories.append((cat_code, name))
    
    # Добавляем кнопки для каждой категории в правильном порядке с информацией о прогрессе (решенных верно/всего)
    for cat_code, category_name in ordered_categories:
        tasks = categories_dict[cat_code]
        try:
            # Подсчитываем количество правильно решенных домашних заданий для данной категории
            conn_task = sqlite3.connect('task_progress.db')
            cursor_task = conn_task.cursor()
            
            cursor_task.execute("""
                SELECT COUNT(*) FROM task_progress 
                WHERE user_id = ? AND cat_code = ? AND type = 'homework' AND status = 'correct'
            """, (user_id, cat_code))
            
            correct_count = cursor_task.fetchone()[0]
            conn_task.close()
            
            # Добавляем кнопку с информацией о прогрессе (решенных верно/всего)
            markup.add(
                InlineKeyboardButton(
                    f"{category_name} ({correct_count}/{len(tasks)})",
                    callback_data=f"quest_homework_cat_{world_id}_{cat_code}"
                )
            )
            logging.info(f"Прогресс в категории домашних заданий {cat_code}: {correct_count}/{len(tasks)}")
        except Exception as e:
            logging.error(f"Ошибка при подсчете прогресса для домашних заданий категории {cat_code}: {e}")
            # В случае ошибки показываем только общее количество
            markup.add(
                InlineKeyboardButton(
                    f"{category_name} ({len(tasks)})",
                    callback_data=f"quest_homework_cat_{world_id}_{cat_code}"
                )
            )
        
    
    # Добавляем кнопку "Назад"
    markup.add(
        InlineKeyboardButton("↩️ Назад", callback_data=f"quest_loaded_world_{world_id}")
    )
    
    # Отправляем сообщение
    bot.edit_message_media(
        media=InputMediaPhoto(
            photo_quest_ritual,
            caption="Здесь собраны задания, которые требуют повторения.\nВыбери тему для практики:"
        ),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    bot.answer_callback_query(call.id)

# Инициализация базы пользователей, если они отсутствуют
for user_id in user_data.keys():
    if "current_index" not in user_data[user_id]:
        user_data[user_id]["current_index"] = 0
    
    # Инициализация основных полей пользователя, если отсутствуют
    if "message_id" not in user_data[user_id]:
        user_data[user_id]["message_id"] = None
    if "current_mode" not in user_data[user_id]:
        user_data[user_id]["current_mode"] = None
    if "challenge_num" not in user_data[user_id]:
        user_data[user_id]["challenge_num"] = None
    if "navigation_stack" not in user_data[user_id]:
        user_data[user_id]["navigation_stack"] = []
    if "current_screen" not in user_data[user_id]:
        user_data[user_id]["current_screen"] = None
# Функциональность избранного включена
logging.info("Функциональность избранного включена в callBack.py")

# Функция для отображения задачи (используется для возврата из подсказки)
def display_task(chat_id, message_id, challenge_num, cat_code, task_idx, from_favorites=False, random_order=False, current_position=0):
    """
    Отображает задачу с указанными параметрами.
    
    Параметры:
        chat_id (str/int): ID чата
        message_id (int): ID сообщения для обновления
        challenge_num (str): ID мира/испытания
        cat_code (str): Код категории
        task_idx (int): Индекс задачи
        from_favorites (bool): Флаг, указывающий, что задача открыта из избранного
        random_order (bool): Флаг, указывающий, что просмотр идет в случайном порядке
        current_position (int): Текущая позиция в случайном списке (начиная с 0)
    """
    from main import is_in_favorites
    
    user_id = str(chat_id)  # Приводим user_id к строковому типу для совместимости с БД
    str_user_id = user_id  # Для логов и запросов к БД используем этот же строковый user_id
    
    logging.info(f"Вызов display_task: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, from_favorites={from_favorites}")
    
    try:
        # Проверяем существование задачи
        if challenge_num not in challenge:
            logging.error(f"display_task: challenge_num={challenge_num} не существует!")
            return False
            
        if cat_code not in challenge[challenge_num]:
            logging.error(f"display_task: cat_code={cat_code} для challenge_num={challenge_num} не существует!")
            return False
            
        tasks = challenge[challenge_num][cat_code].get("tasks", [])
        if not tasks or task_idx >= len(tasks):
            logging.error(f"display_task: task_idx={task_idx} вне диапазона для challenge_num={challenge_num}, cat_code={cat_code}!")
            return False
            
        # Получаем информацию о задаче
        task = tasks[task_idx]
        total_tasks = len(tasks)
        
        # Получаем статус задачи из таблицы main
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 19.0: Теперь статусы main и homework полностью независимы
        # При загрузке обычного задания проверяем только статус в main
        
        # Инициализируем соединение с базой данных
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
            """, (str_user_id, str(challenge_num), cat_code, task_idx))
            result = cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении статуса задачи: {e}")
            result = None
        finally:
            conn.close()
        
        # Формируем текст в том же стиле как в квесте
        caption = f"№{challenge_num}\n{challenge[challenge_num][cat_code]['name']}"
        
        # Добавляем статус
        status_text = "❔ Не решено"
        answer_text = ""
        if not result:
            caption += f"\n{status_text}"
        elif result[0] == "correct":
            status_text = "✅ Верно"
            caption += f"\n{status_text}"
            if 'answer' in task:
                answer_text = f"\n\nПравильный ответ: {task['answer']}"
                caption += answer_text
        else:
            status_text = "❌ Неверно"
            caption += f"\n{status_text}"
            
        # Добавляем текст "введи ответ в чат:" для нерешенных заданий
        if status_text == "❔ Не решено" or status_text == "❌ Неверно":
            caption += "\n\nВведи ответ в чат:"
        
        # Создаем клавиатуру
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Кнопки навигации в стиле квеста, в одной строке с пагинацией
        navigation_buttons = []
        
        # Если задача открыта из избранного, считаем количество задач в избранном
        if from_favorites:
            # Проверяем, есть ли сохраненный перемешанный список для пользователя
            if random_order and user_id in user_data and 'random_favorites' in user_data[user_id]:
                # Используем сохраненный перемешанный список
                favorites = user_data[user_id]['random_favorites']
                logging.info(f"Используется сохраненный перемешанный список: {len(favorites)} заданий")
            else:
                # Стандартный порядок из БД
                from main import get_favorite_tasks
                
                # Проверяем, это просмотр категории или общий просмотр
                if "current_screen" in user_data.get(user_id, {}) and user_data[user_id].get("current_screen") == "favorite_category_view":
                    # Для просмотра категории получаем только задачи этой категории
                    favorites = get_favorite_tasks(user_id, world_id=challenge_num, category_id=cat_code)
                    logging.info(f"Получены задания категории {cat_code} из БД: {len(favorites)} заданий")
                else:
                    # Для общего просмотра получаем все задачи мира
                    favorites = get_favorite_tasks(user_id, world_id=challenge_num)
                    logging.info(f"Получены задания из БД: {len(favorites)} заданий")
            
            real_total = len(favorites)
            
            # Определяем текущий индекс в зависимости от режима просмотра
            if random_order:
                # В режиме случайного порядка используем переданную позицию в списке
                current_index = current_position
                logging.info(f"РЕЖИМ ВПЕРЕМЕШКУ: Используется фиксированная позиция {current_position} из {real_total}")
            else:
                # Находим индекс текущей задачи в списке избранных
                current_index = 0
                for i, fav in enumerate(favorites):
                    if fav[1] == cat_code and int(fav[2]) == task_idx:
                        current_index = i
                        break
            
            # Если в избранном всего одна задача, показываем только счетчик без кнопок навигации
            if real_total <= 1:
                navigation_buttons.append(
                    types.InlineKeyboardButton(" ", callback_data="no_action")
                )
                
                navigation_buttons.append(
                    types.InlineKeyboardButton(f"1/1", callback_data="no_action")
                )
                
                navigation_buttons.append(
                    types.InlineKeyboardButton(" ", callback_data="no_action")
                )
            else:
                # Используем правильную нумерацию для избранного, когда задач больше одной
                # Кнопка влево
                if current_index > 0:
                    # Находим предыдущую задачу
                    prev_task = favorites[current_index - 1]
                    prev_cat_code = prev_task[1]
                    prev_task_idx = int(prev_task[2])
                    
                    # Передаем параметр random_order в callback-данные, если нужно
                    if random_order:
                        # Определяем, является ли это просмотром избранных задач конкретной категории
                        if "current_screen" in user_data.get(user_id, {}) and user_data[user_id].get("current_screen") == "favorite_category_view":
                            navigation_buttons.append(
                                types.InlineKeyboardButton("◀️", callback_data=f"favorite_category_random_by_category_{challenge_num}_{prev_cat_code}_{prev_task_idx}_{current_index-1}")
                            )
                        else:
                            navigation_buttons.append(
                                types.InlineKeyboardButton("◀️", callback_data=f"favorite_category_random_{challenge_num}_{prev_cat_code}_{prev_task_idx}_{current_index-1}")
                            )
                    else:
                        navigation_buttons.append(
                            types.InlineKeyboardButton("◀️", callback_data=f"favorite_category_{challenge_num}_{prev_cat_code}_{prev_task_idx}")
                        )
                else:
                    navigation_buttons.append(
                        types.InlineKeyboardButton(" ", callback_data="no_action")
                    )
                    
                # Счетчик
                navigation_buttons.append(
                    types.InlineKeyboardButton(f"{current_index+1}/{real_total}", callback_data="no_action")
                )
                
                # Кнопка вправо
                if current_index < real_total - 1:
                    # Находим следующую задачу
                    next_task = favorites[current_index + 1]
                    next_cat_code = next_task[1]
                    next_task_idx = int(next_task[2])
                    
                    # Передаем параметр random_order в callback-данные, если нужно
                    if random_order:
                        # Определяем, является ли это просмотром избранных задач конкретной категории
                        if "current_screen" in user_data.get(user_id, {}) and user_data[user_id].get("current_screen") == "favorite_category_view":
                            navigation_buttons.append(
                                types.InlineKeyboardButton("▶️", callback_data=f"favorite_category_random_by_category_{challenge_num}_{next_cat_code}_{next_task_idx}_{current_index+1}")
                            )
                        else:
                            navigation_buttons.append(
                                types.InlineKeyboardButton("▶️", callback_data=f"favorite_category_random_{challenge_num}_{next_cat_code}_{next_task_idx}_{current_index+1}")
                            )
                    else:
                        navigation_buttons.append(
                            types.InlineKeyboardButton("▶️", callback_data=f"favorite_category_{challenge_num}_{next_cat_code}_{next_task_idx}")
                        )
                else:
                    navigation_buttons.append(
                        types.InlineKeyboardButton(" ", callback_data="no_action")
                    )
            
        else:
            # Стандартная навигация для обычного режима
            if task_idx > 0:
                navigation_buttons.append(
                    types.InlineKeyboardButton("◀️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}")
                )
            else:
                navigation_buttons.append(
                    types.InlineKeyboardButton(" ", callback_data="no_action")
                )
                
            navigation_buttons.append(
                types.InlineKeyboardButton(f"{task_idx+1}/{total_tasks}", callback_data="no_action")
            )
            
            if task_idx < total_tasks - 1:
                navigation_buttons.append(
                    types.InlineKeyboardButton("▶️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}")
                )
            else:
                navigation_buttons.append(
                    types.InlineKeyboardButton(" ", callback_data="no_action")
                )
        
        markup.row(*navigation_buttons)
        
        # Кнопка подсказки
        if "hint" in task and task["hint"]:
            markup.add(
                types.InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_solution_{challenge_num}_{cat_code}_{task_idx}")
            )
        
        # Кнопка избранного
        is_favorite = is_in_favorites(user_id, challenge_num, cat_code, task_idx)
        favorite_text = "🗑 Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное"
        markup.add(
            types.InlineKeyboardButton(favorite_text, callback_data=f"quest_favorite_{challenge_num}_{cat_code}_{task_idx}")
        )
        
        # Кнопка назад - зависит от контекста
        if from_favorites:
            # Проверяем, это просмотр категории или общий просмотр
            if "current_screen" in user_data.get(user_id, {}) and user_data[user_id].get("current_screen") == "favorite_category_view":
                # Если просмотр категории, то возвращаемся к списку категорий текущего мира
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_categories_{challenge_num}"))
            else:
                # Возвращаемся к меню выбора способа просмотра задач конкретного мира
                markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"quest_favorite_world_{challenge_num}"))
        else:
            markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))
        
        # Отправляем сообщение
        bot.edit_message_media(
            media=types.InputMediaPhoto(task["photo"], caption=caption),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        # Обновляем данные о текущей задаче пользователя
        user_task_data[str_user_id] = {
            "challenge_num": challenge_num,
            "cat_code": cat_code,
            "task_idx": task_idx,
            "message_id": message_id,
            "type": "main",
            "task": task,
            "current_caption": caption,
            "status": result[0] if result else None,
            "from_favorites": from_favorites  # Сохраняем флаг from_favorites для использования в handle_task_answer
        }
        
        # Сохраняем флаг from_favorites в user_data для использования в handle_quest_solution
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['from_favorites'] = from_favorites
        logging.info(f"Сохранен флаг from_favorites={from_favorites} для user_id={user_id}")
        
        return True
    except Exception as e:
        logging.error(f"Ошибка в display_task: {e}")
        return False

def init_task_progress_db():
    connection = sqlite3.connect('task_progress.db')
    cursor = connection.cursor()
    logging.info(f"Инициализация базы данных task_progress.db")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_progress (
            user_id TEXT,
            challenge_num TEXT, -- Используем challenge_num вместо world_id для совместимости
            cat_code TEXT,
            task_idx INTEGER,
            status TEXT,  -- 'correct', 'wrong', 'unresolved'
            type TEXT DEFAULT 'main', -- 'main', 'homework'
            PRIMARY KEY (user_id, challenge_num, cat_code, task_idx, type)
        )''')
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Создаем таблицу для хранения информации о просмотренных подсказках
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hint_usage (
            user_id TEXT,
            challenge_num TEXT,
            cat_code TEXT,
            task_idx INTEGER,
            used INTEGER DEFAULT 1,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, challenge_num, cat_code, task_idx)
        )''')
    
    connection.commit()
    
    # Для отладки: посмотреть все записи в таблице
    cursor.execute("SELECT * FROM task_progress")
    all_records = cursor.fetchall()
    print(f"Текущие записи в task_progress: {all_records}")
    
    connection.close()
    logging.info("✅ Таблица 'task_progress' создана или уже существует!")
    logging.info("✅ Таблица 'hint_usage' создана или уже существует для хранения информации о просмотренных подсказках")
init_task_progress_db()

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавляем функцию для принудительного перемещения неверных ответов в домашнюю работу
# Объявляем глобальную переменную для хранения заданий с использованными подсказками
hint_used_tasks = []

def force_sync_homework_tasks():
    """Синхронизирует задания с неверными ответами и с использованными подсказками с заданиями в домашней работе"""
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info("⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Запуск синхронизации домашних заданий...")
        
        # Получаем все задачи с неверными ответами основного типа
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress 
            WHERE (status = 'wrong' OR status = '0') AND type = 'main'
        """)
        wrong_tasks = cursor.fetchall()
        
        # Получаем все задачи с использованными подсказками
        # ВАЖНО: Эта часть критична для правила "верный ответ + подсказка"
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM hint_usage
            WHERE used = 1
        """)
        hint_tasks = cursor.fetchall()
        
        # Получаем все задачи с верными ответами (для последующей проверки с подсказками)
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress 
            WHERE (status = 'correct' OR status = '1') AND type = 'main'
        """)
        correct_tasks = cursor.fetchall()
        
        # Получаем все задачи из домашней работы
        cursor.execute("""
            SELECT user_id, challenge_num, cat_code, task_idx FROM task_progress 
            WHERE type = 'homework'
        """)
        homework_tasks = cursor.fetchall()
        
        # Создаем множества для быстрого поиска
        wrong_set = set((user_id, challenge_num, cat_code, task_idx) for user_id, challenge_num, cat_code, task_idx in wrong_tasks)
        hint_set = set((user_id, challenge_num, cat_code, task_idx) for user_id, challenge_num, cat_code, task_idx in hint_tasks)
        correct_set = set((user_id, challenge_num, cat_code, task_idx) for user_id, challenge_num, cat_code, task_idx in correct_tasks)
        homework_set = set((user_id, challenge_num, cat_code, task_idx) for user_id, challenge_num, cat_code, task_idx in homework_tasks)
        
        # Находим задачи с верными ответами но использованной подсказкой
        # Это критическая часть для правила "верный ответ + подсказка"
        correct_with_hint_set = correct_set.intersection(hint_set)
        
        # Находим задачи, которые нужно добавить в домашнюю работу:
        # 1. Все неверные ответы
        # 2. Все верные ответы с использованными подсказками
        tasks_to_add = (wrong_set.union(correct_with_hint_set)) - homework_set
        
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Найдено {len(wrong_set)} задач с неверными ответами и {len(hint_set)} задач с использованными подсказками")
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Найдено {len(correct_with_hint_set)} верных ответов с использованными подсказками")
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Текущее количество домашних заданий: {len(homework_set)}")
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Будет добавлено {len(tasks_to_add)} новых заданий в домашнюю работу")
        
        # Добавляем недостающие задачи в домашнюю работу
        count = 0
        for user_id, challenge_num, cat_code, task_idx in tasks_to_add:
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.0: Используем статус "unresolved" вместо "wrong"
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, challenge_num, cat_code, task_idx, "homework", "unresolved"))
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.0: Задание добавлено со статусом 'unresolved': {user_id}_{challenge_num}_{cat_code}_{task_idx}")
            count += 1
            
            # Особое внимание к заданиям типа 'quad'
            if cat_code == 'quad':
                logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительно добавлено задание типа 'quad' в домашнюю работу: user_id={user_id}, challenge_num={challenge_num}, task_idx={task_idx}")
        
        conn.commit()
        logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Синхронизация завершена. Добавлено {count} заданий в домашнюю работу.")
        
        conn.close()
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 26.0: Автоматически обновляем прогресс для всех миров, где были изменения
        updated_worlds = set()
        for task in wrong_tasks:
            user_id, world_id, _, _ = task
            updated_worlds.add((user_id, world_id))
        
        # Для задач с использованными подсказками, если они есть
        if 'hint_used_tasks' in locals():
            for task in hint_used_tasks:
                user_id, world_id, _, _ = task
                updated_worlds.add((user_id, world_id))
        
        # Обновляем прогресс для каждого мира, где были изменения
        for user_id, world_id in updated_worlds:
            try:
                update_world_progress(user_id, world_id)
                logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 26.0: Автоматически обновлен прогресс для пользователя {user_id} в мире {world_id}")
            except Exception as e:
                logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 26.0: Ошибка при автоматическом обновлении прогресса: {e}")
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Ошибка при синхронизации домашних заданий: {e}")

# Запускаем синхронизацию при старте бота
force_sync_homework_tasks()


# Заглушки для функций избранного
def get_user_favorites(user_id):
    """Получает список избранных заданий пользователя из main.py"""
    from main import get_favorite_tasks
    
    logging.info(f"Вызов функции get_user_favorites для user_id={user_id}")
    try:
        # Получаем все избранные задачи пользователя
        favorites = get_favorite_tasks(user_id)
        
        # Преобразуем в формат, ожидаемый функцией
        result = []
        for world_id, cat_code, task_idx in favorites:
            result.append({
                'challenge_num': world_id,
                'cat_code': cat_code,
                'task_idx': int(task_idx)
            })
            
        logging.info(f"Получены избранные задания для пользователя {user_id}: {len(result)}")
        return result
    except Exception as e:
        logging.error(f"Ошибка при получении избранных заданий: {e}")
        return []

def send_favorite_task(chat_id, message_id, task=None, world_id=None, cat_code=None, task_idx=None):
    """Отправляет задачу из избранного"""
    logging.info(f"Вызов функции send_favorite_task")
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    from instance import photo_quest_main
    try:
        # Если передана конкретная задача, отображаем ее
        if task and world_id and cat_code and task_idx is not None:
            display_task(chat_id, message_id, world_id, cat_code, task_idx, from_favorites=True)
            return
            
        # Иначе получаем список задач из избранного
        user_id = str(chat_id)
        favorites = get_user_favorites(user_id)
        
        if not favorites:
            # Если у пользователя нет избранных заданий
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("↩️ Назад", callback_data="quest_select_world")
            )
            bot.edit_message_media(
                media=InputMediaPhoto(photo_quest_main, caption="У вас нет избранных задач.\nДобавьте задачи в избранное, нажав на звёздочку при просмотре задач."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
            
        # Берем первую задачу из списка
        first_task = favorites[0]
        world_id = first_task['challenge_num']
        cat_code = first_task['cat_code']
        task_idx = first_task['task_idx']
        
        # Отображаем первую задачу
        display_task(chat_id, message_id, world_id, cat_code, task_idx, from_favorites=True)
    except Exception as e:
        logging.error(f"Ошибка в функции send_favorite_task: {e}")
        # В случае ошибки показываем сообщение о ней
        try:
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("↩️ Назад", callback_data="quest_select_world")
            )
            bot.edit_message_media(
                media=InputMediaPhoto(photo_quest_main, caption=f"Ошибка при отображении избранного: {e}"),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        except Exception as e2:
            logging.error(f"Вторичная ошибка в send_favorite_task: {e2}")

# Отправка задачи
def send_challenge_task(chat_id, photo, challenge_num, cat_code, task_idx):
    user_id = str(chat_id)
    if user_id not in user_data:
        user_data[user_id] = {
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }

    task = challenge[challenge_num][cat_code]["tasks"][task_idx]
    category_name = challenge[challenge_num][cat_code]["name"]
    total_tasks = len(challenge[challenge_num][cat_code]["tasks"])

    users_cursor.execute("""
        SELECT status FROM task_progress 
        WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main'
    """, (user_id, challenge_num, cat_code, task_idx))
    result = users_cursor.fetchone()
    status_text = "❔ Не решено" if not result else (
        "✅ Верно\n\nПравильный ответ: " + str(task["answer"]) if result[0] == "correct" else "❌ Не верно")

    caption = (
        f"Задача {challenge_num}\n"
        f"{category_name} {task_idx + 1}/{total_tasks}\n"
        f"{status_text}\n"
        "Введи ответ в чат:"
    )

    markup = types.InlineKeyboardMarkup()
    nav_buttons = []
    if task_idx > 0:
        nav_buttons.append(
            types.InlineKeyboardButton("⬅️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx - 1}"))
    if task_idx < total_tasks - 1:
        nav_buttons.append(
            types.InlineKeyboardButton("➡️", callback_data=f"category_{challenge_num}_{cat_code}_{task_idx + 1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    # Получаем количество подсказок для задания
    hint_count = len(task.get("hint", []))
    if hint_count > 0:
        # Добавляем кнопку подсказки
        markup.add(types.InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0"))

    markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=f"challenge_{challenge_num}"))

    # Отправляем или редактируем сообщение
    if user_data[user_id]["message_id"] is None:
        sent_message = bot.send_photo(chat_id, task["photo"], caption=caption, reply_markup=markup)
        user_data[user_id]["message_id"] = sent_message.message_id
    else:
        bot.edit_message_media(
            media=types.InputMediaPhoto(task["photo"], caption=caption),
            chat_id=chat_id,
            message_id=user_data[user_id]["message_id"],
            reply_markup=markup
        )

    user_task_data[user_id] = {
        "challenge_num": challenge_num,
        "cat_code": cat_code,
        "task_idx": task_idx,
        "correct_answer": task["answer"],
        "message_id": user_data[user_id]["message_id"],
        "type": "main"
    }
    user_data[user_id]["current_screen"] = f"category_{challenge_num}_{cat_code}_{task_idx}"
    logging.info(
        f"Задача отображена: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
# Обработчик для выбора категории домашнего задания
def handle_quest_homework_category(call):
    """Обработчик выбора категории домашних заданий в квесте
    (включает отображение первого задания с упрощенной логикой URL)"""
    from instance import photo_quest_ritual, photo # Добавил photo как fallback
    from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
    import random
    import traceback # Для логирования ошибок

    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)

    # Синхронизация ДЗ
    logging.info(f"⚠️ Синхронизация ДЗ при открытии категории")
    force_sync_homework_tasks()
    logging.info(f"✅ Синхронизация ДЗ завершена")

    # Получаем параметры из колбэка
    parts = call.data.split('_')
    world_id = parts[3]
    cat_code = parts[4]

    logging.info(f"Обработка категории ДЗ {cat_code}, мир {world_id}, user {user_id}")

    # --- Получение категории и данных о задачах ---
    world_challenges = challenge.get(world_id, {})
    category = world_challenges.get(cat_code)
    if not category:
        logging.info(f"⚠️ Категория {cat_code} не найдена в challenge, создаем фиктивную")
        # Логика создания фиктивной категории
        if cat_code == 'quad': category_name = "Квадратичная функция"
        elif cat_code == 'frac': category_name = "Дробно-рациональные выражения"
        elif cat_code == 'log': category_name = "Логарифмические выражения"
        elif cat_code == 'exp': category_name = "Показательные функции"
        elif cat_code == 'odd': category_name = "Разные задания"
        elif cat_code == 'lin': category_name = "Линейные функции"
        else: category_name = f"Тип: {cat_code}"
        fallback_photo_url = "https://i.imgur.com/UYbCNQZ.jpeg" # Используем в фиктивных задачах
        fake_tasks = [{'photo': fallback_photo_url, 'answer': 'Не указан', 'hint': [], 'homework_photo': fallback_photo_url} for _ in range(100)]
        category = {'name': category_name, 'tasks': fake_tasks}
        logging.info(f"✅ Создана фиктивная категория: {category_name}")

    # --- Получение списка домашних заданий из БД ---
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_idx FROM task_progress
            WHERE user_id = ? AND cat_code = ? AND type = 'homework'
            ORDER BY rowid ASC
        """, (user_id, cat_code))
        homework_tasks_rows = cursor.fetchall()
        conn.close()

        if not homework_tasks_rows:
            bot.answer_callback_query(call.id, "В этой категории нет домашних заданий")
            bot.edit_message_media(
                media=InputMediaPhoto(
                    photo_quest_ritual,
                    caption=f"Ритуал повторения - {category.get('name', cat_code)}\n\nВ этой категории нет заданий для повторения."
                ),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("↩️ Назад", callback_data="quest_homework")
                )
            )
            return

        # --- Отображение первого задания ---
        task_idx = homework_tasks_rows[0][0]
        logging.info(f"Отображаем первое задание ДЗ: task_idx={task_idx}")

        # Проверяем валидность индекса
        if task_idx >= len(category.get('tasks', [])):
            logging.error(f"Ошибка: индекс задания {task_idx} вне диапазона для категории {cat_code}")
            bot.answer_callback_query(call.id, "Ошибка: задание не найдено в структуре")
            return

        task = category['tasks'][task_idx]

        # Получаем статус задания из БД
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM task_progress
            WHERE user_id = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
        """, (user_id, cat_code, task_idx))
        result = cursor.fetchone()
        conn.close()
        status = result[0] if result else "wrong" # По умолчанию считаем неверным, если статус не найден

        # --- Логика получения URL изображения для ДЗ ---
        photo_url_to_send = None
        fallback_photo_url = "https://i.imgur.com/UYbCNQZ.jpeg" # Стандартный fallback

        # 1. Приоритет homework_photo (если есть и не пустой)
        if task.get('homework_photo'):
            photo_url_to_send = task['homework_photo']
            logging.info(f"ДЗ URL: Используем homework_photo: {photo_url_to_send}")
        # 2. Затем homework['photo'] (если homework - словарь и есть ключ 'photo')
        elif isinstance(task.get('homework'), dict) and task['homework'].get('photo'):
             photo_url_to_send = task['homework']['photo']
             logging.info(f"ДЗ URL: Используем homework['photo']: {photo_url_to_send}")
        # 3. Если нет фото ДЗ, используем основное фото задачи
        elif task.get('photo'):
             photo_url_to_send = task['photo']
             logging.info(f"ДЗ URL: Фото ДЗ не найдено, используем основное фото задачи: {photo_url_to_send}")

        # 4. Форматируем URL (для imgur без http)
        if photo_url_to_send and not photo_url_to_send.startswith("http"):
            photo_url_to_send = f"https://i.imgur.com/{photo_url_to_send}.jpeg"

        # 5. Если URL так и не определен, используем fallback
        if not photo_url_to_send:
             photo_url_to_send = fallback_photo_url
             logging.warning(f"ДЗ URL: URL не определен, используем fallback: {photo_url_to_send}")

        logging.info(f"ДЗ URL: Финальный URL для попытки отправки: {photo_url_to_send}")
        # --- Конец логики получения URL ---

        # --- Формирование Caption и Markup ---
        status_text_display = {
            "correct": "✅ Верно",
            "wrong": "❌ Неверно",
            "unresolved": "❔ Нерешено"
        }.get(status, "❔ Нерешено") # Используем .get для безопасности
        caption = f"№{task_idx + 1} Домашняя работа\n{category.get('name', cat_code)}\n{status_text_display}\n\nВведи ответ в чат:"
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 22.0: Используем ответ из поля homework, а не из обычной задачи
        if status == "correct":
            if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
                homework_answer = task["homework"]["answer"]
                caption = f"№{task_idx + 1} Домашняя работа\n{category.get('name', cat_code)}\n{status_text_display}\n\nПравильный ответ: {homework_answer}"
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 22.0: Показываем ответ из homework '{homework_answer}' при просмотре списка ДЗ")
            else:
                regular_answer = task.get('answer', '')
                caption = f"№{task_idx + 1} Домашняя работа\n{category.get('name', cat_code)}\n{status_text_display}\n\nПравильный ответ: {regular_answer}"
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 22.0: Поле homework отсутствует, показываем обычный ответ: '{regular_answer}')")

        markup = InlineKeyboardMarkup(row_width=1)
        task_indices = [t[0] for t in homework_tasks_rows]
        total_tasks = len(task_indices)
        current_index = 0 # Индекс первого задания

        nav_buttons = []
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty")) # Левая пустая
        nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty")) # Счетчик
        if total_tasks > 1: # Правая кнопка, если есть еще задания
             if current_index + 1 < len(task_indices):
                  next_task_idx = task_indices[current_index + 1]
                  nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
             else: # Защита на случай ошибки с индексами
                  nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        else: # Если всего одно задание
            nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        markup.row(*nav_buttons)

        if task.get('hint'):
            markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_hint_direct_{world_id}_{cat_code}_{task_idx}_0"))
        markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
        # --- Конец формирования ---

        # --- Отправка сообщения с Fallback ---
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url_to_send, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            logging.info(f"Успешно отправлено фото ДЗ: {photo_url_to_send}")
        except Exception as e:
            logging.error(f"Ошибка при отправке основного фото ДЗ ({photo_url_to_send}): {e}")
            try:
                # Пробуем отправить fallback
                bot.edit_message_media(
                    media=InputMediaPhoto(fallback_photo_url, caption=caption + "\n\n⚠️ Изображение временно недоступно."),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                logging.warning(f"Отправлено fallback фото ДЗ: {fallback_photo_url}")
            except Exception as e2:
                logging.error(f"Ошибка при отправке fallback фото ДЗ: {e2}")
                # Крайний случай - обновляем только текст
                try:
                    bot.edit_message_caption(caption=caption + "\n\n⚠️ Ошибка загрузки изображения.", chat_id=chat_id, message_id=message_id, reply_markup=markup)
                except Exception as e3:
                     logging.error(f"Не удалось обновить даже текст ДЗ: {e3}")
        # --- Конец отправки с Fallback ---

        # --- Сохранение состояния ---
        if user_id not in user_data:
            user_data[user_id] = {}
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Используем ответ из поля homework
        homework_answer = ""
        if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
            homework_answer = task["homework"]["answer"]
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Найден ответ в homework->answer: '{homework_answer}'")
        else:
            homework_answer = task.get('answer', '')
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Не найден ответ в homework, используем обычный ответ: '{homework_answer}'")
        
        user_data[user_id]["current_homework"] = {
            "world_id": world_id,
            "cat_code": cat_code,
            "task_idx": task_idx,
            "message_id": message_id,
            "answer": homework_answer  # Используем ответ из homework
        }
        
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Сохранен ответ '{homework_answer}' для домашнего задания при открытии категории ДЗ")
        user_data[user_id]["current_screen"] = "homework_task"
        logging.info(f"Установлен current_screen = homework_task для пользователя {user_id} при открытии категории ДЗ")
        # --- Конец сохранения ---

    except sqlite3.Error as e:
        logging.error(f"Ошибка БД при получении ДЗ: {e}")
        bot.answer_callback_query(call.id, "Ошибка при получении домашних заданий")
        return
    except Exception as e: # Ловим другие возможные ошибки
        logging.error(f"Общая ошибка при отображении первого задания ДЗ: {e}")
        logging.error(traceback.format_exc())
        bot.answer_callback_query(call.id, "Ошибка при отображении задания")
        # Возврат в меню ДЗ при ошибке
        try:
            bot.edit_message_media(
                media=InputMediaPhoto(photo_quest_ritual, caption="Произошла ошибка при загрузке задания."),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
            )
        except Exception as e2:
            logging.error(f"Не удалось показать сообщение об ошибке: {e2}")
# Обработчик для просмотра конкретного домашнего задания
def handle_quest_homework_task(call):
    """Обработчик для просмотра конкретного домашнего задания в квесте"""
    from instance import photo_quest_ritual
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Всегда запускаем синхронизацию при открытии домашнего задания
    # чтобы гарантировать актуальность списка
    logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Принудительная синхронизация при открытии домашнего задания")
    force_sync_homework_tasks()
    logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Синхронизация завершена")
    
    # Получаем параметры из колбэка
    parts = call.data.split('_')
    # Формат: quest_homework_task_world_id_cat_code_task_idx
    world_id = parts[3]
    cat_code = parts[4]
    task_idx = int(parts[5])
    
    # Для отладки
    logging.info(f"handle_quest_homework_task - данные колбэка: {call.data}, мир: {world_id}, категория: {cat_code}, задание: {task_idx}")
    
    # Получаем информацию о задании
    world_challenges = challenge.get(world_id, {})
    category = world_challenges.get(cat_code)
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обработка неизвестных категорий в конкретных домашних заданиях
    if not category:
        logging.info(f"⚠️ КАТЕГОРИЯ НЕ НАЙДЕНА при выборе задания: {cat_code} для мира {world_id}, но продолжаем обработку")
        # Создаем фиктивную категорию для отображения заданий
        
        # Задаем имя категории
        if cat_code == 'quad':
            category_name = "Квадратичная функция"
        elif cat_code == 'frac':
            category_name = "Дробно-рациональные выражения"
        elif cat_code == 'log':
            category_name = "Логарифмические выражения"
        elif cat_code == 'exp':
            category_name = "Показательные функции"
        elif cat_code == 'odd':
            category_name = "Разные задания"
        elif cat_code == 'lin':
            category_name = "Линейные функции"
        else:
            category_name = f"Тип: {cat_code}"
        
        # Создаем фиктивную структуру категории с фиктивными задачами
        # Для учёта всех задач в БД, создаем список задач с запасом
        fake_tasks = []
        for i in range(100):  # Создаем 100 фиктивных заданий для запаса
            fake_tasks.append({
                'photo': 'https://i.imgur.com/nWJzXKX.jpeg',  # Заглушка изображения
                'answer': 'Не указан',
                'hint': []
            })
        
        category = {
            'name': category_name,
            'tasks': fake_tasks
        }
        logging.info(f"✅ Создана фиктивная категория: {category_name} с {len(fake_tasks)} заданиями")
    
    # Проверяем существование задания
    if task_idx >= len(category['tasks']):
        bot.answer_callback_query(call.id, "Ошибка: задание не найдено")
        return
    
    task = category['tasks'][task_idx]
    
    # Проверяем наличие задания в базе данных с типом homework (не зависимо от мира)
    conn = sqlite3.connect('task_progress.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status FROM task_progress 
        WHERE user_id = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
    """, (user_id, cat_code, task_idx))
    result = cursor.fetchone()
    
    if not result:
        bot.answer_callback_query(call.id, "Ошибка: домашнее задание не найдено в базе данных")
        logging.error(f"Домашнее задание не найдено: user_id={user_id}, cat_code={cat_code}, task_idx={task_idx}")
        conn.close()
        return
    
    status = result[0]
    logging.info(f"Статус задания {world_id}_{cat_code}_{task_idx} для пользователя {user_id}: {status}")
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Усовершенствованная обработка изображений для домашних заданий
    # Используем фото из поля "homework" для домашних заданий, если оно есть
    try:
        # Проверяем наличие поля homework и изображения в нем
        if 'homework' in task:
            if isinstance(task['homework'], dict) and 'photo' in task['homework']:
                # Структура task['homework'] = {'photo': 'url', ...}
                photo_url = task['homework']['photo']
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Используем специальное фото по ключу homework->photo: {photo_url}")
            elif isinstance(task['homework'], str):
                # Структура task['homework'] = 'url'
                photo_url = task['homework']
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Используем специальное фото (строковое значение): {photo_url}")
            else:
                # Если структура homework непонятная, используем стандартное фото
                photo_url = task['photo']
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Неизвестный формат homework, используем стандартное фото: {photo_url}")
        else:
            # Если поля homework нет, используем стандартное фото
            photo_url = task['photo']
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Поле homework отсутствует, используем стандартное фото: {photo_url}")
        
        # Гарантируем полный URL для изображений Imgur
        if not photo_url.startswith("http"):
            photo_url = f"https://i.imgur.com/{photo_url}.jpeg"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Преобразован базовый URL изображения: {photo_url}")
        
        # Добавляем параметр для предотвращения кеширования
        if "?" not in photo_url:
            # Добавляем случайный параметр и размер (больший размер может предотвратить замену на логотип Imgur)
            import random
            random_param = random.randint(10000, 99999)
            photo_url = f"{photo_url}?cache={random_param}&size=l"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Добавлен параметр против кеширования: {photo_url}")
        
        # Предварительная проверка доступности изображения
        if not is_image_accessible(photo_url):
            logging.warning(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Изображение недоступно по URL: {photo_url}, пробуем альтернативные варианты")
            
            # Пробуем альтернативные варианты URL для Imgur
            if "imgur.com" in photo_url:
                # Очищаем URL от параметров и пробуем другой формат
                base_url = photo_url.split("?")[0]
                
                # Альтернатива 1: Пробуем другой формат (png вместо jpeg)
                if base_url.endswith(".jpeg"):
                    alt_url = base_url.replace(".jpeg", ".png")
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Пробуем альтернативный формат PNG: {alt_url}")
                    if is_image_accessible(alt_url):
                        photo_url = alt_url
                        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Успешно заменен формат на PNG")
                    
                # Альтернатива 2: Пробуем прямой URL без расширения
                if "i.imgur.com" in base_url:
                    alt_url = base_url.split(".")[0] + ".".join(base_url.split(".")[1:-1]) 
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Пробуем URL без расширения: {alt_url}")
                    if is_image_accessible(alt_url):
                        photo_url = alt_url
                        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Успешно используем URL без расширения")
    except Exception as e:
        # В случае ошибки обработки URL логируем и используем запасной вариант
        logging.error(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 8.0: Ошибка при обработке URL изображения: {e}")
        photo_url = "https://i.imgur.com/UYbCNQZ.jpeg?nocache=1"  # Запасное изображение
    
    # Маппинг статусов
    status_emoji = {"correct": "✅", "wrong": "❌", "unresolved": "❔"}
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.0: Исправляем логику отображения статуса
    # Если статус не определен или не находится в списке известных, считаем задание "не решенным"
    if status not in status_emoji:
        status = "unresolved"  # По умолчанию считаем задание "не решенным", а не "неверным"
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.0: Установлен статус 'unresolved' (не решено) для задания {world_id}_{cat_code}_{task_idx}")
    
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Получаем все домашние задания для отображения навигации
    try:
        conn_nav = sqlite3.connect('task_progress.db')
        cursor_nav = conn_nav.cursor()
        cursor_nav.execute("""
            SELECT task_idx FROM task_progress 
            WHERE user_id = ? AND cat_code = ? AND type = 'homework'
        """, (user_id, cat_code))
        
        homework_tasks = cursor_nav.fetchall()
        conn_nav.close()
        
        if homework_tasks:
            # Список индексов заданий
            task_indices = [t[0] for t in homework_tasks]
            total_tasks = len(task_indices)
            current_index = task_indices.index(task_idx)
            
            # Кнопки навигации (влево/вправо) и счетчик - всегда видимы
            nav_buttons = []
            
            # Если первое задание, добавляем фантомную кнопку влево
            if current_index > 0:
                prev_task_idx = task_indices[current_index - 1]
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{prev_task_idx}"))
            else:
                # Фантомная кнопка без функционала и без текста
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
            # Счетчик текущего положения
            nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty"))
            
            # Если последнее задание, добавляем фантомную кнопку вправо
            if current_index < total_tasks - 1:
                next_task_idx = task_indices[current_index + 1]
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
            else:
                # Фантомная кнопка без функционала и без текста
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            
            markup.row(*nav_buttons)
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении данных для навигации: {e}")
    
    # Убираем кнопку "Ответить", так как ответ будет приниматься автоматически
    
    # Кнопка для просмотра подсказки, если она есть
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Добавляем специальную кнопку подсказки для домашнего задания
    if task.get('hint'):
        # Используем специальный формат callback для подсказок в домашних заданиях
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_homework_hint_{world_id}_{cat_code}_{task_idx}_0"))
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Добавлена кнопка подсказки для домашнего задания с callback=quest_homework_hint_{world_id}_{cat_code}_{task_idx}_0")
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Удалена кнопка добавления в избранное из домашних заданий
    # Так как это не имеет смысла в контексте повторения
    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Кнопка добавления в избранное удалена из домашних заданий")
    
    # Кнопка возврата
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Отображаем статус домашнего задания и динамический номер задания
    status_text = {
        "correct": "✅ Верно",
        "wrong": "❌ Неверно",
        "unresolved": "❔ Не решено"
    }.get(status, "❔ Не решено")
    
    # Динамический номер задания вместо статичного "№6"
    caption = f"№{task_idx + 1} Домашняя работа\n{category['name']}\n{status_text}\n\nВведи ответ в чат:"
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 23.0: Используем ответ из поля homework вместо обычного ответа
    if status == "correct":
        if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
            homework_answer = task["homework"]["answer"]
            caption = f"№{task_idx + 1} Домашняя работа\n{category['name']}\n{status_text}\n\nПравильный ответ: {homework_answer}"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 23.0: Показываем ответ из homework '{homework_answer}' при просмотре конкретного задания")
        else:
            regular_answer = task.get('answer', '')
            caption = f"№{task_idx + 1} Домашняя работа\n{category['name']}\n{status_text}\n\nПравильный ответ: {regular_answer}"
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 23.0: Поле homework отсутствует, показываем обычный ответ: '{regular_answer}')")
    
    bot.edit_message_media(
        media=InputMediaPhoto(photo_url, caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    # Сохраняем состояние для обработки ответа
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # Проверяем, есть ли ответ в задании
    answer = task.get('answer', '')
    
    # Устанавливаем флаг текущего экрана как homework_task
    user_data[user_id]["current_screen"] = "homework_task"
    
    # Сохраняем информацию о текущем домашнем задании
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем ответ из поля homework
    # Получаем ответ из поля homework для домашней работы
    homework_answer = ""
    if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
        homework_answer = task["homework"]["answer"]
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Найден ответ в поле homework->answer: '{homework_answer}'")
    else:
        # Если структура другая, пытаемся получить хоть какой-то ответ
        homework_answer = task.get('answer', '')
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Не найдено поле homework->answer, используем обычный ответ: '{homework_answer}'")
    
    user_data[user_id]["current_homework"] = {
        "world_id": world_id,
        "cat_code": cat_code,
        "task_idx": task_idx,
        "answer": homework_answer,  # Используем ответ из поля homework
        "message_id": message_id
    }
    
    # Логируем использование ответа из homework
    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Сохранен ответ '{homework_answer}' для домашнего задания {world_id}_{cat_code}_{task_idx}")
    
    # Вывод отладочной информации в лог
    logging.info(f"Установлен current_screen = homework_task для пользователя {user_id}")
    
    conn.close()
# ================== Теория по заданиям и другие callback запросы ==================
@bot.callback_query_handler(func=lambda call: call.data == "quest_empty")
def handle_quest_empty(call):
    """Обработчик для пустой кнопки навигации"""
    # Просто отвечаем на callback без действий
    bot.answer_callback_query(call.id)
    return

def handle_quest_achievement(call):
    """Обработчик для просмотра достижений на карте прогресса"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Разбираем callback_data: quest_achievement_world_id_percent
    parts = call.data.split('_')
    world_id = int(parts[2])
    percent = int(parts[3])
    
    # Список всех возможных достижений в порядке разблокировки
    # Добавляем метку времени для предотвращения кеширования
    timestamp = int(time.time())
    achievements = [
        {"percent": 10, "image": f"https://imgur.com/CpoEJlh.jpeg?t={timestamp}", "name": "Первые шаги", "description": "Вы начали свой путь в мире математики!"},
        {"percent": 20, "image": f"https://imgur.com/e8zRNnb.jpeg?t={timestamp}", "name": "Исследователь", "description": "Вы открываете новые математические концепции."},
        {"percent": 30, "image": f"https://imgur.com/JPQyYFl.jpeg?t={timestamp}", "name": "Ученик", "description": "Вы осваиваете основы науки."},
        {"percent": 40, "image": f"https://imgur.com/NIyz1pZ.jpeg?t={timestamp}", "name": "Практик", "description": "Вы применяете теорию на практике."},
        {"percent": 50, "image": f"https://imgur.com/5NqBjbr.jpeg?t={timestamp}", "name": "Мыслитель", "description": "Вы умеете решать сложные задачи."},
        {"percent": 60, "image": f"https://imgur.com/WJ78LW2.jpeg?t={timestamp}", "name": "Стратег", "description": "Вы видите лучшие пути решения."},
        {"percent": 70, "image": f"https://imgur.com/EofCZc2.jpeg?t={timestamp}", "name": "Мастер", "description": "Вы достигли высокого уровня мастерства."},
        {"percent": 80, "image": f"https://imgur.com/bLRhu4t.jpeg?t={timestamp}", "name": "Эксперт", "description": "Вы глубоко понимаете материал."},
        {"percent": 90, "image": f"https://imgur.com/t0IHj3H.jpeg?t={timestamp}", "name": "Мудрец", "description": "Вы близки к полному освоению темы!"}
    ]
    
    # Находим запрошенное достижение
    achievement = None
    for ach in achievements:
        if ach["percent"] == percent:
            achievement = ach
            break
    
    if not achievement:
        bot.answer_callback_query(call.id, "Достижение не найдено")
        return
    
    # Получаем текущий прогресс пользователя с принудительным пересчетом для отображения в сообщении
    progress = get_world_progress(user_id, world_id, force_recount=True)
    completed_tasks = progress.get('completed_tasks', 0)
    total_tasks = progress.get('total_tasks', 32)
    completion_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # Дополнительный лог для отладки
    logging.info(f"Прогресс пользователя {user_id} в мире {world_id}: {completion_percentage}% ({completed_tasks}/{total_tasks}) - просмотр достижения")
    
    # Создаем визуальный прогресс-бар для отображения в сообщении
    progress_bar_length = 10
    filled_blocks = int((progress_bar_length * completion_percentage) / 100)
    progress_bar = '█' * filled_blocks + '░' * (progress_bar_length - filled_blocks)
    
    # Формируем текст сообщения о достижении
    message_text = (
        f"🏆 Достижение: {achievement['name']}\n\n"
        f"{achievement['description']}\n\n"
        f"Прогресс в мире {world_id}:\n"
        f"Выполнено задач: {completed_tasks} из {total_tasks}\n"
        f"[{progress_bar}] {completion_percentage}%"
    )
    
    try:
        # Создаем клавиатуру с кнопкой возврата к карте прогресса
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("↩️ Вернуться к карте прогресса", callback_data=f"quest_progress_map_{world_id}"))
        
        # Обновляем сообщение, показывая картинку достижения
        bot.edit_message_media(
            media=InputMediaPhoto(achievement["image"], caption=message_text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        
        logging.info(f"Пользователь {user_id} просмотрел достижение {percent}% в мире {world_id}")
    except Exception as e:
        logging.error(f"Ошибка при отображении достижения: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки достижения")

def handle_quest_progress_map(call):
    """Обработчик для отображения карты прогресса мира"""
    from telebot.types import InputMediaPhoto
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    # Извлекаем ID мира из данных обратного вызова
    # Формат: quest_progress_map_ID
    parts = call.data.split('_')
    world_id = int(parts[-1])
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 27.0: Принудительная синхронизация ДЗ при открытии карты прогресса
    logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 27.0: Принудительная синхронизация при просмотре карты прогресса")
    try:
        force_sync_homework_tasks()
        logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 27.0: Синхронизация ДЗ завершена")
    except Exception as e:
        logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 27.0: Ошибка при синхронизации ДЗ: {e}")
    
    # Получаем прогресс пользователя в этом мире с принудительным пересчетом
    progress = get_world_progress(user_id, world_id, force_recount=True)
    completed_tasks = progress.get('completed_tasks', 0)
    total_tasks = progress.get('total_tasks', 32)  # Минимум 32 задачи в каждом мире
    
    # Вычисляем процент выполнения
    completion_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # Создаем прогресс-бар
    progress_bar_length = 10
    filled_blocks = int((progress_bar_length * completion_percentage) / 100)
    progress_bar = '█' * filled_blocks + '░' * (progress_bar_length - filled_blocks)
    
    # Формируем информационное сообщение в простом формате
    message_text = (
        f"Выполнено задач: {completed_tasks} из {total_tasks}\n"
        f"[{progress_bar}] {completion_percentage}%"
    )
    
    # Получаем карту с гусем в соответствии с прогрессом
    world_image = get_world_progress_image(user_id, world_id)
    
    # Дополнительный лог для отладки
    logging.info(f"🖼️ Выбрано изображение для карты прогресса {completion_percentage}%: {world_image}")
    
    try:
        # Создаем клавиатуру с кнопками достижений и кнопкой возврата
        markup = InlineKeyboardMarkup(row_width=3)
        
        # Создаем кнопки достижений (3x3 сетка)
        # Разблокированные достижения имеют callback, неразблокированные - нет
        
        # Список всех возможных достижений в порядке разблокировки
        # Добавляем метку времени к URL для предотвращения кеширования
        timestamp = int(time.time())
        achievements = [
            {"percent": 10, "locked": "⬛️", "unlocked": "1️⃣", "image": f"https://imgur.com/CpoEJlh.jpeg?t={timestamp}"},
            {"percent": 20, "locked": "⬛️", "unlocked": "2️⃣", "image": f"https://imgur.com/e8zRNnb.jpeg?t={timestamp}"},
            {"percent": 30, "locked": "⬛️", "unlocked": "3️⃣", "image": f"https://imgur.com/JPQyYFl.jpeg?t={timestamp}"},
            {"percent": 40, "locked": "⬛️", "unlocked": "4️⃣", "image": f"https://imgur.com/NIyz1pZ.jpeg?t={timestamp}"},
            {"percent": 50, "locked": "⬛️", "unlocked": "5️⃣", "image": f"https://imgur.com/5NqBjbr.jpeg?t={timestamp}"},
            {"percent": 60, "locked": "⬛️", "unlocked": "6️⃣", "image": f"https://imgur.com/WJ78LW2.jpeg?t={timestamp}"},
            {"percent": 70, "locked": "⬛️", "unlocked": "7️⃣", "image": f"https://imgur.com/EofCZc2.jpeg?t={timestamp}"},
            {"percent": 80, "locked": "⬛️", "unlocked": "8️⃣", "image": f"https://imgur.com/bLRhu4t.jpeg?t={timestamp}"},
            {"percent": 90, "locked": "⬛️", "unlocked": "9️⃣", "image": f"https://imgur.com/t0IHj3H.jpeg?t={timestamp}"}
        ]
        
        # Создаем кнопки в вертикальном порядке (1,2,3 в первом столбце; 4,5,6 во втором; 7,8,9 в третьем)
        # Формируем массив кнопок
        buttons = []
        for achievement in achievements:
            if completion_percentage >= achievement["percent"]:
                # Разблокированное достижение
                button = InlineKeyboardButton(
                    achievement["unlocked"], 
                    callback_data=f"quest_achievement_{world_id}_{achievement['percent']}"
                )
            else:
                # Заблокированное достижение
                button = InlineKeyboardButton(
                    achievement["locked"], 
                    callback_data="quest_empty"
                )
            buttons.append(button)
        
        # Переупорядочиваем кнопки для отображения в вертикальном порядке
        # Создаем три строки по три кнопки в каждой
        markup.row(buttons[0], buttons[3], buttons[6])  # 1, 4, 7 (индексы 0, 3, 6)
        markup.row(buttons[1], buttons[4], buttons[7])  # 2, 5, 8 (индексы 1, 4, 7)
        markup.row(buttons[2], buttons[5], buttons[8])  # 3, 6, 9 (индексы 2, 5, 8)
        
        # Добавляем кнопку возврата внизу
        markup.add(InlineKeyboardButton("↩️ Вернуться в мир", callback_data=f"quest_loaded_world_{world_id}"))
        
        # Проверяем, является ли путь локальным файлом или URL
        import os
        
        if os.path.isfile(world_image):
            # Если это локальный файл, открываем его и отправляем
            with open(world_image, 'rb') as photo:
                bot.edit_message_media(
                    media=InputMediaPhoto(photo, caption=message_text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                logging.info(f"Отправлено локальное изображение карты прогресса: {world_image}")
        else:
            # Если это URL, отправляем как обычно
            bot.edit_message_media(
                media=InputMediaPhoto(world_image, caption=message_text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            logging.info(f"Отправлен URL изображения карты прогресса: {world_image}")
        
        logging.info(f"Пользователь {user_id} просмотрел карту прогресса мира {world_id}")
    except Exception as e:
        logging.error(f"Ошибка при отображении карты прогресса: {e}")
        bot.answer_callback_query(call.id, "Ошибка загрузки карты прогресса")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data
    username = call.from_user.username
    register_user(user_id, call.from_user.username)
    if user_id not in user_data:
        user_data[user_id] = {
            "favorite_tasks": [],
            "current_index": 0,
            "message_id": None,
            "current_mode": None,
            "challenge_num": None,
            "navigation_stack": [],
            "current_screen": None
        }
    logging.debug(f"Получен callback: {call.data} от user_id={user_id}")
    try:
        logging.info(f"Callback received: {data} from user_id={user_id}")
        
        # Уже обрабатывается отдельным хендлером выше
        # Оставляем эту проверку на всякий случай
        if data == "quest_empty":
            return
            
        # Подтверждаем обработку остальных callback
        bot.answer_callback_query(call.id)

        # Обработка колбэков математического квеста
        if data == "mathQuest_call":
            logging.info(f"Пользователь {user_id} открыл математический квест")
            handle_mathquest_call(call)
            return
        elif data == "mathQuest_back_call":
            handle_mathquest_back(call)
            return
        elif data == "quest_select_world":
            handle_quest_select_world(call)
            return
        elif data == "quest_profile":
            handle_quest_profile(call)
            return
        elif data == "quest_trophies":
            handle_quest_trophies(call)
            return
        elif data == "quest_shop":
            handle_quest_shop(call)
            return
        elif data.startswith("quest_world_next_") or data.startswith("quest_world_prev_"):
            handle_quest_navigation(call)
            return
        elif data.startswith("quest_enter_world_"):
            handle_quest_enter_world(call)
            return
        elif data.startswith("quest_loaded_world_"):
            handle_quest_loaded_world(call)
            return
        elif data == "quest_back_to_worlds":
            handle_quest_back_to_worlds(call)
            return
        elif data.startswith("quest_theory_"):
            handle_quest_theory(call)
            return
        elif data.startswith("quest_progress_map_"):
            handle_quest_progress_map(call)
            return
        elif data.startswith("quest_achievement_"):
            handle_quest_achievement(call)
            return
        elif data.startswith("theory_fsu_"):
            # Обработка фото "Формулы Сокращённого Умножения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_fsy  # URL изображения ФСУ из instance.py

            text = ("Формулы сокращённого умножения\n\n"
                    "Базовые тождества, которые упрощают раскрытие скобок и преобразование выражений: квадраты, кубы, разности и суммы.")
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_quadratic_"):
            # Обработка фото "Квадратные уравнения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_quadratic_equations  # URL изображения квадратных уравнений из instance.py

            text = (
                "Квадратные уравнения\n\n"
                "Классическое уравнение второй степени. Здесь — формулы дискриминанта, разложение на множители и теорема Виета."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_powers_"):
            # Обработка фото "Степени"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_powers  # URL изображения степеней из instance.py

            text = (
                "Степени\n\n"
                "Свойства степеней с одинаковыми и разными основаниями.\n"
                "Базовый инструмент для упрощения выражений и решения уравнений."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_roots_"):
            # Обработка фото "Корни"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_roots  # URL изображения корней

            text = (
                "Корни\n\n"
                "Свойства корней и их связь со степенями. Всё, что нужно для рациональных преобразований и упрощения выражений."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trigonometry_"):
            # Обработка раздела "Тригонометрия"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("Тригонометрическая окружность", callback_data=f"theory_trig_circle_{world_id}"),
                InlineKeyboardButton("Окружность для тангенса", callback_data=f"theory_trig_tangent_circle_{world_id}"),
                InlineKeyboardButton("Определения", callback_data=f"theory_trig_definitions_{world_id}"),
                InlineKeyboardButton("Тригонометрические формулы", callback_data=f"theory_trig_formulas_{world_id}"),
                InlineKeyboardButton("Формулы приведения", callback_data=f"theory_trig_reduction_{world_id}"),
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            # Используем изображение книги знаний
            photo_url = photo_quest_book
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_circle_"):
            # Обработка фото "Тригонометрическая окружность"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_trigonometric_circle  # URL изображения тригонометрической окружности

            text = (
                "Тригонометрическая окружность\n\n"
                "Единичная окружность, на которой наглядно отображаются значения тригонометрических функций."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_tangent_circle_"):
            # Обработка фото "Окружность для тангенса"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_tangent_circle  # URL изображения окружности для тангенса

            text = (
                "Окружность для тангенса\n\n"
                "Специальная тригонометрическая окружность для наглядного представления функции тангенса и определения её значений."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_definitions_"):
            # Обработка фото "Определения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_definition  # URL изображения определений

            text = (
                "Определения тригонометрических функций\n\n"
                "Синус, косинус, тангенс и котангенс через стороны прямоугольного треугольника. Основа всей тригонометрии."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_formulas_"):
            # Обработка фото "Тригонометрические формулы"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_trigonometric_formulas  # URL изображения тригонометрических формул

            text = (
                "Тригонометрические формулы\n\n"
                "Формулы сложения, двойного угла и другие тождества. Ключ к решению уравнений и преобразованию выражений."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_trig_reduction_"):
            # Обработка фото "Формулы приведения"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            photo_url = photo_reduction_formulas  # URL изображения формул приведения

            text = (
                "Формулы приведения\n\n"
                "Позволяют упростить тригонометрические выражения с углами больше 90° и 180°. Сохраняем функцию, меняем знак."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"theory_trigonometry_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_logarithms_"):
            # Обработка фото "Логарифмы"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            # Используем изображение логарифмов из instance.py
            photo_url = photo_logarithms

            text = (
                "Логарифмы\n\n"
                "Определение, свойства и преобразования логарифмов. Всё, что нужно для решения логарифмических уравнений."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("theory_modules_"):
            # Обработка фото "Модули"
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            parts = call.data.split('_')
            world_id = int(parts[-1])
            
            # Используем изображение модулей из instance.py
            photo_url = photo_modules

            text = (
                "Модули\n\n"
                "Модуль превращает отрицательные значения в положительные. Здесь — правила раскрытия и базовые свойства."
            )
            
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("↩️ Назад", callback_data=f"quest_theory_{world_id}")
            )
            
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            return
        elif data.startswith("quest_task_list_"):
            handle_quest_task_list(call)
            return
        elif data.startswith("quest_category_"):
            handle_quest_category(call)
            return
        elif data.startswith("quest_task_") and not data.startswith("quest_task_list"):
            handle_quest_task(call)
            return
        elif data.startswith("quest_answer_"):
            handle_quest_answer(call)
            return
        elif data.startswith("quest_solution_"):
            handle_quest_solution(call)
            return
        elif data.startswith("quest_hint_next_") or data.startswith("quest_hint_prev_"):
            handle_quest_hint_navigation(call)
            return
        elif data.startswith("quest_hint_direct_"):
            handle_hint_direct(call)
            return
        elif data.startswith("quest_favorite_"):
            # Проверяем точное соответствие паттерну "quest_favorite_world_id_category_id_task_id"
            parts = data.split('_')
            if len(parts) == 5 and parts[0] == "quest" and parts[1] == "favorite":
                logging.info(f"Вызов обработчика избранного для: {data}")
                handle_quest_favorite(call)
                return
            elif data.startswith("quest_favorite_world_") or data.startswith("quest_favorite_category_"):
                # Другие обработчики связанные с избранным (просмотр по мирам/категориям)
                # Обработчик для выбора мира из избранного
                if data.startswith("quest_favorite_world_"):
                    handle_quest_favorite_world(call)
                    return
                # Этот обработчик использует декоратор @bot.callback_query_handler
                # поэтому здесь не требуется ручной вызов функции
                elif data.startswith("quest_favorite_category_"):
                    # handle_quest_favorite_category(call) - теперь используется через декоратор
                    return
        elif data == "quest_favorites":
            # Используем версию с красивой анимацией загрузки
            handle_quest_favorites(call)
            return
        elif data == "quest_favorites_no_animation":
            # Версия без анимации загрузки для более быстрого ответа
            handle_quest_favorites_no_animation(call)
            return
        # Обработчики уже добавлены выше
        # Эти обработчики используют декоратор @bot.callback_query_handler, 
        # поэтому здесь не требуется ручной вызов
        # Оставляем для поддержки обратной совместимости
        elif data.startswith("quest_favorite_view_ordered_"):
            # handle_quest_favorite_view_ordered(call) - теперь выполняется через декоратор
            return
        elif data.startswith("quest_favorite_view_random_"):
            # handle_quest_favorite_view_random(call) - теперь выполняется через декоратор
            return
        elif data.startswith("quest_favorite_view_by_category_"):
            # handle_quest_favorite_view_by_category(call) - теперь выполняется через декоратор
            return
        # Этот обработчик использует декоратор @bot.callback_query_handler
        # поэтому здесь не требуется ручной вызов функции
        elif data.startswith("quest_favorite_world_categories_"):
            # handle_quest_favorite_world_categories(call) - теперь выполняется через декоратор
            return
        # Обработка подсказок - используем стандартный обработчик
        elif data.startswith("hint_"):
            handle_hint_direct(call)
            return
        # Обработка навигации по избранному (перенаправляем на основной обработчик)
        elif data.startswith("favorite_nav_"):
            # Перенаправляем на обработчик избранного
            handle_quest_favorites(call)
            return
        # Обработка навигации по избранному в режиме случайного порядка
        elif data.startswith("favorite_category_random_"):
            handle_favorite_category_random(call)
            return
        elif data == "quest_homework":
            # Проверяем, хочет ли пользователь посмотреть домашнюю работу или его просто автоматически перенаправляют
            # Если есть флаг homework_added, не перенаправляем пользователя автоматически
            if user_id in user_data and 'homework_added' in user_data[user_id]:
                # Получаем информацию о добавленной задаче
                homework_data = user_data[user_id].get('homework_added', {})
                message_reason = homework_data.get('reason', 'добавили задачу в ритуал повторения')
                
                # Удаляем флаг, чтобы пользователь мог вручную перейти к домашней работе
                del user_data[user_id]['homework_added']
                logging.info(f"Флаг homework_added удален для user_id={user_id}")
                
                # Отправляем сообщение пользователю вместо перенаправления
                # Убрана нотификация о добавлении в "Ритуал повторения"
                bot.answer_callback_query(call.id, "")
                # Убрано отправление сообщения пользователю о добавлении в ритуал повторения
                return
            else:
                # Если обычный переход - обрабатываем как обычно
                handle_quest_homework(call)
                return
        
        # Обработка "quest_homework_cat_*" - выбор категории домашних заданий
        elif data.startswith("quest_homework_cat_"):
            print(f"Обрабатываем callback для категории домашних заданий: {data}")
            handle_quest_homework_category(call)
            return
            
        # Обработка "quest_homework_task_*" - выбор конкретного домашнего задания
        elif data.startswith("quest_homework_task_"):
            print(f"Обрабатываем callback для задания домашней работы: {data}")
            handle_quest_homework_task(call)
            return
            
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Обработчик подсказок для домашних заданий
        elif data.startswith("quest_homework_hint_"):
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Обрабатываем подсказку для домашнего задания: {data}")
            # Переиспользуем стандартный обработчик, так как логика идентична,
            # а кнопка возврата будет правильной благодаря проверке current_screen
            handle_hint_direct(call)
            return
            
        # Обработка "Связь"
        elif data == "contact_call":
            text = (
                "📞 Связь и поддержка\n\n"
                "⬇️ Присоединяйтесь к нашему Telegram-каналу:\n"
                "@egenut\n"
                "💬 Если у вас есть вопросы или вам нужна помощь:\n"
                "@dmitriizamaraev\n"
            )
            photo_url = photo_contact
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=contact_screen()
            )

        # Обработка "Возврата в главное меню"
        elif data == "main_back_call":
            if user_id in user_data:
                del user_data[user_id]
            text = (
                "Ты в умном боте для подготовки к ЕГЭ по профильной математике.\n\n"
                "Главное здесь — чёткая структура: квест от задания к заданию, теория по каждому номеру и никакой путаницы.\n\n"
                "А ещё — трекер занятий, карточки, варианты и помощь от репетитора."
            )
            photo_url = photo_main
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=main_screen()
            )

        # Занятие с репетитором
        elif data == "tutor_call":
            text = (
                "Хотите уверенно сдать ЕГЭ по математике? Мы вам поможем! 🚀\n\n"
                "🔹 Гарантированно разберёмся в сложных темах — даже если сейчас кажется, что это невозможно.\n"
                "🔹 Подготовим к любым задачам ЕГЭ — от простых до самых сложных.\n"
                "🔹 Объясняю понятно и просто — без заумных терминов, только суть.\n\n"
                "💡 У нас уникальный метод подготовки — благодаря ему ты 100% встретишь на ЕГЭ задание, которое уже решал.\n\n"
                "P.S: Подробнее о форматах обучения и отзывах выпускников — по кнопкам ниже.\n\n"
                "🎯 Не откладывай на потом — начинай подготовку уже сегодня!"
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("📚 Формат обучения", callback_data="tutor_formats"),
                InlineKeyboardButton("⭐ Отзывы", callback_data="tutor_reviews")
            )
            markup.add(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="main_back_call"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        # Формат обучения
        elif data == "tutor_formats":
            text = (
                "Теперь хотим тебе рассказать про самое классное в подготовке – наш подход к обучению, который помогает ученикам набирать высокие баллы на экзамене!\n\n"
                "💡 Мы не будем просто нарешивать варианты — при таком подходе в голове образуется каша из геометрии, логарифмов, производных и всего подряд. Это непродуктивно!\n\n"
                "По нашей методике мы берём одно конкретное задание и шаг за шагом разбираем все возможные прототипы. Попутно изучаем теорию и сразу закрепляем её на практике. Такой подход даёт структуру и понимание, а не механическое заучивание.\n\n"
                "Также готовиться будем на прототипах с реальных экзаменов прошлых лет. Разберём все типы заданий, которые могут встретиться на ЕГЭ, чтобы на экзамене тебе попалось 100% то, что мы уже разбирали."
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Подробнее о форматах", callback_data="tutor_format_details"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_call"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )

        # Подробности о форматах
        elif data == "tutor_format_details":
            text = (
                "Какой формат подготовки тебе подойдёт больше всего? Давай разберёмся 🎯\n\n"
                "У всех свой ритм и стиль обучения: кому-то важна личная поддержка, а кто-то заряжается от командного духа. Мы учли всё и собрали несколько форматов подготовки — выбирай тот, который подходит именно тебе:\n\n"
                "✅ *Индивидуальные занятия со мной* — если хочешь, чтобы вся фокусировка была на тебе, твоих слабых местах и темпах. Разбираем всё до мельчайших деталей, пока ты не скажешь: “Теперь я это понял!”.\n\n"
                "✅ *Групповые занятия со мной* — если тебе важна динамика, поддержка и соревновательный дух. Вместе всегда проще держать темп и не сдаваться, когда лень подкрадывается.\n\n"
                "✅ *Индивидуальные занятия с топовыми преподами моей команды* — я собрал вокруг себя сильнейших преподавателей, которым сам доверяю. Ты в надёжных руках!\n\n"
                "P.S: Выбирай свой формат и заполняй анкету по кнопке «Оставить заявку»"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📩 Оставить заявку", callback_data="tutor_request"))
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="tutor_formats"))
            bot.edit_message_media(
                media=InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            bot.edit_message_caption(
                caption=text,
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )

        # Оставить заявку
        elif data == "tutor_request":
            user_data[user_id] = {
                "tutor_step": 0,
                "tutor_answers": {},
                "message_id": message_id,
                "username": call.from_user.username
            }
            ask_tutor_question(chat_id, user_id, message_id)

        # Отзывы
        elif data == "tutor_reviews":
            user_data[user_id] = {
                "review_index": 0,
                "message_id": message_id
            }
            show_review(chat_id, user_id, message_id)

        elif data == "review_prev" or data == "review_next":
            if user_id not in user_data or "review_index" not in user_data[user_id]:
                bot.answer_callback_query(call.id, "Ошибка! Начните просмотр отзывов заново.")
                return
            current_index = user_data[user_id]["review_index"]
            if data == "review_prev" and current_index > 0:
                user_data[user_id]["review_index"] -= 1
            elif data == "review_next" and current_index < len(TUTOR_REVIEWS) - 1:
                user_data[user_id]["review_index"] += 1
            show_review(chat_id, user_id, message_id)

    #Задания
        elif data == "tasks_call" or data == "tasksBack_call":
            text = (
                    "Здесь ты найдёшь всё, что нужно для решения каждого типа задания.\n"
                    "Выбирай номер — и получай точную теорию, нужные формулы и пояснения.")

            photo_url = photo_tasks

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=tasks_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "1 Задачи"
        elif data == "task_1_call":
            text = ("Задание 1 \n\n"
                "Углы, треугольники и окружности — всё, что нужно для решения базовой планиметрии."
                )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_1_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Биссектриса, медиана, серединный перпендикуляр"
        elif data == "task_triangle_lines_call":
            text = ("Биссектриса, медиана, серединный перпендикуляр\n\n"
                "Три важных отрезка внутри треугольника: как они устроены, где проходят и что о них нужно знать."
                    )
            photo_url = photo_task_triangle_lines

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Группы Треугольники"
        elif data == "task_groupTriangles_call":
            text = ("Треугольники\n\n"
                    "Всё, что нужно знать о треугольниках: от общих свойств до частных случаев. Выберите тему и разберите её по частям."
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupTriangles_screen()
            )
        # Обработка "Прямоугольный треугольник"
        elif data == "task_right_triangle_call":
            text = ("Прямоугольный треугольник\n\n"
                    "Площадь, высоты, радиусы, теорема Пифагора — здесь собраны все основные формулы и свойства прямоугольных треугольников."
                    )
            photo_url = photo_task_right_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Равнобедренный/Равносторонний треугольник"
        elif data == "task_isosceles_equilateral_triangle_call":
            text = ("Равнобедренный и равносторонний треугольник\n\n"
                    "Основные признаки, формулы и особенности равнобедренных и равносторонних треугольников."
                    )
            photo_url = photo_task_isosceles_equilateral_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Равенство/Подобие треугольников"
        elif data == "task_triangle_similarity_call":
            text = ("Равенство/Подобие треугольников\n\n"
                    "Признаки равенства и подобия треугольников. Формулировки, схемы и то, как применять их на практике."
                    )
            photo_url = photo_task_triangle_similarity

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Треугольник"
        elif data == "task_triangle_call":
            text = ("Треугольник\n\n"
                    "Повторим ключевые свойства треугольника: сумма углов, зависимости между сторонами и важные отрезки внутри."
                    )
            photo_url = photo_task_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropTriangles_screen()
            )
        # Обработка "Группы Окружность"
        elif data == "task_groupCircle_call":
            text = ("Окружность\n\n"
                    "Выберите теорему, связанную с окружностями.\n"
                    "Здесь и про вписанные углы, и про касательные — всё, что пригодится на экзамене."
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupCircle_screen()
            )
        # Обработка "Окружность 1"
        elif data == "task_circle_1_call":
            text = ("Окружность №1\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Вспоминаем площадь, длину, центральные и вписанные углы.\n"
                    "Плюс признаки вписанного и описанного четырёхугольников."
                    )
            photo_url = photo_task_circle_1

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropCircle_screen()
            )
        # Обработка "Окружность 2"
        elif data == "task_circle_2_call":
            text = ("Окружность №2\n\n"
                    "Касательные, секущие, хорды — тут всё, что обычно путается.\n"
                    "Каждое свойство — важная подсказка при решении задач."
                    )
            photo_url = photo_task_circle_2

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_gropCircle_screen()
            )
        # Обработка "Параллелограмм"
        elif data == "task_parallelogram_call":
            text = ("Параллелограмм\n\n"
                    "Формулы площадей, признаки параллелограмма и его свойства. Всё, что может пригодиться в задаче."
                    )
            photo_url = photo_task_parallelogram

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Равносторонний шестиугольник"
        elif data == "task_regular_hexagon_call":
            text = ("Равносторонний шестиугольник\n\n"
                    "Шестиугольник, где все стороны и углы равны.\n"
                    "Внутренние углы — по 120°.\n"                        
                    "Его можно разбить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен стороне."
                    )
            photo_url = photo_task_regular_hexagon

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Ромб и Трапеция"
        elif data == "task_rhombus_trapezoid_call":
            text = ("Ромб и Трапеция\n\n"
                    "Повторим определения, формулы площадей и важные свойства двух часто встречающихся четырёхугольников."
                    )
            photo_url = photo_task_rhombus_trapezoid

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Углы"
        elif data == "task_angles_call":
            text = ("Углы\n\n"
                    "Углы — основа планиметрии. Здесь — виды углов, их свойства и ключевые признаки параллельности прямых."
                    )
            photo_url = photo_task_angles

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_1_screen()
            )
        # Обработка "Возврат в задания Треугольники"
        elif data == "back_to_task_gropTriangles_call":
            text = ("Треугольники\n\n"
                    "Всё, что нужно знать о треугольниках: от общих свойств до частных случаев. Выберите тему и разберите её по частям."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupTriangles_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания Окружность"
        elif data == "back_to_task_gropCircle_call":
            text = ("Окружность\n\n"
                    "Выберите теорему, связанную с окружностями.\n"
                    "Здесь и про вписанные углы, и про касательные — всё, что пригодится на экзамене."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_groupCircle_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 1"
        elif data == "taskBack_1_call":
            text = ("Задание 1 \n\n"
                    "Здесь вы можете получить все теоремы для успешного решения задания"
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_1_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "2 Задачи"
        elif data == "task_2_call":
            text = ("Задание 2 \n\n"
                    "Работаем с векторами: длины, направления и скалярное произведение."
                    )
            photo_url = photo_task2

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_2_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "3 Задачи"
        elif data == "task_3_call":

            text = ("Задание 3 \n\n"
                    "Объёмы, углы, площади поверхности — здесь теория по стереометрии."
                    )
            photo_url = photo_task3

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_3_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "4,5 Задачи"
        elif data == "task_45_call":
            text = ("Задание 4,5 \n\n"
                    "Вероятности: классическая, сложные события, сумма, произведение и формулы."
                    )
            photo_url = photo_task45

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_45_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "6,7,9 Задачи"
        elif data == "task_679_call":
            text = ("Задание 6,7,9 \n\n"
                    "Упрощение, преобразования, вычисления. Здесь всё, чтобы не теряться в формулах."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_679_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "ФСУ" +
        elif data == "task_fsu_call":
            text = ("Формулы сокращённого умножения\n\n"
                    "Базовые тождества, которые упрощают раскрытие скобок и преобразование выражений: квадраты, кубы, разности и суммы.")

            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Квадратные уравнения"
        elif data == "task_quadratic_equations_call":
            text = (
                "Квадратные уравнения\n\n"
                "Классическое уравнение второй степени. Здесь — формулы дискриминанта, разложение на множители и теорема Виета."
            )
            photo_url = photo_quadratic_equations #Замените на URL изображения квадратного уравнения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Степени" +
        elif data == "task_powers_call":
            text = (
                "Степени\n\n"
                "Свойства степеней с одинаковыми и разными основаниями.\n"
                "Базовый инструмент для упрощения выражений и решения уравнений."
            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Корни"
        elif data == "task_roots_call":
            text = (
                "Корни\n\n"
                "Свойства корней и их связь со степенями. Всё, что нужно для рациональных преобразований и упрощения выражений."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        # Обработка "Группа тригонометрия"
        elif data == "task_group_trigonometry_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task_trigonometric_circle_call":
            text = (
                "Тригонометрическая окружность\n\n"
                "Единичная окружность, на которой наглядно отображаются значения тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Окружность для тангенса"
        elif data == "task_tangent_circle_call":
            text = (
                "Окружность для тангенса\n\n"
                "Специальная тригонометрическая окружность для наглядного представления функции тангенса и определения её значений."
            )
            photo_url = photo_tangent_circle  # Ссылка на изображение для окружности тангенса

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task_definitions_call":
            text = (
                "Определения тригонометрических функций\n\n"
                "Синус, косинус, тангенс и котангенс через стороны прямоугольного треугольника. Основа всей тригонометрии."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task_trigonometric_formulas_call":
            text = (
                "Тригонометрические формулы\n\n"
                "Формулы сложения, двойного угла и другие тождества. Ключ к решению уравнений и преобразованию выражений."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task_reduction_formulas_call":
            text = (
                "Формулы приведения\n\n"
                "Позволяют упростить тригонометрические выражения с углами больше 90° и 180°. Сохраняем функцию, меняем знак."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Логарифмы"+
        elif data == "task_logarithms_call":
            text = (
                "Логарифмы\n\n"
                "Определение, свойства и преобразования логарифмов. Всё, что нужно для решения логарифмических уравнений."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Модули"
        elif data == "task_modules_call":
            text = (
                "Модули\n\n"
                "Модуль превращает отрицательные значения в положительные. Здесь — правила раскрытия и базовые свойства."
            )
            photo_url = photo_modules  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_679_screen()
            )
        #Обработка "Возврат в задания 6,7,9"
        elif data == "taskBack_679_call":
            text = ("Задание 6,7,9 \n\n"
                    "Упрощение, преобразования, вычисления. Здесь всё, чтобы не теряться в формулах."
            )
            photo_url = photo
            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_679_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTaskBack_call":
            text = (
                "Тригонометрия\n\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_group_trigonometry_screen()  # Добавляем плашку с кнопками
            )


        #Обработка "8 Задачи"
        elif data == "task_8_call":
            text = ("Задание 8 \n\n"
                    "Производные, графики и исследование функций — строго по сути."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_8_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Обычная функция и производная"
        elif data == "task_usual_function_and_derivative_call":
            text = (
                "Функция и производная\n\n"
                "Функция отражает, как меняется одна величина в зависимости от другой. Производная показывает, как быстро это изменение происходит."
            )
            photo_url = photo_task81  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_8_screen()
            )
        # Обработка "Производная"
        elif data == "task_8_derivatives_call":
            text = (
                "Производная\n\n"
                "Производная описывает поведение функции в окрестности точки: её наклон, скорость изменения и связь с первообразной.."
            )
            photo_url = photo_task82  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_8_screen()
            )
        #Обработка "Возврат в задания 8"
        elif data == "taskBack_8_call":
            text = ("Задание 8 \n\n"
                    "Производные, графики и исследование функций — строго по сути."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_8_screen()  # Добавляем плашку с кнопками
            )


        #Обработка "10 Задачи"
        elif data == "task_10_call":
            text = ("Задание 10 \n\n"
                    "Текстовые задачи. Учимся переводить условие на математический язык и находить нужную модель."
                    )
            photo_url = photo_task10

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_10_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "11 Задачи"
        elif data == "task_11_call":
            text = ("Задание 11 \n\n"
                    "Теория по свойствам функций, графикам и графическим преобразованиям."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_11_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Прямая"+
        elif data == "task_direct_call":
            text = (
                "Прямая\n\n"
                "График линейной зависимости. Наклон задаёт скорость изменения, а точка пересечения с осью — начальное значение."
            )
            photo_url = photo_direct  # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Парабола"+
        elif data == "task_parabola_call":
            text = (
                "Парабола\n\n"
                "График квадратной функции с осью симметрии. Направление ветвей, вершина и сдвиги легко читаются по формуле."
            )
            photo_url = photo_parabola  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Гипербола" +
        elif data == "task_hyperbola_call":
            text = (
                "Гипербола\n\n"
                "Функция, у которой значения приближаются к осям, но никогда их не достигают. Поведение зависит от знака и сдвигов."
            )
            photo_url = photo_hyperbola  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Функция Корня"+
        elif data == "task_root_function_call":
            text = (
                "Функция Корня\n\n"
                "Функция, при которой значению x ставится в соответствие корень. Определена только при x ≥ 0."
            )
            photo_url = photo_root_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Показательная функция"+
        elif data == "task_exponential_function_call":
            text = (
                "Показательная функция\n\n"
                "Рост или убывание зависит от основания. Чем больше a, тем резче изменения. При a > 1 — рост, при 0 < a < 1 — убывание."
            )
            photo_url = photo_exponential_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Логарифмическая функция"+
        elif data == "task_logarithmic_function_call":
            text = (
                "Логарифмическая функция\n\n"
                "Обратная к показательной. Определена при x > 0. График проходит через (1,0) и растёт медленно."
            )
            photo_url = photo_logarithmic_function  # Укажите URL изображения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_11_screen()
            )
        #Обработка "Возврат в задания 11"
        elif data == "taskBack_11_call":
            text = ("Задание 11 \n\n"
                    "Теория по свойствам функций, графикам и графическим преобразованиям."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_11_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "12 Задачи"
        elif data == "task_12_call":
            text = ("Задание 12 \n\n"
                    "Теория по свойствам функций, графикам и графическим преобразованиям."
                    )
            photo_url = photo_task12

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "13 Задачи"
        elif data == "task_13_call":
            text = ("Задание 13 \n\n"
                    "Решение тригонометрических уравнений: подстановка, формулы, преобразования."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_13_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task13trigonometric_circle_call":
            text = (
                "Тригонометрическая окружность\n\n"
                "Единичная окружность, на которой наглядно отображаются значения тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Окружность для тангенса"
        elif data == "task13tangent_circle_call":
            text = (
                "Окружность для тангенса\n\n"
                "Специальная тригонометрическая окружность для наглядного представления функции тангенса и определения её значений."
            )
            photo_url = photo_tangent_circle  # Ссылка на изображение для окружности тангенса

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task13definitions_call":
            text = (
                "Определения тригонометрических функций\n\n"
                "Синус, косинус, тангенс и котангенс через стороны прямоугольного треугольника. Основа всей тригонометрии."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task13trigonometric_formulas_call":
            text = (
                "Тригонометрические формулы\n\n"
                "Формулы сложения, двойного угла и другие тождества. Ключ к решению уравнений и преобразованию выражений."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task13reduction_formulas_call":
            text = (
                "Формулы приведения\n\n"
                "Позволяют упростить тригонометрические выражения с углами больше 90° и 180°. Сохраняем функцию, меняем знак."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группа тригонометрия"
        elif data == "tasks13trigGroup_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Логарифмы"
        elif data == "tasks13log_call":
            text = (
                "Логарифмы\n\n"
                "Определение, свойства и преобразования логарифмов. Всё, что нужно для решения логарифмических уравнений."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Корни"
        elif data == "tasks13root_call":
            text = (
                "Корни\n\n"
                "Свойства корней и их связь со степенями. Всё, что нужно для рациональных преобразований и упрощения выражений."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Степени"
        elif data == "tasks13powers_call":
            text = (
                "Степени\n\n"
                "Свойства степеней с одинаковыми и разными основаниями.\n"
                "Базовый инструмент для упрощения выражений и решения уравнений."

            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        #Обработка "ФСУ"
        elif data == "tasks13fcy_call":
            text = ("Формулы сокращённого умножения\n\n"
                    "Базовые тождества, которые упрощают раскрытие скобок и преобразование выражений: квадраты, кубы, разности и суммы.")

            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_13_screen()
            )
        # Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTask13Back_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task13group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 13"
        elif data == "taskBack_13_call":
            text = ("Задание 13 \n\n"
                    "Решение тригонометрических уравнений: подстановка, формулы, преобразования."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_13_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "14 Задачи"
        elif data == "task_14_call":
            text = ("Задание 14 \n\n"
                    "Объём и площадь в пространстве. Повторяем стереометрию без перегрузки."
                    )

            photo_url = photo_task14

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "15 Задачи"
        elif data == "task_15_call":
            text = ("Задание 15 \n\n"
                    "Неравенства всех типов: логарифмические, линейные, дробные, показательные."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_15_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Логарифмы"
        elif data == "tasks15log_call":
            text = (
                "Логарифмы\n\n"
                "Определение, свойства и преобразования логарифмов. Всё, что нужно для решения логарифмических уравнений."
            )
            photo_url = photo_logarithms  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Метод рационализации"
        elif data == "tasks15rationalization_call":
            text = (
                "Метод рационализации\n\n"
                "Позволяет заменить иррациональные выражения на более удобные, чтобы упростить расчёты и решить задачу стандартными способами."
            )
            photo_url = photo_rationalization  # Укажите URL изображения для логарифмов

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Степени"
        elif data == "tasks15powers_call":
            text = (
                "Степени\n\n"
                "Свойства степеней с одинаковыми и разными основаниями.\n"
                "Базовый инструмент для упрощения выражений и решения уравнений."
            )
            photo_url = photo_powers  # Замените на URL изображения степеней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Корни"
        elif data == "tasks15roots_call":
            text = (
                "Корни\n\n"
                "Свойства корней и их связь со степенями. Всё, что нужно для рациональных преобразований и упрощения выражений."
            )
            photo_url = photo_roots  # Замените на URL изображения корней

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "ФСУ"
        elif data == "tasks15fcy_call":
            text = ("Формулы сокращённого умножения\n\n"
                    "Базовые тождества, которые упрощают раскрытие скобок и преобразование выражений: квадраты, кубы, разности и суммы."
                    )
            photo_url = photo_fsy # Ссылка на ваше изображение

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "Квадратные уравнения"
        elif data == "task15quadratic_equations_call":
            text = (
                "Квадратные уравнения\n\n"
                "Классическое уравнение второй степени. Здесь — формулы дискриминанта, разложение на множители и теорема Виета."
            )

            photo_url = photo_quadratic_equations #Замените на URL изображения квадратного уравнения

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        #Обработка "Модули"
        elif data == "task15modules_call":
            text = (
                "Модули\n\n"
                "Модуль превращает отрицательные значения в положительные. Здесь — правила раскрытия и базовые свойства."
            )
            photo_url = photo_modules  # Укажите URL изображения для модулей

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_15_screen()
            )
        # Обработка "Возврат в задания 15"
        elif data == "taskBack_15_call":
            text = ("Задание 15 \n\n"
                    "Неравенства всех типов: логарифмические, линейные, дробные, показательные."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_15_screen()  # Добавляем плашку с кнопками
            )

        # Обработка "16 Задачи"
        elif data == "task_16_call":
            text = ("Задание 16 \n\n"
                    "Экономическая задача: доходы, расходы, проценты и формулы. Всё, чтобы не запутаться в условиях."
                    )

            photo_url = photo_task16

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_12_screen()  # Добавляем плашку с кнопками
            )

        #Обработка "17 Задачи"
        elif data == "task_17_call":
            text = ("Задание 17 \n\n"
                "Планиметрия продвинутого уровня. Теоремы, свойства и признаки — всё по полочкам."
                )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_17_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Группы Треугольники"
        elif data == "task17groupTriangles_call":
            text = ("Треугольники\n\n"
                    "Всё, что нужно знать о треугольниках: от общих свойств до частных случаев. Выберите тему и разберите её по частям."
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupTriangles_screen()
            )
        # Обработка "Прямоугольный треугольник"
        elif data == "task17right_triangle_call":
            text = ("Прямоугольный треугольник\n\n"
                    "Площадь, высоты, радиусы, теорема Пифагора — здесь собраны все основные формулы и свойства прямоугольных треугольников."
                    )
            photo_url = photo_task_right_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Равнобедренный/Равносторонний треугольник"
        elif data == "task17isosceles_equilateral_triangle_call":
            text = ("Равнобедренный и равносторонний треугольник\n\n"
                    "Основные признаки, формулы и особенности равнобедренных и равносторонних треугольников."
                    )
            photo_url = photo_task_isosceles_equilateral_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Равенство/Подобие треугольников"
        elif data == "task17triangle_similarity_call":
            text = ("Равенство/Подобие треугольников\n\n"
                    "Признаки равенства и подобия треугольников. Формулировки, схемы и то, как применять их на практике."
                    )
            photo_url = photo_task_triangle_similarity

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Треугольник"
        elif data == "task17triangle_call":
            text = ("Треугольник\n\n"
                    "Повторим ключевые свойства треугольника: сумма углов, зависимости между сторонами и важные отрезки внутри."
                    )
            photo_url = photo_task_triangle

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()
            )
        # Обработка "Биссектриса, медиана, серединный перпендикуляр"
        elif data == "task17triangle_lines_call":
            text = ("Биссектриса, медиана, серединный перпендикуляр\n\n"
                    "Три важных отрезка внутри треугольника: как они устроены, где проходят и что о них нужно знать."
                    )
            photo_url = photo_task_triangle_lines

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropTriangles_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группы Окружность"
        elif data == "task17groupCircle_call":
            text = ("Окружность\n\n"
                    "Выберите теорему, связанную с окружностями.\n"
                    "Здесь и про вписанные углы, и про касательные — всё, что пригодится на экзамене."
                    )
            photo_url = photo

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupCircle_screen()
            )
        # Обработка "Окружность 1"
        elif data == "task17circle_1_call":
            text = ("Окружность №1\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Вспоминаем площадь, длину, центральные и вписанные углы.\n"
                    "Плюс признаки вписанного и описанного четырёхугольников."
                    )
            photo_url = photo_task_circle_1

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropCircle_screen()
            )
        # Обработка "Окружность 2"
        elif data == "task17circle_2_call":
            text = ("Окружность №2\n\n"
                    "Касательные, секущие, хорды — тут всё, что обычно путается.\n"
                    "Каждое свойство — важная подсказка при решении задач."
                    )
            photo_url = photo_task_circle_2

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17gropCircle_screen()
            )
        # Обработка "Параллелограмм"
        elif data == "task17parallelogram_call":
            text = ("Параллелограмм\n\n"
                    "Формулы площадей, признаки параллелограмма и его свойства. Всё, что может пригодиться в задаче."
                    )
            photo_url = photo_task_parallelogram

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Равносторонний шестиугольник"
        elif data == "task17regular_hexagon_call":
            text = ("Равносторонний шестиугольник\n\n"
                    "Шестиугольник, где все стороны и углы равны.\n"
                    "Внутренние углы — по 120°.\n"
                    "Его можно разбить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен стороне."
                    )
            photo_url = photo_task_regular_hexagon

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Ромб и Трапеция"
        elif data == "task17rhombus_trapezoid_call":
            text = ("Ромб и Трапеция\n\n"
                    "Повторим определения, формулы площадей и важные свойства двух часто встречающихся четырёхугольников."
                    )
            photo_url = photo_task_rhombus_trapezoid

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Углы"
        elif data == "task17angles_call":
            text = ("Углы\n\n"
                    "Углы — основа планиметрии. Здесь — виды углов, их свойства и ключевые признаки параллельности прямых."
                    )
            photo_url = photo_task_angles

            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task_17_screen()
            )
        # Обработка "Возврат в задания Треугольники"
        elif data == "back_to_task17gropTriangles_call":
            text = ("Треугольники\n\n"
                    "Всё, что нужно знать о треугольниках: от общих свойств до частных случаев. Выберите тему и разберите её по частям."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupTriangles_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания Окружность"
        elif data == "back_to_task17gropCircle_call":
            text = ("Окружность\n\n"
                    "Выберите теорему, связанную с окружностями.\n"
                    "Здесь и про вписанные углы, и про касательные — всё, что пригодится на экзамене."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17groupCircle_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Группа тригонометрия"
        elif data == "task17group_trigonometry_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo_trigonometry  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрическая окружность"
        elif data == "task17trigonometric_circle_call":
            text = (
                "Тригонометрическая окружность\n\n"
                "Единичная окружность, на которой наглядно отображаются значения тригонометрических функций."
            )
            photo_url = photo_trigonometric_circle  # Ссылка на ваше изображение

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Определения"
        elif data == "task17definitions_call":
            text = (
                "Определения тригонометрических функций\n\n"
                "Синус, косинус, тангенс и котангенс через стороны прямоугольного треугольника. Основа всей тригонометрии."
            )
            photo_url = photo_definition  # Ссылка на изображение для определений

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Тригонометрические формулы"
        elif data == "task17trigonometric_formulas_call":
            text = (
                "Тригонометрические формулы\n\n"
                "Формулы сложения, двойного угла и другие тождества. Ключ к решению уравнений и преобразованию выражений."
            )
            photo_url = photo_trigonometric_formulas  # Ссылка на изображение для тригонометрических формул

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Формулы приведения"
        elif data == "task17reduction_formulas_call":
            text = (
                "Формулы приведения\n\n"
                "Позволяют упростить тригонометрические выражения с углами больше 90° и 180°. Сохраняем функцию, меняем знак."
            )
            photo_url = photo_reduction_formulas  # Ссылка на изображение для формул приведения

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=back_to_task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        #Обработка "Возврат в задания тригонометрия"
        elif data == "trigonometryTask17Back_call":
            text = (
                "Тригонометрия\n"
                "Раздел математики, связанный с углами и тригонометрическими функциями. Здесь — определения, формулы и преобразования."
            )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task17group_trigonometry_screen()  # Добавляем плашку с кнопками
            )
        # Обработка "Возврат в задания 17"
        elif data == "taskBack_17_call":
            text = ("Задание 17 \n\n"
                    "Планиметрия продвинутого уровня. Теоремы, свойства и признаки — всё по полочкам."
                    )
            photo_url = photo

            # Обновляем существующее сообщение, заменяя его на изображение с текстом и оставляя плашку
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),  # Заменяем фото и добавляем текст
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=task_17_screen()  # Добавляем плашку с кнопками
            )

        # Обрабатывает выбор "Теория по темам" и показывает начальный экран с разделами
        elif data == "tasks_by_topic_call":
            text = ("Выбирай раздел и переходи к нужной теме.\n"
                    "Внутри тебя ждёт подробная теория по каждому ключевому блоку."
                    )

            photo_url = photo_tasks
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=tasks_by_topic_screen()
            )
        # Обрабатывает выбор раздела "Алгебра" и показывает список тем алгебры
        elif data == "topics_algebra_call":
            text = ("Выбери тему, по которой хочешь изучить теорию.")
            photo_url = photo
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=algebra_topics_screen()
            )
        # Обрабатывает выбор раздела "Геометрия" и показывает список тем геометрии
        elif data == "topics_geometry_call":
            text = ("Выбери тему, по которой хочешь изучить теорию.")
            photo_url = photo
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=geometry_topics_screen()
            )

        # --- Темы Алгебры ---
        elif data == "topic_probability_call":
            text = ("📘 Теория вероятностей\n\n"
                    "Теория вероятностей — раздел математики, изучающий закономерности случайных явлений и их количественное описание с помощью вероятностей.")
            photo_url = photo_task45
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "ФСУ" из заданий 6,7,9
        elif data == "topic_fsu_call":
            text = ("Формулы сокращённого умножения\n\n"
                   "Математические выражения, упрощающие вычисления и преобразования многочленов, например:\n"
                   "квадрат суммы, разность квадратов, куб суммы и разности.")
            photo_url = photo_fsy
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_quadratic_call":
            text = ("Квадратные уравнения\n\n"
                   "Уравнение вида ax² + bx + c = 0, где a ≠ 0. Для его решения используют дискриминант или метод разложения на множители.")
            photo_url = photo_quadratic_equations
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Степени" из заданий 6,7,9
        elif data == "topic_powers_call":
            text = ("Степени\n\n"
                   "Степень числа показывает, сколько раз число умножается само на себя.")
            photo_url = photo_powers
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Корни" из заданий 6,7,9
        elif data == "topic_roots_call":
            text = ("Корни\n\n"
                   "Значение, которое, возведённое в степень, даёт исходное число.")
            photo_url = photo_roots
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Тригонометрическая окружность" из заданий 6,7,9
        elif data == "topic_trigonometric_circle_call":
            text = ("Тригонометрическая окружность\n\n"
                   "Единичная окружность с центром в начале координат, используемая для геометрического представления тригонометрических функций.")
            photo_url = photo_trigonometric_circle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Окружность для тангенса"
        elif data == "topic_tangent_circle_call":
            text = ("Окружность для тангенса\n\n"
                   "Специальная тригонометрическая окружность для наглядного представления функции тангенса и определения её значений.")
            photo_url = photo_tangent_circle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_definitions_call":
            text = "Определения тригонометрических функций"
            photo_url = photo_definition
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_trigonometric_formulas_call":
            text = "Основные тригонометрические формулы"
            photo_url = photo_trigonometric_formulas
            photo_url = photo_reduction_formulas
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Логарифмы" из заданий 6,7,9
        elif data == "topic_reduction_formulas_call":
            text = "Формулы приведения"
            photo_url = photo_reduction_formulas
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Модули" из заданий 6,7,9
        elif data == "topic_modules_call":
            text = "Модули"
            photo_url = photo_modules
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Обычная функция и производная" из задания 8
        elif data == "topic_usual_function_and_derivative_call":
            text = (
                "Обычная функция и производная\n\n"
                "Обычная функция показывает зависимость одной переменной от другой,\n"
                "а производная описывает скорость изменения этой зависимости в каждой точке."
            )
            photo_url = photo_task81
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        elif data == "topic_modules_call":
            text = "Модули"
            photo_url = photo_modules
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("↩️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Производная" из задания 8
        elif data == "topic_derivative_call":
            text = (
                "Производная\n\n"
                "Производная функции в точке характеризует скорость изменения этой функции в данной точке."
            )
            photo_url = photo_task82
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Функция корня" из задания 11
        elif data == "topic_root_function_call":
            text = ("📘 Функция корня\n\n"
                    r"Это функция вида y = √x, которая каждому неотрицательному значению x ставит в соответствие арифметическое значение корня.")
            photo_url = photo_root_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Показательная функция" из задания 11
        elif data == "topic_exponential_function_call":
            text = ("📘 Показательная функция\n\n"
                    r"Функция вида y = a^x, где 'a' — положительное число, называемое основанием, а 'x' — переменная в показателе.")
            photo_url = photo_exponential_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Логарифмическая функция" из задания 11
        elif data == "topic_logarithmic_function_call":
            text = ("📘 Логарифмическая функция\n\n"
                    r"Это функция, заданная формулой y = logax, где a > 0, a ≠ 1. Она определена при x > 0, а множество её значений — вся числовая ось.")
            photo_url = photo_logarithmic_function
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )
        # Показывает теорию по теме "Метод рационализации" из задания 15
        elif data == "topic_rationalization_call":
            text = ("📘 Метод рационализации\n\n"
                    "Заключается в преобразовании иррациональных выражений или уравнений в рациональные для упрощения их анализа и решения.")
            photo_url = photo_rationalization
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_algebra_call"))
            )

        # --- Темы Геометрии ---
        elif data == "topic_triangle_lines_call":
            text = ("📘 Биссектриса, медиана, серединный перпендикуляр\n\n"
                    "Биссектриса делит угол пополам.\n"
                    "Медиана соединяет вершину треугольника с серединой противоположной стороны.\n"
                    "Серединный перпендикуляр проходит через середину стороны под прямым углом.")
            photo_url = photo_task_triangle_lines
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Прямоугольный треугольник" из задания 1
        elif data == "topic_right_triangle_call":
            text = ("📘 Прямоугольный треугольник\n\n"
                    "Прямоугольный треугольник содержит прямой угол (90°).\n"
                    "Катеты — стороны, образующие прямой угол.\n"
                    "Гипотенуза — самая длинная сторона, противоположная прямому углу.")
            photo_url = photo_task_right_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равнобедренный/Равносторонний треугольник" из задания 1
        elif data == "topic_isosceles_equilateral_triangle_call":
            text = ("📘 Равнобедренный и равносторонний треугольник\n\n"
                    "Равнобедренный — две стороны равны, углы при основании тоже равны.\n"
                    "Равносторонний — все три стороны и углы (по 60°) равны.\n"
                    "В равностороннем треугольнике все медианы, высоты и биссектрисы совпадают.\n"
                    "В равнобедренном треугольнике высота, проведённая к основанию, является биссектрисой и медианой.")
            photo_url = photo_task_isosceles_equilateral_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равенство/Подобие треугольников" из задания 1
        elif data == "topic_triangle_similarity_call":
            text = ("📘 Равенство/Подобие треугольников\n\n"
                    "Треугольники равны, если совпадают по 3 сторонам, 2 сторонам и углу между ними или 2 углам и стороне.\n"
                    "Треугольники подобны, если их углы равны или стороны пропорциональны.")
            photo_url = photo_task_triangle_similarity
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Треугольник" из задания 1
        elif data == "topic_triangle_call":
            text = ("📘 Треугольник\n\n"
                    "Сумма углов треугольника всегда 180°.\n"
                    "Сторона треугольника меньше суммы двух других сторон.\n"
                    "Высота, медиана и биссектриса, проведённые из одной вершины, могут совпадать в равнобедренном и равностороннем треугольнике.")
            photo_url = photo_task_triangle
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Окружность" из задания 1
        elif data == "topic_circle_call":
            text = ("📘 Окружность\n\n"
                    "Окружность — это множество точек, равноудалённых от центра.\n"
                    "Радиус соединяет центр окружности с её точкой.\n"
                    "Диаметр — это удвоенный радиус, проходит через центр окружности.")
            photo_url = photo_task_circle_1
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Параллелограмм" из задания 1
        elif data == "topic_parallelogram_call":
            text = ("📘 Параллелограмм\n\n"
                    "Параллелограмм — четырёхугольник, у которого противоположные стороны параллельны.\n"
                    "Противоположные стороны равны, противоположные углы равны.\n"
                    "Диагонали точкой пересечения делятся пополам.")
            photo_url = photo_task_parallelogram
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Равносторонний шестиугольник" из задания 1
        elif data == "topic_regular_hexagon_call":
            text = ("📘 Равносторонний шестиугольник\n\n"
                    "Равносторонний (правильный) шестиугольник — это многоугольник с шестью равными сторонами и углами.\n"
                    "Все внутренние углы равны 120°.\n"
                    "Его можно разделить на 6 равносторонних треугольников.\n"
                    "Радиус описанной окружности равен длине стороны.")
            photo_url = photo_task_regular_hexagon
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Ромб и Трапеция" из задания 1
        elif data == "topic_rhombus_trapezoid_call":
            text = ("📘 Ромб и Трапеция\n\n"
                    "Ромб — четырёхугольник, все стороны которого равны между собой.\n"
                    "Трапеция — четырёхугольник, у которого две стороны параллельны, а две другие — нет.")
            photo_url = photo_task_rhombus_trapezoid
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Углы" из задания 1
        elif data == "topic_angles_call":
            text = ("📘 Углы\n\n"
                    "Геометрическая фигура, образованная двумя лучами, выходящими из одной точки.")
            photo_url = photo_task_angles
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Вектор" из задания 2
        elif data == "topic_vector_call":
            text = ("📘 Вектор\n\n"
                    "Вектор — это направленный отрезок, то есть отрезок,\n"
                    "для которого указано, какая из его граничных точек начало, а какая — конец.")
            photo_url = photo_task2
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Стереометрия" из задания 3
        elif data == "topic_stereometry_call":
            text = ("📘 Стереометрия\n\n"
                    "Стереометрия - раздел евклидовой геометрии, в котором изучаются свойства фигур в пространстве.")
            photo_url = photo_task3
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Прямая" из задания 11
        elif data == "topic_direct_call":
            text = ("📘 Прямая\n\n"
                    "Это отрезок (линия), у которого нет ни начала, ни конца.")
            photo_url = photo_direct
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Парабола" из задания 11
        elif data == "topic_parabola_call":
            text = ("📘 Парабола\n\n"
                    "График квадратичной функции, у которой существует ось симметрии,\n"
                    "и она имеет форму буквы U или перевёрнутой U.")
            photo_url = photo_parabola
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Показывает теорию по теме "Гипербола" из задания 11
        elif data == "topic_hyperbola_call":
            text = ("📘 Гипербола\n\n"
                    "Это множество точек на плоскости, для которых модуль разности расстояний от двух точек (фокусов) — величина постоянная и меньшая, чем расстояние между фокусами.")
            photo_url = photo_hyperbola
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("◀️ Назад", callback_data="topics_geometry_call"))
            )
        # Обработка кнопки "Теория"
        elif data == "theory_call":
            text = (
                    "Здесь собрана вся теория, которую нужно знать — без лишнего.\n"
                    "Можно изучать двумя способами:\n"
                    "— по заданиям ЕГЭ (от №1 до №19)\n"
                    "— по темам, если хочешь систематизировать знания иначе.\n\n"
                    "Выбери, как тебе удобнее:")
            photo_url = photo_tasks  # Можно использовать другое фото, если хотите
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=text),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=theory_screen()
            )

    # Quiz
        elif data == "quiz_call":
            text = ("Практика реальных заданий. Здесь — варианты, статистика и проверка ответов.")
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo_quize, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen()
            )

        elif data.startswith("quiz_page_"):
            page = int(call.data.split("_")[-1])
            text = (
                "Практика реальных заданий. Здесь — варианты, статистика и проверка ответов."
            )
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen(page=page)
            )

        elif data.startswith("start_quiz_"):
            day = int(call.data.split("_")[-1])  # Вариант = день
            current_option = day  # Вариант соответствует номеру варианта
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            user_id = str(call.from_user.id)
            username = call.from_user.username or call.from_user.first_name or "Unknown"

            # Проверяем, есть ли незавершённый прогресс
            cursor = quiz_conn.cursor()
            cursor.execute('''
                SELECT task_number, attempt_id, primary_score, secondary_score 
                FROM user_quiz_state 
                WHERE user_id = ? AND option = ? AND day = ? AND completed = 0
                ORDER BY timestamp DESC LIMIT 1
            ''', (user_id, current_option, day))
            state = cursor.fetchone()
            cursor.close()

            if state and user_id in user_data and "attempt_id" in user_data[user_id]:
                # Продолжаем незавершённую попытку
                task_number, attempt_id, primary_score, secondary_score = state
                user_data[user_id]["task_number"] = task_number
                user_data[user_id]["message_id"] = message_id
                user_data[user_id]["correct"] = primary_score
                user_data[user_id]["secondary_score"] = secondary_score
            else:
                # Начинаем новую попытку
                attempt_id = int(datetime.now().timestamp())  # Timestamp не требует МСК
                user_data[user_id] = {
                    "task_number": 1,
                    "day": day,
                    "current_option": current_option,
                    "attempt_id": attempt_id,
                    "correct": 0,
                    "secondary_score": 0,
                    "results": [],
                    "message_id": message_id
                }
                logging.info(f"Новая попытка начата для пользователя {user_id}: attempt_id={attempt_id}")

            # Загружаем задание
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                           (current_option, day, user_data[user_id]["task_number"]))
            task = cursor.fetchone()
            cursor.close()

            if task:
                quiz_id, image_url = task
                user_data[user_id]["quiz_id"] = quiz_id
                logging.info(
                    f"Загружена задача quiz_id={quiz_id}, option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведи ответ:"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(image_url, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                # Сохраняем текущий прогресс
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, current_option, day, user_data[user_id]["task_number"], user_data[user_id]["attempt_id"],
                      user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
                      username))
                quiz_conn.commit()
                cursor.close()
                # Регистрируем обработчик для ответа
                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
            else:
                logging.error(
                    f"Задача не найдена для option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                # Пробуем загрузить задачи из обоих возможных путей к файлу
                success = False
                for file_path in ['week.csv', '../week.csv', '/week.csv']:
                    if os.path.exists(file_path):
                        logging.info(f"Пробуем загрузить задачи из {file_path}")
                        if load_quiz_from_csv(file_path):
                            logging.info(f"Задачи успешно загружены из {file_path}, пробуем снова найти задачу")
                            
                            # Пробуем еще раз найти задачу
                            cursor = quiz_conn.cursor()
                            cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                                          (current_option, day, user_data[user_id]["task_number"]))
                            task = cursor.fetchone()
                            cursor.close()
                            
                            if task:
                                success = True
                                quiz_id, image_url = task
                                user_data[user_id]["quiz_id"] = quiz_id
                                logging.info(f"Задача найдена после перезагрузки CSV: quiz_id={quiz_id}")
                                
                                text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведи ответ:"
                                markup = types.InlineKeyboardMarkup()
                                markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
                                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
                                bot.edit_message_media(
                                    media=types.InputMediaPhoto(image_url, caption=text),
                                    chat_id=chat_id,
                                    message_id=message_id,
                                    reply_markup=markup
                                )
                                
                                # Сохраняем текущий прогресс
                                cursor = quiz_conn.cursor()
                                cursor.execute('''
                                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (user_id, current_option, day, user_data[user_id]["task_number"], user_data[user_id]["attempt_id"],
                                      user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
                                      username))
                                quiz_conn.commit()
                                cursor.close()
                                
                                # Регистрируем обработчик для ответа
                                bot.clear_step_handler_by_chat_id(chat_id)
                                bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
                                break  # Выходим из цикла, т.к. задача найдена
                
                # Если после всех попыток задача не найдена, показываем сообщение об ошибке
                if not success:
                    bot.edit_message_media(
                        media=types.InputMediaPhoto(photo, caption="Ошибка! Задачи не найдены."),
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=quiz_screen()
                    )

        elif data == "quiz_back_call":
            text = ("✨ Варианты ЕГЭ ✨\n\n"
                    "📝 Практикуйтесь, решая реальные варианты ЕГЭ.\n"
                    "➡️ Выберите вариант и вводите ответы в чат:")
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=quiz_screen()
            )
            # Сохраняем прогресс, но не очищаем user_data полностью
            if user_id in user_data:
                # Получаем имя пользователя
                username = call.from_user.username or call.from_user.first_name or "Unknown"
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, user_data[user_id]["current_option"], user_data[user_id]["day"],
                    user_data[user_id]["task_number"],
                    user_data[user_id]["attempt_id"], user_data[user_id]["correct"], user_data[user_id]["secondary_score"],
                    0,
                    datetime.now().isoformat(), username))
                quiz_conn.commit()
                cursor.close()
                # Очищаем обработчик для текущего чата
                bot.clear_step_handler_by_chat_id(chat_id)

        elif data.startswith("reset_quiz_"):
            day = int(call.data.split("_")[-1])
            current_option = day
            # Удаляем текущий прогресс
            cursor = quiz_conn.cursor()
            cursor.execute('DELETE FROM user_quiz_state WHERE user_id = ? AND option = ? AND day = ? AND completed = 0',
                           (user_id, current_option, day))
            quiz_conn.commit()
            cursor.close()
            # Начинаем новую попытку
            attempt_id = int(datetime.now().timestamp())
            # Получаем имя пользователя
            username = call.from_user.username or call.from_user.first_name or "Unknown"
            user_data[user_id] = {
                "task_number": 1,
                "day": day,
                "current_option": current_option,
                "attempt_id": attempt_id,
                "correct": 0,
                "secondary_score": 0,
                "results": [],
                "message_id": message_id
            }
            # Загружаем первое задание
            cursor = quiz_conn.cursor()
            cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                           (current_option, day, user_data[user_id]["task_number"]))
            task = cursor.fetchone()
            cursor.close()
            if task:
                quiz_id, image_url = task
                user_data[user_id]["quiz_id"] = quiz_id
                logging.info(
                    f"Загружена задача после сброса quiz_id={quiz_id}, option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведи ответ:"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(image_url, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
                # Сохраняем текущий прогресс
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, current_option, day, user_data[user_id]["task_number"], user_data[user_id]["attempt_id"],
                      user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
                      username))
                quiz_conn.commit()
                cursor.close()
                # Очищаем предыдущие обработчики и регистрируем новый
                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
            else:
                logging.error(
                    f"Задача не найдена после сброса для option={current_option}, day={day}, task_number={user_data[user_id]['task_number']}")
                bot.edit_message_text(
                    "❌ Задачи для этого варианта ещё не загружены!",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=quiz_screen()
                )

        elif data == "quiz_stats":
            text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_screen(user_id, page=1)  # Передаём user_id
            )

        elif data.startswith("stats_page_"):
            page = int(call.data.split("_")[-1])
            text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_screen(user_id, page=page)  # Передаём user_id
            )

        elif data.startswith("stats_variant_"):
            variant = int(call.data.split("_")[-1])
            text = f"📊 Статистика для Варианта {variant}\n\nВыберите попытку для просмотра:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_attempts_screen(user_id, variant, page=1)
            )

        elif data.startswith("stats_attempt_"):
            parts = call.data.split("_")
            logging.info(f"Обработка stats_attempt_, call.data: {call.data}, parts: {parts}")
            if len(parts) != 4:  # Ожидаем ["stats", "attempt", variant, attempt_id]
                logging.error(f"Некорректный формат callback_data для stats_attempt_: {call.data}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            _, _, variant, attempt_id = parts
            try:
                variant = int(variant)
                attempt_id = int(attempt_id)
            except ValueError as e:
                logging.error(
                    f"Ошибка при преобразовании variant или attempt_id: variant={variant}, attempt_id={attempt_id}, ошибка: {e}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            # Получаем данные попытки
            cursor = quiz_conn.cursor()
            cursor.execute('''
                SELECT primary_score, secondary_score 
                FROM user_quiz_state 
                WHERE user_id = ? AND option = ? AND attempt_id = ?
            ''', (user_id, variant, attempt_id))
            state = cursor.fetchone()
            cursor.close()
            if state:
                primary_score, secondary_score = state
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    SELECT task_number, user_answer 
                    FROM user_quiz_progress 
                    WHERE user_id = ? AND attempt_id = ? AND option = ?
                    ORDER BY task_number
                ''', (user_id, attempt_id, variant))
                user_answers = cursor.fetchall()
                cursor.close()
                cursor = quiz_conn.cursor()
                cursor.execute('''
                    SELECT task_number, correct_answer 
                    FROM quiz_tasks 
                    WHERE option = ? AND day = ?
                    ORDER BY task_number
                ''', (variant, variant))
                correct_answers = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.close()
                result_text = []
                for task_number, user_answer in user_answers:
                    if task_number < 10:
                        spaces = "   "
                    else:
                        spaces = "  "
                    correct_answer = correct_answers.get(task_number, "")
                    is_correct = str(user_answer).lower() == str(correct_answer).lower()
                    if is_correct:
                        line = f"#️⃣ {task_number:02d}{spaces}✅"
                    else:
                        line = f"#️⃣ {task_number:02d}{spaces}❌ (Ответ: {correct_answer})"
                    result_text.append(line)
                full_text = "\n".join(result_text) if result_text else "Нет ответов."
                caption = (
                        f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
                        f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
                        + full_text
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data=f"stats_variant_{variant}"))
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=caption),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
            else:
                logging.error(f"Попытка не найдена: user_id={user_id}, variant={variant}, attempt_id={attempt_id}")
                bot.edit_message_text(
                    "❌ Данные попытки не найдены.",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_attempts_screen(user_id, variant)
                )

        elif data.startswith("stats-attempts-page-"):
            parts = call.data.split("-")
            logging.info(f"Обработка stats-attempts-page-, call.data: {call.data}, parts: {parts}")
            if len(parts) != 5:  # Ожидаем ["stats", "attempts", "page", variant, page]
                logging.error(f"Некорректный формат callback_data для stats-attempts-page-: {call.data}")
                text = "📊 Статистика\n\nВыберите вариант для просмотра статистики:"
                bot.edit_message_media(
                    media=types.InputMediaPhoto(photo, caption=text),
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=stats_screen(user_id, page=1)
                )
                return
            _, _, _, variant, page = parts
            variant = int(variant)
            page = int(page)
            text = f"📊 Статистика для Варианта {variant}\n\nВыберите попытку для просмотра:"
            bot.edit_message_media(
                media=types.InputMediaPhoto(photo, caption=text),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=stats_attempts_screen(user_id, variant, page=page)
            )
    except AttributeError as e:
        logging.error(f"Ошибка в callback: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте снова.")
# ================== Quiz ==================
def save_user_data(user_id):
    """Сохраняет состояние user_data в базу данных."""
    # Обновляем дату последнего взаимодействия с ботом при сохранении данных
    update_last_seen(user_id)
    
    try:
        cursor = quiz_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_data_temp (user_id, data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(user_data.get(user_id, {}))))
        quiz_conn.commit()
        logging.info(f"Состояние user_data для пользователя {user_id} сохранено в базе данных")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении user_data для пользователя {user_id}: {e}")
    finally:
        cursor.close()

def load_user_data():
    """Загружает состояние user_data из базы данных при запуске."""
    global user_data
    
    # Сначала загружаем основные данные пользователей из quiz.db
    try:
        cursor = quiz_conn.cursor()
        cursor.execute('SELECT user_id, data FROM user_data_temp')
        rows = cursor.fetchall()
        for user_id, data in rows:
            # Преобразуем ID в строку для единообразия
            user_id_str = str(user_id)
            user_data[user_id_str] = json.loads(data)
        logging.info("Состояние user_data загружено из базы данных quiz.db")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при загрузке user_data из quiz.db: {e}")
    finally:
        cursor.close()
    
    # Затем загружаем информацию о группах карточек из cards.db
    try:
        # Подключаемся к базе данных cards.db
        cards_conn = sqlite3.connect("cards.db", check_same_thread=False)
        cards_cursor = cards_conn.cursor()
        
        # Получаем все группы карточек
        cards_cursor.execute("SELECT user_id, group_name, themes FROM user_groups")
        groups = cards_cursor.fetchall()
        
        # Добавляем информацию о группах в user_data
        for user_id, group_name, themes in groups:
            # Преобразуем ID в строку для единообразия
            user_id_str = str(user_id)
            
            # Если пользователя нет в user_data, создаем запись
            if user_id_str not in user_data:
                user_data[user_id_str] = {}
                
            # Если у пользователя нет ключа card_groups, добавляем его
            if "card_groups" not in user_data[user_id_str]:
                user_data[user_id_str]["card_groups"] = {}
                
            # Если у пользователя нет ключа selected_themes, добавляем его
            if "selected_themes" not in user_data[user_id_str]:
                user_data[user_id_str]["selected_themes"] = []
                
            # Добавляем группу карточек
            user_data[user_id_str]["card_groups"][group_name] = json.loads(themes)
            
        logging.info(f"Группы карточек загружены из cards.db: найдено {len(groups)} групп")
        print(f"Загружены группы карточек: {user_data}")
        
        # Очистка данных - удаляем числовые ключи, если есть соответствующие строковые
        keys_to_remove = []
        for key in user_data.keys():
            if isinstance(key, int) and str(key) in user_data:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del user_data[key]
            logging.info(f"Удалён дублирующийся числовой ключ {key} в пользу строкового '{key}'")
            
    except sqlite3.Error as e:
        logging.error(f"Ошибка при загрузке групп карточек из cards.db: {e}")
    finally:
        cards_conn.close()

def process_quiz_answer(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)

    if user_id not in user_data or "quiz_id" not in user_data[user_id]:
        logging.error(f"Пользователь {user_id} не найден в user_data или отсутствует quiz_id")
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption="❌ Ошибка! Начните Quize заново."),
            chat_id=chat_id,
            message_id=user_data[user_id]["message_id"] if user_id in user_data else message.message_id,
            reply_markup=quiz_screen()
        )
        bot.delete_message(chat_id, message.message_id)
        return

    # Проверяем наличие attempt_id
    if "attempt_id" not in user_data[user_id]:
        logging.warning(f"attempt_id отсутствует для пользователя {user_id}, генерируем новый")
        user_data[user_id]["attempt_id"] = str(int(time.time()))

    quiz_id = user_data[user_id]["quiz_id"]
    task_number = user_data[user_id]["task_number"]
    day = user_data[user_id]["day"]
    current_option = user_data[user_id]["current_option"]
    attempt_id = user_data[user_id]["attempt_id"]
    message_id = user_data[user_id]["message_id"]
    user_answer = message.text.strip().replace(",", ".").lower()

    # Получаем правильный ответ
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT correct_answer FROM quiz_tasks WHERE id = ?', (quiz_id,))
    correct_answer_row = cursor.fetchone()
    correct_answer = correct_answer_row[0].strip().replace(",", ".").lower() if correct_answer_row else ""
    cursor.close()

    is_correct = user_answer == correct_answer
    user_data[user_id]["results"].append((is_correct, correct_answer))
    if is_correct:
        user_data[user_id]["correct"] += 1

    # Сохраняем ответ пользователя
    cursor = quiz_conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_quiz_progress (user_id, attempt_id, option, task_number, user_answer)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, attempt_id, current_option, task_number, user_answer))
    quiz_conn.commit()
    cursor.close()

    # Переходим к следующей задаче
    user_data[user_id]["task_number"] += 1
    cursor = quiz_conn.cursor()
    cursor.execute('SELECT id, image_url FROM quiz_tasks WHERE option = ? AND day = ? AND task_number = ?',
                   (current_option, day, user_data[user_id]["task_number"]))
    next_task = cursor.fetchone()
    cursor.close()

    if next_task:
        quiz_id, image_url = next_task
        user_data[user_id]["quiz_id"] = quiz_id
        text = f"В-{day}, №{user_data[user_id]['task_number']:02d}\nВведи ответ:"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Начать с начала", callback_data=f"reset_quiz_{day}"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_back_call"))
        bot.edit_message_media(
            media=types.InputMediaPhoto(image_url, caption=text),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )
        # Сохраняем текущий прогресс
        cursor = quiz_conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_quiz_state (user_id, option, day, task_number, attempt_id, primary_score, secondary_score, completed, timestamp, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, current_option, day, user_data[user_id]["task_number"], attempt_id,
              user_data[user_id]["correct"], user_data[user_id]["secondary_score"], 0, datetime.now().isoformat(),
              message.from_user.username or message.from_user.first_name or "Unknown"))
        quiz_conn.commit()
        cursor.close()
        bot.register_next_step_handler_by_chat_id(chat_id, process_quiz_answer)
    else:
        # Завершаем викторину
        cursor = quiz_conn.cursor()
        cursor.execute('''
            UPDATE user_quiz_state 
            SET completed = 1, primary_score = ?, secondary_score = ?, timestamp = ?
            WHERE user_id = ? AND attempt_id = ? AND option = ?
        ''', (user_data[user_id]["correct"], get_secondary_score(user_data[user_id]["correct"]), datetime.now().isoformat(),
              user_id, attempt_id, current_option))
        quiz_conn.commit()
        cursor.close()
        show_quiz_result(chat_id, user_id, day, message_id)

    bot.delete_message(chat_id, message.message_id)
    save_user_data(user_id)  # Сохраняем состояние после каждого ответа
# Показ результата
def show_quiz_result(chat_id, user_id, day, message_id):
    if user_id not in user_data or "results" not in user_data[user_id]:
        logging.error(f"Данные пользователя {user_id} не найдены в user_data")
        bot.edit_message_text(
            "❌ Ошибка! Данные викторины отсутствуют.",
            chat_id=chat_id,
            message_id=message_id
        )
        return

    correct = user_data[user_id]["correct"]
    results = user_data[user_id]["results"]

    # Первичные баллы — это количество правильных ответов
    primary_score = correct

    # Вторичные баллы — функция от первичных баллов
    secondary_score = get_secondary_score(primary_score)

    # Формируем список всех задач (правильных и неправильных)
    result_text = []
    for i, (is_correct, correct_answer) in enumerate(results, 1):
        if i < 10:
            spaces = "   "  # Три пробела для 1–9
        else:
            spaces = "  "  # Два пробела для 10–12
        if is_correct:
            line = f"#️⃣ {i:02d}{spaces}✅"
        else:
            line = f"#️⃣ {i:02d}{spaces}❌"
        result_text.append(line)

    # Полный текст сообщения с баллами и списком ответов
    full_text = "\n".join(result_text)

    # Формируем итоговое сообщение
    caption = (
        f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
        f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
        + full_text
    )

    # Логируем содержимое caption для отладки
    logging.info(f"Сформированное сообщение: {caption}")
    logging.info(f"Длина текста: {len(caption)} символов")

    # Проверяем длину текста и обрезаем, если превышает 1024 символа
    if len(caption) > 1024:
        header_length = len(
            f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
            f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
        )
        max_result_length = 1024 - header_length - len("\n...") - 1

        truncated_result_text = []
        current_length = 0
        for line in result_text:
            new_length = current_length + len(line) + 1
            if new_length <= max_result_length:
                truncated_result_text.append(line)
                current_length = new_length
            else:
                break

        truncated_full_text = "\n".join(truncated_result_text) + "\n..."
        caption = (
            f"⭐️ Первичных баллы: {primary_score}/12 ⭐️\n"
            f"⭐️ Вторичные баллы: {secondary_score} ⭐️\n"
            + truncated_full_text
        )

    bot.edit_message_media(
        media=types.InputMediaPhoto(photo, caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("◀️ Назад", callback_data="quiz_call")
        )
    )

    # Логируем удаление user_data
    logging.info(f"Удаление user_data для пользователя {user_id} после завершения викторины")
    del user_data[user_id]  # Очищаем данные пользователя

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Новые универсальные функции для работы с подсказками
def mark_hint_as_used(user_id, challenge_num, cat_code, task_idx):
    """Единая функция для отметки использования подсказки"""
    task_key = f"{challenge_num}_{cat_code}_{task_idx}"
    
    # 1. Сначала сохраняем в памяти для быстрого доступа
    if user_id not in user_data:
        user_data[user_id] = {}
    if 'viewed_hints' not in user_data[user_id]:
        user_data[user_id]['viewed_hints'] = {}
        
    user_data[user_id]['viewed_hints'][task_key] = True
    logging.info(f"✅ Факт использования подсказки сохранен в памяти для {task_key}")
    
    # 2. Затем сохраняем в БД для надежности и постоянства
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        
        # Убеждаемся, что таблица hint_usage существует
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hint_usage (
                user_id TEXT,
                challenge_num TEXT,
                cat_code TEXT,
                task_idx INTEGER,
                used INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, challenge_num, cat_code, task_idx)
            )
        ''')
        
        # Сохраняем запись о том, что подсказка использовалась
        cursor.execute('''
            INSERT OR REPLACE INTO hint_usage (user_id, challenge_num, cat_code, task_idx, used)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, str(challenge_num), cat_code, task_idx))
        
        conn.commit()
        logging.info(f"✅ Факт использования подсказки сохранен в БД для {task_key}")
        
        conn.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении информации о подсказке в БД: {e}")
    
    return True

def check_hint_usage(user_id, challenge_num, cat_code, task_idx):
    """Единая функция для проверки использования подсказки"""
    task_key = f"{challenge_num}_{cat_code}_{task_idx}"
    used_hint = False
    
    logging.info(f"🔍🔍🔍 РАСШИРЕННАЯ ДИАГНОСТИКА: проверка использования подсказки для задачи {task_key}")
    logging.info(f"ПЕРЕДАННЫЕ ПАРАМЕТРЫ: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}")
    
    # 1. Сначала проверяем в памяти (быстрый доступ)
    logging.info(f"ШАГ 1: Проверка в оперативной памяти...")
    memory_hint = False
    if user_id in user_data:
        logging.info(f"...user_id={user_id} найден в user_data")
        if 'viewed_hints' in user_data[user_id]:
            logging.info(f"...структура viewed_hints существует для пользователя {user_id}")
            memory_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
            logging.info(f"...проверка ключа {task_key} в viewed_hints: {memory_hint}")
            if memory_hint:
                used_hint = True
                logging.info(f"...подсказка найдена в памяти: {memory_hint}")
        else:
            logging.info(f"...структура viewed_hints отсутствует для пользователя {user_id}")
    else:
        logging.info(f"...user_id={user_id} не найден в user_data")
    
    # 2. Если не нашли в памяти, проверяем в БД (надежное хранилище)
    logging.info(f"ШАГ 2: Проверка в базе данных...")
    if not used_hint:
        logging.info(f"...подсказка не найдена в памяти, проверяем БД")
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Проверяем существование таблицы hint_usage
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hint_usage'")
            table_exists = cursor.fetchone()
            if table_exists:
                logging.info(f"...таблица hint_usage существует в БД")
                # Таблица существует, проверяем наличие записи
                cursor.execute('''
                    SELECT * FROM hint_usage 
                    WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=?
                ''', (user_id, str(challenge_num), cat_code, task_idx))
                
                result = cursor.fetchone()
                logging.info(f"...результат запроса к БД: {result}")
                
                if result:
                    db_hint = bool(result[4]) if len(result) > 4 else True  # В позиции 4 должен быть столбец used
                    logging.info(f"...подсказка найдена в БД, значение used: {db_hint}")
                    
                    if db_hint:
                        used_hint = True
                        # Также обновляем данные в памяти для согласованности
                        if user_id not in user_data:
                            user_data[user_id] = {}
                        if 'viewed_hints' not in user_data[user_id]:
                            user_data[user_id]['viewed_hints'] = {}
                        user_data[user_id]['viewed_hints'][task_key] = True
                        logging.info(f"...обновлены данные в памяти для согласованности")
                else:
                    logging.info(f"...подсказка не найдена в БД")
            else:
                logging.info(f"...таблица hint_usage не существует в БД")
            
            conn.close()
        except Exception as e:
            logging.error(f"❌ Ошибка при проверке использования подсказки в БД: {e}")
            logging.error(f"Трассировка стека:", exc_info=True)
    
    logging.info(f"ИТОГОВЫЙ результат проверки использования подсказки для {task_key}: {used_hint}")
    return used_hint

# ================== Обработчик текстовых запросов ==================
@bot.message_handler(func=lambda message: str(message.from_user.id) in user_task_data)
def handle_task_answer(message):
    user_id = str(message.from_user.id)
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    task_data = user_task_data.get(user_id)
    if not task_data:
        logging.error(f"Нет данных задачи для user_id={user_id}")
        bot.send_message(user_id, "Ошибка: задача не найдена. Попробуйте выбрать задачу заново.")
        return

    logging.info(f"Обработка ответа для user_id={user_id}: {message.text}, task_data={task_data}")
    user_answer = message.text.strip().replace(',', '.').replace(' ', '').lower()
    
    # Извлекаем информацию о задаче для быстрого доступа
    challenge_num = task_data["challenge_num"]
    cat_code = task_data["cat_code"]
    task_idx = task_data["task_idx"]

    # Удаление сообщения пользователя
    try:
        bot.delete_message(user_id, message.message_id)
    except Exception as e:
        logging.error(f"Ошибка удаления сообщения: {e}")

    # Проверяем, это задание из избранного или обычное
    from_favorites = task_data.get("from_favorites", False)
    
    total_tasks = len(challenge[task_data["challenge_num"]][task_data["cat_code"]]["tasks"])
    
    # Проверяем наличие ключа task и ключа answer внутри task
    if "task" not in task_data or not task_data["task"]:
        logging.error(f"Ошибка: task_data не содержит ключ 'task' или он пустой: {task_data}")
        bot.send_message(user_id, "Произошла ошибка при проверке ответа. Пожалуйста, выберите задачу заново.")
        return
    
    if "answer" not in task_data["task"]:
        logging.error(f"Ошибка: task_data['task'] не содержит ключ 'answer': {task_data['task']}")
        bot.send_message(user_id, "Произошла ошибка при проверке ответа. Пожалуйста, выберите задачу заново.")
        return
    
    # Получаем правильный ответ из объекта задачи
    correct_answer = task_data["task"]["answer"].strip().replace(',', '.').replace(' ', '').lower()
    category_name = challenge[task_data["challenge_num"]][task_data["cat_code"]]['name']
    logging.info(f"Правильный ответ для задачи: {correct_answer}, пользовательский ответ: {user_answer}")
    
    # Формируем базовый текст в зависимости от типа задания
    if from_favorites:
        base_text = f"№{task_data['challenge_num']} Избранное\n{category_name}\n"
    else:
        base_text = (f"Задача {task_data['challenge_num']}\n"
                     f"{category_name} "
                     f"{task_data['task_idx'] + 1}/{total_tasks}\n")

    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()
    
    # Для обычных заданий добавляем навигационные кнопки
    if not from_favorites:
        nav_buttons = []
        if task_data["task_idx"] > 0:
            nav_buttons.append(
                types.InlineKeyboardButton("⬅️",
                                          callback_data=f"category_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx'] - 1}")
            )
        if task_data["task_idx"] < total_tasks - 1:
            nav_buttons.append(
                types.InlineKeyboardButton("➡️",
                                          callback_data=f"category_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx'] + 1}")
            )
        if nav_buttons:
            markup.row(*nav_buttons)
    # Для избранных заданий добавляем свои кнопки навигации
    else:
        if user_id in user_data and "favorite_tasks" in user_data[user_id]:
            tasks = user_data[user_id]["favorite_tasks"]
            current_index = user_data[user_id].get("current_index", 0)
            total_tasks = len(tasks)
            
            nav_buttons = []
            if current_index == 0:
                # Первая страница: пустая стрелка, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            elif current_index == total_tasks - 1:
                # Последняя страница: стрелка назад, счетчик, пустая стрелка
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            else:
                # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            
            markup.row(*nav_buttons)
    
    # Добавляем кнопку подсказки для всех типов заданий
    if "hint" in task_data["task"] and task_data["task"]["hint"]:
        markup.add(
            types.InlineKeyboardButton("💡 Подсказка",
                                       callback_data=f"hint_{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}_0")
        )
    
    # Добавляем кнопку избранного (Добавить в избранное / Удалить из избранного)
    from main import is_in_favorites
    challenge_num = task_data["challenge_num"]
    cat_code = task_data["cat_code"]
    task_idx = task_data["task_idx"]
    is_favorite = is_in_favorites(user_id, challenge_num, cat_code, task_idx)
    favorite_text = "🗑 Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное"
    markup.add(
        types.InlineKeyboardButton(favorite_text, callback_data=f"quest_favorite_{challenge_num}_{cat_code}_{task_idx}")
    )
    
    # Кнопка "Назад" в зависимости от типа задания
    if from_favorites:
        world_id = user_data[user_id].get("current_world_id", "")
        back_callback = f"quest_favorite_world_{world_id}"
    else:
        back_callback = f"challenge_{task_data['challenge_num']}"
        
    markup.add(types.InlineKeyboardButton("↩️ Назад", callback_data=back_callback))

    # Проверяем текущий статус задачи
    current_status = task_data.get("status")
    
    # Проверяем ответ
    is_correct = False
    try:
        user_answer_num = float(user_answer)
        correct_answer_num = float(correct_answer)
        is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
    except ValueError:
        is_correct = user_answer == correct_answer  # Точное совпадение для строк
    
    # ВАЖНО: Добавляем подробное логирование при обработке ответа
    logging.info(f"ОБРАБОТКА ОТВЕТА: user_id={user_id}, задача={challenge_num}_{cat_code}_{task_idx}, введенный ответ={user_answer}, правильный ответ={correct_answer}, результат={is_correct}")
        
    # Проверка на наличие подсказок - важно для правила "верный ответ + подсказка"
    logging.info(f"Проверка подсказок для правила 'верный ответ + подсказка': user_id={user_id}")
    used_hint = False
    task_key = f"{challenge_num}_{cat_code}_{task_idx}"
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Теперь проверяем использование подсказки напрямую в БД
    logging.info(f"КРИТИЧЕСКАЯ ПРОВЕРКА: Ищем информацию о подсказках для задачи {task_key} в БД")
    
    # 1. Сначала проверяем в памяти (быстрый доступ)
    if user_id in user_data and 'viewed_hints' in user_data[user_id]:
        memory_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
        logging.info(f"Результат проверки использования подсказки в памяти: {memory_hint}")
        if memory_hint:
            used_hint = True
    
    # 2. Затем проверяем в БД (надежное хранилище)
    try:
        # Подключаемся к БД
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        
        # Проверяем существование таблицы hint_usage
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hint_usage'")
        if cursor.fetchone():
            # Таблица существует, проверяем наличие записи
            cursor.execute('''
                SELECT used FROM hint_usage 
                WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=?
            ''', (user_id, str(challenge_num), cat_code, task_idx))
            
            result = cursor.fetchone()
            if result:
                db_hint = bool(result[0])
                logging.info(f"Результат проверки использования подсказки в БД: {db_hint}")
                if db_hint:
                    used_hint = True
                    # Обновляем данные в памяти для согласованности
                    if user_id not in user_data:
                        user_data[user_id] = {}
                    if 'viewed_hints' not in user_data[user_id]:
                        user_data[user_id]['viewed_hints'] = {}
                    user_data[user_id]['viewed_hints'][task_key] = True
        else:
            logging.info("Таблица hint_usage не существует")
        
        conn.close()
    except Exception as e:
        logging.error(f"❌ Ошибка при проверке использования подсказки в БД: {e}")
    
    # Подробное логирование для диагностики
    logging.info(f"ПОДРОБНАЯ ДИАГНОСТИКА ПОДСКАЗОК:")
    logging.info(f"- user_id: {user_id}")
    logging.info(f"- task_key: {task_key}")
    logging.info(f"- Наличие в user_data: {user_id in user_data}")
    if user_id in user_data:
        logging.info(f"- Наличие 'viewed_hints': {'viewed_hints' in user_data[user_id]}")
        if 'viewed_hints' in user_data[user_id]:
            logging.info(f"- Содержимое 'viewed_hints': {user_data[user_id]['viewed_hints']}")
    logging.info(f"- ИТОГОВЫЙ результат проверки использования подсказки: {used_hint}")
    
    # Решаем, нужно ли обрабатывать ответ, даже если задача уже решена верно
    # Продолжаем для случаев: 1) Новый ответ или 2) Верный ответ + подсказка
    if current_status == "correct" and not used_hint:
        # Если задача уже решена верно и нет подсказки, игнорируем ответ
        logging.info(f"Задача {task_key} уже решена верно, подсказка не использовалась - игнорируем ответ")
        return
    
    # ДОБАВЛЕНО: Дополнительное логирование для прозрачности работы механизма
    logging.info(f"ВАЖНО: Задача {task_key} будет обработана. current_status={current_status}, used_hint={used_hint}")

    if is_correct:
        if from_favorites:
            new_caption = base_text + f"✅ Верно\n\nПравильный ответ: {correct_answer}"
        else:
            new_caption = base_text + f"✅ Верно\n\nПравильный ответ: {correct_answer}"
        new_status = "correct"
    else:
        if from_favorites:
            new_caption = base_text + f"❌ Неверно\n\nВведи ответ в чат:"
        else:
            new_caption = base_text + "❌ Не верно\nВведи ответ в чат:"
        new_status = "incorrect"

    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 20.0: Полностью разделяем логику обновления статуса для основных задач и домашних заданий
    # Часть 1: Обновление статуса в базе (если он изменился ИЛИ ответ неверный)
    main_status_updated = False
    if current_status != new_status or not is_correct:
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 20.0: Обновляем ТОЛЬКО основной статус задачи '{challenge_num}_{cat_code}_{task_idx}'")
        try:
            # Используем прямое подключение к базе данных task_progress.db с правильным путем
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            logging.info(f"Подключение к базе данных task_progress.db успешно установлено")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 20.1: Проверяем, существует ли ранее правильный ответ
            cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'main' AND status = 'correct'
            """, (user_id, challenge_num, cat_code, task_idx))
            was_correct_before = cursor.fetchone()
            
            # Если ответ был верным ранее, всегда сохраняем статус "correct"
            if was_correct_before:
                status_text = "correct"
                logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 20.1: Задача была решена верно ранее - сохраняем статус correct")
            else:
                # ИСПРАВЛЕНИЕ: Статус должен сохраняться как correct, если ответ верен,
                # независимо от использования подсказки
                status_text = "correct" if is_correct else "wrong"
            
            # Обновляем ТОЛЬКО основной статус задачи, не трогая домашнее задание
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, challenge_num, cat_code, task_idx, "main", status_text))
            
            main_status_updated = True
            logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 20.0: Основной статус задачи '{challenge_num}_{cat_code}_{task_idx}' обновлен на '{status_text}'")
            
            # ВАЖНО: Если ответ был верным, не меняем его на неверный независимо от использования подсказки
            if is_correct:
                status_text = "correct"
                new_status = "correct"
                # Убедимся, что далее по коду статус не изменится на "wrong"
                logging.info(f"✅ Сохранен статус 'correct' для верного ответа, даже с подсказкой")
            
        except Exception as e:
            logging.error(f"❌ Ошибка при обновлении основного статуса задачи: {e}")
            # Если произошла ошибка, создаем подключение для второй части
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
    else:
        # Создаем подключение для второй части
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        logging.info(f"⚙️ Основной статус задачи не требует обновления, но проверим необходимость добавления в ДЗ")
    
    # Часть 2: Логика добавления в домашнюю работу (ВСЕГДА выполняется, независимо от обновления статуса)
    try:
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Независимая проверка использования подсказки для '{challenge_num}_{cat_code}_{task_idx}'")
        
        # Используем единую функцию проверки использования подсказки
        task_key = f"{challenge_num}_{cat_code}_{task_idx}"
        used_hint = check_hint_usage(user_id, challenge_num, cat_code, task_idx)
        
        logging.info(f"✅ ПРОВЕРКА: Состояние использования подсказки для задачи {task_key}: {used_hint}")
            
        # Применяем правила для добавления задачи в домашнюю работу:
        # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
        # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ
        # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
        # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
        
        logging.info(f"*** ИДЁТ ПРОВЕРКА ПРАВИЛ ДОБАВЛЕНИЯ В РИТУАЛ ПОВТОРЕНИЯ ***")
        logging.info(f"Задача: {challenge_num}_{cat_code}_{task_idx}, ответ правильный: {is_correct}, использована подсказка: {used_hint}")
        
        # Более детальное логирование для отладки
        logging.info(f"ОТЛАДКА ПОДСКАЗОК: user_id={user_id}, task={challenge_num}_{cat_code}_{task_idx}")
        if user_id in user_data:
            logging.info(f"ОТЛАДКА VIEWED_HINTS: структура user_data для {user_id} существует")
            if 'viewed_hints' in user_data[user_id]:
                all_hints = user_data[user_id]['viewed_hints']
                logging.info(f"ОТЛАДКА VIEWED_HINTS: все подсказки пользователя: {all_hints}")
            else:
                logging.info(f"ОТЛАДКА VIEWED_HINTS: структура viewed_hints отсутствует для {user_id}")
        else:
            logging.info(f"ОТЛАДКА VIEWED_HINTS: пользователь {user_id} не найден в user_data")
        
        # Решаем добавлять ли в ДЗ строго по правилам:
        # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
        # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ
        # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
        # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Полностью переписываем логику добавления в ДЗ с нуля
        # Сначала сбрасываем флаг - по умолчанию НЕ добавляем в ДЗ
        add_to_homework = False
        
        # Явно проверяем все три случая, когда нужно добавлять в ДЗ:
        # 1. Верный ответ + использована подсказка
        if is_correct and used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 1: Верный ответ + использована подсказка -> Добавляем в ДЗ")
            
        # 2. Неверный ответ + использована подсказка
        elif not is_correct and used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 2: Неверный ответ + использована подсказка -> Добавляем в ДЗ")
            
        # 3. Неверный ответ без подсказки
        elif not is_correct and not used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 3: Неверный ответ без подсказки -> Добавляем в ДЗ")
            
        # 4. Верный ответ без подсказки - НЕ добавляем в ДЗ
        else:  # is_correct and not used_hint:
            logging.info(f"!!! ОПРЕДЕЛЕНО УСЛОВИЕ CASE 4 ДЛЯ ЗАДАЧИ {challenge_num}_{cat_code}_{task_idx}")
            logging.info(f"!!! ПЕРЕПРОВЕРКА КРИТЕРИЕВ: is_correct={is_correct}, used_hint={used_hint}, match=(is_correct and not used_hint)={(is_correct and not used_hint)}")
            add_to_homework = False
            logging.info(f"СЛУЧАЙ 4: Верный ответ без подсказки -> НЕ добавляем в ДЗ, add_to_homework={add_to_homework}")
            logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Задача с верным ответом без подсказки НЕ будет добавлена в 'Ритуал повторения'")
            
            # ВАЖНО! Принудительно проверяем, не было ли ошибочно добавлено задание в домашнюю работу ранее
            try:
                # Проверяем, существует ли задание в домашней работе
                check_cursor = conn.cursor()
                check_cursor.execute("""
                    SELECT * FROM task_progress WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'
                """, (user_id, challenge_num, cat_code, task_idx))
                existing_hw = check_cursor.fetchone()
                logging.info(f"!!! ПРОВЕРКА НАЛИЧИЯ В ДОМАШНЕМ ЗАДАНИИ: {existing_hw}")
                
                # Если задание есть в домашней работе, удаляем его
                if existing_hw:
                    logging.info(f"⚠️ ОБНАРУЖЕНА ОШИБКА: Задание {challenge_num}_{cat_code}_{task_idx} было неправильно добавлено в ДЗ ранее. Исправляем...")
                    check_cursor.execute("""
                        DELETE FROM task_progress 
                        WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'
                    """, (user_id, challenge_num, cat_code, task_idx))
                    conn.commit()
                    logging.info(f"✅ ИСПРАВЛЕНО: Задание {challenge_num}_{cat_code}_{task_idx} удалено из домашней работы, т.к. это верный ответ без подсказки")
            except Exception as e:
                logging.error(f"❌ Ошибка при проверке/удалении задания из домашней работы: {e}")
        
        logging.info(f"Решение о добавлении в ДЗ: add_to_homework={add_to_homework}")
        logging.info(f"Основания: used_hint={used_hint}, is_correct={is_correct}")
        logging.info(f"ПРОВЕРКА УСЛОВИЙ: 1.Верный+подсказка: {is_correct and used_hint}, 2.Неверный+подсказка: {not is_correct and used_hint}, 3.Неверный+не подсказка: {not is_correct and not used_hint}, 4.Верный+не подсказка: {is_correct and not used_hint}")
        
        if add_to_homework:
            # Определяем причину добавления для логирования
            if used_hint and is_correct:
                reason = "верный ответ + использование подсказки"
                message_reason = "правильно решили задачу, но использовали подсказку"
            elif used_hint and not is_correct:
                reason = "неверный ответ + использование подсказки"
                message_reason = "использовали подсказку, но ответили неверно"
            else:  # not is_correct and not used_hint
                reason = "неверный ответ без подсказки"
                message_reason = "ответили неверно"
            
            logging.info(f"⚠️ Добавляем задачу {challenge_num}_{cat_code}_{task_idx} в ДЗ. Причина: {reason}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.2: Используем 'unresolved' вместо 'wrong' для статуса в домашних заданиях
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, challenge_num, cat_code, task_idx, "homework", "unresolved"))
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Явно делаем коммит транзакции
            conn.commit()
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Немедленное обновление мира в таблице world_progress
            # Это гарантирует, что домашние задания сразу будут учтены на карте прогресса
            try:
                # Получаем текущий прогресс для обновления
                current_world_id = challenge_num  # Это ID мира
                logging.info(f"🔄 ПРОГРЕСС: Обновляем счетчик домашних заданий для мира {current_world_id}")
                
                # Обновляем состояние мира принудительно, чтобы учесть новое домашнее задание
                update_world_progress(user_id, current_world_id)
                logging.info(f"✅ ПРОГРЕСС: Счетчик домашних заданий для мира {current_world_id} обновлен")
            except Exception as e:
                logging.error(f"❌ ПРОГРЕСС: Ошибка при обновлении счетчика домашних заданий: {e}")
            
            # Отладочная информация
            logging.info(f"⚠️⚠️⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ДОБАВЛЕНО В ДОМАШНЮЮ РАБОТУ: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, причина: {reason}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Сразу обновляем текущий список домашних заданий
            # и отправляем немедленное уведомление пользователю
            force_sync_homework_tasks()
            
            # Проверяем добавленную запись
            cursor.execute("SELECT * FROM task_progress WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'",
                          (user_id, challenge_num, cat_code, task_idx))
            result = cursor.fetchone()
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Отправляем уведомление пользователю о добавлении задания в домашнюю работу
            try:
                bot.send_message(
                    user_id, 
                    f"⚠️ *Ритуал повторения* ⚠️\n\nЗадание по теме *{challenge[challenge_num][cat_code]['name']}* добавлено в домашнюю работу ({message_reason}).", 
                    parse_mode="Markdown"
                )
                logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Отправлено уведомление о добавлении задания в ДЗ")
            except Exception as e:
                logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Ошибка при отправке уведомления: {e}")
            logging.info(f"⚠️⚠️⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Запись в БД (homework): {result}")
    except Exception as e:
        logging.error(f"❌ Ошибка при обработке логики домашней работы: {e}")
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Закрываем соединение при ошибке
        if conn:
            conn.close()
        
    # Завершающие действия после обработки ДЗ
    # Убираем флаг автоматического перенаправления в ДЗ
    # Теперь пользователь останется на экране задачи даже после добавления её в ДЗ
    logging.info(f"Задача обработана для user_id={user_id}")
    
    # Сохраняем состояние user_data для персистентности
    save_user_data(user_id)
    
    # Если задание было добавлено в ДЗ, регистрируем это в логах
    if add_to_homework:
        # Определяем причину добавления для логирования
        if used_hint and is_correct:
            message_reason = "правильно решили задачу, но использовали подсказку"
        elif used_hint and not is_correct:
            message_reason = "использовали подсказку, но ответили неверно"
        else:  # not is_correct and not used_hint
            message_reason = "ответили неверно"
            
        logging.info(f"✅ Задача добавлена в 'Ритуал повторения' для пользователя {user_id}, причина: {message_reason}")
        
        # НОВОЕ ИСПРАВЛЕНИЕ: Принудительно синхронизируем домашние задания для актуального состояния
        force_sync_homework_tasks()
        logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Принудительная синхронизация домашних заданий выполнена после добавления задачи в ДЗ")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Немедленно обновляем прогресс в мире
        try:
            # Получаем ID мира из данных задачи
            world_id = int(challenge_num)
            
            # Вызываем функцию обновления прогресса с force_recount=True для немедленного пересчета
            update_world_progress(user_id, world_id)
            logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Выполнено принудительное обновление прогресса в мире {world_id} для пользователя {user_id}")
        except Exception as e:
            logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Ошибка при обновлении прогресса в мире: {e}")
    
    # Выводим все записи в базе данных для отладки
    try:
        debug_conn = sqlite3.connect('task_progress.db')
        debug_cursor = debug_conn.cursor()
        debug_cursor.execute("SELECT * FROM task_progress WHERE user_id=? AND type='homework'", (user_id,))
        hw_records = debug_cursor.fetchall()
        print(f"Домашние задания пользователя {user_id}: {hw_records}")
        debug_conn.close()
    except Exception as e:
        logging.error(f"Ошибка при получении отладочной информации: {e}")
    
    # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
    if is_correct:
        if 'user_solutions' not in user_data.get(user_id, {}):
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['user_solutions'] = {}
        task_key = f"{task_data['challenge_num']}_{task_data['cat_code']}_{task_data['task_idx']}"
        user_data[user_id]['user_solutions'][task_key] = "correct"
    
    # Сохраняем изменения в базе и закрываем соединение
    try:
        conn.commit()
        conn.close()
        logging.info(f"Соединение с базой данных успешно закрыто")
    except Exception as e:
        logging.error(f"Ошибка при закрытии соединения с базой данных: {e}")
    
    # Обновляем сообщение с задачей
    try:
        # Эта логика теперь полностью содержится в блоке обработки viewed_hints выше,
        # поэтому здесь нет необходимости дублировать код - теперь используется единый механизм
        # добавления задач в домашнюю работу для всех случаев
        bot.edit_message_media(
            media=types.InputMediaPhoto(task_data["task"]["photo"], caption=new_caption),
            chat_id=user_id,
            message_id=task_data["message_id"],
            reply_markup=markup
        )
        task_data["current_caption"] = new_caption
        task_data["status"] = new_status
        user_task_data[user_id] = task_data
        
        # Сохраняем состояние экрана и текущую задачу для корректной навигации
        if user_id not in user_data:
            user_data[user_id] = {}
            
        user_data[user_id]['current_screen'] = 'quest_task'
        user_data[user_id]['current_task'] = {
            "challenge_num": task_data["challenge_num"],
            "cat_code": task_data["cat_code"],
            "task_idx": task_data["task_idx"],
            "screen": "quest_task"
        }
        logging.info(f"Сохранен контекст current_screen='quest_task' и текущая задача для user_id={user_id} после обработки ответа")
        
        logging.info(f"Сообщение успешно обновлено после ответа пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка обновления сообщения: {e}")
        bot.send_message(user_id, "Ошибка при обработке ответа. Попробуйте снова.")

@bot.message_handler(func=lambda message: str(message.from_user.id) in user_data and "quiz_id" in user_data[str(message.from_user.id)])
def handle_quiz_text(message):
    user_id = str(message.from_user.id)
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    process_quiz_answer(message)  # Используем существующую функцию из вашего кода

# Обработчик ответов на задания из избранного
def handle_favorite_answer(message):
    """Обработчик ответов на задания из избранного"""
    user_id = str(message.from_user.id)
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Логируем полученный ответ
    logging.info(f"Получен ответ на задание из избранного от пользователя {user_id}: '{text}'")
    
    # Проверяем, что у пользователя отображается задание из избранного
    if user_id not in user_data or "current_task" not in user_data[user_id]:
        bot.send_message(chat_id, "Ошибка: не найдено активное задание. Пожалуйста, перейдите в раздел избранного.")
        return
    
    # Получаем информацию о текущем задании
    current_task = user_data[user_id]["current_task"]
    challenge_num = current_task.get("challenge_num")
    cat_code = current_task.get("cat_code")
    task_idx = current_task.get("task_idx")
    message_id = current_task.get("message_id")
    
    if not challenge_num or not cat_code or task_idx is None or not message_id:
        bot.send_message(chat_id, "Ошибка: неполная информация о задании.")
        return
        
    # Получаем задачу из challenge
    world_challenges = challenge.get(str(challenge_num), {})
    if not world_challenges:
        bot.send_message(chat_id, "Ошибка: мир не найден.")
        return
        
    category = world_challenges.get(cat_code)
    if not category or 'tasks' not in category:
        bot.send_message(chat_id, "Ошибка: категория не найдена.")
        return
        
    # Находим задание
    if task_idx < 0 or task_idx >= len(category['tasks']):
        bot.send_message(chat_id, "Ошибка: задание не найдено.")
        return
        
    task = category['tasks'][task_idx]
    
    # Удаляем сообщение пользователя
    try:
        bot.delete_message(chat_id, message.message_id)
        logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
    
    # Проверяем ответ пользователя
    user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
    correct_answer = str(task.get("answer", "")).strip().replace(',', '.').replace(' ', '').lower()
    
    # Проверяем точное совпадение
    is_correct = user_answer == correct_answer
    
    # Проверка с числами (если строгое сравнение не сработало)
    if not is_correct:
        try:
            user_answer_num = float(user_answer)
            correct_answer_num = float(correct_answer)
            is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
        except ValueError:
            # Если не удалось преобразовать в число, оставляем результат сравнения строк
            pass
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Исправлена проблема с изменением статуса с "Верно" на "Неверно" при перезаходе
    # для правильных ответов с использованной подсказкой
    # Обновляем статус в базе данных
    new_status = "correct" if is_correct else "incorrect"
    status_value = 1 if is_correct else 0  # 1 - верно, 0 - неверно
    
    # ВАЖНО! Используем правильное значение статуса для записи в БД
    # status_text должен быть "correct", а не "wrong" при is_correct=True
    status_text = "correct" if is_correct else "wrong"
    
    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 5.0: Установка статуса задачи {challenge_num}_{cat_code}_{task_idx} для пользователя {user_id}: {status_text}")
    
    # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Логирование неверного ответа  
    if not is_correct:
        logging.info(f"⚠️ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ (favorites): Неверный ответ от пользователя {user_id} на задачу {challenge_num}_{cat_code}_{task_idx}")
        
    try:
        conn = sqlite3.connect('task_progress.db')
        cursor = conn.cursor()
        # Обновляем статус задачи в основной таблице
        cursor.execute("""
            INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, str(challenge_num), cat_code, task_idx, "main", status_text))
        
        # Получаем информацию о том, использовал ли пользователь подсказку с помощью унифицированной функции
        logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверка использования подсказки в избранном через единую функцию")
        logging.info(f"Проверка использования подсказки для задачи из избранного, user_id={user_id}, задача={challenge_num}_{cat_code}_{task_idx}")
        
        # Используем единую функцию проверки использования подсказки
        task_key = f"{challenge_num}_{cat_code}_{task_idx}"
        used_hint = check_hint_usage(user_id, str(challenge_num), cat_code, task_idx)
        
        logging.info(f"✅ ПРОВЕРКА: Состояние использования подсказки для избранной задачи {task_key}: {used_hint}")
        
        # ДОБАВЛЕНО: Дополнительное логирование для прозрачности работы механизма
        logging.info(f"ВАЖНО: Обрабатываем избранное задание {task_key}. used_hint={used_hint}, is_correct={is_correct}")
        
        # Применяем правила для добавления задачи в домашнюю работу:
        # 1. Верный ответ + использование подсказки -> Добавить в ДЗ
        # 2. Неверный ответ + использование подсказки -> Добавить в ДЗ 
        # 3. Неверный ответ + без подсказки -> Добавить в ДЗ
        # 4. Верный ответ + без подсказки -> НЕ добавлять в ДЗ
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Полностью переписываем логику добавления в ДЗ с нуля
        # Сначала сбрасываем флаг - по умолчанию НЕ добавляем в ДЗ
        add_to_homework = False
        
        # Явно проверяем все три случая, когда нужно добавлять в ДЗ:
        # 1. Верный ответ + использована подсказка
        if is_correct and used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 1 (избранное): Верный ответ + использована подсказка -> Добавляем в ДЗ")
            
        # 2. Неверный ответ + использована подсказка
        elif not is_correct and used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 2 (избранное): Неверный ответ + использована подсказка -> Добавляем в ДЗ")
            
        # 3. Неверный ответ без подсказки
        elif not is_correct and not used_hint:
            add_to_homework = True
            logging.info(f"СЛУЧАЙ 3 (избранное): Неверный ответ без подсказки -> Добавляем в ДЗ")
            
        # 4. Верный ответ без подсказки - НЕ добавляем в ДЗ
        else:  # is_correct and not used_hint:
            logging.info(f"!!! ОПРЕДЕЛЕНО УСЛОВИЕ CASE 4 ДЛЯ ИЗБРАННОЙ ЗАДАЧИ {challenge_num}_{cat_code}_{task_idx}")
            logging.info(f"!!! ПЕРЕПРОВЕРКА КРИТЕРИЕВ (ИЗБРАННОЕ): is_correct={is_correct}, used_hint={used_hint}, match=(is_correct and not used_hint)={(is_correct and not used_hint)}")
            add_to_homework = False
            logging.info(f"СЛУЧАЙ 4 (избранное): Верный ответ без подсказки -> НЕ добавляем в ДЗ, add_to_homework={add_to_homework}")
            logging.info(f"✅✅✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ (избранное): Задача с верным ответом без подсказки НЕ будет добавлена в 'Ритуал повторения'")
            
            # ВАЖНО! Принудительно проверяем, не было ли ошибочно добавлено задание в домашнюю работу ранее
            try:
                # Проверяем, существует ли задание в домашней работе
                check_cursor = conn.cursor()
                check_cursor.execute("""
                    SELECT * FROM task_progress WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'
                """, (user_id, str(challenge_num), cat_code, task_idx))
                existing_hw = check_cursor.fetchone()
                logging.info(f"!!! ПРОВЕРКА НАЛИЧИЯ В ДОМАШНЕМ ЗАДАНИИ (ИЗБРАННОЕ): {existing_hw}")
                
                # Если задание есть в домашней работе, удаляем его
                if existing_hw:
                    logging.info(f"⚠️ ОБНАРУЖЕНА ОШИБКА: Задание {challenge_num}_{cat_code}_{task_idx} было неправильно добавлено в ДЗ ранее. Исправляем...")
                    check_cursor.execute("""
                        DELETE FROM task_progress 
                        WHERE user_id=? AND challenge_num=? AND cat_code=? AND task_idx=? AND type='homework'
                    """, (user_id, str(challenge_num), cat_code, task_idx))
                    conn.commit()
                    logging.info(f"✅ ИСПРАВЛЕНО: Задание {challenge_num}_{cat_code}_{task_idx} удалено из домашней работы, т.к. это верный ответ без подсказки")
            except Exception as e:
                logging.error(f"❌ Ошибка при проверке/удалении задания из избранного из домашней работы: {e}")
        
        # ВАЖНО: Если ответ был верным, не меняем его на неверный независимо от использования подсказки
        # Это исправляет баг, когда верно решенная задача помечалась как неверная после просмотра подсказок
        if is_correct:
            status_text = "correct"
            new_status = "correct"
            # Убедимся, что далее по коду статус не изменится на "wrong"
            logging.info(f"✅ Сохраняем статус 'correct' для верного ответа из избранного даже с подсказкой")
        
        logging.info(f"Решение о добавлении задания из избранного в ДЗ: add_to_homework={add_to_homework}")
        logging.info(f"Основания: used_hint={used_hint}, is_correct={is_correct}")
        logging.info(f"ПРОВЕРКА УСЛОВИЙ: 1.Верный+подсказка: {is_correct and used_hint}, 2.Неверный+подсказка: {not is_correct and used_hint}, 3.Неверный+не подсказка: {not is_correct and not used_hint}, 4.Верный+не подсказка: {is_correct and not used_hint}")
        
        if add_to_homework:
            # Определяем причину добавления для логирования
            if used_hint and is_correct:
                reason = "верный ответ + использование подсказки"
                message_reason = "правильно решили задачу, но использовали подсказку"
            elif used_hint and not is_correct:
                reason = "неверный ответ + использование подсказки"
                message_reason = "использовали подсказку, но ответили неверно"
            else:  # not is_correct and not used_hint
                reason = "неверный ответ без подсказки"
                message_reason = "ответили неверно"
            
            logging.info(f"⚠️ Добавляем избранную задачу {challenge_num}_{cat_code}_{task_idx} в ДЗ. Причина: {reason}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.3: Используем 'unresolved' вместо 'wrong' для статуса в домашних заданиях
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, str(challenge_num), cat_code, task_idx, "homework", "unresolved"))
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Явно делаем коммит транзакции для избранного
            conn.commit()
            
            # Отладочная информация
            print(f"ДОБАВЛЕНО В ДОМАШНЮЮ РАБОТУ ИЗ ИЗБРАННОГО: user_id={user_id}, challenge_num={challenge_num}, cat_code={cat_code}, task_idx={task_idx}, причина: {reason}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Сразу обновляем текущий список домашних заданий
            # и отправляем немедленное уведомление пользователю
            force_sync_homework_tasks()
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Немедленно обновляем прогресс в мире для избранных заданий
            try:
                # Получаем ID мира из данных задачи
                world_id = int(challenge_num)
                
                # Вызываем функцию обновления прогресса с force_recount=True для немедленного пересчета
                update_world_progress(user_id, world_id)
                logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Выполнено принудительное обновление прогресса в мире {world_id} для пользователя {user_id} (избранное)")
            except Exception as e:
                logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 24.0: Ошибка при обновлении прогресса для избранного задания: {e}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Отправляем уведомление пользователю о добавлении задания в домашнюю работу
            try:
                bot.send_message(
                    user_id, 
                    f"⚠️ *Ритуал повторения* ⚠️\n\nЗадание из избранного по теме *{category['name']}* добавлено в домашнюю работу ({message_reason}).", 
                    parse_mode="Markdown"
                )
                logging.info(f"✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Отправлено уведомление о добавлении задания из избранного в ДЗ")
            except Exception as e:
                logging.error(f"❌ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 3.0: Ошибка при отправке уведомления: {e}")
                
            logging.info(f"✅ Задача из избранного добавлена в 'Ритуал повторения' для пользователя {user_id}, причина: {message_reason}")
        
        # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
        if is_correct:
            if 'user_solutions' not in user_data.get(user_id, {}):
                if user_id not in user_data:
                    user_data[user_id] = {}
                user_data[user_id]['user_solutions'] = {}
            task_key = f"{challenge_num}_{cat_code}_{task_idx}"
            user_data[user_id]['user_solutions'][task_key] = "correct"
        
        conn.commit()
        conn.close()
        logging.info(f"Статус задачи из избранного обновлён на '{new_status}' для user_id={user_id}")
    except sqlite3.OperationalError as e:
        # Если таблица не существует, инициализируем её
        if "no such table" in str(e):
            init_task_progress_db()
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, str(challenge_num), cat_code, task_idx, "main", status_text))
            
            # Добавляем в домашнюю работу если нужно
            if not is_correct:
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 11.4: Используем 'unresolved' вместо 'wrong'
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, str(challenge_num), cat_code, task_idx, "homework", "unresolved"))
                
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Явно делаем коммит транзакции в блоке обработки ошибок
                conn.commit()
                
                # Убрано оповещение пользователя о добавлении в "Ритуал повторения"
                # Только логируем операцию
                logging.info(f"✅ Задача добавлена в 'Ритуал повторения' для пользователя {user_id} из-за неверного ответа")
            
            conn.commit()
            conn.close()
            logging.info(f"Таблица task_progress инициализирована и статус обновлён на '{new_status}' для user_id={user_id}")
        else:
            logging.error(f"Ошибка при обновлении статуса задачи из избранного: {e}")
    
    # Получаем название категории
    category_name = category.get("name", "Неизвестная категория")
    
    # Получаем информацию о текущем индексе и общем количестве задач
    current_index = user_data[user_id].get("current_index", 0)
    total_tasks = len(user_data[user_id].get("favorite_tasks", []))
    
    # Формируем и обновляем сообщение с результатом
    if is_correct:
        status_text = "✅ Верно"
        answer_text = f"\n\nПравильный ответ: {task['answer']}"
    else:
        status_text = "❌ Неверно"
        answer_text = "\n\nВведи ответ в чат:"
    
    caption = f"Задача {challenge_num}\n{category_name}\n{status_text}{answer_text}"
    
    # Обновляем интерфейс
    # Создаем клавиатуру с кнопками навигации
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Формируем навигационные кнопки: всегда 3 кнопки с разными обработчиками в зависимости от страницы
    nav_buttons = []
    
    if current_index == 0:
        # Первая страница: пустая стрелка, счетчик, стрелка вперед
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
    elif current_index == total_tasks - 1:
        # Последняя страница: стрелка назад, счетчик, пустая стрелка
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
    else:
        # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
        nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
    
    # Добавляем все кнопки в одном ряду
    markup.row(*nav_buttons)
    
    # Получаем количество подсказок для задания
    hint_count = len(task.get("hint", []))
    if hint_count > 0:
        # Добавляем кнопку подсказки без указания количества шагов
        markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{challenge_num}_{cat_code}_{task_idx}_0"))
    
    # Добавляем кнопку удаления из избранного
    markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_{challenge_num}_{cat_code}_{task_idx}"))
    
    # Кнопка возврата - используем callback в зависимости от текущего режима
    back_callback = f"quest_favorite_world_{challenge_num}"
    markup.add(InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
    
    bot.edit_message_media(
        media=InputMediaPhoto(task["photo"], caption=caption),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=markup
    )
    
    logging.info(f"Обработан ответ на задачу из избранного: world={challenge_num}, cat={cat_code}, task={task_idx}, правильно: {is_correct}")

# Обработчик для репетитора
@bot.message_handler(func=lambda message: str(message.from_user.id) in user_data and "tutor_step" in user_data[str(message.from_user.id)])
def handle_tutor_text(message):
    user_id = str(message.from_user.id)
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    if "tutor_step" not in user_data.get(user_id, {}) or "message_id" not in user_data.get(user_id, {}):
        bot.send_message(message.chat.id, "Процесс прерван. Начните заново.")
        if user_id in user_data:
            del user_data[user_id]
        return

    register_user(user_id, message.from_user.username)
    chat_id = message.chat.id
    step = user_data[user_id]["tutor_step"]
    message_id = user_data[user_id]["message_id"]

    questions = [
        "Ваше имя?",
        "Класс в школе?",
        "Писали пробники? Если да, то какой балл в среднем?",
        "Занятия по какой цене за час (60 минут) ожидаете?"
    ]

    if step >= len(questions):
        finish_tutor_questions(chat_id, user_id, message_id)
        return

    # Сохраняем ответы в зависимости от шага
    if step == 0:
        user_data[user_id]["tutor_answers"] = {"name": message.text}
    elif step == 1:
        user_data[user_id]["tutor_answers"]["school_class"] = message.text
    elif step == 2:
        user_data[user_id]["tutor_answers"]["test_score"] = message.text
    elif step == 3:
        user_data[user_id]["tutor_answers"]["expected_price"] = message.text

    user_data[user_id]["tutor_step"] += 1

    if user_data[user_id]["tutor_step"] < len(questions):
        text = questions[user_data[user_id]["tutor_step"]]
        markup = InlineKeyboardMarkup()
# Обработчик для навигации по избранным заданиям в режиме случайного порядка
def handle_favorite_category_random(call):
    """Обработчик для навигации по избранным заданиям в режиме случайного порядка"""
    
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = str(call.from_user.id)
    
    try:
        # Парсим данные из callback
        # Формат: favorite_category_random_<world_id>_<category_code>_<task_idx>_<position>
        parts = call.data.split("_")
        world_id = parts[3]
        category_code = parts[4]
        task_idx = int(parts[5])
        position = int(parts[6])  # Позиция в списке перемешанных задач
        
        logging.info(f"Обработка навигации по избранным заданиям в режиме случайного порядка: world_id={world_id}, category={category_code}, task_idx={task_idx}, position={position}")
        
        # Отображаем задачу с указанием, что это избранное, в режиме random_order и с правильной позицией
        display_task(chat_id, message_id, world_id, category_code, task_idx, from_favorites=True, random_order=True, current_position=position)
        
    except Exception as e:
        logging.error(f"Ошибка при обработке навигации по избранным заданиям в режиме случайного порядка: {e}")
        bot.answer_callback_query(call.id, "Ошибка при навигации по избранным")

# Обработчик для текстовых сообщений (ответы на задачи)
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    import logging
    import sqlite3
    from datetime import datetime
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
    
    user_id = str(message.from_user.id)
    user_id_int = message.from_user.id  # int версия для проверки admin_update_states
    # Обновляем дату последнего взаимодействия с ботом
    update_last_seen(user_id)
    
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Логируем полученное сообщение
    logging.info(f"Получено сообщение от пользователя {user_id}: '{text}'")
    
    # Проверяем, ожидаем ли мы сообщение для рассылки от админа
    if user_id_int in admin_update_states and admin_update_states[user_id_int] == "waiting_for_broadcast_message":
        # Удаляем состояние ожидания
        del admin_update_states[user_id_int]
        
        # Выполняем массовую рассылку
        bot.send_message(chat_id, "✅ Сообщение принято для рассылки. Начинаю процесс...")
        broadcast_message_to_all_users(user_id_int, text)
        return
    
    # Используем встроенный обработчик ответов из избранного
    
    # Получаем текущий экран пользователя
    current_screen = user_data.get(user_id, {}).get("current_screen", "")
    
    # Обработка ответов на задания в математическом квесте
    if current_screen == "quest_task":
        handle_task_answer(message)
        return
    
    # Обработка ответов на задания в избранном
    elif current_screen == "favorite_view":
        handle_favorite_answer(message)
        return
    
    # Обработка ответов на задания из вариантов
    elif current_screen == "quiz":
        handle_quiz_text(message)
        return
        
    # Обработка ответов на домашние задания
    elif "current_homework" in user_data.get(user_id, {}) and user_data[user_id].get("current_screen") == "homework_task":
        # Извлекаем данные о текущем домашнем задании
        homework_data = user_data[user_id]["current_homework"]
        user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Используем правильный ответ из поля homework
        # Ответ уже был сохранен в поле answer при открытии задания (из функции handle_quest_homework_task)
        correct_answer_original = str(homework_data.get("answer", "")).strip()
        correct_answer = correct_answer_original.replace(',', '.').replace(' ', '').lower()
        
        # Сохраняем оригинальный ответ с запятой для проверки в чистом виде
        correct_answer_comma = correct_answer_original.replace('.', ',').strip().lower()
        
        # Подробное логирование проверки ответа
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Проверка ответа для домашней работы")
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Пользовательский ответ: '{user_answer}'")
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Правильный ответ (из homework данных): '{correct_answer}'")
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Правильный ответ с запятой: '{correct_answer_comma}'")
        
        # Проверяем правильность ответа - несколько вариантов форматирования
        is_correct = (user_answer == correct_answer) or (user_answer == correct_answer_comma) or (user_answer == correct_answer_original.lower().strip())
        
        # Если строгое сравнение не сработало, пробуем с числами
        if not is_correct and user_answer and correct_answer:
            try:
                user_answer_num = float(user_answer)
                correct_answer_num = float(correct_answer)
                is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Числовое сравнение - '{user_answer_num}' и '{correct_answer_num}', результат: {is_correct}")
            except ValueError:
                # Если не удалось преобразовать в число, проверяем дополнительные варианты форматирования
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Не удалось выполнить числовое сравнение")
                
                # Если ответ содержит запятую, дополнительно проверяем точное соответствие с версией с запятой
                if ',' in correct_answer_original:
                    is_correct_exact = user_answer == correct_answer_comma
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 10.0: Дополнительная проверка с запятой: '{user_answer}' == '{correct_answer_comma}', результат: {is_correct_exact}")
                    is_correct = is_correct or is_correct_exact
        
        # Получаем параметры задачи
        world_id = homework_data["world_id"]
        cat_code = homework_data["cat_code"]
        task_idx = homework_data["task_idx"]
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 14.0: Проверяем, был ли раньше верный ответ
        # Если задача когда-либо была решена верно, никогда не меняем статус на wrong
        task_was_solved_correctly = False
        
        # Создаем ключ задачи для поиска в базе данных и кэше
        task_key = f"{world_id}_{cat_code}_{task_idx}"
        
        # Сначала проверяем в оперативной памяти
        if 'user_solutions' in user_data.get(user_id, {}) and task_key in user_data[user_id]['user_solutions']:
            if user_data[user_id]['user_solutions'][task_key] == "correct":
                task_was_solved_correctly = True
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 14.0: Задача {task_key} была ранее решена верно (из памяти)")
        
        # Если не удалось найти в памяти, проверяем в БД
        if not task_was_solved_correctly:
            try:
                check_conn = sqlite3.connect('task_progress.db')
                check_cursor = check_conn.cursor()
                check_cursor.execute("""
                    SELECT status FROM task_progress 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework' AND status = 'correct'
                """, (user_id, world_id, cat_code, task_idx))
                prev_correct = check_cursor.fetchone()
                check_conn.close()
                
                if prev_correct:
                    task_was_solved_correctly = True
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 14.0: Задача {task_key} была ранее решена верно (из БД)")
            except Exception as e:
                logging.error(f"Ошибка при проверке предыдущих решений: {e}")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 15.0: Если задача уже решена верно, просто удаляем сообщение
        # пользователя и не выполняем никаких дополнительных действий
        if task_was_solved_correctly and not is_correct:
            try:
                bot.delete_message(chat_id, message.message_id)
                logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 15.0: Задача {task_key} уже решена верно ранее. Просто удаляем новый ответ без изменения статуса.")
                return  # Прерываем дальнейшее выполнение функции
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения: {e}")
                return
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Если ответ верный или задача ранее решалась верно, 
        # всегда обновляем статус на correct
        status = "correct" if (is_correct or task_was_solved_correctly) else "wrong"
        
        # Логируем решение
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 14.0: Проверка ответа для задачи {task_key}")
        logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 14.0: is_correct={is_correct}, task_was_solved_correctly={task_was_solved_correctly}, итоговый status={status}")
        
        # Добавляем подробное логирование текущего задания
        logging.info(f"ОТЛАДКА ДОМАШНЕЙ РАБОТЫ: user_id={user_id}, текущее задание={world_id}_{cat_code}_{task_idx}")
        logging.info(f"ОТЛАДКА ДОМАШНЕЙ РАБОТЫ: пользовательский ответ='{user_answer}', правильный ответ='{correct_answer}', is_correct={is_correct}")

        # Проверяем, использовал ли пользователь подсказку
        # task_key был ранее определен
        used_hint = False
        if 'viewed_hints' in user_data.get(user_id, {}):
            used_hint = user_data[user_id]['viewed_hints'].get(task_key, False)
            logging.info(f"Проверка использования подсказки для домашнего задания: task_key={task_key}, used_hint={used_hint}")
        
        # Удаляем сообщение пользователя с ответом
        try:
            bot.delete_message(chat_id, message.message_id)
        except Exception as e:
            logging.error(f"Ошибка при удалении сообщения: {e}")
        
        # Обновляем статус задания в базе данных
        try:
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Проверим, существует ли такая запись в домашней работе
            cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
            """, (user_id, world_id, cat_code, task_idx))
            record_exists = cursor.fetchone()
            
            # Выводим информацию о наличии задания
            logging.info(f"Проверка существования задания {task_key} в домашних: {'Существует' if record_exists else 'Не существует'}")
            
            # Обновляем статус задания в домашней работе
            if record_exists:
                cursor.execute("""
                    UPDATE task_progress 
                    SET status = ? 
                    WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
                """, (status, user_id, world_id, cat_code, task_idx))
                logging.info(f"Обновлен статус задания {task_key} в домашних: status={status}")
            else:
                # Если задания нет в домашней работе, добавляем его
                cursor.execute("""
                    INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, world_id, cat_code, task_idx, "homework", status))
                logging.info(f"Создано задание {task_key} в домашних: status={status}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 18.0: Не обновляем статус в основной таблице
            # Удаляем обновление статуса основного задания, чтобы они были независимы
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 18.0: Статус основного задания НЕ обновляется при изменении домашнего задания {task_key}")
            
            # Если пользователь решил задачу верно, но использовал подсказку, 
            # всё равно оставляем её в домашней работе для повторения
            if is_correct and used_hint:
                logging.info(f"Задача решена верно, но с использованием подсказки. Оставляем в домашней работе.")
                # Ничего не делаем, задача остается в домашней работе
            
            conn.commit()
            conn.close()
            logging.info(f"Статус домашнего задания обновлен: task={task_key}, status={status}, used_hint={used_hint}")
            
            # НОВОЕ ИСПРАВЛЕНИЕ: Сразу обновляем текущий список домашних заданий,
            # чтобы изменения были видны без перезапуска бота
            force_sync_homework_tasks()
            logging.info(f"✅ ИСПРАВЛЕНИЕ: Принудительная синхронизация домашних заданий выполнена")
            
            # Проверяем статус после обновления для контроля
            check_conn = sqlite3.connect('task_progress.db')
            check_cursor = check_conn.cursor()
            check_cursor.execute("""
                SELECT status FROM task_progress 
                WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ? AND type = 'homework'
            """, (user_id, world_id, cat_code, task_idx))
            check_status = check_cursor.fetchone()
            check_conn.close()
            
            logging.info(f"Финальная проверка статуса {task_key}: {'status=' + str(check_status[0]) if check_status else 'Не найден'}")
        except Exception as e:
            logging.error(f"Ошибка обновления статуса домашнего задания: {e}")
        
        # Отправляем сообщение о результате
        world_id = homework_data["world_id"]
        cat_code = homework_data["cat_code"]
        task_idx = homework_data["task_idx"]
        message_id = homework_data["message_id"]
        
        # Получаем задание и категорию
        category = challenge.get(world_id, {}).get(cat_code, {})
        task = category.get('tasks', [])[task_idx] if category and 'tasks' in category and task_idx < len(category['tasks']) else None
        
        if task:
            # Обновляем отображение задания с новым статусом
            status_text = "✅ Верно" if is_correct else "❌ Неверно"
            caption = f"№{task_idx + 1} Домашняя работа\n{category['name']}\n{status_text}\n"
            
            if is_correct:
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем ответ из поля homework
                if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
                    homework_answer = task["homework"]["answer"]
                    caption += f"\nПравильный ответ: {homework_answer}"
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Показываем ответ из homework '{homework_answer}' в результате проверки")
                else:
                    regular_answer = task.get('answer', '')
                    caption += f"\nПравильный ответ: {regular_answer}"
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Показываем обычный ответ '{regular_answer}' (поле homework->answer не найдено)")
            else:
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 12.0: Удалена фраза "Попробуйте ещё раз или воспользуйтесь подсказкой"
                caption += "\nВведите ответ в чат:"
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем безопасный способ получения изображения из задания
            try:
                # Пытаемся получить URL изображения
                if "homework" in task and isinstance(task["homework"], dict) and "photo" in task["homework"]:
                    photo_url = task["homework"]["photo"]
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем фото из homework->photo: {photo_url}")
                elif "homework" in task and isinstance(task["homework"], str):
                    photo_url = task["homework"]
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем фото из homework (строка): {photo_url}")
                else:
                    photo_url = task.get("photo", "https://i.imgur.com/UYbCNQZ.jpeg")
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Используем основное фото: {photo_url}")
                
                # Форматируем URL для Imgur если нужно
                if not photo_url.startswith("http"):
                    photo_url = f"https://i.imgur.com/{photo_url}.jpeg"
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Преобразован URL изображения: {photo_url}")
            except Exception as e:
                photo_url = "https://i.imgur.com/UYbCNQZ.jpeg"
                logging.error(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 9.0: Ошибка при получении URL изображения: {e}, используем запасное")
                
            # Создаём клавиатуру
            markup = types.InlineKeyboardMarkup(row_width=1)
            
            # Получаем все домашние задания для навигации
            try:
                conn_nav = sqlite3.connect('task_progress.db')
                cursor_nav = conn_nav.cursor()
                cursor_nav.execute("""
                    SELECT task_idx FROM task_progress 
                    WHERE user_id = ? AND cat_code = ? AND type = 'homework'
                """, (user_id, cat_code))
                
                homework_tasks = cursor_nav.fetchall()
                conn_nav.close()
                
                if homework_tasks:
                    # Список индексов заданий
                    task_indices = [t[0] for t in homework_tasks]
                    total_tasks = len(task_indices)
                    current_index = task_indices.index(task_idx)
                    
                    # Кнопки навигации (всегда видимы)
                    nav_buttons = []
                    
                    # Если первое задание, добавляем фантомную кнопку влево
                    if current_index > 0:
                        prev_task_idx = task_indices[current_index - 1]
                        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{prev_task_idx}"))
                    else:
                        # Фантомная кнопка без функционала и без текста
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    # Счетчик текущего положения
                    nav_buttons.append(InlineKeyboardButton(f"{current_index + 1}/{total_tasks}", callback_data="quest_empty"))
                    
                    # Если последнее задание, добавляем фантомную кнопку вправо
                    if current_index < total_tasks - 1:
                        next_task_idx = task_indices[current_index + 1]
                        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_homework_task_{world_id}_{cat_code}_{next_task_idx}"))
                    else:
                        # Фантомная кнопка без функционала и без текста
                        nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                    
                    markup.row(*nav_buttons)
            except Exception as e:
                logging.error(f"Ошибка при построении навигации домашнего задания: {e}")
            
            # Кнопка для просмотра подсказки, если она есть
            if task.get('hint'):
                markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_hint_direct_{world_id}_{cat_code}_{task_idx}_0"))
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Удалена кнопка добавления в избранное для домашних заданий
            # Так как это не имеет смысла в контексте повторения
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 4.0: Кнопка добавления в избранное удалена из домашних заданий")
            
            # Кнопка возврата
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data="quest_homework"))
            
            # Отправляем обновленное сообщение
            bot.edit_message_media(
                media=InputMediaPhoto(photo_url, caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
        
        return
    
    # Обработка сообщений для запроса репетитора
    elif current_screen == "tutor_questions":
        handle_tutor_text(message)
        return
    
    # Обработка ввода имени для таймера
    elif current_screen == "timer_name_input":
        process_timer_name(message, user_id)
        return
    
    # Обработка ввода имени группы карточек
    elif current_screen == "cards_group_name_input":
        process_group_name(message, user_id, user_messages.get(user_id, 0))
        return
        
    # Проверяем наличие задачи из избранного
    if user_id in user_task_data:
        task_data = user_task_data[user_id]
        # Проверяем, что это задача из избранного
        if task_data.get("from_favorites", False):
            logging.info(f"Обработка ответа для задачи из избранного: challenge_num={task_data['challenge_num']}, cat_code={task_data['cat_code']}, task_idx={task_data['task_idx']}")
            
            # Удаляем сообщение пользователя
            try:
                bot.delete_message(chat_id, message.message_id)
                logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
            except Exception as e:
                logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
            
            # Проверяем ответ пользователя
            user_answer = text.strip().replace(',', '.').replace(' ', '').lower()
            correct_answer = str(task_data.get("correct_answer", "")).strip().replace(',', '.').replace(' ', '').lower()
            
            # Проверяем точное совпадение
            is_correct = user_answer == correct_answer
            
            # Проверка с числами (если строгое сравнение не сработало)
            if not is_correct:
                try:
                    user_answer_num = float(user_answer)
                    correct_answer_num = float(correct_answer)
                    is_correct = abs(user_answer_num - correct_answer_num) < 0.01  # Допуск для чисел
                except ValueError:
                    # Если не удалось преобразовать в число, оставляем результат сравнения строк
                    pass
            
            # Формируем текст сообщения
            world_id = task_data["challenge_num"]
            cat_code = task_data["cat_code"]
            task_idx = task_data["task_idx"]
            message_id = task_data["message_id"]
            task = task_data["task"]
            
            category_name = challenge[world_id][cat_code]["name"]
            current_index = user_data[user_id]["current_index"]
            total_tasks = len(user_data[user_id]["favorite_tasks"])
            
            # Обновляем статус в базе данных
            new_status = "correct" if is_correct else "incorrect"
            status_value = 1 if is_correct else 0  # 1 - верно, 0 - неверно
            try:
                conn = sqlite3.connect('task_progress.db')
                cursor = conn.cursor()
                # Обновляем статус задачи
                cursor.execute("""
                    INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, world_id, cat_code, task_idx, "main", status_value))
                
                # Если задача решена верно, добавляем её в словарь решенных задач в памяти для быстрого доступа
                if is_correct:
                    if 'user_solutions' not in user_data.get(user_id, {}):
                        if user_id not in user_data:
                            user_data[user_id] = {}
                        user_data[user_id]['user_solutions'] = {}
                    task_key = f"{world_id}_{cat_code}_{task_idx}"
                    user_data[user_id]['user_solutions'][task_key] = "correct"
                
                conn.commit()
                conn.close()
                logging.info(f"Статус задачи из избранного обновлён на '{new_status}' для user_id={user_id}")
            except sqlite3.OperationalError as e:
                # Если таблица не существует, инициализируем её
                if "no such table" in str(e):
                    init_task_progress_db()
                    conn = sqlite3.connect('task_progress.db')
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_progress (user_id, challenge_num, cat_code, task_idx, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, world_id, cat_code, task_idx, "main", status_value))
                    conn.commit()
                    conn.close()
                    logging.info(f"Таблица task_progress инициализирована и статус обновлён на '{new_status}' для user_id={user_id}")
                else:
                    logging.error(f"Ошибка при обновлении статуса задачи из избранного: {e}")
            
            # Формируем и обновляем сообщение с результатом
            if is_correct:
                status_text = "✅ Верно"
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 21.0: Используем homework_answer для избранных заданий при необходимости
                if "homework" in task and isinstance(task["homework"], dict) and "answer" in task["homework"]:
                    homework_answer = task["homework"]["answer"]
                    answer_text = f"\n\nПравильный ответ: {homework_answer}"
                    logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 21.0: Показываем ответ из homework '{homework_answer}' в результате проверки избранного")
                else:
                    answer_text = f"\n\nПравильный ответ: {task['answer']}"
            else:
                status_text = "❌ Неверно"
                answer_text = "\n\nВведи ответ в чат:"
            
            caption = f"№{world_id}\n{category_name}\n{status_text}\n{answer_text}"
            
            # Обновляем интерфейс
            # Создаем клавиатуру с кнопками навигации
            markup = InlineKeyboardMarkup(row_width=3)
            
            # Формируем навигационные кнопки: всегда 3 кнопки с разными обработчиками в зависимости от страницы
            nav_buttons = []
            
            if current_index == 0:
                # Первая страница: пустая стрелка, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            elif current_index == total_tasks - 1:
                # Последняя страница: стрелка назад, счетчик, пустая стрелка
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton(" ", callback_data="quest_empty"))
            else:
                # Промежуточная страница: стрелка назад, счетчик, стрелка вперед
                nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"favorite_nav_{current_index-1}"))
                nav_buttons.append(InlineKeyboardButton(f"{current_index+1}/{total_tasks}", callback_data="quest_empty"))
                nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"favorite_nav_{current_index+1}"))
            
            # Добавляем все кнопки в одном ряду
            markup.row(*nav_buttons)
            
            # Получаем количество подсказок для задания
            hint_count = len(task.get("hint", []))
            if hint_count > 0:
                # Добавляем кнопку подсказки без указания количества шагов
                markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"hint_{world_id}_{cat_code}_{task_idx}_0"))
            
            # Добавляем кнопку удаления из избранного
            markup.add(InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"quest_favorite_{world_id}_{cat_code}_{task_idx}"))
            
            # Кнопка возврата - используем callback в зависимости от текущего режима
            back_callback = f"quest_favorite_world_{world_id}"
            markup.add(InlineKeyboardButton("↩️ Назад", callback_data=back_callback))
            
            bot.edit_message_media(
                media=InputMediaPhoto(task["photo"], caption=caption),
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=markup
            )
            
            logging.info(f"Обработан ответ на задачу из избранного: world={world_id}, cat={cat_code}, task={task_idx}, правильно: {is_correct}")
            return
            
    # Пытаемся удалить сообщение пользователя если сообщение не было обработано как ответ на избранное
    try:
        bot.delete_message(chat_id, message.message_id)
        logging.info(f"Сообщение {message.message_id} от пользователя {user_id} удалено")
    except Exception as e:
        # Если не удалось удалить сообщение, просто продолжаем работу
        logging.warning(f"Не удалось удалить сообщение {message.message_id} от пользователя {user_id}: {e}")
        
    # Сразу проверяем, есть ли в памяти данные о правильно решенных задачах
    task_already_solved = False
    current_task_key = None
    
    # Проверяем, если у пользователя есть текущая задача
    if user_id in user_data and 'current_task' in user_data[user_id]:
        current_task = user_data[user_id]['current_task']
        world_id = current_task.get('world_id')
        cat_code = current_task.get('cat_code')
        task_idx = current_task.get('task_idx')
        
        if world_id and cat_code is not None and task_idx is not None:
            current_task_key = f"{world_id}_{cat_code}_{task_idx}"
            
            # Проверяем, решена ли уже эта задача правильно
            if 'user_solutions' in user_data[user_id] and current_task_key in user_data[user_id]['user_solutions']:
                if user_data[user_id]['user_solutions'][current_task_key] == "correct":
                    task_already_solved = True
                    logging.info(f"Задача {current_task_key} уже была решена пользователем {user_id} ранее (из памяти)")
                    
            # Если не нашли в памяти, проверяем базу данных
            if not task_already_solved:
                try:
                    conn = sqlite3.connect('task_progress.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                        (user_id, str(world_id), cat_code, task_idx)
                    )
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result and result[0] == 1:
                        task_already_solved = True
                        # Добавляем в память для ускорения будущих проверок
                        if 'user_solutions' not in user_data[user_id]:
                            user_data[user_id]['user_solutions'] = {}
                        user_data[user_id]['user_solutions'][current_task_key] = "correct"
                        logging.info(f"Задача {current_task_key} уже была решена пользователем {user_id} ранее (из базы данных)")
                        
                        # ОТКЛЮЧАЕМ автоматическое удаление ответов для обычных заданий (не для домашних заданий)
                        # Даем пользователю возможность видеть результат и повторно решать одни и те же задачи
                        logging.info(f"Пользователь повторно ответил на уже решенную задачу {current_task_key}, но мы позволяем это для обычных задач")
                except Exception as e:
                    logging.error(f"Ошибка при проверке статуса задачи: {e}")
    
    try:
        # Проверяем, есть ли информация о текущей задаче у пользователя
        if user_id in user_data and "current_task" in user_data[user_id]:
            # Извлекаем данные о текущей задаче
            task_info = user_data[user_id]["current_task"]
            world_id = task_info["world_id"]
            cat_code = task_info["cat_code"]
            task_idx = task_info["task_idx"]
            
            # Получаем информацию о задаче
            world_challenge = challenge.get(str(world_id), {})
            category = world_challenge.get(cat_code, {"name": "Неизвестная категория", "tasks": []})
            tasks = category.get("tasks", [])
            
            if task_idx < 0 or task_idx >= len(tasks):
                bot.send_message(chat_id, "Ошибка: задача не найдена")
                return
            
            task = tasks[task_idx]
            correct_answer = str(task.get("answer", "")).strip()
            
            # Удаляем сообщение пользователя (если есть доступ)
            try:
                # Сохраняем ID сообщения для возможного использования в логах
                user_message_id = message.message_id
                
                # В этом месте сообщение пользователя может уже быть удалено
                # Безопасно пытаемся удалить его, игнорируя ошибки "сообщение не найдено"
                try:
                    bot.delete_message(chat_id, message.message_id)
                except Exception as delete_err:
                    if "message to delete not found" not in str(delete_err):
                        logging.error(f"Ошибка при удалении сообщения: {delete_err}")
                    # Если сообщение не найдено, просто продолжаем работу
            except Exception as e:
                logging.error(f"Ошибка при работе с сообщением пользователя: {e}")
            
            # Проверяем ответ пользователя - убираем лишние пробелы и переводим в нижний регистр
            user_answer = text.lower().strip()
            correct_answer_clean = correct_answer.lower().strip()
            
            # Проверяем точное совпадение
            is_correct = user_answer == correct_answer_clean
            
            # Проверяем отрицательные числа (например, "-17" и "17" с учётом минуса)
            if not is_correct and user_answer.replace('-', '', 1).isdigit() and correct_answer_clean.replace('-', '', 1).isdigit():
                # Если пользователь ввёл число без минуса, но правильный ответ отрицательный
                if user_answer.isdigit() and correct_answer_clean.startswith('-'):
                    is_correct = '-' + user_answer == correct_answer_clean
                # Если пользователь ввёл отрицательное число, но правильный ответ без минуса
                elif user_answer.startswith('-') and correct_answer_clean.isdigit():
                    is_correct = user_answer == '-' + correct_answer_clean
            
            # Если ответ не совпал, попробуем проверить числовой ответ
            if not is_correct:
                try:
                    # Проверяем, если это числа с разными форматами (например, "2.5" и "2,5")
                    user_num = user_answer.replace(',', '.').replace(' ', '')
                    correct_num = correct_answer_clean.replace(',', '.').replace(' ', '')
                    
                    # Проверяем, являются ли строки числами (учитывая возможные минусы)
                    if (user_num.replace('-', '', 1).replace('.', '', 1).isdigit() and 
                        correct_num.replace('-', '', 1).replace('.', '', 1).isdigit()):
                        user_float = float(user_num)
                        correct_float = float(correct_num)
                        is_correct = abs(user_float - correct_float) < 0.0001  # Допуск для сравнения чисел с плавающей точкой
                        
                        # Специальная проверка для случаев, когда ответы отличаются только знаком
                        if not is_correct and user_float == -correct_float:
                            logging.warning(f"Внимание: ответы отличаются только знаком: {user_float} и {correct_float}")
                except (ValueError, TypeError) as e:
                    # Если не удалось преобразовать в числа, оставляем is_correct = False
                    logging.debug(f"Не удалось сравнить как числа: {e}")
            
            # Логируем информацию о проверке ответа
            logging.info(f"Проверка ответа: пользователь ввел '{user_answer}', правильный ответ '{correct_answer_clean}', результат: {is_correct}")
            
            # Проверяем, была ли задача уже правильно решена ранее
            # ВАЖНАЯ ПРОВЕРКА: делаем ее ДО обновления статуса в базе
            conn = sqlite3.connect('task_progress.db')
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже запись для этой задачи
            cursor.execute(
                "SELECT status FROM task_progress WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                (user_id, str(world_id), cat_code, task_idx)
            )
            existing_record = cursor.fetchone()
            
            # Определяем текущий статус и переменную "задача уже была решена ранее"
            task_was_correct_before = False
            if existing_record and existing_record[0] == "correct":
                task_was_correct_before = True
                logging.info(f"Задача {world_id}_{cat_code}_{task_idx} уже была правильно решена ранее пользователем {user_id}")
            
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 13.0: Определяем новый статус ТОЛЬКО если задача решена верно
            # Если задача была решена ранее или решена верно сейчас - всегда "correct"
            # Неверный ответ НИКОГДА не меняет статус с "correct" на "wrong"
            if task_was_correct_before or is_correct:
                new_status = "correct"
            else:
                # Только если задача никогда не решалась верно, обновляем статус на "wrong"
                new_status = "wrong"
                
            # Логируем логику обновления статуса
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 13.0: Обновление статуса задачи {world_id}_{cat_code}_{task_idx}")
            logging.info(f"КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 13.0: task_was_correct_before={task_was_correct_before}, is_correct={is_correct}, new_status={new_status}")
            
            # Теперь обновляем базу данных в соответствии с новой логикой
            if existing_record:
                # Обновляем существующую запись
                cursor.execute(
                    "UPDATE task_progress SET status = ? WHERE user_id = ? AND challenge_num = ? AND cat_code = ? AND task_idx = ?",
                    (new_status, user_id, str(world_id), cat_code, task_idx)
                )
            else:
                # Создаем новую запись
                cursor.execute(
                    "INSERT INTO task_progress (user_id, challenge_num, cat_code, task_idx, status) VALUES (?, ?, ?, ?, ?)",
                    (user_id, str(world_id), cat_code, task_idx, new_status)
                )
            
            conn.commit()
            conn.close()
            
            try:
                # Получаем фото задания для любого исхода
                photo_url = task['photo']
                if not photo_url.startswith("http"):
                    photo_url = f"https://i.imgur.com/{photo_url}.jpeg"
                
                # Общие элементы интерфейса
                markup = InlineKeyboardMarkup(row_width=2)
                navigation_buttons = []
                total_tasks = len(tasks)
                
                if task_idx > 0:
                    navigation_buttons.append(InlineKeyboardButton("◀️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx-1}"))
                else:
                    navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
                    
                navigation_buttons.append(InlineKeyboardButton(f"{task_idx+1}/{total_tasks}", callback_data="no_action"))
                
                if task_idx < total_tasks - 1:
                    navigation_buttons.append(InlineKeyboardButton("▶️", callback_data=f"quest_task_{world_id}_{cat_code}_{task_idx+1}"))
                else:
                    navigation_buttons.append(InlineKeyboardButton(" ", callback_data="no_action"))
                
                markup.row(*navigation_buttons)
                # Получаем количество подсказок для задания
                hint_count = len(task.get("hint", []))
                if hint_count > 0:
                    # Добавляем кнопку подсказки
                    markup.add(InlineKeyboardButton("💡 Подсказка", callback_data=f"quest_solution_{world_id}_{cat_code}_{task_idx}"))
                
                # Получаем избранные задания пользователя
                favorites = get_user_favorites(user_id)
                is_favorite = any(f['challenge_num'] == str(world_id) and f['cat_code'] == cat_code and f['task_idx'] == task_idx for f in favorites)
                
                # Кнопка для добавления/удаления из избранного
                # is_favorite уже определен выше, используем существующее значение
                favorite_text = "🗑 Удалить из избранного" if is_favorite else "⭐️ Добавить в избранное"
                markup.add(InlineKeyboardButton(favorite_text, callback_data=f"quest_favorite_{world_id}_{cat_code}_{task_idx}"))
                
                # Кнопка возврата в меню выбора тем
                markup.add(InlineKeyboardButton("↩️ Назад", callback_data=f"quest_task_list_{world_id}"))
                
                # Используем переменную task_was_correct_before из предыдущей проверки выше в коде
                task_key = f"{world_id}_{cat_code}_{task_idx}"
                
                # Мы уже сделали проверку на правильность решения задачи ранее,
                # поэтому не повторяем эту проверку снова, а просто используем полученное значение
                
                # Если ответ верный или задача уже была решена правильно ранее - всегда показываем "Верно"
                if is_correct or task_was_correct_before or task_already_solved:
                    if is_correct and not task_was_correct_before and not task_already_solved:
                        logging.info(f"Пользователь {user_id} правильно решил задачу {world_id}_{cat_code}_{task_idx}")
                        
                        # Если задача решена верно впервые, сохраняем это в память
                        if 'user_solutions' not in user_data[user_id]:
                            user_data[user_id]['user_solutions'] = {}
                        user_data[user_id]['user_solutions'][f"{world_id}_{cat_code}_{task_idx}"] = "correct"
                    
                    # Всегда получаем статус "Верно" (даже если текущий ответ неверный, но задача ранее была решена верно)
                    status_text = "✅ Верно"
                    answer_text = ""
                    
                    # Добавляем правильный ответ если известен
                    if 'answer' in task:
                        answer_text = f"\n\nПравильный ответ: {task['answer']}"
                    
                    caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}"
                else:
                    logging.info(f"Пользователь {user_id} дал неверный ответ на задачу {world_id}_{cat_code}_{task_idx}")
                    
                    # Только если задача ранее не была решена правильно, показываем статус "Неверно"
                    status_text = "❌ Неверно"
                    answer_text = ""
                    
                    caption = f"№{world_id}\n{category['name']}\n{status_text}{answer_text}\n\nВведи ответ в чат:"
                
                # Обновляем сообщение в чате
                message_id = user_data[user_id].get('quest_message_id', None)
                
                # Мы уже проверили статус задачи выше и сформировали правильный caption
                # Теперь просто определяем, нужно ли обновлять сообщение
                
                # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ 16.0: Отключаем пропуск обновления сообщения для уже решенных задач
                # Теперь для обычных задач всегда обновляем сообщение с результатом проверки,
                # даже если задача была правильно решена ранее
                if False:  # Отключаем эту логику, но оставляем код для возможности восстановления
                    logging.info(f"Пропускаем обновление сообщения для {task_key} - задача уже решена")
                    
                    # Для уже решенных заданий просто тихо удаляем сообщение пользователя 
                    # и НЕ отправляем никаких дополнительных сообщений
                    # Это предотвратит дублирование сообщений с заданием в чате
                    logging.info(f"Задача {task_key} была решена ранее, не отправляем новое сообщение")
                    
                    # Не делаем никаких дополнительных действий
                    return
                
                # Обновляем сообщение, только если задача ещё не была правильно решена
                if message_id:
                    try:
                        # Вместо обновления существующего сообщения, отправляем новое 
                        # с тем же содержимым, если предыдущее сообщение не найдено
                        try:
                            bot.edit_message_media(
                                media=InputMediaPhoto(photo_url, caption=caption),
                                chat_id=chat_id,
                                message_id=message_id,
                                reply_markup=markup
                            )
                        except Exception as edit_err:
                            if "message to edit not found" in str(edit_err) or "message to be edited" in str(edit_err):
                                # Отправляем новое сообщение, если предыдущее не найдено
                                new_message = bot.send_photo(
                                    chat_id=chat_id,
                                    photo=photo_url,
                                    caption=caption,
                                    reply_markup=markup
                                )
                                # Сохраняем ID нового сообщения для последующих обновлений
                                if user_id not in user_data:
                                    user_data[user_id] = {}
                                user_data[user_id]['quest_message_id'] = new_message.message_id
                                logging.info(f"Отправлено новое сообщение с задачей, message_id={new_message.message_id}")
                            elif "message is not modified" not in str(edit_err):
                                # Логируем, но игнорируем ошибку, если содержимое не изменилось
                                logging.error(f"Ошибка при обновлении сообщения: {edit_err}")
                            # Если сообщение не изменилось, просто продолжаем
                    except Exception as e:
                        logging.error(f"Критическая ошибка при работе с сообщением: {e}")
                        # В случае критической ошибки пытаемся отправить информационное сообщение
                        try:
                            bot.send_message(
                                chat_id=chat_id,
                                text="Возникла проблема при отображении задания. Пожалуйста, вернитесь в список заданий и попробуйте снова."
                            )
                        except:
                            pass
            except Exception as e:
                logging.error(f"Ошибка при обработке ответа: {e}")
                # При ошибке, отправляем поясняющее сообщение
                try:
                    bot.send_message(
                        chat_id=chat_id,
                        text="Произошла ошибка при обработке ответа. Попробуйте вернуться в задание заново."
                    )
                except Exception as send_err:
                    logging.error(f"Не удалось отправить сообщение об ошибке: {send_err}")
        else:
            # Если не ожидается ответ на задачу, игнорируем сообщение
            # Не отправляем никаких сообщений, просто логируем
            logging.info(f"Получено текстовое сообщение от пользователя {user_id}, но ответ на задачу не ожидался")
    except Exception as e:
        logging.error(f"Ошибка при обработке текстового сообщения от user_id={user_id}: {e}")
        bot.send_message(
            chat_id=chat_id,
            text="Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте еще раз."
        )
# 