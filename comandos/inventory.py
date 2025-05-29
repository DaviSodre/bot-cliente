import discord
from discord.ext import commands
from database import get_usuario
from cartas import cartas_disponiveis
from collections import Counter

class InventoryView(discord.ui.View):
    def __init__(self, user_id, grupo=None, raridade=None, page=0):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.grupo = grupo
        self.raridade = raridade
        self.page = page

    async def get_filtered_cards(self):
        user_data = await get_usuario(self.user_id)
        user_cards = user_data.get("cartas", [])  # lista com repetições

        # contar quantas vezes cada carta aparece
        carta_counts = Counter(user_cards)

        # montar lista de cartas únicas com quantidade
        cartas_info = []
        for carta_id, quantidade in carta_counts.items():
            carta = next((c for c in cartas_disponiveis if c["id"] == carta_id), None)
            if not carta:
                continue
            if self.grupo and carta["grupo"].lower() != self.grupo.lower():
                continue
            if self.raridade and carta["raridade"].lower() != self.raridade.lower():
                continue
            cartas_info.append({
                "nome": carta["nome"],
                "id": carta["id"],
                "grupo": carta["grupo"],
                "raridade": carta["raridade"],
                "quantidade": quantidade
            })

        return cartas_info

    async def get_embed(self):
        cartas = await self.get_filtered_cards()
        total_paginas = max(1, (len(cartas) + 8) // 9)

        # limitar página
        self.page = max(0, min(self.page, total_paginas - 1))

        start = self.page * 9
        end = start + 9
        cartas_pagina = cartas[start:end]

        embed = discord.Embed(
            title=f"📦 Inventário de Cartas",
            description=f"Total: {len(cartas)} carta(s) únicas\nPágina {self.page + 1} de {total_paginas}",
            color=discord.Color.blurple()
        )

        for carta in cartas_pagina:
            embed.add_field(
                name=f"**{carta['nome']}** (ID: `{carta['id']}`)",
                value=(
                    f"Grupo: {carta['grupo']}\n"
                    f"Quantidade: {carta['quantidade']}\n"
                    f"Raridade: {carta['raridade']}"
                ),
                inline=True
            )

        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Só quem usou o comando pode navegar aqui!", ephemeral=True)
            return
        
        await interaction.response.defer()
        self.page -= 1
        await interaction.message.edit(embed=await self.get_embed(), view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Só quem usou o comando pode navegar aqui!", ephemeral=True)
            return

        await interaction.response.defer()
        self.page += 1
        await interaction.message.edit(embed=await self.get_embed(), view=self)

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="inventory", description="Mostra seu inventário de cartas")
    @discord.app_commands.describe(grupo="Filtrar por grupo da carta", raridade="Filtrar por raridade da carta")
    async def inventory(self, interaction: discord.Interaction, grupo: str = None, raridade: str = None):
        view = InventoryView(interaction.user.id, grupo=grupo, raridade=raridade)
        embed = await view.get_embed()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
