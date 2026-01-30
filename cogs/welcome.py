import discord
from discord.ext import commands
from easy_pil import Editor, load_image, Font, Canvas
import io
import os
import config

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_welcome_card(self, member: discord.Member):
        # Загрузка фона из конфига
        if os.path.exists(config.WELCOME_BG_PATH):
            background = Editor(config.WELCOME_BG_PATH).resize((1100, 500))
        else:
            background = Editor(Canvas((1100, 500), color="#1e1e2e"))

        # Обработка аватара
        try:
            avatar_url = member.display_avatar.url
            avatar_image = load_image(avatar_url)
        except Exception as e:
            print(f" [!] Не удалось загрузить аватар для {member}: {e}")
            avatar_image = load_image("https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png")

        profile = Editor(avatar_image).resize((250, 250)).circle_image()
        background.paste(profile, (425, 70))
        
        font_big = Font.poppins(size=60, variant="bold")
        font_small = Font.poppins(size=40, variant="regular")

        background.text((550, 360), f"Welcome, {member.name}!", color="#00ffff", font=font_big, align="center")
        
        member_count = len(member.guild.members)
        background.text((550, 430), f"You are member #{member_count}", color="#ff00ff", font=font_small, align="center")

        file_out = io.BytesIO()
        background.save(file_out, "PNG")
        file_out.seek(0)
        
        return discord.File(file_out, filename="welcome.png")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(config.WELCOME_CHANNEL_ID)
        if not channel:
            print(f" [!] Канал для приветствий (ID: {config.WELCOME_CHANNEL_ID}) не найден.")
            return

        try:
            file = await self.generate_welcome_card(member)
            await channel.send(f"Добро пожаловать на сервер, {member.mention}!", file=file)
        except Exception as e:
            print(f" [!] Ошибка при отправке приветствия: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
