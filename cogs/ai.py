import discord
from discord.ext import commands
from discord import app_commands
from google import genai # НОВАЯ БИБЛИОТЕКА
from google.genai import types
import config

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Инициализация клиента по-новому
        if config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        else:
            self.client = None
            print(" [!] Внимание: GEMINI_API_KEY не найден. AI модуль отключен.")

    @app_commands.command(name="ask", description="Задать вопрос нейросети Gemini 2.0")
    @app_commands.describe(prompt="Ваш вопрос к ИИ")
    async def ask(self, interaction: discord.Interaction, prompt: str):
        if not self.client:
            await interaction.response.send_message("❌ Модуль ИИ не настроен.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Используем асинхронную версию метода
            response = await self.client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            if not response.text:
                await interaction.followup.send("❌ ИИ вернул пустой ответ или ответ заблокирован фильтрами.")
                return

            text = response.text

            # Обрезка до 1900 символов для Discord
            if len(text) > 1900:
                text = text[:1900] + "\n\n... (ответ обрезан Discord)"

            await interaction.followup.send(f"**Вопрос:** {prompt}\n\n**Ответ:**\n{text}")

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                await interaction.followup.send(" Превышен лимит запросов к ИИ. Пожалуйста, попробуйте позже.")
            else:
                print(f" [!] Ошибка ИИ: {e}")
                await interaction.followup.send("❌ Произошла ошибка при генерации ответа.")

async def setup(bot):
    await bot.add_cog(AI(bot))