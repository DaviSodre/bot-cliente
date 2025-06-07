import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

MEUS_IDS = [209387134715559946, 1069582140834066442]

class RemoveMoney(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="removemoney", description="Remove moedas de um usuário")
    @app_commands.describe(user="Usuário para remover moedas", amount="Quantidade de moedas a remover")
    async def removemoney(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if interaction.user.id not in MEUS_IDS:
            return await interaction.response.send_message("❌ você não tem permissão.", ephemeral=True)

        user_data = await get_usuario(user.id)
        moedas_atuais = user_data.get("moedas", 0)
        user_data["moedas"] = max(0, moedas_atuais - amount)
        await update_usuario(user.id, user_data)

        await interaction.response.send_message(f"✅ removido {amount:,} moedas de {user.name}!".replace(",", "."))

async def setup(bot):
    await bot.add_cog(RemoveMoney(bot))
