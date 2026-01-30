import aiosqlite
import os

DB_PATH = os.path.join("database", "bot_database.db")

async def get_db():
    return await aiosqlite.connect(DB_PATH)

async def create_tables():
    async with await get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER
            )
        """)
        
        await db.commit()
        print(" [DB] Таблицы 'users' и 'guild_config' успешно проверены/созданы.")
