import discord
from discord import app_commands
from discord.ext import commands
from database import usuarios # Importa a coleção 'usuarios' diretamente

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="top2", description="Mostra o ranking dos usuários")
    @app_commands.describe(criterio="O critério para o ranking (moedas ou cartas)")
    @app_commands.choices(
        criterio=[
            app_commands.Choice(name="Moedas", value="moedas"),
            app_commands.Choice(name="Cartas", value="cartas")
        ]
    )
    async def top(self, interaction: discord.Interaction, criterio: app_commands.Choice[str]):
        await interaction.response.defer()

        # Busca todos os usuários do banco de dados
        # A função find().to_list(length=None) recupera todos os documentos
        todos_usuarios = await usuarios.find({}).to_list(length=None)

        if criterio.value == "moedas":
            # Ordena os usuários por moedas em ordem decrescente
            ranking_sorted = sorted(todos_usuarios, key=lambda x: x.get("moedas", 0), reverse=True)
            titulo = "💰 Top 10 Usuários por Moedas"
            campo_valor = "moedas"
            emoji = "💰"
        elif criterio.value == "cartas":
            # Ordena os usuários por quantidade de cartas em ordem decrescente
            ranking_sorted = sorted(todos_usuarios, key=lambda x: len(x.get("cartas", [])), reverse=True)
            titulo = "🎴 Top 10 Usuários por Cartas"
            campo_valor = "cartas"
            emoji = "🎴"
        else:
            await interaction.followup.send("❌ Critério inválido. Escolha entre 'moedas' ou 'cartas'.")
            return

        embed = discord.Embed(
            title=titulo,
            color=discord.Color.gold()
        )

        if not ranking_sorted:
            embed.description = "Nenhum usuário encontrado no ranking."
        else:
            description_lines = []
            for i, user_data in enumerate(ranking_sorted[:10]): # Limita aos 10 primeiros
                user_id = user_data["user_id"]
                member = interaction.guild.get_member(user_id) # Tenta pegar o membro do servidor
                
                if member:
                    nome_usuario = member.display_name
                else:
                    # Se o membro não for encontrado no servidor, tenta buscar o nome do usuário pelo ID
                    try:
                        user_obj = await self.bot.fetch_user(user_id)
                        nome_usuario = user_obj.display_name
                    except discord.NotFound:
                        nome_usuario = "Usuário Desconhecido"


                valor = user_data.get(campo_valor, 0)
                if campo_valor == "cartas":
                    valor = len(valor) # Pega o tamanho da lista de cartas

                description_lines.append(f"{i+1}º. **{nome_usuario}** - {valor:,} {emoji}".replace(",", "."))

            embed.description = "\n".join(description_lines)

        embed.set_footer(text="Bot desenvolvido por TwiceFla & Kendo", icon_url=self.bot.user.avatar.url)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Top(bot))
