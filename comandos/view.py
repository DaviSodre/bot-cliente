import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario
import importlib
import cartas


def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis


class ViewCarta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view", description="Veja os detalhes de uma carta sua")
    @app_commands.describe(id="ID da carta que você quer visualizar")
    async def view(self, interaction: discord.Interaction, id: str):
        await interaction.response.defer()

        user_id = interaction.user.id
        usuario = await get_usuario(user_id)
        cartas_usuario = usuario.get("cartas", [])
        todas_cartas = get_cartas_atualizadas()

        # verifica se a carta tá na coleção do usuário
        if id not in cartas_usuario:
            return await interaction.followup.send("❌ Você não possui essa carta.")

        # pega dados da carta
        carta = next((c for c in todas_cartas if c["id"] == id), None)
        if not carta:
            return await interaction.followup.send("❌ Carta não encontrada no sistema.")

        embed = discord.Embed(
            title=f"{carta['nome']} (ID: {carta['id']})",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🎤 Grupo", value=carta.get("grupo", "Desconhecido"), inline=True)
        embed.add_field(name="📀 Era", value=carta.get("era", "Desconhecida"), inline=True)
        embed.add_field(name="⭐ Raridade", value=carta.get("raridade", "Desconhecida"), inline=True)

        # imagem ou gif
        imagem_url = carta.get("gif") or carta.get("imagem")
        if imagem_url:
            embed.set_image(url=imagem_url)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ViewCarta(bot))
