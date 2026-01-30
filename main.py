import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database.db import create_tables

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Создание таблиц в БД при запуске
        await create_tables()
        
        # Подгрузка когов из папки /cogs
        print("--- Загрузка расширений ---")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f" [+] Загружен ког: {filename}")
                except Exception as e:
                    print(f" [!] Ошибка при загрузке {filename}: {e}")
        
        # Регистрация персистентных View (для тикетов)
        from cogs.tickets import PersistentTicketView, TicketControlView
        self.add_view(PersistentTicketView())
        self.add_view(TicketControlView())
        
        # Синхронизация слэш-команд
        print("--- Синхронизация команд ---")
        try:
            synced = await self.tree.sync()
            print(f" [✓] Синхронизировано команд: {len(synced)}")
        except Exception as e:
            print(f" [!] Ошибка синхронизации: {e}")

    async def on_ready(self):
        print("---------------------------")
        print(f" [!] Бот запущен как {self.user} (ID: {self.user.id})")
        print("---------------------------")

if __name__ == "__main__":
    bot = MyBot()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print(" [!] Ошибка: DISCORD_TOKEN не найден в .env")
