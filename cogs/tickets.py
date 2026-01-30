import discord
from discord.ext import commands
from discord import app_commands
import datetime
import io

# Конфигурация (замените на свои ID)
LOG_CHANNEL_ID = 123456789012345678 

class TicketModal(discord.ui.Modal, title="Создание тикета"):
    reason = discord.ui.TextInput(
        label="Причина обращения",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите вашу проблему максимально подробно...",
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        # Поиск или создание категории
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        # Настройка прав (приватность)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Добавляем доступ для админов (если есть роль Admin)
        admin_role = discord.utils.get(guild.roles, name="Admin")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Создание канала
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites
        )

        # Отправка начального сообщения
        embed = discord.Embed(
            title="🎫 Тикет открыт",
            description=f"Здравствуйте, {user.mention}!\nАдминистрация скоро свяжется с вами.\n\n**Ваша причина:**\n{self.reason.value}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        view = TicketControlView()
        await channel.send(f"{user.mention} | {admin_role.mention if admin_role else ''}", embed=embed, view=view)
        
        await interaction.response.send_message(f"Тикет создан: {channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Закрыть тикет", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Создаю транскрипт и закрываю канал...", ephemeral=True)
        
        channel = interaction.channel
        
        # Генерация транскрипта
        transcript = f"--- Транскрипт тикета: {channel.name} ---\n"
        transcript += f"Сгенерировано: {datetime.datetime.now()}\n\n"
        
        async for message in channel.history(limit=None, oldest_first=True):
            time_str = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript += f"[{time_str}] {message.author}: {message.content}\n"
            if message.attachments:
                for att in message.attachments:
                    transcript += f" [Вложение: {att.url}]\n"

        # Сохранение в файл
        file_data = io.BytesIO(transcript.encode("utf-8"))
        file = discord.File(file_data, filename=f"{channel.name}-logs.txt")
        
        # Отправка в лог-канал
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"🔒 Тикет `{channel.name}` закрыт пользователем {interaction.user}.", file=file)

        # Удаление канала
        await channel.delete(reason="Тикет закрыт пользователем")

class PersistentTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Создать тикет", style=discord.ButtonStyle.green, emoji="🎫", custom_id="create_ticket_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_panel", description="Отправить панель создания тикетов")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 Поддержка сервера",
            description="Если у вас возникли вопросы или проблемы, нажмите на кнопку ниже, чтобы создать тикет и связаться с администрацией.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Приватный канал будет создан автоматически")
        
        await interaction.response.send_message("Панель отправлена.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=PersistentTicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
