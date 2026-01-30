import discord
from discord.ext import commands
from discord import app_commands
import datetime
import io
import config
from config import UIConfig

class TicketModal(discord.ui.Modal, title="✨ Создание нового тикета"):
    reason = discord.ui.TextInput(
        label="Причина обращения",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите вашу проблему максимально подробно, чтобы мы могли помочь быстрее...",
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Новый стиль — уведомление о создании
        guild = interaction.guild
        user = interaction.user
        
        category = discord.utils.get(guild.categories, name=config.TICKET_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(config.TICKET_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        admin_role = discord.utils.get(guild.roles, name=config.ADMIN_ROLE_NAME)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"🎫-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Тикет пользователя {user} | ID: {user.id}"
        )

        # Новый стиль — приветственное сообщение в тикете
        embed = discord.Embed(
            title="Система Поддержки • Тикет Открыт",
            description=(
                f"Здравствуйте, {user.mention}!\n\n"
                "Ваше обращение было успешно зарегистрировано. Администрация сервера уведомлена и свяжется с вами в ближайшее время.\n\n"
                f"**Ваша причина:**\n> {self.reason.value}\n\n"
                "** Правила тикета:**\n"
                "• Не спамьте тегами администрации.\n"
                "• Подготовьте скриншоты, если они необходимы.\n"
                "• После решения проблемы закройте тикет кнопкой ниже."
            ),
            color=UIConfig.CYAN,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Служба поддержки", icon_url=UIConfig.ICON_TICKET)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=UIConfig.FOOTER)
        
        view = TicketControlView()
        await channel.send(f"{user.mention} | {admin_role.mention if admin_role else ''}", embed=embed, view=view)
        
        # Эфемерное подтверждение
        confirm_embed = discord.Embed(
            description=f"✅ **Ваш тикет успешно создан:** {channel.mention}",
            color=UIConfig.SUCCESS
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Закрыть обращение", style=discord.ButtonStyle.danger, emoji=None, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Новый стиль — процесс закрытия
        await interaction.response.send_message("⌛ **Генерация архива и закрытие тикета...**", ephemeral=True)
        
        channel = interaction.channel
        
        transcript = f"--- ТРАНСКРИПТ ТИКЕТА: {channel.name} ---\n"
        transcript += f"Сервер: {interaction.guild.name}\n"
        transcript += f"Закрыл: {interaction.user} ({interaction.user.id})\n"
        transcript += f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        transcript += "-" * 40 + "\n\n"
        
        async for message in channel.history(limit=None, oldest_first=True):
            time_str = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript += f"[{time_str}] {message.author}: {message.content}\n"
            if message.attachments:
                for att in message.attachments:
                    transcript += f" [ФАЙЛ: {att.url}]\n"

        file_data = io.BytesIO(transcript.encode("utf-8"))
        file = discord.File(file_data, filename=f"archive-{channel.name}.txt")
        
        log_channel = interaction.guild.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Архив Тикета",
                description=f"**Канал:** `{channel.name}`\n**Закрыл:** {interaction.user.mention}\n**ID:** `{interaction.user.id}`",
                color=UIConfig.INFO,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            log_embed.set_thumbnail(url=UIConfig.ICON_SHIELD)
            log_embed.set_footer(text=UIConfig.FOOTER)
            await log_channel.send(embed=log_embed, file=file)

        await channel.delete(reason=f"Тикет закрыт пользователем {interaction.user}")

class PersistentTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Открыть тикет", style=discord.ButtonStyle.primary, emoji=None, custom_id="create_ticket_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_panel", description="Отправить панель создания тикетов (Админ)")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        # Новый стиль — главная панель тикетов
        embed = discord.Embed(
            title="Центр Поддержки Пользователей",
            description=(
                "Нужна помощь администрации или вы хотите сообщить о нарушении?\n\n"
                "**Как это работает:**\n"
                "1️⃣ Нажмите на кнопку **'Открыть тикет'** ниже.\n"
                "2️⃣ Укажите причину обращения в появившемся окне.\n"
                "3️⃣ Бот создаст для вас **персональный канал**, видимый только вам и модераторам.\n\n"
                "*Пожалуйста, будьте вежливы и четко формулируйте свои мысли.*"
            ),
            color=UIConfig.CYAN
        )
        embed.set_image(url="https://i.imgur.com/kP8UvS1.png") # Заглушка для баннера, если захотите добавить
        embed.set_author(name="Официальная поддержка сервера", icon_url=UIConfig.ICON_SHIELD)
        embed.set_footer(text=UIConfig.FOOTER)
        
        await interaction.response.send_message("✅ Панель успешно отправлена в этот канал.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=PersistentTicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
