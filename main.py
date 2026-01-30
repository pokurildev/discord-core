import discord
from discord.ext import commands
import os
import config
from database.db import create_tables

class MyBot(commands.Bot):
    def __init__(self):
        # Включаем все намерения (Intents)
        intents = discord.Intents.all()
        # Префикс для текстовых команд (нужен для !sync)
        super().__init__(command_prefix=config.PREFIX, intents=intents)

    async def setup_hook(self):
        # 1. База данных
        await create_tables()
        
        # 2. Загрузка когов
        print("--- Загрузка расширений ---")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f" [+] Загружен ког: {filename}")
                except Exception as e:
                    print(f" [!] Ошибка при загрузке {filename}: {e}")
        
        # 3. Регистрация View (для кнопок, чтобы работали после рестарта)
        try:
            from cogs.tickets import PersistentTicketView, TicketControlView
            self.add_view(PersistentTicketView())
            self.add_view(TicketControlView())
        except Exception as e:
            print(f" [!] Не удалось загрузить Ticket Views (возможно, модуль отключен): {e}")

    async def on_ready(self):
        print("---------------------------")
        print(f" [!] Бот запущен как {self.user} (ID: {self.user.id})")
        print("---------------------------")

# Создаем экземпляр бота
bot = MyBot()

# --- МАГИЧЕСКАЯ КОМАНДА ДЛЯ МГНОВЕННОГО ПОЯВЛЕНИЯ СЛЭШ-КОМАНД ---
@bot.command()
@commands.is_owner()
async def sync(ctx, spec: str = None):
    print(f" [!] Синхронизация для {ctx.guild.name} (режим: {spec or 'local'})...")
    async with ctx.typing():
        if spec == "global":
            # Глобальная синхронизация (может занять до часа)
            synced = await bot.tree.sync()
            await ctx.send(f"✅ Глобальная синхронизация завершена ({len(synced)} команд).")
        elif spec == "clear":
            # Удаление локальных команд сервера
            bot.tree.clear_commands(guild=ctx.guild)
            await bot.tree.sync(guild=ctx.guild)
            await ctx.send("🧹 Локальные команды сервера очищены.")
        else:
            # Мгновенная синхронизация для текущего сервера (копирование глобальных)
            bot.tree.copy_global_to(guild=ctx.guild)
            synced = await bot.tree.sync(guild=ctx.guild)
            await ctx.send(f" Мгновенная синхронизация: {len(synced)} команд теперь доступны на этом сервере.")

# Запуск
if __name__ == "__main__":
    bot.run(config.TOKEN)