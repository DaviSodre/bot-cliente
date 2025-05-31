import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario

class VerMoedasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mostrar_moedas(self, interaction: discord.Interaction):
        user_data = await get_usuario(interaction.user.id)
        moedas = user_data.get("moedas", 0)

        embed = discord.Embed(
            title="💰 Suas moedas",
            description=f"Você tem **{moedas} moedas**.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="coins", description="Veja quantas moedas você tem")
    async def coins(self, interaction: discord.Interaction):
        await self.mostrar_moedas(interaction)

    @app_commands.command(name="money", description="Veja quantas moedas você tem")
    async def money(self, interaction: discord.Interaction):
        await self.mostrar_moedas(interaction)

async def setup(bot):
    await bot.add_cog(VerMoedasCog(bot))
