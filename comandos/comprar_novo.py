import discord
from discord import app_commands
from discord.ext import commands
from database import get_usuario, update_usuario

import packs.blackpink as blackpink_pack
import packs.twice as twice_pack
# Importe outros packs que você tiver (ex: import packs.newjeans as newjeans_pack)

# Dicionários de packs (Mantenha a mesma estrutura do seu comprar.py atual)
# Certifique-se de que PACKS_FUNCS está mapeando corretamente para as funções de abertura de pack

class MockInteraction:
    def __init__(self, original_interaction: discord.Interaction):
        self.user = original_interaction.user
        self.channel = original_interaction.channel # Adicionar o canal também pode ser útil
        self.guild = original_interaction.guild # Adicionar o guild (servidor)
        self.response = original_interaction.response # Encaminha a resposta
        self.followup = original_interaction.followup # Encaminha o followup
        # Adicione outras propriedades se suas funções de pack as usarem (ex: message)
        self.message = original_interaction.message # Se a função do pack edita a mensagem
        self.client = original_interaction.client # O cliente do bot
PACKS = {
    "blackpink": [
        {"id": "blackpink_silverpack", "nome": "🎀 Blackpink Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "blackpink_goldpack", "nome": "🎀 Blackpink Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    "twice": [
        {"id": "twice_silverpack", "nome": "🍭 Twice Silver Pack", "cartas": 5, "preco": 50_000},
        {"id": "twice_goldpack", "nome": "🍭 Twice Gold Pack", "cartas": 10, "preco": 100_000},
    ],
    # Adicione outros grupos aqui, seguindo o mesmo padrão
}

PACKS_FUNCS = {
    "blackpink_silverpack": blackpink_pack.pack_blackpink_5, # Certifique-se que o nome da função está correto
    "blackpink_goldpack": blackpink_pack.pack_blackpink,     # Certifique-se que o nome da função está correto
    "twice_silverpack": twice_pack.pack_twice_5,
    "twice_goldpack": twice_pack.pack_twice,
    # Adicione as funções de packs para outros grupos
}

# --- Views de Interação (Dropdowns e Botões) ---

class ConfirmPurchaseView(discord.ui.View):
    def __init__(self, pack_info, user_id, abrir_pack_func, bot):
        super().__init__(timeout=60)
        self.pack_info = pack_info
        self.user_id = user_id
        self.abrir_pack_func = abrir_pack_func
        self.bot = bot # Passar o bot para poder usar suas funcionalidades (ex: await bot.get_channel)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa interação é apenas para quem usou o comando!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar Compra", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False) # Deferir para permitir o processamento
        self.stop() # Parar a view para que os botões fiquem desabilitados

        user_data = await get_usuario(self.user_id)
        saldo = user_data.get("moedas", 0)
        preco = self.pack_info["preco"]

        if saldo < preco:
            await interaction.followup.send(f"❌ Você não tem moedas suficientes para comprar **{self.pack_info['nome']}**! Seu saldo atual: `{saldo:,}` moedas.".replace(",", "."))
            return

        user_data["moedas"] -= preco
        await update_usuario(self.user_id, user_data)

        # Abrir o pack e dar as cartas
        mock_interaction = MockInteraction(interaction) # PASSE A INTERAÇÃO ORIGINAL COMPLETA AQUI
        cartas_sorteadas = await self.abrir_pack_func(self.bot, mock_interaction)   
        
        # MENSAGEM DE SUCESSO PÓS-COMPRA E ABERTURA
        embed_compra = discord.Embed(
            title=f"🎉 Compra e Abertura Realizadas!",
            description=f"Você comprou e abriu **{self.pack_info['nome']}** por `{preco:,}` moedas!".replace(",", "."),
            color=discord.Color.gold()
        )
        
        cartas_string = []
        for carta_data in cartas_sorteadas:
            # Encontrar o nome da carta, o ID e a raridade para exibir
            # Você precisa de um método para buscar a carta completa dado o ID
            # Por simplicidade, vou assumir que 'carta_data' já contém nome, grupo, raridade
            # Se 'carta_data' for apenas o ID da carta, você precisará buscar a info dela
            # Ex: carta_info = next((c for c in cartas_disponiveis if c["id"] == carta_data), None)
            # Para este exemplo, vou supor que cartas_sorteadas já retorna o dicionário completo da carta.
            # Se a função do pack retorna apenas os IDs, você precisará adaptar essa parte.
            # No seu `packs/blackpink.py` e `packs/twice.py`, as funções de pack já retornam objetos de carta completos.
            cartas_string.append(f"• {carta_data['nome']} ({carta_data['grupo']}) - {carta_data['raridade']}")
        
        embed_compra.add_field(name="Cartas Recebidas:", value="\n".join(cartas_string) if cartas_string else "Nenhuma carta.", inline=False)
        embed_compra.set_footer(text="Confira seu inventário com /inventory")
        
        await interaction.followup.send(embed=embed_compra)


    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Compra cancelada.", ephemeral=True)
        self.stop() # Parar a view

class SelectPackView(discord.ui.View):
    def __init__(self, user_id, bot):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.bot = bot # Passar o bot para o handler do select

        # Criar o Select para os Grupos
        grupo_options = [
            discord.SelectOption(label=grupo.capitalize(), value=grupo)
            for grupo in PACKS.keys()
        ]
        self.add_item(GroupSelect(grupo_options))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa interação é apenas para quem usou o comando!", ephemeral=True)
            return False
        return True

class GroupSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Selecione um grupo...", options=options, custom_id="group_select")

    async def callback(self, interaction: discord.Interaction):
        # NOTA: Não precisamos mais de interaction.response.defer(ephemeral=True) aqui.
        # Vamos diretamente editar a mensagem.

        selected_group = self.values[0]
        packs_do_grupo = PACKS.get(selected_group, [])

        if not packs_do_grupo:
            # Se não houver packs, ainda é bom enviar uma mensagem efêmera.
            await interaction.response.send_message("Nenhum pack disponível para este grupo.", ephemeral=True)
            return

        pack_options = [
            discord.SelectOption(label=pack["nome"], value=pack["id"], description=f"{pack['preco']:,} moedas".replace(",", "."))
            for pack in packs_do_grupo
        ]

        # Remover o Select de grupo e adicionar o Select de packs
        self.view.clear_items() # Remove o Select de grupo
        self.view.add_item(PackSelect(pack_options, selected_group)) # Adiciona o Select de packs
        
        # Opcional: Adicionar um botão "Voltar" para o Select de grupos
        self.view.add_item(BackButton(self.view.user_id, self.view.bot))

        # Criar um novo embed para exibir a mensagem "Escolha um pack"
        # e talvez detalhes do grupo
        new_embed = discord.Embed(
            title=f"🛒 Loja de Packs - {selected_group.capitalize()}",
            description=f"Você selecionou o grupo **{selected_group.capitalize()}**. Agora escolha um pack da lista abaixo:",
            color=discord.Color.blue()
        )
        # Opcional: Mostrar saldo atual aqui também
        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        new_embed.add_field(name="Seu Saldo Atual", value=f"`{saldo:,}` moedas".replace(",", "."), inline=False)

                # --- ADICIONE ESTE BLOCO DE CÓDIGO AQUI ---
        if selected_group.lower() == "blackpink":
            new_embed.set_image(url="https://i.pinimg.com/originals/4f/e7/d0/4fe7d00b623737e2c5131a70c967c0e3.gif")
        elif selected_group.lower() == "twice":
            # Exemplo de GIF para TWICE (substitua pelo que você quiser)
            new_embed.set_image(url="https://i.pinimg.com/originals/ea/f6/db/eaf6dba8ab5d3d07c293e52e68812882.gif")
        elif selected_group.lower() == "new jeans":
            # Exemplo de GIF para NEW JEANS
            new_embed.set_image(url="https://i.pinimg.com/originals/03/24/d5/0324d507b865b7a195c0a43033884667.gif")
        # Você pode continuar adicionando 'elif' para todos os seus outros grupos
        # Ex: elif selected_group.lower() == "aespa":
        #         new_embed.set_image(url="URL_DO_GIF_AESPA")
        # ... e assim por diante para DREAMCATCHER, GIDLE, etc.
        # --- FIM DO BLOCO DE CÓDIGO A SER ADICIONADO ---



        # **AQUI ESTÁ A MUDANÇA PRINCIPAL:** Edite a mensagem original.
        await interaction.response.edit_message(
            embed=new_embed, # O novo embed com a instrução
            view=self.view,
            content=None # Limpa qualquer conteúdo de texto anterior, se houver
        )
        # Remova a linha await interaction.followup.send(...)


class PackSelect(discord.ui.Select):
    def __init__(self, options, group_id):
        super().__init__(placeholder="Selecione um pack...", options=options, custom_id="pack_select")
        self.group_id = group_id # Para saber de qual grupo este pack pertence

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False) # Deferir para a resposta visível
        
        selected_pack_id = self.values[0]
        pack_info = next(
            (pack for pack in PACKS.get(self.group_id, []) if pack["id"] == selected_pack_id),
            None
        )

        if not pack_info:
            await interaction.followup.send("❌ Pack inválido. Tente novamente.", ephemeral=True)
            return

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)
        preco = pack_info["preco"]

        embed = discord.Embed(
            title=f"Confirmar Compra: {pack_info['nome']}",
            description=f"Você está prestes a comprar **{pack_info['nome']}** por `{preco:,}` moedas.".replace(",", "."),
            color=discord.Color.blue()
        )
        embed.add_field(name="Seu Saldo Atual", value=f"`{saldo:,}` moedas".replace(",", "."), inline=True)
        embed.add_field(name="Moedas Restantes (após compra)", value=f"`{saldo - preco:,}` moedas".replace(",", "."), inline=True)
        
        if saldo < preco:
            embed.set_footer(text="❌ Saldo insuficiente!")
            view = discord.ui.View(timeout=60) # Apenas para desabilitar, sem botões de compra
        else:
            view = ConfirmPurchaseView(pack_info, interaction.user.id, PACKS_FUNCS.get(selected_pack_id), self.view.bot)
            
        # Edita a mensagem original com o embed de confirmação e os botões
        await interaction.message.edit(embed=embed, view=view, content=None)
        


class BackButton(discord.ui.Button):
    def __init__(self, user_id, bot):
        super().__init__(label="🔙 Voltar aos Grupos", style=discord.ButtonStyle.secondary, custom_id="back_to_groups")
        self.user_id = user_id
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa interação é apenas para quem usou o comando!", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Recriar a view com os selects de grupo
        new_view = SelectPackView(self.user_id, self.bot)
        
        embed = discord.Embed(
            title="🛒 Loja de Packs",
            description=(
                f"Bem-vindo à loja de packs!\n"
                "Para comprar, siga os passos abaixo:\n"
                "1️⃣ Escolha um **Grupo** abaixo.\n"
                "2️⃣ Em seguida, escolha o **Pack** desejado para ver os detalhes e confirmar a compra.\n\n"
                "Boa sorte com suas coleções! ✨"
            ),
            color=discord.Color.green()
        )
        
        # Pegar o saldo atual do usuário para exibir no embed
        user_data = await get_usuario(self.user_id)
        saldo = user_data.get("moedas", 0)
        embed.add_field(name="Seu Saldo Atual", value=f"`{saldo:,}` moedas".replace(",", "."), inline=False)


        await interaction.message.edit(embed=embed, view=new_view, content=None)
        await interaction.followup.send("Você retornou à seleção de grupos.", ephemeral=True)

# --- Cog Principal ---

class ComprarV2Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="comprar2", description="Compre packs de cartas de forma interativa")
    async def comprar_v2(self, interaction: discord.Interaction):
        await interaction.response.defer() # Deferir para mostrar que está pensando

        user_data = await get_usuario(interaction.user.id)
        saldo = user_data.get("moedas", 0)

        embed = discord.Embed(
            title="🛒 Loja de Packs",
            description=(
                f"💰 **Saldo:** `{saldo:,}` moedas\n\n".replace(",", ".") +
                "Bem-vindo à loja de packs!\n"
                "Para comprar, siga os passos abaixo:\n"
                "1️⃣ Escolha um **Grupo** abaixo.\n"
                "2️⃣ Em seguida, escolha o **Pack** desejado para ver os detalhes e confirmar a compra.\n\n"
                "Boa sorte com suas coleções! ✨"
            ),
            color=discord.Color.green()
        )

        view = SelectPackView(interaction.user.id, self.bot)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ComprarV2Cog(bot))
