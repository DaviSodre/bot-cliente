import discord
from discord import app_commands
from discord.ext import commands
from database import usuarios # Importa diretamente a coleção 'usuarios' do seu database.py

# Seus IDs autorizados (garanta que estes IDs estão corretos e atualizados)
IDS_AUTORIZADOS = [209387134715559946, 1069582140834066442] # Os mesmos IDs do seu bot.py e dar_carta.py

class DeletarDatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="deletardatabase", description="Apaga um usuário da base de dados (apenas IDs autorizados)")
    @app_commands.describe(user_id="O ID do usuário a ser apagado da base de dados")
    async def deletar_database_command(self, interaction: discord.Interaction, user_id: str):
        # 1. Verificação de Permissão: Apenas IDs autorizados podem usar este comando.
        if interaction.user.id not in IDS_AUTORIZADOS:
            await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True) # Deferir para que a operação possa levar um tempo

        try:
            # Tenta converter o user_id para inteiro, pois IDs do Discord são numéricos
            user_id_int = int(user_id)
        except ValueError:
            await interaction.followup.send("❌ O ID do usuário fornecido não é um número válido.")
            return

        # 2. Busca e Deleção: Tenta encontrar e deletar o usuário
        result = await usuarios.delete_one({"user_id": user_id_int})

        # 3. Confirmação: Verifica se a deleção foi bem-sucedida
        if result.deleted_count == 1:
            # Tenta pegar o nome do usuário para a mensagem de sucesso
            try:
                user_obj = await self.bot.fetch_user(user_id_int)
                user_name = user_obj.display_name
            except discord.NotFound:
                user_name = f"ID: {user_id_int}" # Se não encontrar o usuário, mostra o ID

            await interaction.followup.send(f"✅ Usuário `{user_name}` (ID: `{user_id_int}`) foi apagado da base de dados com sucesso.")
        else:
            await interaction.followup.send(f"⚠️ Usuário com ID `{user_id_int}` não foi encontrado na base de dados.")

# Função de setup para carregar o cog
async def setup(bot):
    await bot.add_cog(DeletarDatabase(bot))
