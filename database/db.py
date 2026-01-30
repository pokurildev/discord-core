import aiosqlite
import config

def get_db():
    return aiosqlite.connect(config.DB_PATH)

async def create_tables():
    async with get_db() as db:
        # 1. Создание таблицы users, если её нет
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                warns INTEGER DEFAULT 0
            )
        """)
        
        # 2. Авто-миграция: добавляем колонку 'warns', если она отсутствует (для старых баз данных)
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = [row[1] for row in await cursor.fetchall()]
            if "warns" not in columns:
                print(" [DB] Миграция: Добавление колонки 'warns' в таблицу 'users'...")
                await db.execute("ALTER TABLE users ADD COLUMN warns INTEGER DEFAULT 0")
        
        # 3. Другие таблицы
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER
            )
        """)
        
        await db.commit()
        print(" [DB] База данных успешно инициализирована.")
