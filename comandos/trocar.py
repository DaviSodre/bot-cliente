import discord
from discord import app_commands
from discord.ext import commands
import importlib
from database import get_usuario, update_usuario
import cartas

def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis

class ConfirmTrocaView(discord.ui.View):
    def __init__(self, autor_id, alvo_id, carta_dada, carta_recebida):
        super().__init__(timeout=120)
        self.autor_id = autor_id
        self.alvo_id = alvo_id
        self.carta_dada = carta_dada
        self.carta_recebida = carta_recebida
        self.trocado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.alvo_id:
            await interaction.response.send_message("Só quem recebeu a proposta pode responder aqui.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar troca", style=discord.ButtonStyle.success)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_a_data = await get_usuario(self.autor_id)
        user_b_data = await get_usuario(self.alvo_id)

        if self.carta_dada["id"] not in user_a_data.get("cartas", []):
            await interaction.response.send_message(f"Você não tem mais a carta **{self.carta_dada['nome']}**, troca cancelada.", ephemeral=True)
            self.stop()
            return
        if self.carta_recebida["id"] not in user_b_data.get("cartas", []):
            await interaction.response.send_message(f"Você não tem a carta **{self.carta_recebida['nome']}**, troca cancelada.", ephemeral=True)
            self.stop()
            return

        user_a_cartas = user_a_data["cartas"]
        user_b_cartas = user_b_data["cartas"]

        user_a_cartas.remove(self.carta_dada["id"])
        user_a_cartas.append(self.carta_recebida["id"])

        user_b_cartas.remove(self.carta_recebida["id"])
        user_b_cartas.append(self.carta_dada["id"])

        await update_usuario(self.autor_id, {"cartas": user_a_cartas})
        await update_usuario(self.alvo_id, {"cartas": user_b_cartas})

        await interaction.response.edit_message(content=f"✅ Troca feita com sucesso entre <@{self.autor_id}> e <@{self.alvo_id}>!", embed=None, view=None)
        self.trocado = True
        self.stop()

    @discord.ui.button(label="Recusar troca", style=discord.ButtonStyle.danger)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Troca recusada.", embed=None, view=None)
        self.stop()

class TrocaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trocar", description="Propor troca de cartas com outro usuário")
    @app_commands.describe(alvo="Usuário que vai receber a proposta", carta_dada="ID da carta que você oferece", carta_recebida="ID da carta que quer receber")
    async def trocar(self, interaction: discord.Interaction, alvo: discord.Member, carta_dada: str, carta_recebida: str):
        if alvo.id == interaction.user.id:
            await interaction.response.send_message("Você não pode trocar cartas consigo mesmo.", ephemeral=True)
            return

        cartas_disponiveis = get_cartas_atualizadas()

        carta_oferecida = next((c for c in cartas_disponiveis if c["id"] == carta_dada), None)
        carta_pedida = next((c for c in cartas_disponiveis if c["id"] == carta_recebida), None)

        if not carta_oferecida or not carta_pedida:
            await interaction.response.send_message("Uma ou ambas as cartas não foram encontradas.", ephemeral=True)
            return

        user_data = await get_usuario(interaction.user.id)
        if carta_dada not in user_data.get("cartas", []):
            await interaction.response.send_message(f"Você não tem a carta **{carta_oferecida['nome']}** para oferecer.", ephemeral=True)
            return

        embed = discord.Embed(title="Proposta de Troca", color=discord.Color.blue())
        embed.add_field(name="De", value=interaction.user.mention, inline=True)
        embed.add_field(name="Para", value=alvo.mention, inline=True)
        embed.add_field(name="Carta oferecida", value=f"**{carta_oferecida['nome']}**", inline=False)
        embed.add_field(name="Carta pedida", value=f"**{carta_pedida['nome']}**", inline=False)

        view = ConfirmTrocaView(interaction.user.id, alvo.id, carta_oferecida, carta_pedida)
        await interaction.response.send_message(f"{alvo.mention}, você recebeu uma proposta de troca!", embed=embed, view=view, ephemeral=False)

async def setup(bot):
    await bot.add_cog(TrocaCog(bot))
