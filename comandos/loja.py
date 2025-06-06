import discord
from discord import app_commands
from discord.ext import commands
import packs.blackpink as blackpink_pack
import packs.twice as twice_pack
from database import get_usuario, update_usuario

CATEGORIAS = ["BLACKPINK", "TWICE", "NEW JEANS", "GIDLE"]

PACKS = {
    "BLACKPINK": [
        {"nome": "Pack Blackpink 1", "cartas": 10, "preco": 100_000, "emoji": "🎀"},
        {"nome": "Pack Blackpink 2", "cartas": 5, "preco": 50_000, "emoji": "🎀"},
    ],
    "TWICE": [
        {"nome": "Pack Twice 1", "cartas": 10, "preco": 100_000, "emoji": "🍭"},
        {"nome": "Pack Twice 2", "cartas": 5, "preco": 50_000, "emoji": "🍭"},
    ],
    # adiciona outras categorias aqui
}

class LojaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for categoria in CATEGORIAS:
            self.add_item(LojaButton(categoria))

class LojaButton(discord.ui.Button):
    def __init__(self, categoria):
        super().__init__(label=categoria, style=discord.ButtonStyle.primary)
        self.categoria = categoria

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🧺 Loja - {self.categoria}",
            description="Escolha um dos packs disponíveis abaixo:",
            color=discord.Color.purple()
        )

        packs_da_categoria = PACKS.get(self.categoria)

        if packs_da_categoria:
            for pack in packs_da_categoria:
                nome = f"{pack['emoji']} {pack['nome']}"
                valor = f"📦 **{pack['cartas']} cartas**\n💰 **{pack['preco']:,} moedas**".replace(",", ".")
                embed.add_field(name=nome, value=valor, inline=False)
        else:
            embed.description = "🚧 Essa categoria ainda está em construção..."

        view = CategoriaView(self.categoria)
        await interaction.response.edit_message(embed=embed, view=view)

class CategoriaView(discord.ui.View):
    def __init__(self, categoria):
        super().__init__(timeout=120)
        self.categoria = categoria
        
        # dicionário com packs, cada um com nome e preço
        packs = {
            "BLACKPINK": [
                {"nome": "Pack Blackpink 1", "cartas": 10, "preco": 100_000, "emoji": "🎀"},
                {"nome": "Pack Blackpink 2", "cartas": 5, "preco": 50_000, "emoji": "🎀"},
            ],
            "TWICE": [
                {"nome": "Pack Twice 1", "cartas": 10, "preco": 100_000, "emoji": "🍭"},
                {"nome": "Pack Twice 2", "cartas": 5, "preco": 50_000, "emoji": "🍭"},
            ],
            # adiciona outras categorias aqui
        }


        packs_da_categoria = packs.get(categoria, [])

        for i, pack_info in enumerate(packs_da_categoria, start=1):
            self.add_item(ComprarButton(categoria, i, pack_info["nome"], pack_info["preco"]))

        self.add_item(VoltarButton())

class ComprarButton(discord.ui.Button):
    def __init__(self, categoria, pack_numero, pack_nome, preco):
        super().__init__(label=f"Comprar {pack_nome}", style=discord.ButtonStyle.success)
        self.categoria = categoria
        self.pack_numero = pack_numero
        self.pack_nome = pack_nome
        self.preco = preco

    async def callback(self, interaction: discord.Interaction):
        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)

        if saldo < self.preco:
            await interaction.response.send_message(
                f"😢 Você não tem moedas suficientes! Precisa de {self.preco}, mas tem {saldo}.",
                ephemeral=True
            )
            return

        # desconta o preço
        user_data["moedas"] = saldo - self.preco
        await update_usuario(interaction.user.id, user_data)

        await interaction.response.defer()
        await interaction.followup.send(f"🎉 Parabéns, você comprou **{self.pack_nome}**! Abrindo seu pack...")

        # chama função do pack correto
        if self.categoria == "BLACKPINK":
            if self.pack_numero == 1:
                await blackpink_pack.pack_blackpink(interaction.client, interaction)
            elif self.pack_numero == 2:
                await blackpink_pack.pack_blackpink_5(interaction.client, interaction)
            else:
                await interaction.response.send_message("Pack ainda não implementado.", ephemeral=True)
                return
        elif self.categoria == "TWICE":
            if self.pack_numero == 1:
                await twice_pack.pack_twice(interaction.client, interaction)
            elif self.pack_numero == 2:
                await twice_pack.pack_twice_5(interaction.client, interaction)
            else:
                await interaction.response.send_message("Pack ainda não implementado.", ephemeral=True)
                return

        
    

class VoltarButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Voltar", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)  
        embed = discord.Embed(
            title="🛒 Loja de Packs & Itens",
            description=(
                f"💰 **Saldo:** `{saldo} moedas`\n\n"
                "Aqui você pode comprar packs de cartas, itens especiais, e muitas outras coisas!\n\n"
                "Cada categoria tem packs diferentes, escolha uma abaixo para ver o que tem.\n"
                "Quando abrir uma categoria, verá os packs numerados para escolher o que comprar.\n\n"
                "💰 Use suas moedas para comprar, ganhe cartas e colecione!\n"
                "🎉 Packs especiais podem conter cartas raras e épicas com efeitos incríveis.\n"
                "⚠️ Fique de olho no saldo para não ficar sem moedas!\n\n"
                "Clique nos botões abaixo para começar sua compra."
            ),
            color=discord.Color.green()
        )
        view = LojaView()
        await interaction.response.edit_message(embed=embed, view=view)

class LojaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loja", description="Abra a loja de packs")
    async def loja(self, interaction: discord.Interaction):
        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        embed = discord.Embed(
            title="🛒 Loja de Packs & Itens",
            description=(
                f"💰 **Saldo:** `{saldo} moedas`\n\n"
                "Aqui você pode comprar packs de cartas, itens especiais, e muitas outras coisas!\n\n"
                "Cada categoria tem packs diferentes, escolha uma abaixo para ver o que tem.\n"
                "Quando abrir uma categoria, verá os packs numerados para escolher o que comprar.\n\n"
                "💰 Use suas moedas para comprar, ganhe cartas e colecione!\n"
                "🎉 Packs especiais podem conter cartas raras e épicas com efeitos incríveis.\n"
                "⚠️ Fique de olho no saldo para não ficar sem moedas!\n\n"
                "Clique nos botões abaixo para começar sua compra."
            ),
            color=discord.Color.green()
        )
        view = LojaView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LojaCog(bot))
