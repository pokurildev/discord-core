import discord
from discord.ext import commands
from discord import app_commands
import time
import datetime
import config
from config import UIConfig
from database.db import get_db

class ConfirmBuyView(discord.ui.View):
    def __init__(self, item_name, price, user_id):
        super().__init__(timeout=30)
        self.item_name = item_name
        self.price = price
        self.user_id = user_id

    @discord.ui.button(label="Подтвердить покупку", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Новый стиль — подтверждение покупки
        if interaction.user.id != self.user_id:
            msg = discord.Embed(description="**Это не ваша транзакция!**", color=UIConfig.ERROR)
            await interaction.response.send_message(embed=msg, ephemeral=True)
            return

        async with get_db() as db:
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                user_balance = row[0] if row else 0

        if user_balance < self.price:
            error_embed = discord.Embed(
                title="Ошибка Транзакции",
                description=f"Недостаточно средств на балансе.\n\n**Ваш баланс:** `{user_balance}` монет\n**Стоимость:** `{self.price}` монет",
                color=UIConfig.ERROR
            )
            error_embed.set_footer(text=UIConfig.FOOTER)
            await interaction.response.edit_message(content=None, embed=error_embed, view=None)
            return

        role = discord.utils.get(interaction.guild.roles, name=self.item_name)
        if not role:
            error_embed = discord.Embed(
                description=f"**Техническая ошибка:** Роль `{self.item_name}` не найдена на сервере. Обратитесь к администратору.",
                color=UIConfig.ERROR
            )
            await interaction.response.edit_message(content=None, embed=error_embed, view=None)
            return

        try:
            await interaction.user.add_roles(role)
            async with get_db() as db:
                await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (self.price, self.user_id))
                await db.commit()
            
            success_embed = discord.Embed(
                title="Поздравляем с приобретением!",
                description=(
                    f"Вы успешно приобрели статус {role.mention}!\n\n"
                    f"**💰 Списано:** `{self.price}` монет\n"
                    f"**Статус:** `{self.item_name}`\n\n"
                    "*Новые права и возможности уже доступны вам!*"
                ),
                color=UIConfig.SUCCESS,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            success_embed.set_thumbnail(url=UIConfig.ICON_GIFT)
            success_embed.set_footer(text=UIConfig.FOOTER)
            await interaction.response.edit_message(content=None, embed=success_embed, view=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"❌ **Произошла ошибка:** {e}", embed=None, view=None)

    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.secondary, emoji=None)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        cancel_embed = discord.Embed(description="**Покупка была отменена.** Ждем вас снова!", color=UIConfig.WARNING)
        await interaction.response.edit_message(content=None, embed=cancel_embed, view=None)

class ShopView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.items = list(config.SHOP_ITEMS.items())
        self.index = 0

    def create_embed(self):
        # Новый стиль — карточка товара в магазине
        item_key, item_data = self.items[self.index]
        item_name = item_data["role_name"]
        price = item_data["price"]
        description = item_data["desc"]
        color = item_data.get("color", UIConfig.MAGENTA)
        image_url = item_data["image"]

        embed = discord.Embed(
            title=f"Коллекционный Статус: {item_name}",
            description=f"{description}\n\n**🛒 Информация о товаре:**",
            color=color
        )
        embed.set_author(name="Внутриигровой Магазин", icon_url=UIConfig.ICON_COIN)
        embed.add_field(name="💰 Стоимость", value=f"```ansi\n\u001b[0;36m{price} монет\u001b[0m\n```", inline=True)
        embed.add_field(name=" Наличие", value="```ansi\n\u001b[0;32mДоступно\u001b[0m\n```", inline=True)
        
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Товар {self.index + 1} из {len(self.items)} {UIConfig.FOOTER}")
        return embed

    def update_buttons(self):
        self.first.disabled = self.index == 0
        self.back.disabled = self.index == 0
        self.forward.disabled = self.index == len(self.items) - 1
        self.last.disabled = self.index == len(self.items) - 1
        
        # Обновляем ценник на кнопке покупки
        _, item_data = self.items[self.index]
        self.buy.label = f"Купить за {item_data['price']}"

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary, emoji=None)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = 0
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary, emoji=None)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Купить", style=discord.ButtonStyle.success, emoji=None)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            msg = discord.Embed(description="**Это не ваше меню!** Пропишите `/shop` самостоятельно.", color=UIConfig.ERROR)
            await interaction.response.send_message(embed=msg, ephemeral=True)
            return

        item_key, item_data = self.items[self.index]
        view = ConfirmBuyView(item_data["role_name"], item_data["price"], self.user_id)
        
        confirm_embed = discord.Embed(
            title="Подтверждение Покупки",
            description=f"Вы действительно хотите приобрести роль **{item_data['role_name']}** за **{item_data['price']}** монет?",
            color=UIConfig.INFO
        )
        confirm_embed.set_footer(text="Действие необратимо")
        
        await interaction.response.send_message(embed=confirm_embed, view=view, ephemeral=True)

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary, emoji=None)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary, emoji=None)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = len(self.items) - 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Открыть премиум-магазин статусов")
    async def shop(self, interaction: discord.Interaction):
        # Новый стиль — открытие магазина
        if not config.SHOP_ITEMS:
            error_embed = discord.Embed(
                description="**Магазин в данный момент закрыт.** Администрация обновляет ассортимент!",
                color=UIConfig.WARNING
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
            
        view = ShopView(interaction.user.id)
        view.update_buttons()
        await interaction.response.send_message(embed=view.create_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Economy(bot))
