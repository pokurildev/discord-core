import discord
from discord.ext import commands

# Конфигурация (замените на свои ID)
HUB_CHANNEL_ID = 123456789012345678  # Канал "➕ Создать комнату"
CATEGORY_ID = 123456789012345678     # Категория для новых каналов

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Список ID временных каналов для отслеживания
        self.temporary_channels = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # 1. Логика создания канала
        if after.channel and after.channel.id == HUB_CHANNEL_ID:
            guild = member.guild
            category = guild.get_channel(CATEGORY_ID)
            
            if not category or not isinstance(category, discord.CategoryChannel):
                print(f" [!] Ошибка: Категория с ID {CATEGORY_ID} не найдена или не является категорией.")
                return

            # Создание канала
            channel_name = f"Комната {member.display_name}"
            
            # Права для создателя (Manage Channel)
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
                
                # Сохраняем ID для отслеживания
                self.temporary_channels.append(new_channel.id)
                
                # Перемещение пользователя
                await member.move_to(new_channel)
                print(f" [✓] Создана комната для {member}")
                
            except discord.Forbidden:
                print(f" [!] Ошибка: Недостаточно прав для создания/перемещения в {guild.name}")
            except Exception as e:
                print(f" [!] Непредвиденная ошибка: {e}")

        # 2. Логика удаления канала
        if before.channel and before.channel.id in self.temporary_channels:
            # Если в канале никого не осталось
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete(reason="Временная комната пуста")
                    self.temporary_channels.remove(before.channel.id)
                    print(f" [✓] Удалена пустая комната: {before.channel.name}")
                except discord.NotFound:
                    # Канал уже удален (возможно, вручную)
                    if before.channel.id in self.temporary_channels:
                        self.temporary_channels.remove(before.channel.id)
                except Exception as e:
                    print(f" [!] Ошибка при удалении канала: {e}")

async def setup(bot):
    await bot.add_cog(Voice(bot))
