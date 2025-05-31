import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario
import importlib
import cartas
from collections import Counter


def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis


class PerfilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perfil", description="Veja seu perfil de colecionador de cartas")
    async def perfil(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = interaction.user.id
        usuario = await get_usuario(user_id)
        todas_cartas = get_cartas_atualizadas()
        cartas_ids_usuario = usuario.get("cartas", [])

        # Cartas do usuário
        cartas_usuario = [c for c in todas_cartas if c["id"] in cartas_ids_usuario]

        # Totais
        total_cartas = len(todas_cartas)
        total_usuario = len(cartas_usuario)

        comuns = [c for c in todas_cartas if c["raridade"] == "Comum"]
        raras = [c for c in todas_cartas if c["raridade"] == "Rara"]
        epicas = [c for c in todas_cartas if c["raridade"] == "Épica"]

        comuns_usuario = [c for c in cartas_usuario if c["raridade"] == "Comum"]
        raras_usuario = [c for c in cartas_usuario if c["raridade"] == "Rara"]
        epicas_usuario = [c for c in cartas_usuario if c["raridade"] == "Épica"]

        # Grupo com mais cartas
        grupo_mais = Counter([c["grupo"] for c in cartas_usuario]).most_common(1)
        grupo_top = grupo_mais[0][0] if grupo_mais else "Nenhum"

        # Era com mais cartas
        era_mais = Counter([c["era"] for c in cartas_usuario]).most_common(1)
        era_top = era_mais[0][0] if era_mais else "Nenhuma"

        # Eras completas
        

        background_id = usuario.get("background")
        if background_id:
            carta_background = next((c for c in todas_cartas if c["id"] == background_id), None)
        else:
    # pega última carta do usuário, se não tiver background setado
            if cartas_ids_usuario:
                ultima_carta_id = cartas_ids_usuario[-1]
                carta_background = next((c for c in todas_cartas if c["id"] == ultima_carta_id), None)
            else:
                carta_background = None
        # Imagem de fundo
        imagem_url = carta_background["imagem"] if carta_background else None
        

        embed = discord.Embed(
            title=f"Perfil de {interaction.user.display_name}",
            description=f"🃏 **Cartas:** {total_usuario}/{total_cartas}\n"
                        f"• Comuns: {len(comuns_usuario)}/{len(comuns)}\n"
                        f"• Raras: {len(raras_usuario)}/{len(raras)}\n"
                        f"• Épicas: {len(epicas_usuario)}/{len(epicas)}",
            color=discord.Color.purple()
        )
        embed.add_field(name="🎤 Grupo com mais cartas", value=grupo_top, inline=False)
        embed.add_field(name="📀 Era com mais cartas", value=era_top, inline=False)
        embed.add_field(name="💰 Dinheiro", value=f"{usuario.get('moedas', 0)} moedas", inline=False)
        embed.set_footer(text="Perfil do Usuário", icon_url=interaction.client.user.avatar.url)
        embed.set_thumbnail(url=interaction.user.avatar.url)

        if imagem_url:
            embed.set_image(url=imagem_url)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PerfilCog(bot))