import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario
from embeds import criar_embed_carta_preview
import importlib
import cartas

IDS_AUTORIZADOS = [209387134715559946, 1069582140834066442] 

def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis


class ConfirmDarCartaView(discord.ui.View):
    def __init__(self, carta, usuario_data, usuario_member, autor_id):
        super().__init__(timeout=60)
        self.carta = carta
        self.usuario_data = usuario_data
        self.usuario_member = usuario_member
        self.autor_id = autor_id
        self.confirmado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message("Só quem usou o comando pode interagir aqui!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = await get_usuario(self.usuario_member.id)

        if self.carta["id"] in user_data["cartas"]:
            await interaction.response.send_message(
                f"❌ {self.usuario_member.mention} já tem a carta **{self.carta['nome']}**.", ephemeral=True)
            return

        user_data["cartas"].append(self.carta["id"])
        await update_usuario(self.usuario_member.id, user_data)

        await interaction.response.edit_message(
            content=f"✅ Carta **{self.carta['nome']}** dada para {self.usuario_member.mention}!",
            embed=None,
            view=None,
        )
        self.confirmado = True
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Ação cancelada.", embed=None, view=None)
        self.stop()


class DarCartaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dar_carta", description="Dar uma carta específica para um usuário (somente autorizados)")
    @app_commands.describe(usuario="Quem vai receber", carta_id="ID da carta que será dada")
    async def dar_carta(self, interaction: discord.Interaction, usuario: discord.Member, carta_id: str):
        if interaction.user.id not in IDS_AUTORIZADOS:
            await interaction.response.send_message("❌ Você não tem permissão pra usar esse comando.", ephemeral=True)
            return
        
        usuario_data = await get_usuario(usuario.id)
        cartas_disponiveis = get_cartas_atualizadas()
        carta = next((c for c in cartas_disponiveis if c["id"] == carta_id), None)

        if not carta:
            await interaction.response.send_message("❌ Carta com esse ID não encontrada.", ephemeral=True)
            return

        embed = criar_embed_carta_preview(carta, usuario, interaction.client)

        view = ConfirmDarCartaView(carta, usuario_data, usuario, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(DarCartaCog(bot))
