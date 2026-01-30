import os
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PREFIX = "!"

# ID Каналов (ЗАМЕНИТЬ НА РЕАЛЬНЫЕ ID)
LOG_CHANNEL_ID = 1466841045584314511 # Канал для аудит-логов и транскриптов
WELCOME_CHANNEL_ID = 1466128329911570436 # Канал для приветственных карточек
HUB_CHANNEL_ID = 1466843088021622805 # Голосовой канал "➕ Создать комнату"
CATEGORY_VOICE_ID = 1466128329911570437 # Категория для временных голосовых каналов

# Настройки Модерации
BAD_WORDS = {"скам", "реклама", "токсик"}

# Настройки Тикетов
TICKET_CATEGORY_NAME = "Tickets"
ADMIN_ROLE_NAME = "Admin"

# Настройки экономики
DAILY_REWARD = 100

# Обновленная структура магазина
# Format: "Ключ": {"price": Цена, "role_name": "Имя роли", "desc": "Описание", "color": HEX_цвет, "image": "URL_картинки"}
SHOP_ITEMS = {
    "Vip": {
        "price": 500, 
        "role_name": "Vip", 
        "desc": "✨ **Базовый статус**\n• Доступ к VIP чату\n• Возможность менять никнейм\n• Иконка короны",
        "color": 0x9b59b6, # Фиолетовый
        "image": "https://cdn-icons-png.flaticon.com/512/6941/6941697.png" 
    },
    "Premium": {
        "price": 1500, 
        "role_name": "Premium", 
        "desc": "💎 **Продвинутый статус**\n• Все бонусы VIP\n• Приоритетная поддержка\n• Доступ к голосовым комнатам высокого качества",
        "color": 0x3498db, # Синий
        "image": "https://cdn-icons-png.flaticon.com/512/3665/3665909.png"
    },
    "Legend": { 
        "price": 5000, 
        "role_name": "Legend", 
        "desc": "👑 **Элитный статус**\n• Уникальный цвет ника\n• Право создавать свои каналы\n• Иммунитет к медленному режиму",
        "color": 0xf1c40f, # Золотой
        "image": "https://cdn-icons-png.flaticon.com/512/5406/5406813.png"
    }
}

# Пути к ресурсам
ASSETS_DIR = "assets"
WELCOME_BG_PATH = os.path.join(ASSETS_DIR, "welcome_bg.png")

# Настройки базы данных
DB_PATH = os.path.join("database", "bot_database.db")

# --- СТИЛЬ И ДИЗАЙН (UI 2025) ---
class UIConfig:
    # Цветовая палитра
    CYAN = 0x00ffff     # Основной неон
    MAGENTA = 0xff00ff  # Акцент
    SUCCESS = 0x2ecc71  # Зеленый
    WARNING = 0xf39c12  # Оранжевый
    ERROR = 0xe74c3c    # Красный
    INFO = 0x5865f2     # Blurple (Discord)
    DARK = 0x1e1e2e     # Фон компонент

    # Иконки (PNG с прозрачным фоном)
    ICON_SHIELD = "https://cdn-icons-png.flaticon.com/512/3135/3135754.png"
    ICON_COIN = "https://cdn-icons-png.flaticon.com/512/1490/1490844.png"
    ICON_TROPHY = "https://cdn-icons-png.flaticon.com/512/3112/3112946.png"
    ICON_TICKET = "https://cdn-icons-png.flaticon.com/512/1550/1550614.png"
    ICON_GIFT = "https://cdn-icons-png.flaticon.com/512/1169/1169971.png"
    ICON_WARN = "https://cdn-icons-png.flaticon.com/512/564/564619.png"
    ICON_WELCOME = "https://cdn-icons-png.flaticon.com/512/1269/1269558.png"
    # ICON_ADMIN = "https://img.icons8.com/ios-glyphs/512/ffffff/administrator-male.png"
    ICON_ADMIN = "https://img.icons8.com/?size=100&id=uWOKQW4wPHn6&format=png&color=ffffff"

    # Текстовые шаблоны
    FOOTER = "• dev-bot • v2.1 • Dark Neon Premium"
