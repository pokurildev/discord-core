import discord
from discord.ext import commands
from easy_pil import Editor, load_image, Font, Canvas
import io
import os

# Константы (можно вынести в .env или базу данных позже)
WELCOME_CHANNEL_ID = 123456789012345678  # ЗАМЕНИТЕ НА ВАШ ID КАНАЛА
BG_PATH = os.path.join("assets", "welcome_bg.png")

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def generate_welcome_card(self, member: discord.Member):
        # Загрузка фона
        if os.path.exists(BG_PATH):
            background = Editor(BG_PATH).resize((1100, 500))
        else:
            # Фолбэк на пустой темный холст, если файла нету
            background = Editor(Canvas((1100, 500), color="#1e1e2e"))

        # Обработка аватара
        try:
            # Пытаемся загрузить аватар пользователя
            avatar_url = member.display_avatar.url
            avatar_image = load_image(avatar_url)
        except Exception as e:
            print(f" [!] Не удалось загрузить аватар для {member}: {e}")
            # Фолбэк на дефолтную картинку (можно заменить на свой файл)
            avatar_image = load_image("https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png")

        profile = Editor(avatar_image).resize((250, 250)).circle_image()
        
        # Наложение аватара
        background.paste(profile, (425, 70))
        
        # Настройка шрифтов (используем стандартные, если нет своих)
        # Примечание: easy-pil может требовать путь к .ttf файлу для кастомных шрифтов
        font_big = Font.poppins(size=60, variant="bold")
        font_small = Font.poppins(size=40, variant="regular")

        # Текст приветствия
        background.text((550, 360), f"Welcome, {member.name}!", color="#00ffff", font=font_big, align="center")
        
        # Текст с номером участника
        member_count = len(member.guild.members)
        background.text((550, 430), f"You are member #{member_count}", color="#ff00ff", font=font_small, align="center")

        # Сохранение в байтовую строку для отправки в Discord
        file_out = io.BytesIO()
        background.save(file_out, format="PNG")
        file_out.seek(0)
        
        return discord.File(file_out, filename="welcome.png")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            print(f" [!] Канал для приветствий (ID: {WELCOME_CHANNEL_ID}) не найден.")
            return

        print(f" [+] {member} присоединился к серверу. Генерирую карточку...")
        
        try:
            file = await self.generate_welcome_card(member)
            await channel.send(f"Добро пожаловать на сервер, {member.mention}!", file=file)
            print(f" [✓] Приветствие для {member} успешно отправлено.")
        except Exception as e:
            print(f" [!] Ошибка при отправке приветствия: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
