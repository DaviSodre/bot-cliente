import discord
from discord import app_commands
from discord.ext import commands

class TesteImagem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teste_imagem", description="Testa se a imagem aparece no embed")
    @app_commands.describe(url="URL da imagem para testar")
    async def teste_imagem(self, interaction: discord.Interaction, url: str):
        embed = discord.Embed(
            title="Teste de Imagem",
            description="Se a imagem aparecer aqui, tá tudo certo!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TesteImagem(bot))
