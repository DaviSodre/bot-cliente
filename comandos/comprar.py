import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

import packs.blackpink as blackpink_pack
import packs.twice as twice_pack

ITENS = ["silverpack", "goldpack"]
GRUPOS = ["blackpink", "twice"]

PACKS = {
    "blackpink": [
        {"id": "blackpink_silverpack", "nome": "🎀 Blackpink Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "blackpink_goldpack", "nome": "🎀 Blackpink Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "twice": [
        {"id": "twice_silverpack", "nome": "🍭 Twice Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "twice_goldpack", "nome": "🍭 Twice Gold Pack", "cartas": 10, "preco": 100_000},
    ],
}

PACKS_FUNCS = {
    "blackpink_silverpack": blackpink_pack.pack_blackpink_5,
    "blackpink_goldpack": blackpink_pack.pack_blackpink,
    "twice_silverpack": twice_pack.pack_twice_5,
    "twice_goldpack": twice_pack.pack_twice,
}

class ComprarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="comprar", description="Compre um item da loja")
    @app_commands.describe(item="Ex: silverpack ou goldpack", grupo="Nome do grupo, ex: blackpink")
    @app_commands.choices(
        item=[
            app_commands.Choice(name="Silver Pack", value="silverpack"),
            app_commands.Choice(name="Gold Pack", value="goldpack")
        ],
        grupo=[
            app_commands.Choice(name="BLACKPINK", value="blackpink"),
            app_commands.Choice(name="TWICE", value="twice")
        ]
    )
    async def comprar(self, interaction: discord.Interaction, item: app_commands.Choice[str], grupo: app_commands.Choice[str]):
        await interaction.response.defer()
        pack_id = f"{grupo.value}_{item.value}"

        pack_info = next(
            (pack for pack in PACKS.get(grupo.value, []) if pack["id"] == pack_id),
            None
        )

        if not pack_info:
            await interaction.followup.send("❌ Item inválido! Verifique os dados e tente novamente.")
            return

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        preco = pack_info["preco"]

        if saldo < preco:
            await interaction.followup.send(f"❌ Você não tem moedas suficientes! Seu saldo atual: `{saldo:,}` moedas".replace(",", "."))
            return

        user_data["moedas"] -= preco
        await update_usuario(interaction.user.id, user_data)

        await interaction.followup.send(f"🎉 Você comprou **{pack_info['nome']}**! Abrindo o pacote...")

        abrir_pack = PACKS_FUNCS.get(pack_id)
        if abrir_pack:
            await abrir_pack(self.bot, interaction)
        else:
            await interaction.followup.send("❌ Esse item ainda não está disponível para compra.")

async def setup(bot):
    await bot.add_cog(ComprarCog(bot))
