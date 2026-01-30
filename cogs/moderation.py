import discord
from discord.ext import commands
import datetime
import collections
import config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_control = collections.defaultdict(lambda: collections.deque(maxlen=5))

    async def send_log(self, guild, embed=None, content=None):
        channel = guild.get_channel(config.LOG_CHANNEL_ID)
        if channel:
            await channel.send(content=content, embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # --- 1. Проверка на запрещенные слова ---
        content_lower = message.content.lower()
        if any(word in content_lower for word in config.BAD_WORDS):
            try:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, ваше сообщение содержит запрещенные слова!", delete_after=5)
                return
            except discord.Forbidden:
                print(f" [!] Нет прав на удаление сообщения в {message.guild.name}")

        # --- 2. Антиспам защита ---
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        user_id = message.author.id
        user_messages = self.spam_control[user_id]
        
        user_messages.append(now)
        
        if len(user_messages) == 5:
            if now - user_messages[0] < 5:
                try:
                    duration = datetime.timedelta(minutes=1)
                    await message.author.timeout(duration, reason="Спам (автомод)")
                    await message.channel.send(f"⚠️ {message.author.mention} получил тайм-аут на 1 минуту за спам.")
                    user_messages.clear()
                except discord.Forbidden:
                    print(f" [!] Нет прав на выдачу тайм-аута {message.author}")

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
        
        await self.send_log(before.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_log(member.guild, content=f"📥 **Участник вошел:** {member} (ID: {member.id})")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_log(member.guild, content=f"📤 **Участник вышел:** {member} (ID: {member.id})")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
