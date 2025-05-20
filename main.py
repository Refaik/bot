from instance import bot
from callBack import *
import logging
import sys
from logging.handlers import RotatingFileHandler

# Импорт нужных функций из callBack
from callBack import init_task_progress_db, init_quest_db, load_user_data, init_quiz_db, init_cards_db, init_favorites_db

# Функция настройки логирования (перенесена из logger.py)
def setup_logging():
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

# Настройка логирования
setup_logging()

if __name__ == "__main__":
    try:
        print("Бот запускается...")
        
        # Инициализируем квест
        init_quest_db()
        
        # Инициализируем базу данных task_progress
        init_task_progress_db()
        print("База данных прогресса задач инициализирована")
        
        # Инициализируем базу данных избранного
        init_favorites_db()
        print("База данных избранного инициализирована (данные сохраняются между перезапусками)")
        
        # Инициализируем базу данных quiz
        init_quiz_db()
        
        # Инициализируем базу данных cards
        init_cards_db()
        
        # Загружаем пользовательские данные
        load_user_data()
        print("Данные пользователей загружены (включая группы карточек)")
        
        # ВАЖНО: Удалено отключение функциональности избранного!
        # Теперь функциональность избранного включена по умолчанию
        logging.info("Функциональность избранного включена")
        
        # Запускаем бота
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        logging.error(f"Произошла критическая ошибка: {e}")
        print(f"Произошла ошибка: {e}")
    finally:
        print("Бот остановлен.")