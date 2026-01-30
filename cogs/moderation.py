import discord
from discord.ext import commands
from discord import app_commands
import datetime
import collections
import config
from config import UIConfig
from database.db import get_db

class BanModal(discord.ui.Modal, title="Ограничение доступа: БАН"):
    reason = discord.ui.TextInput(
        label="Обоснование блокировки",
        style=discord.TextStyle.paragraph,
        placeholder="Укажите пункты правил или описание нарушения...",
        required=True,
        max_length=500
    )

    def __init__(self, member: discord.Member, moderation_cog):
        super().__init__()
        self.member = member
        self.moderation_cog = moderation_cog

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.member.ban(reason=self.reason.value)
            
            # Новый стиль — лог бана
            embed = discord.Embed(
                title="Глобальная Блокировка",
                description=f"Пользователь был навсегда удален с сервера.",
                color=UIConfig.ERROR,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_SHIELD)
            embed.add_field(name="Нарушитель", value=f"**{self.member}**\n`{self.member.id}`", inline=True)
            embed.add_field(name="Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Причина", value=f"```\n{self.reason.value}\n```", inline=False)
            embed.set_footer(text=UIConfig.FOOTER)
            
            await self.moderation_cog.send_log(interaction.guild, embed=embed)
            
            success_embed = discord.Embed(description=f"✅ **{self.member}** успешно забанен.", color=UIConfig.SUCCESS)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ **Ошибка:** Недостаточно прав для бана этого пользователя.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **Произошла ошибка:** {e}", ephemeral=True)

class KickModal(discord.ui.Modal, title="Исключение пользователя"):
    reason = discord.ui.TextInput(
        label="Причина исключения",
        style=discord.TextStyle.paragraph,
        placeholder="Введите причину...",
        required=True,
        max_length=500
    )

    def __init__(self, member: discord.Member, moderation_cog):
        super().__init__()
        self.member = member
        self.moderation_cog = moderation_cog

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.member.kick(reason=self.reason.value)
            
            embed = discord.Embed(
                title="Исключение Участника",
                description=f"Пользователь был исключен с сервера.",
                color=UIConfig.WARNING,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_SHIELD)
            embed.add_field(name="Участник", value=f"**{self.member}**\n`{self.member.id}`", inline=True)
            embed.add_field(name="Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Причина", value=f"```\n{self.reason.value}\n```", inline=False)
            embed.set_footer(text=UIConfig.FOOTER)
            
            await self.moderation_cog.send_log(interaction.guild, embed=embed)
            
            success_embed = discord.Embed(description=f"✅ **{self.member}** успешно исключен.", color=UIConfig.SUCCESS)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ **Ошибка:** Недостаточно прав для исключения этого пользователя.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **Произошла ошибка:** {e}", ephemeral=True)

class MuteModal(discord.ui.Modal, title="Ограничение общения"):
    minutes = discord.ui.TextInput(
        label="Длительность (в минутах)",
        placeholder="Например: 10, 60, 1440...",
        required=True,
        min_length=1,
        max_length=5
    )

    def __init__(self, member: discord.Member, moderation_cog):
        super().__init__()
        self.member = member
        self.moderation_cog = moderation_cog

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mins = int(self.minutes.value)
            if mins <= 0: raise ValueError
            
            duration = datetime.timedelta(minutes=mins)
            await self.member.timeout(duration, reason=f"Мут через панель (Модератор: {interaction.user})")
            
            embed = discord.Embed(
                title="Приглушение Участника",
                description=f"Пользователю временно ограничен доступ к чату.",
                color=UIConfig.INFO,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_SHIELD)
            embed.add_field(name="Участник", value=f"**{self.member}**", inline=True)
            embed.add_field(name="Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Длительность", value=f"`{mins}` минут", inline=True)
            embed.set_footer(text=UIConfig.FOOTER)
            
            await self.moderation_cog.send_log(interaction.guild, embed=embed)
            
            success_embed = discord.Embed(description=f"✅ **{self.member}** приглушен на `{mins}` мин.", color=UIConfig.SUCCESS)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ **Ошибка:** Введите корректное число минут.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ **Ошибка:** Недостаточно прав.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **Ошибка:** {e}", ephemeral=True)

class ManageView(discord.ui.View):
    def __init__(self, member: discord.Member, moderation_cog):
        super().__init__(timeout=180)
        self.member = member
        self.moderation_cog = moderation_cog

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, emoji=None, row=0)
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanModal(self.member, self.moderation_cog))

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.secondary, emoji=None, row=0)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(KickModal(self.member, self.moderation_cog))

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.primary, emoji=None, row=1)
    async def mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MuteModal(self.member, self.moderation_cog))

    @discord.ui.button(label="Unmute", style=discord.ButtonStyle.secondary, emoji=None, row=1)
    async def unmute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.member.timeout(None, reason=f"Размут через панель (Модератор: {interaction.user})")
            
            embed = discord.Embed(
                title="Снятие Приглушения",
                description="Пользователю возвращен доступ к общению.",
                color=UIConfig.SUCCESS,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_SHIELD)
            embed.add_field(name="Участник", value=f"**{self.member}**", inline=True)
            embed.add_field(name="Модератор", value=interaction.user.mention, inline=True)
            embed.set_footer(text=UIConfig.FOOTER)
            
            await self.moderation_cog.send_log(interaction.guild, embed=embed)
            
            success_embed = discord.Embed(description=f"✅ Мут с **{self.member}** успешно снят.", color=UIConfig.SUCCESS)
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **Ошибка:** {e}", ephemeral=True)

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.success, emoji=None, row=2)
    async def warn_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with get_db() as db:
            await db.execute("UPDATE users SET warns = warns + 1 WHERE user_id = ?", (self.member.id,))
            await db.commit()
            
            async with db.execute("SELECT warns FROM users WHERE user_id = ?", (self.member.id,)) as cursor:
                row = await cursor.fetchone()
                warn_count = row[0] if row else 1

        embed = discord.Embed(
            title="Регистрация Нарушения",
            description="Пользователю вынесено официальное предупреждение.",
            color=UIConfig.WARNING,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_WARN)
        embed.add_field(name="Участник", value=f"**{self.member}**", inline=True)
        embed.add_field(name="Модератор", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name="Всего варнов", value=f"```ansi\n\u001b[0;31m{warn_count}\u001b[0m\n```", inline=True)
        embed.set_footer(text=UIConfig.FOOTER)
        
        await self.moderation_cog.send_log(interaction.guild, embed=embed)
        
        success_embed = discord.Embed(description=f"✅ Предупреждение выдано. Всего варнов: **{warn_count}**.", color=UIConfig.SUCCESS)
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    @discord.ui.button(label="Unwarn", style=discord.ButtonStyle.secondary, emoji=None, row=2)
    async def unwarn_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with get_db() as db:
            async with db.execute("SELECT warns FROM users WHERE user_id = ?", (self.member.id,)) as cursor:
                row = await cursor.fetchone()
                current_warns = row[0] if row else 0

            if current_warns <= 0:
                await interaction.response.send_message("❌ **У этого пользователя нет варнов.**", ephemeral=True)
                return

            new_warns = current_warns - 1
            await db.execute("UPDATE users SET warns = ? WHERE user_id = ?", (new_warns, self.member.id))
            await db.commit()

        embed = discord.Embed(
            title="Снятие Предупреждения",
            description="Счетчик нарушений пользователя был уменьшен.",
            color=UIConfig.SUCCESS,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Система Безопасности", icon_url=UIConfig.ICON_SHIELD)
        embed.add_field(name="Участник", value=f"**{self.member}**", inline=True)
        embed.add_field(name="Модератор", value=interaction.user.mention, inline=True)
        embed.add_field(name="Осталось варнов", value=f"```ansi\n\u001b[0;32m{new_warns}\u001b[0m\n```", inline=True)
        embed.set_footer(text=UIConfig.FOOTER)
        
        await self.moderation_cog.send_log(interaction.guild, embed=embed)
        
        success_embed = discord.Embed(description=f"✅ Варн снят. Теперь у пользователя **{new_warns}**.", color=UIConfig.SUCCESS)
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_control = collections.defaultdict(lambda: collections.deque(maxlen=5))

    async def send_log(self, guild, embed=None, content=None):
        channel = guild.get_channel(config.LOG_CHANNEL_ID)
        if channel:
            await channel.send(content=content, embed=embed)

    @app_commands.command(name="manage", description="Открыть премиум-панель управления (Админ)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def manage(self, interaction: discord.Interaction, member: discord.Member):
        if member.id == interaction.user.id:
            await interaction.response.send_message("**Вы не можете управлять самим собой!**", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Модерация Участника: {member.name}",
            description="Выберите необходимое действие в меню ниже.",
            color=UIConfig.MAGENTA
        )
        embed.set_author(name="Панель Администратора", icon_url=UIConfig.ICON_ADMIN)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="User ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="На сервере", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        
        roles = [role.mention for role in member.roles[1:][::-1]]
        embed.add_field(name=f"Роли ({len(roles)})", value=", ".join(roles[:5]) + ("..." if len(roles) > 5 else "") if roles else "Нет ролей", inline=False)
        
        embed.set_footer(text=f"Запросил: {interaction.user.name} {UIConfig.FOOTER}")
        
        view = ManageView(member, self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @manage.error
    async def manage_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("**Доступ запрещен!** Эта команда только для высшего персонала.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return

        content_lower = message.content.lower()
        if any(word in content_lower for word in config.BAD_WORDS):
            try:
                await message.delete()
                warning_embed = discord.Embed(
                    description=f"{message.author.mention}, **ваше сообщение удалено.** Мат и оскорбления запрещены!",
                    color=UIConfig.ERROR
                )
                await message.channel.send(embed=warning_embed, delete_after=5)
                return
            except discord.Forbidden: pass

        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        user_id = message.author.id
        user_messages = self.spam_control[user_id]
        user_messages.append(now)
        
        if len(user_messages) == 5:
            if now - user_messages[0] < 5:
                try:
                    duration = datetime.timedelta(minutes=1)
                    await message.author.timeout(duration, reason="Спам (Автомод)")
                    
                    spam_embed = discord.Embed(
                        description=f" {message.author.mention} получил авто-мут на **1 минуту** за спам.",
                        color=UIConfig.WARNING
                    )
                    await message.channel.send(embed=spam_embed)
                    user_messages.clear()
                except discord.Forbidden: pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
            
        embed = discord.Embed(
            title="Сообщение Удалено",
            color=UIConfig.ERROR,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Аудит Чата", icon_url=UIConfig.ICON_SHIELD)
        embed.add_field(name="Автор", value=f"{message.author.mention}\n`{message.author.id}`", inline=True)
        embed.add_field(name="Канал", value=message.channel.mention, inline=True)
        embed.add_field(name="Содержание", value=f"```\n{message.content or '(Нет текста)'}\n```", inline=False)
        embed.set_footer(text=UIConfig.FOOTER)
        
        await self.send_log(message.guild, embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
            
        embed = discord.Embed(
            title="Сообщение Отредактировано",
            color=UIConfig.WARNING,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Аудит Чата", icon_url=UIConfig.ICON_SHIELD)
        embed.add_field(name="Автор", value=f"{before.author.mention}", inline=True)
        embed.add_field(name="Канал", value=before.channel.mention, inline=True)
        embed.add_field(name="Было", value=f"```\n{before.content[:512]}\n```", inline=False)
        embed.add_field(name="✅ Стало", value=f"```\n{after.content[:512]}\n```", inline=False)
        embed.set_footer(text=UIConfig.FOOTER)
        
        await self.send_log(before.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="Новый Участник",
            description=f"**{member}** присоединился к серверу.",
            color=UIConfig.SUCCESS,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID Пользователя", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Аккаунт создан", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
        embed.set_footer(text=UIConfig.FOOTER)
        await self.send_log(member.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Участник Покинул Нас",
            description=f"**{member}** ушел с сервера.",
            color=UIConfig.ERROR,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name=" ID Пользователя", value=f"`{member.id}`", inline=True)
        embed.set_footer(text=UIConfig.FOOTER)
        await self.send_log(member.guild, embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
