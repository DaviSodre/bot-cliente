import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

# Suas categorias de packs
CATEGORIAS = ["BLACKPINK", "TWICE", "NEW JEANS", "AESPA", "DREAMCATCHER", "GIDLE"] # Adicione todas as suas categorias aqui!

PACKS = {
    "BLACKPINK": [
        {"id": "blackpink_silver", "nome": "🎀 Blackpink Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "blackpink_gold", "nome": "🎀 Blackpink Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "TWICE": [
        {"id": "twice_silver", "nome": "🍭 Twice Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "twice_gold", "nome": "🍭 Twice Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    # Adicione as outras categorias e seus packs aqui
    "NEW JEANS": [
        # Exemplo de packs para New Jeans (assumindo que você os tenha)
        {"id": "newjeans_silver", "nome": "👖 New Jeans Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "newjeans_gold", "nome": "👖 New Jeans Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "AESPA": [
        {"id": "aespa_silver", "nome": "✨ AESPA Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "aespa_gold", "nome": "✨ AESPA Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "DREAMCATCHER": [
        {"id": "dreamcatcher_silver", "nome": "🕷️ Dreamcatcher Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "dreamcatcher_gold", "nome": "🕷️ Dreamcatcher Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "GIDLE": [
        {"id": "gidle_silver", "nome": "👑 GIDLE Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "gidle_gold", "nome": "👑 GIDLE Gold Pack", "cartas": 10, "preco": 100_000},
    ]
}


# --- Views de Interação ---

class LojaCategorySelect(discord.ui.Select):
    def __init__(self, user_id):
        super().__init__(
            placeholder="Escolha uma categoria de packs...",
            options=[discord.SelectOption(label=cat, value=cat) for cat in CATEGORIAS],
            custom_id="loja_category_select"
        )
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa interação é apenas para quem usou o comando!", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False) # Deferir para que a resposta seja visível

        selected_category = self.values[0]
        
        embed = discord.Embed(
            title=f"💳 Loja - {selected_category}",
            color=discord.Color.purple()
        )

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        embed.description = f"💰 **Seu Saldo:** `{saldo:,} moedas`".replace(",", ".")

        packs_da_categoria = PACKS.get(selected_category)

        if packs_da_categoria:
            descricao_formatada = ""
            for i, pack in enumerate(packs_da_categoria, start=1):
                nome = pack['nome']
                preco = f"{pack['preco']:,}".replace(",", ".")
                # Para mostrar como usar o /comprar_v2
                item_value_for_command = pack['id'].split("_")[1].replace("pack", "").lower()
                grupo_value_for_command = pack['id'].split("_")[0].lower()
                descricao_formatada += (
                    f"**{nome}**\n"
                    f"  💳 Preço: `{preco} moedas`\n"
                    f"  📦 Cartas por pack: {pack['cartas']}\n"
                    f"  👉 Use `/comprar2` e selecione **{grupo_value_for_command.capitalize()}** e depois **{nome}**.\n\n" # Instrução para o novo comando
                )
            embed.add_field(name="Itens disponíveis", value=descricao_formatada, inline=False)
            embed.set_footer(text="Use o comando /comprar2 para adquirir um item de forma interativa.")
        else:
            embed.description += "\n🚧 Essa categoria ainda está em construção ou não possui packs."

        view = LojaCategorySelectView(interaction.user.id, selected_category_value=selected_category)
        await interaction.message.edit(embed=embed, view=view)


class LojaCategorySelectView(discord.ui.View):
    def __init__(self, user_id, selected_category_value=None):
        super().__init__(timeout=120)
        self.user_id = user_id
        
        # Adiciona o dropdown de categorias
        self.add_item(LojaCategorySelect(user_id))
        
        # Opcional: pré-selecionar a categoria no dropdown se já houver uma selecionada
        if selected_category_value:
            for option in self.children[0].options:
                if option.value == selected_category_value:
                    option.default = True
                    break

        self.add_item(ReturnToMainLojaButton(user_id))


class ReturnToMainLojaButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="🔙 Voltar ao Início da Loja", style=discord.ButtonStyle.secondary, custom_id="loja_main_button")
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa interação é apenas para quem usou o comando!", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # Re-cria e envia o embed inicial da loja
        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        embed = discord.Embed(
            title="🛒 Loja de Packs & Itens",
            description=(
                f"💰 **Seu Saldo:** `{saldo:,} moedas`\n\n".replace(",", ".") +
                "Bem-vindo à loja de packs & itens!\n"
                "Aqui você pode explorar os packs disponíveis.\n"
                "Para comprar, use o comando `/comprar2` e siga as instruções interativas.\n\n"
                "👇 **Escolha uma categoria de packs no menu abaixo:**"
            ),
            color=discord.Color.green()
        )
        view = LojaCategorySelectView(interaction.user.id)
        await interaction.message.edit(embed=embed, view=view)


class Loja2Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loja2", description="Abra a loja de packs e veja os itens disponíveis")
    async def loja(self, interaction: discord.Interaction):
        await interaction.response.defer() # Deferir para mostrar que está pensando

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        embed = discord.Embed(
            title="🛒 Loja de Packs & Itens",
            description=(
                f"💰 **Seu Saldo:** `{saldo:,}` moedas\n\n".replace(",", ".") +
                "Bem-vindo à loja de packs & itens!\n"
                "Aqui você pode explorar os packs disponíveis.\n"
                "Para comprar, use o comando `/comprar2` e siga as instruções interativas.\n\n"
                "👇 **Escolha uma categoria de packs no menu abaixo:**"
            ),
            color=discord.Color.green()
        )
        view = LojaCategorySelectView(interaction.user.id)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LojaCog(bot))
