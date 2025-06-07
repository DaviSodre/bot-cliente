import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

import packs.blackpink as blackpink_pack
import packs.twice as twice_pack

CATEGORIAS = ["BLACKPINK", "TWICE", "NEW JEANS", "GIDLE"]

PACKS = {
    "BLACKPINK": [
        {"id": "blackpink_silver", "nome": "🎀 Blackpink Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "blackpink_gold", "nome": "🎀 Blackpink Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "TWICE": [
        {"id": "twice_silver", "nome": "🍭 Twice Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "twice_gold", "nome": "🍭 Twice Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    # outras categorias...
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
            title=f"💳 Loja - {self.categoria}",
            color=discord.Color.purple()
        )

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        embed.description = f"💰 **Saldo:** `{saldo:,} moedas`".replace(",", ".")

        packs_da_categoria = PACKS.get(self.categoria)

        if packs_da_categoria:
            descricao_formatada = f"══════ {self.categoria.upper()} ══════\n"
            for i, pack in enumerate(packs_da_categoria, start=1):
                nome = pack['nome']
                preco = f"{pack['preco']:,}".replace(",", ".")
                item = pack['id'].split("_")[1].lower() + "pack"
                grupo = pack['id'].split("_")[0].lower()
                descricao_formatada += (
                    f"{i}) {nome:<28} 💳 {preco} moedas\n"
                    f"     /comprar {item} {grupo}\n"
                )
            embed.add_field(name="Itens disponíveis", value=f"```{descricao_formatada}```", inline=False)
            embed.set_footer(text="Use /comprar <item> <grupo> para adquirir um item.")
        else:
            embed.description += "\n🚧 Essa categoria ainda está em construção..."

        view = VoltarOnlyView()
        await interaction.response.edit_message(embed=embed, view=view)

class VoltarOnlyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(VoltarButton())

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
                "🛒 Bem-vindo à loja de packs & itens! Para comprar:\n"
                "1️⃣ Escolha uma categoria clicando nos botões abaixo.\n"
                "2️⃣ Veja os itens disponíveis e copie o comando indicado abaixo de cada um!\n"
                "3️⃣ Use o comando `/comprar <item> <grupo>` para comprar.\n"
                "   Ex: `/comprar goldpack blackpink`\n"
                "4️⃣ Após a compra, receba suas cartas e aproveite sua coleção!\n\n"
                "💡 Packs especiais podem conter cartas raras e efeitos exclusivos.\n"
                "⚠️ Verifique seu saldo antes de comprar.\n\n"
                "👇 Clique nos botões abaixo para começar a explorar."
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
                "🛒 Bem-vindo à loja de packs & itens! Para comprar:\n"
                "1️⃣ Escolha uma categoria clicando nos botões abaixo.\n"
                "2️⃣ Veja os itens disponíveis e copie o comando indicado abaixo de cada um!\n"
                "3️⃣ Use o comando `/comprar <item> <grupo>` para comprar.\n"
                "   Ex: `/comprar goldpack blackpink`\n"
                "4️⃣ Após a compra, receba suas cartas e aproveite sua coleção!\n\n"
                "💡 Packs especiais podem conter cartas raras e efeitos exclusivos.\n"
                "⚠️ Verifique seu saldo antes de comprar.\n\n"
                "👇 Clique nos botões abaixo para começar a explorar."
            ),
            color=discord.Color.green()
        )
        view = LojaView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LojaCog(bot))
