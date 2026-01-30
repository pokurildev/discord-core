import discord
from discord.ext import commands
import config

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temporary_channels = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 1. Логика создания канала
        if after.channel and after.channel.id == config.HUB_CHANNEL_ID:
            guild = member.guild
            category = guild.get_channel(config.CATEGORY_VOICE_ID)
            
            if not category or not isinstance(category, discord.CategoryChannel):
                print(f" [!] Ошибка: Категория с ID {config.CATEGORY_VOICE_ID} не найдена.")
                return

            channel_name = f"Комната {member.display_name}"
            overwrites = {
                member: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True),
                guild.me: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True, move_members=True)
            }

            try:
                new_channel = await guild.create_voice_channel(
                    name=channel_name,
                    category=category,
                    overwrites=overwrites
                )
                self.temporary_channels.append(new_channel.id)
                await member.move_to(new_channel)
            except Exception as e:
                print(f" [!] Ошибка в Voice системе: {e}")

        # 2. Логика удаления канала
        if before.channel and before.channel.id in self.temporary_channels:
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="Временная комната пуста")
                    self.temporary_channels.remove(before.channel.id)
                except Exception as e:
                    print(f" [!] Ошибка при удалении канала: {e}")

async def setup(bot):
    await bot.add_cog(Voice(bot))
