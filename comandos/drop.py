import random
import discord
from discord.ext import commands
from utils.imagens import juntar_imagens_lado_a_lado
from database import get_usuario, update_usuario
from cartas import cartas_disponiveis
from utils.conquistas import atualizar_conquistas
import time

probabilidades = {
    "Comum": 80,
    "Rara": 29,
    "Épica": 1
}

def sortear_raridade():
    raridades = list(probabilidades.keys())
    pesos = list(probabilidades.values())
    return random.choices(raridades, weights=pesos, k=1)[0]

claim_cooldowns = {}

class ClaimView(discord.ui.View):
    def __init__(self, ctx, cartas, caminho_imagem):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.cartas = cartas
        self.caminho_imagem = caminho_imagem
        self.reivindicadas = {}  # index: username
        self.claimed_users = set()  # user_id de quem já pegou
        self.message = None

        for i, carta in enumerate(cartas):
            self.add_item(ClaimButton(i, carta, self))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

        # criar embed com resultado final
        resultado_embed = discord.Embed(
            title="📦 Resultado do Drop",
            description="Veja quem pegou o quê!",
            color=discord.Color.dark_purple()
        )

        for i, carta in enumerate(self.cartas):
            pego_por = self.reivindicadas.get(i, "Ninguém pegou")
            era = carta.get("era", "Desconhecida")
            resultado_embed.add_field(
                name=f"{carta['nome']}",
                value=f"👤 Dono: **{pego_por}**\n🧪 Raridade: {carta['raridade']}\n📀 Era: {era}\n🆔 ID: `{carta['id']}`",
                inline=True
            )

        await self.ctx.send(embed=resultado_embed)

class ClaimButton(discord.ui.Button):
    def __init__(self, index, carta, parent_view):
        super().__init__(label=str(index + 1), style=discord.ButtonStyle.primary)
        self.index = index
        self.carta = carta
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_name = interaction.user.display_name

        now = time.time()
        last_claim = claim_cooldowns.get(user_id, 0)
        cooldown_time = 30

        if now - last_claim < cooldown_time:
            restante = int(cooldown_time - (now - last_claim))
            await interaction.response.send_message(
                f"⏳ Você está em cooldown! Não pode mais claimar cartas! Tente novamente em {restante} segundos.", ephemeral=True
            )
            return

        if user_id in self.parent_view.claimed_users:
            await interaction.response.send_message(
                "❌ Você já pegou uma carta nesse drop!", ephemeral=True
            )
            return

        if self.index in self.parent_view.reivindicadas:
            quem = self.parent_view.reivindicadas[self.index]
            await interaction.response.send_message(
                f"⚠️ A carta {self.carta['nome']} já foi escolhida por **{quem}**.", ephemeral=True
            )
            return

        claim_cooldowns[user_id] = now
        self.parent_view.reivindicadas[self.index] = user_name
        self.parent_view.claimed_users.add(user_id)

        user_data = await get_usuario(user_id)
        user_cartas = user_data.get("cartas", [])

        if self.carta["id"] in user_cartas:
            moedas = 50
            user_data["moedas"] = user_data.get("moedas", 0) + moedas
            await update_usuario(user_id, {"moedas": user_data["moedas"]})
            await interaction.response.send_message(
                f"💰 Você pegou **{self.carta['nome']}**, mas já tinha. Ganhou {moedas} moedas.",
                ephemeral=True
            )
        else:
            user_cartas.append(self.carta["id"])
            await update_usuario(user_id, {"cartas": user_cartas})
            await interaction.response.send_message(
                f"🎉 Você pegou a carta **{self.carta['nome']}**!",
                ephemeral=True
            )
            mensagens = await atualizar_conquistas(user_data, self.carta, user_id)
            for msg in mensagens:
                await interaction.followup.send(msg)

class Drop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def drop(self, ctx):
        cartas_sorteadas = []
        usadas = set()

        while len(cartas_sorteadas) < 3:
            raridade = sortear_raridade()
            candidatas = [c for c in cartas_disponiveis if c["raridade"] == raridade and c["id"] not in usadas]

            if not candidatas:
                continue
            carta = random.choice(candidatas)
            usadas.add(carta["id"])
            cartas_sorteadas.append(carta)

        cartas_para_juntar = [
            {"url": carta["imagem"], "raridade": carta["raridade"]}
            for carta in cartas_sorteadas
]
        caminho = juntar_imagens_lado_a_lado(cartas_para_juntar)

        embed = discord.Embed(
            title="🎴 Drop de Cartas!",
            description="Clique no botão abaixo para escolher **1** carta.\nOutras pessoas também podem pegar o resto!",
            color=discord.Color.purple()
        )
        embed.set_image(url="attachment://drop.png")

        file = discord.File(caminho, filename="drop.png")
        view = ClaimView(ctx, cartas_sorteadas, caminho)
        msg = await ctx.send(embed=embed, file=file, view=view)
        view.message = msg
    @drop.error
    async def drop_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            tempo = round(error.retry_after)
            minutos = tempo // 5
            segundos = tempo % 5

            tempo_formatado = f"{minutos}m {segundos}s" if minutos else f"{segundos}s"
            await ctx.send(f"🕒 Calma aí! Você só pode usar `drop` de novo em **{tempo_formatado}**.")


# carregar extensão
async def setup(bot):
    await bot.add_cog(Drop(bot))
