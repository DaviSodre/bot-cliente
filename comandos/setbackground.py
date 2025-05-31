import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario
import importlib
import cartas

def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis

class SetBackgroundCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setbackground", description="Define a carta que será usada como imagem de fundo do seu perfil")
    @app_commands.describe(carta_id="ID da carta para usar como fundo")
    async def setbackground(self, interaction: discord.Interaction, carta_id: str):
        await interaction.response.defer()

        usuario = await get_usuario(interaction.user.id)
        todas_cartas = get_cartas_atualizadas()

        carta_escolhida = next((c for c in todas_cartas if c["id"] == carta_id), None)
        if not carta_escolhida:
            await interaction.followup.send("❌ Carta com esse ID não encontrada.", ephemeral=True)
            return

        cartas_ids_usuario = usuario.get("cartas", [])
        if carta_id not in cartas_ids_usuario:
            await interaction.followup.send("❌ Você não possui essa carta.", ephemeral=True)
            return

        # atualiza background no banco
        usuario["background"] = carta_id
        await update_usuario(interaction.user.id, usuario)

        # escolhe url da imagem: gif se tiver, senão imagem normal
        url_imagem = carta_escolhida.get("gif") or carta_escolhida.get("imagem")

        embed = discord.Embed(
            title="✅ Background atualizado!",
            description=f"Sua imagem de perfil foi atualizada para a carta **{carta_escolhida['nome']}**.",
            color=discord.Color.green()
        )
        if url_imagem:
            embed.set_image(url=url_imagem)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetBackgroundCog(bot))
