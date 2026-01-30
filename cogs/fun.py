import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import datetime
from config import UIConfig

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coin", description="Подбросить неоновую монетку")
    async def coin(self, interaction: discord.Interaction):
        # Новый стиль — монетка
        result = random.choice(["Орёл", "Решка"])
        thumbnail_url = UIConfig.ICON_COIN
        
        embed = discord.Embed(
            title="Квантовое Подбрасывание...",
            description=f"Гравитация сделала свой выбор!\n\nРезультат: ```ansi\n\u001b[0;36m{result}\u001b[0m\n```",
            color=UIConfig.CYAN,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Игровой Модуль", icon_url=UIConfig.ICON_GIFT)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=UIConfig.FOOTER)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Задать вопрос магическому шару судьбы")
    @app_commands.describe(question="Ваш вопрос к магическому шару")
    async def ball(self, interaction: discord.Interaction, question: str):
        # Новый стиль — магический шар
        responses = [
            "Да, определенно", "Никаких сомнений", "Мне кажется — «да»", 
            "Вероятнее всего", "Знаки говорят — «да»", "Пока не ясно", 
            "Спроси позже", "Лучше не рассказывать", "Даже не думай",
            "Мой ответ — «нет»", "Перспективы не очень", "Весьма сомнительно"
        ]
        
        result = random.choice(responses)
        embed = discord.Embed(
            title="Магический Шар Судьбы",
            description="Энергия космоса концентрируется для ответа...",
            color=UIConfig.MAGENTA,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_author(name="Предсказание системы", icon_url=UIConfig.ICON_ADMIN)
        
        embed.add_field(name="Ваш Вопрос", value=f"```\n{question}\n```", inline=False)
        embed.add_field(name="✨ Ответ Шара", value=f"```ansi\n\u001b[0;35m{result}\u001b[0m\n```", inline=False)
        
        embed.set_footer(text=f"Запросил: {interaction.user.name} {UIConfig.FOOTER}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Получить порцию юмора с Reddit")
    async def meme(self, interaction: discord.Interaction):
        # Новый стиль — мемы
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as response:
                    if response.status != 200:
                        err_embed = discord.Embed(description="**API Reddit временно недоступно.** Попробуйте позже!", color=UIConfig.ERROR)
                        await interaction.followup.send(embed=err_embed)
                        return
                        
                    data = await response.json()
                    title = data.get("title", "Без названия")
                    url = data.get("url")
                    subreddit = data.get("subreddit", "memes")

                    embed = discord.Embed(
                        title=f"{title}",
                        color=UIConfig.SUCCESS,
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    embed.set_author(name=f"Reddit • r/{subreddit}", icon_url="https://www.redditstatic.com/desktop2x/img/favicon/android-icon-192x192.png")
                    embed.set_image(url=url)
                    embed.set_footer(text=UIConfig.FOOTER)
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            await interaction.followup.send("**Произошла критическая ошибка** при загрузке медиа-контента.")

async def setup(bot):
    await bot.add_cog(Fun(bot))
