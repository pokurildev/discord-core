import discord
from discord.ext import commands
from discord import app_commands
import random
import time
import datetime
import config
from config import UIConfig
from database.db import get_db

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {} # {user_id: last_xp_time}

    def get_xp_for_level(self, level):
        if level < 0: return 0
        return 5 * (level ** 2) + 50 * level + 100

    def calculate_level(self, total_xp):
        lvl = 0
        while total_xp >= self.get_xp_for_level(lvl):
            total_xp -= self.get_xp_for_level(lvl)
            lvl += 1
        return lvl, total_xp

    async def update_user_xp(self, user_id, xp_to_add):
        async with get_db() as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                
            if row:
                new_xp = row[0] + xp_to_add
                await db.execute("UPDATE users SET xp = ? WHERE user_id = ?", (new_xp, user_id))
            else:
                new_xp = xp_to_add
                await db.execute("INSERT INTO users (user_id, xp) VALUES (?, ?)", (user_id, new_xp))
            
            await db.commit()
            return new_xp

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        current_time = time.time()

        last_time = self.xp_cooldown.get(user_id, 0)
        if current_time - last_time < 60:
            return

        xp_gain = random.randint(10, 20)
        old_xp_row = 0
        
        async with get_db() as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row: old_xp_row = row[0]

        new_total_xp = await self.update_user_xp(user_id, xp_gain)
        self.xp_cooldown[user_id] = current_time

        old_level, _ = self.calculate_level(old_xp_row)
        new_level, _ = self.calculate_level(new_total_xp)

        if new_level > old_level:
            # Новый стиль — уведомление о новом уровне
            level_embed = discord.Embed(
                title="Новый Уровень Достигнут!",
                description=(
                    f"Поздравляем, {message.author.mention}!\n\n"
                    f"Вы перешли на новый этап развития.\n"
                    f"Теперь ваш уровень: ```ansi\n\u001b[0;36m{new_level}\u001b[0m\n```"
                ),
                color=UIConfig.CYAN,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            level_embed.set_author(name="Система Прогресса", icon_url=UIConfig.ICON_TROPHY)
            level_embed.set_thumbnail(url=message.author.display_avatar.url)
            level_embed.set_footer(text=UIConfig.FOOTER)
            
            await message.channel.send(embed=level_embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
