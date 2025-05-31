import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario
import importlib
import cartas

def get_cartas_atualizadas():
    importlib.reload(cartas)
    return cartas.cartas_disponiveis

valores_raridade = {
    "Comum": 10,
    "Rara": 25,
    "Épica": 50
}

class ConfirmSellCartaView(discord.ui.View):
    def __init__(self, carta, usuario_data, interaction_user_id):
        super().__init__(timeout=60)
        self.carta = carta
        self.usuario_data = usuario_data
        self.interaction_user_id = interaction_user_id
        self.confirmado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.interaction_user_id:
            await interaction.response.send_message("❌ Só quem usou o comando pode interagir aqui!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar venda", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = await get_usuario(interaction.user.id)
        
        if self.carta["id"] not in user_data["cartas"]:
            await interaction.response.send_message("❌ Você não tem essa carta mais.", ephemeral=True)
            self.stop()
            return

        user_data["cartas"].remove(self.carta["id"])
        valor = valores_raridade.get(self.carta["raridade"], 0)
        user_data["moedas"] = user_data.get("moedas", 0) + valor

        await update_usuario(interaction.user.id, user_data)

        await interaction.response.edit_message(
            content=f"✅ Você vendeu a carta **{self.carta['nome']}** por **{valor} moedas**!",
            embed=None,
            view=None,
        )
        self.confirmado = True
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Venda cancelada.", embed=None, view=None)
        self.stop()


class VenderCartaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sell", description="Venda uma carta da sua coleção")
    @app_commands.describe(carta_id="ID da carta que será vendida")
    async def sell(self, interaction: discord.Interaction, carta_id: str):
        user_data = await get_usuario(interaction.user.id)
        cartas_ids = user_data.get("cartas", [])
        cartas_disponiveis = get_cartas_atualizadas()

        carta = next((c for c in cartas_disponiveis if c["id"] == carta_id), None)

        if not carta:
            await interaction.response.send_message("❌ Carta com esse ID não encontrada.", ephemeral=True)
            return

        if carta_id not in cartas_ids:
            await interaction.response.send_message("❌ Você não possui essa carta.", ephemeral=True)
            return

        valor = valores_raridade.get(carta["raridade"], 0)
        embed = discord.Embed(
            title="💸 Confirmar venda",
            description=f"Tem certeza que deseja vender a carta **{carta['nome']}** por **{valor} moedas**?",
            color=discord.Color.orange()
        )

        view = ConfirmSellCartaView(carta, user_data, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(VenderCartaCog(bot))
