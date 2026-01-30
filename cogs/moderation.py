import discord
from discord.ext import commands
import datetime
import collections
from database.db import get_db

# Конфигурация (в идеале подтягивать из БД)
BAD_WORDS = {"скам", "реклама", "токсик"} # Пример списка
LOG_CHANNEL_ID = 123456789012345678 # ЗАМЕНИТЕ НА ВАШ ID

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Словарь для антиспама: {user_id: deque([timestamps])}
        self.spam_control = collections.defaultdict(lambda: collections.deque(maxlen=5))

    async def send_log(self, guild, embed=None, content=None):
        """Вспомогательная функция для отправки логов"""
        # В будущем здесь можно добавить получение ID канала из БД (guild_config)
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(content=content, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # --- 1. Проверка на запрещенные слова ---
        content_lower = message.content.lower()
        if any(word in content_lower for word in BAD_WORDS):
            try:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, ваше сообщение содержит запрещенные слова!", delete_after=5)
                return # Прерываем, так как сообщение удалено
            except discord.Forbidden:
                print(f" [!] Нет прав на удаление сообщения в {message.guild.name}")

        # --- 2. Антиспам защита ---
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        user_id = message.author.id
        user_messages = self.spam_control[user_id]
        
        user_messages.append(now)
        
        if len(user_messages) == 5:
            # Если 5 сообщений отправлены меньше чем за 5 секунд
            if now - user_messages[0] < 5:
                try:
                    duration = datetime.timedelta(minutes=1)
                    await message.author.timeout(duration, reason="Спам (автомод)")
                    await message.channel.send(f"⚠️ {message.author.mention} получил тайм-аут на 1 минуту за спам.")
                    # Очищаем историю сообщений пользователя для антиспама
                    user_messages.clear()
                except discord.Forbidden:
                    print(f" [!] Нет прав на выдачу тайм-аута {message.author}")

    # --- Логирование событий ---

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
            
        embed = discord.Embed(
            title="🗑️ Сообщение удалено",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Автор", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Канал", value=message.channel.mention, inline=True)
        embed.add_field(name="Содержание", value=message.content or "*(Нет текста или вложение)*", inline=False)
        
        await self.send_log(message.guild, embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
            
        embed = discord.Embed(
            title="📝 Сообщение изменено",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Автор", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Было", value=before.content[:1024], inline=False)
        embed.add_field(name="Стало", value=after.content[:1024], inline=False)
        embed.add_field(name="Ссылка", value=after.jump_url, inline=False)
        
        await self.send_log(before.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Текстовый лог входа
        await self.send_log(member.guild, content=f"📥 **Участник вошел:** {member} (ID: {member.id})")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Текстовый лог выхода
        await self.send_log(member.guild, content=f"📤 **Участник вышел:** {member} (ID: {member.id})")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
