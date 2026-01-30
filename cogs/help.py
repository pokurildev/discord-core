import discord
from discord.ext import commands
from discord import app_commands

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Модерация", description="Защита сервера и аудит", emoji="👮", value="Moderation"),
            discord.SelectOption(label="Уровни", description="XP, ранги и прогресс", emoji="🆙", value="Leveling"),
            discord.SelectOption(label="Тикеты", description="Связь с администрацией", emoji="🎫", value="Tickets"),
            discord.SelectOption(label="Голос", description="Динамические каналы", emoji="🔊", value="Voice"),
            discord.SelectOption(label="Развлечения", description="Команды для веселья", emoji="🎉", value="Fun"),
        ]
        super().__init__(placeholder="Выберите категорию команд...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)
        
        if not cog:
            await interaction.response.send_message(f"Ошибка: Модуль {cog_name} не найден.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{self.placeholder} — {cog_name}",
            description=f"Список доступных команд в категории **{cog_name}**:",
            color=discord.Color.from_str("#00ffff")
        )

        # Сбор слэш-команд
        app_cmds = cog.get_app_commands()
        if app_cmds:
            cmds_text = ""
            for cmd in app_cmds:
                cmds_text += f"`/{cmd.name}` — {cmd.description or 'Нет описания'}\n"
            embed.add_field(name="Слэш-команды", value=cmds_text, inline=False)

        # Сбор обычных команд
        pref_cmds = cog.get_commands()
        if pref_cmds:
            cmds_text = ""
            for cmd in pref_cmds:
                cmds_text += f"`!{cmd.name}` — {cmd.help or cmd.description or 'Нет описания'}\n"
            embed.add_field(name="Префиксные команды", value=cmds_text, inline=False)

        if not app_cmds and not pref_cmds:
            embed.description = "В этой категории пока нет команд."

        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180) # Меню активно 3 минуты
        self.add_item(HelpDropdown(bot))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Отключаем стандартную команду help
        self.bot.help_command = None

    @app_commands.command(name="help", description="Показать меню помощи с командами")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Центр помощи бота",
            description="Добро пожаловать в меню помощи! Воспользуйтесь выпадающим списком ниже, чтобы выбрать интересующую вас категорию и узнать больше о командах.",
            color=discord.Color.from_str("#ff00ff")
        )
        
        # Можно добавить изображение, если есть ссылка или путь
        # embed.set_image(url="...")
        
        embed.add_field(name="Как пользоваться?", value="1. Нажмите на меню.\n2. Выберите категорию.\n3. Изучите список команд.", inline=False)
        embed.set_footer(text="Версия бота: 1.2.0 | Дизайн: Dark Neon")

        await interaction.response.send_message(embed=embed, view=HelpView(self.bot))

async def setup(bot):
    await bot.add_cog(Help(bot))
