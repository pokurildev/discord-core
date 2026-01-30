import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

# ID Каналов (ЗАМЕНИТЬ НА РЕАЛЬНЫЕ ID)
LOG_CHANNEL_ID = 1466841045584314511 # Канал для аудит-логов и транскриптов
WELCOME_CHANNEL_ID = 1466128329911570436 # Канал для приветственных карточек
HUB_CHANNEL_ID = 1466128329911570441 # Голосовой канал "➕ Создать комнату"
CATEGORY_VOICE_ID = 1466128329911570437 # Категория для временных голосовых каналов

# Настройки Модерации
BAD_WORDS = {"скам", "реклама", "токсик"}

# Настройки Тикетов
TICKET_CATEGORY_NAME = "Tickets"
ADMIN_ROLE_NAME = "Admin"

# Пути к ресурсам
ASSETS_DIR = "assets"
WELCOME_BG_PATH = os.path.join(ASSETS_DIR, "welcome_bg.png")

# Настройки базы данных
DB_PATH = os.path.join("database", "bot_database.db")
