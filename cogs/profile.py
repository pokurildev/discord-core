import discord
from discord.ext import commands
from discord import app_commands
from easy_pil import Editor, load_image, Font, Canvas
import io
import os
import time
import datetime
import config
from config import UIConfig
from database.db import get_db

class ProfileView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Забрать Daily", style=discord.ButtonStyle.success, emoji=None)
    async def daily(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Новый стиль — ежедневная награда
        if interaction.user.id != self.user_id:
            msg = discord.Embed(description="**Это не ваш профиль!** Вы не можете забрать чужую награду.", color=UIConfig.ERROR)
            await interaction.response.send_message(embed=msg, ephemeral=True)
            return

        current_time = int(time.time())
        day_seconds = 86400

        async with get_db() as db:
            async with db.execute("SELECT balance, last_daily FROM users WHERE user_id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()

            if not row:
                await db.execute("INSERT INTO users (user_id, balance, last_daily) VALUES (?, ?, ?)", 
                               (self.user_id, config.DAILY_REWARD, current_time))
                await db.commit()
                reward = config.DAILY_REWARD
            else:
                balance, last_daily = row
                if current_time - last_daily < day_seconds:
                    remaining = day_seconds - (current_time - last_daily)
                    hours = remaining // 3600
                    minutes = (remaining % 3600) // 60
                    
                    wait_embed = discord.Embed(
                        title="Ежедневная награда",
                        description=f"Вы уже забирали бонус сегодня!\nВернитесь через **{hours}ч. {minutes}м.**",
                        color=UIConfig.WARNING
                    )
                    wait_embed.set_footer(text=UIConfig.FOOTER)
                    await interaction.response.send_message(embed=wait_embed, ephemeral=True)
                    self.stop()
                    return

                reward = config.DAILY_REWARD
                new_balance = balance + reward
                await db.execute("UPDATE users SET balance = ?, last_daily = ? WHERE user_id = ?", 
                               (new_balance, current_time, self.user_id))
                await db.commit()

        success_embed = discord.Embed(
            title="💰 Награда Получена!",
            description=f"Вы успешно забрали ежедневный бонус в размере ```ansi\n\u001b[0;36m{reward} монет\u001b[0m\n```",
            color=UIConfig.SUCCESS,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        success_embed.set_thumbnail(url=UIConfig.ICON_COIN)
        success_embed.set_footer(text=UIConfig.FOOTER)
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    @discord.ui.button(label="Лидерборд", style=discord.ButtonStyle.primary, emoji=None)
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Новый стиль — лидерборд
        async with get_db() as db:
            async with db.execute("SELECT user_id, xp FROM users ORDER BY xp DESC LIMIT 10") as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("**Лидерборд пока пуст.** Станьте первым!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Топ-10 Игроков Сервера",
            color=UIConfig.MAGENTA,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_thumbnail(url=UIConfig.ICON_TROPHY)
        
        description = ""
        for i, (uid, xp) in enumerate(rows, 1):
            user = self.bot.get_user(uid)
            user_str = f"<@{uid}>" if not user else f"**{user.name}**"
            
            # Эмодзи для мест
            medal = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            description += f"{medal} {user_str} — `{xp}` XP\n"
        
        embed.description = description
        embed.set_footer(text=UIConfig.FOOTER)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Мои роли", style=discord.ButtonStyle.secondary, emoji=None)
    async def my_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Новый стиль — список ролей
        user_roles = [role.name for role in interaction.user.roles]
        shop_roles = [data["role_name"] for data in config.SHOP_ITEMS.values()]
        
        owned_shop_roles = [role for role in user_roles if role in shop_roles]
        
        if not owned_shop_roles:
            fail_embed = discord.Embed(
                description="**У вас пока нет купленных ролей из магазина.** Посетите `/shop`!",
                color=UIConfig.ERROR
            )
            await interaction.response.send_message(embed=fail_embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="Ваши Коллекционные Роли",
            description="\n".join([f"• **{role}**" for role in owned_shop_roles]),
            color=UIConfig.CYAN
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=UIConfig.FOOTER)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_xp_for_level(self, level):
        if level < 0: return 0
        return 5 * (level ** 2) + 50 * level + 100

    def calculate_level(self, total_xp):
        lvl = 0
        while total_xp >= self.get_xp_for_level(lvl):
            total_xp -= self.get_xp_for_level(lvl)
            lvl += 1
        return lvl, total_xp

    async def create_rank_card(self, member, user_xp, rank):
        level, current_xp = self.calculate_level(user_xp)
        next_level_xp = self.get_xp_for_level(level)
        percentage = min(100, max(5, int((current_xp / next_level_xp) * 100)))

        # Цвета из конфига
        accent_color = "#00ffff"
        magenta_color = "#ff00ff"

        background = Editor(Canvas((900, 250), color="#1e1e2e"))
        if os.path.exists(config.WELCOME_BG_PATH):
            bg_image = Editor(config.WELCOME_BG_PATH).resize((900, 250), crop=True)
            background.paste(bg_image, (0, 0))

        avatar_image = load_image(str(member.display_avatar.url))
        profile_img = Editor(avatar_image).resize((180, 180)).circle_image()
        background.paste(profile_img, (35, 35))

        font_main = Font.poppins(size=40, variant="bold")
        font_sub = Font.poppins(size=30, variant="regular")

        background.text((250, 50), str(member.name), color=accent_color, font=font_main)
        background.text((850, 50), f"RANK #{rank}", color=magenta_color, font=font_sub, align="right")
        background.text((850, 110), f"LEVEL {level}", color=accent_color, font=font_sub, align="right")

        background.rectangle((250, 180), width=600, height=40, fill="#444455", radius=20)
        bar_width = int(600 * (percentage / 100))
        background.rectangle((250, 180), width=bar_width, height=40, fill=accent_color, radius=20)
        
        background.text((550, 185), f"{current_xp} / {next_level_xp} XP", color="#ffffff", font=Font.poppins(size=25), align="center")

        file_out = io.BytesIO()
        background.save(file_out, "PNG")
        file_out.seek(0)
        return discord.File(file_out, filename="profile.png")

    @app_commands.command(name="profile", description="Посмотреть свой личный кабинет (Premium UI)")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        # Новый стиль — эмбед профиля
        member = member or interaction.user
        await interaction.response.defer()

        async with get_db() as db:
            async with db.execute("SELECT balance, xp, warns FROM users WHERE user_id = ?", (member.id,)) as cursor:
                row = await cursor.fetchone()
                balance, xp, warns = row if row else (0, 0, 0)
            
            async with db.execute("SELECT COUNT(*) FROM users WHERE xp > ?", (xp,)) as cursor:
                rank_row = await cursor.fetchone()
                rank = (rank_row[0] + 1) if row else "N/A"

        file = await self.create_rank_card(member, xp, rank)
        
        embed = discord.Embed(
            title=f"Персональный Кабинет • {member.display_name}",
            color=UIConfig.CYAN,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Информация о профиле", icon_url=UIConfig.ICON_ADMIN)
        embed.set_image(url="attachment://profile.png")
        
        embed.add_field(name="💰 Текущий Баланс", value=f"```ansi\n\u001b[0;36m{balance} монет\u001b[0m\n```", inline=True)
        embed.add_field(name=" Предупреждения", value=f"```ansi\n\u001b[0;31m{warns}\u001b[0m\n```", inline=True)
        embed.add_field(name="Дата Входа", value=f"• <t:{int(member.joined_at.timestamp())}:D>\n• <t:{int(member.joined_at.timestamp())}:R>", inline=True)
        
        embed.set_footer(text=UIConfig.FOOTER)
        
        view = ProfileView(self.bot, member.id)
        await interaction.followup.send(embed=embed, file=file, view=view)

async def setup(bot):
    await bot.add_cog(Profile(bot))
