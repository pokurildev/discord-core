import discord
from discord.ext import commands
from discord import app_commands
from config import UIConfig

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Безопасность", description="Модерация, логи и защита сервера", emoji=None, value="Moderation"),
            discord.SelectOption(label="Прогресс", description="Ранги, XP и уровни участников", emoji=None, value="Leveling"),
            discord.SelectOption(label="Поддержка", description="Система тикетов и помощь", emoji=None, value="Tickets"),
            discord.SelectOption(label="Голос", description="Управление приватными каналами", emoji=None, value="Voice"),
            discord.SelectOption(label="Развлечения", description="Игры, экономика и фан-команды", emoji=None, value="Fun"),
        ]
        super().__init__(placeholder="Выберите категорию команд здесь...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Новый стиль — страница категории в меню помощи
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)
        
        if not cog:
            await interaction.response.send_message(f"❌ **Ошибка:** Модуль `{cog_name}` не найден или временно отключен.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Справочник • Категория {cog_name}",
            description=f"Ниже представлен список доступных инструментов в модуле **{cog_name}**.\nВсе команды оптимизированы для использования в 2025 году.",
            color=UIConfig.CYAN
        )
        embed.set_author(name="Вспомогательная система", icon_url=UIConfig.ICON_ADMIN)

        # Сбор слэш-команд
        app_cmds = cog.get_app_commands()
        if app_cmds:
            cmds_text = ""
            for cmd in app_cmds:
                cmds_text += f"• `/{cmd.name}` — {cmd.description or 'Описание отсутствует'}\n"
            embed.add_field(name="✨ Слэш-команды (Рекомендуется)", value=cmds_text, inline=False)

        # Сбор обычных команд
        pref_cmds = cog.get_commands()
        if pref_cmds:
            cmds_text = ""
            for cmd in pref_cmds:
                cmds_text += f"• `!{cmd.name}` — {cmd.help or cmd.description or 'Описание отсутствует'}\n"
            embed.add_field(name="Префиксные команды", value=cmds_text, inline=False)

        if not app_cmds and not pref_cmds:
            embed.description = "**Интересный факт:** В этой категории пока нет опубликованных команд."

        embed.set_footer(text=f"Категория: {cog_name} {UIConfig.FOOTER}")
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown(bot))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = None

    @app_commands.command(name="help", description="Открыть интерактивный центр помощи Premium UI")
    async def help(self, interaction: discord.Interaction):
        # Новый стиль — главная страница меню помощи
        embed = discord.Embed(
            title="База Знаний Сервера",
            description=(
                "Добро пожаловать в интеллектуальный центр управления ботом.\n\n"
                "**Как найти нужную команду?**\n"
                "1️⃣ Нажмите на выпадающее меню **'Выберите категорию'** ниже.\n"
                "2️⃣ Ознакомьтесь со списком доступных функций.\n"
                "3️⃣ Используйте `/команда` для быстрого доступа.\n\n"
                "*Нужна дополнительная помощь? Напишите нам в поддержку через `/ticket_panel`.*"
            ),
            color=UIConfig.MAGENTA
        )
        
        embed.set_author(name="Гайд по использованию", icon_url=UIConfig.ICON_SHIELD)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="О системе", 
            value=f"```ansi\n\u001b[0;36mИмя:\u001b[0m {self.bot.user.name}\n\u001b[0;36mВерсия:\u001b[0m 2.1.0-PREMIUM\n\u001b[0;36mСтатус:\u001b[0m ONLINE\n```", 
            inline=False
        )
        
        embed.set_footer(text=f"Запросил: {interaction.user.name} {UIConfig.FOOTER}")

        await interaction.response.send_message(embed=embed, view=HelpView(self.bot))

async def setup(bot):
    await bot.add_cog(Help(bot))
