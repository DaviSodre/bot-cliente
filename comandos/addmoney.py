import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

MEUS_IDS = [209387134715559946, 1069582140834066442]

class AddMoney(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addmoney", description="Adiciona moedas a um usuário")
    @app_commands.describe(user="Usuário para adicionar moedas", amount="Quantidade de moedas a adicionar")
    async def addmoney(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if interaction.user.id not in MEUS_IDS:
            return await interaction.response.send_message("❌ você não tem permissão.", ephemeral=True)

        user_data = await get_usuario(user.id)
        user_data["moedas"] = user_data.get("moedas", 0) + amount
        await update_usuario(user.id, user_data)
        await interaction.response.send_message(f"✅ adicionado {amount:,} moedas para {user.name}!".replace(",", "."))

async def setup(bot):
    await bot.add_cog(AddMoney(bot))
