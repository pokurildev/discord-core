import discord
from discord.ext import commands
from discord import app_commands
from easy_pil import Editor, load_image, Font, Canvas
import io
import os
import random
import time
import config
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
            await message.channel.send(f"🎉 Поздравляем, {message.author.mention}! Вы достигли **уровня {new_level}**!")

    @app_commands.command(name="rank", description="Посмотреть свой текущий уровень и ранг")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        
        async with get_db() as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (member.id,)) as cursor:
                row = await cursor.fetchone()
                user_xp = row[0] if row else 0
            
            async with db.execute("SELECT COUNT(*) FROM users WHERE xp > ?", (user_xp,)) as cursor:
                rank_row = await cursor.fetchone()
                leaderboard_rank = (rank_row[0] + 1) if row else "N/A"

        level, current_xp = self.calculate_level(user_xp)
        next_level_xp = self.get_xp_for_level(level)
        percentage = min(100, max(5, int((current_xp / next_level_xp) * 100)))

        background = Editor(Canvas((900, 250), color="#1e1e2e"))
        if os.path.exists(config.WELCOME_BG_PATH):
            bg_image = Editor(config.WELCOME_BG_PATH).resize((900, 250), crop=True)
            background.paste(bg_image, (0, 0))

        avatar_image = load_image(str(member.display_avatar.url))
        profile = Editor(avatar_image).resize((180, 180)).circle_image()
        background.paste(profile, (35, 35))

        font_main = Font.poppins(size=40, variant="bold")
        font_sub = Font.poppins(size=30, variant="regular")

        background.text((250, 50), str(member), color="#00ffff", font=font_main)
        background.text((850, 50), f"RANK #{leaderboard_rank}", color="#ff00ff", font=font_sub, align="right")
        background.text((850, 110), f"LEVEL {level}", color="#00ffff", font=font_sub, align="right")

        background.rectangle((250, 180), width=600, height=40, fill="#444455", radius=20)
        bar_width = int(600 * (percentage / 100))
        background.rectangle((250, 180), width=bar_width, height=40, fill="#00ffff", radius=20)
        
        background.text((550, 185), f"{current_xp} / {next_level_xp} XP", color="#ffffff", font=Font.poppins(size=25), align="center")

        file_out = io.BytesIO()
        background.save(file_out, format="PNG")
        file_out.seek(0)
        
        file = discord.File(file_out, filename="rank.png")
        await interaction.response.send_message(file=file)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
