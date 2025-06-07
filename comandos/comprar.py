import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

import packs.blackpink as blackpink_pack
import packs.twice as twice_pack

RARIDADES = ["silver", "gold"]
GRUPOS = ["blackpink", "twice"]

PACKS = {
    "blackpink": [
        {"id": "blackpink_silver", "nome": "🎀 Blackpink Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "blackpink_gold", "nome": "🎀 Blackpink Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "twice": [
        {"id": "twice_silver", "nome": "🍭 Twice Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "twice_gold", "nome": "🍭 Twice Gold Pack", "cartas": 10, "preco": 100_000},
    ],
}

PACKS_FUNCS = {
    "blackpink_silver": blackpink_pack.pack_blackpink_5,
    "blackpink_gold": blackpink_pack.pack_blackpink,
    "twice_silver": twice_pack.pack_twice_5,
    "twice_gold": twice_pack.pack_twice,
}

class ComprarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="comprar", description="Compre um pack de cartas na loja")
    @app_commands.describe(raridade="silver ou gold", grupo="Nome do grupo, ex: blackpink")
    @app_commands.choices(
        raridade=[app_commands.Choice(name="Silver", value="silver"),
                  app_commands.Choice(name="Gold", value="gold")],
        grupo=[app_commands.Choice(name="BLACKPINK", value="blackpink"),
               app_commands.Choice(name="TWICE", value="twice")]
    )
    async def comprar(self, interaction: discord.Interaction, raridade: app_commands.Choice[str], grupo: app_commands.Choice[str]):
        await interaction.response.defer()
        pack_id = f"{grupo.value}_{raridade.value}"

        pack_info = next(
            (pack for pack in PACKS.get(grupo.value, []) if pack["id"] == pack_id),
            None
        )

        if not pack_info:
            await interaction.followup.send("❌ Pack inválido! Verifique os dados e tente novamente.")
            return

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        preco = pack_info["preco"]

        if saldo < preco:
            await interaction.followup.send(f"❌ Você não tem moedas suficientes! Seu saldo atual: `{saldo:,}` moedas".replace(",", "."))
            return

        # desconta
        user_data["moedas"] -= preco
        await update_usuario(interaction.user.id, user_data)

        await interaction.followup.send(f"🎉 Você comprou o pack **{pack_info['nome']}**! Abrindo o pacote...")

        abrir_pack = PACKS_FUNCS.get(pack_id)
        if abrir_pack:
            await abrir_pack(self.bot, interaction)
        else:
            await interaction.followup.send("❌ Esse pack ainda não está disponível para compra.")

async def setup(bot):
    await bot.add_cog(ComprarCog(bot))
