import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario
from cartas import cartas_disponiveis 
from collections import Counter


def get_unique_groups_and_eras():
    groups = set()
    eras = set()
    for carta in cartas_disponiveis:
        groups.add(carta["grupo"])
        if "era" in carta:
            eras.add(carta["era"])
    return sorted(list(groups)), sorted(list(eras))


class ColecaoView(discord.ui.View):
    def __init__(self, bot, user_id, filtro_grupo=None, filtro_era=None, page=0):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.filtro_grupo = filtro_grupo.lower() if filtro_grupo else None
        self.filtro_era = filtro_era.lower() if filtro_era else None
        self.page = page
        self.total_paginas = 1

    async def get_collection_data(self):
        user_data = await get_usuario(self.user_id)
        user_card_ids = user_data.get("cartas", [])
        user_card_counts = Counter(user_card_ids)

        filtered_available_cards = []
        for carta in cartas_disponiveis:
            match_group = (self.filtro_grupo is None) or (carta["grupo"].lower() == self.filtro_grupo)
            match_era = (self.filtro_era is None) or (carta.get("era", "desconhecida").lower() == self.filtro_era)

            if match_group and match_era:
                filtered_available_cards.append(carta)

        filtered_available_cards.sort(key=lambda c: (c["grupo"], c["nome"], c["raridade"]))

        collection_status = []
        for carta in filtered_available_cards:
            possessed = carta["id"] in user_card_ids
            quantity = user_card_counts.get(carta["id"], 0)
            collection_status.append({
                "carta": carta,
                "possessed": possessed,
                "quantity": quantity
            })
        
        return collection_status

    async def get_embed(self):
        collection_status = await self.get_collection_data()
        
        total_cards_in_filter = len(collection_status)
        possessed_cards_in_filter = sum(1 for item in collection_status if item["possessed"])

        self.total_paginas = max(1, (total_cards_in_filter + 8) // 9)
        self.page = max(0, min(self.page, self.total_paginas - 1))

        start = self.page * 9
        end = start + 9
        cards_on_page = collection_status[start:end]

        embed_title = "📸 Sua Coleção de Cartas"
        filter_description = ""
        if self.filtro_grupo and self.filtro_era:
            filter_description = f"Grupo: **{self.filtro_grupo.capitalize()}** | Era: **{self.filtro_era.capitalize()}**"
        elif self.filtro_grupo:
            filter_description = f"Grupo: **{self.filtro_grupo.capitalize()}**"
        elif self.filtro_era:
            filter_description = f"Era: **{self.filtro_era.capitalize()}**"
        else:
            filter_description = "Todas as cartas disponíveis"

        embed = discord.Embed(
            title=embed_title,
            description=(
                f"{filter_description}\n"
                f"Progresso: **{possessed_cards_in_filter}/{total_cards_in_filter}** cartas ({((possessed_cards_in_filter / total_cards_in_filter) * 100):.2f}%)\n\n"
                f"Página {self.page + 1} de {self.total_paginas}"
            ),
            color=discord.Color.dark_magenta()
        )

        for item in cards_on_page:
            carta = item["carta"]
            status_emoji = "✅" if item["possessed"] else "❌"
            quantity_str = f" ({item['quantity']}x)" if item["quantity"] > 1 else ""

            embed.add_field(
                name=f"{status_emoji} {carta['nome']}{quantity_str} (ID: `{carta['id']}`)",
                value=(
                    f"Grupo: {carta['grupo']}\n"
                    f"Raridade: {carta['raridade']}\n"
                    f"Era: {carta.get('era', 'Desconhecida')}"
                ),
                inline=True
            )
        
        embed.set_footer(text="Bot desenvolvido por TwiceFla & Kendo", icon_url=self.bot.user.avatar.url)
        return embed

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, custom_id="colecao_prev")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Só quem usou o comando pode navegar aqui!", ephemeral=True)
            return
        
        if self.page > 0:
            await interaction.response.defer()
            self.page -= 1
            await interaction.message.edit(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.send_message("Você já está na primeira página!", ephemeral=True)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, custom_id="colecao_next")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Só quem usou o comando pode navegar aqui!", ephemeral=True)
            return

        if self.page < self.total_paginas - 1:
            await interaction.response.defer()
            self.page += 1
            await interaction.message.edit(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.send_message("Você já está na última página!", ephemeral=True)


class Colecao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    async def grupo_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        groups, _ = get_unique_groups_and_eras()
        return [
            app_commands.Choice(name=group, value=group)
            for group in groups if current.lower() in group.lower()
        ][:25] 

    
    async def era_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        _, eras = get_unique_groups_and_eras()
        return [
            app_commands.Choice(name=era, value=era)
            for era in eras if current.lower() in era.lower()
        ][:25] 

    @app_commands.command(name="colecao", description="Mostra o progresso da sua coleção de cartas por grupo ou era")
    @app_commands.describe(grupo="Filtrar por grupo", era="Filtrar por era")
    
    @app_commands.autocomplete(grupo=grupo_autocomplete)
    @app_commands.autocomplete(era=era_autocomplete)
    async def colecao_command(self, interaction: discord.Interaction, grupo: str = None, era: str = None):
        await interaction.response.defer()

        view = ColecaoView(self.bot, interaction.user.id, filtro_grupo=grupo, filtro_era=era)
        embed = await view.get_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Colecao(bot))
