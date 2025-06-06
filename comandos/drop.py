import random
import discord
from discord.ext import commands
from utils.imagens import juntar_imagens_lado_a_lado
from database import get_usuario, update_usuario
from cartas import cartas_disponiveis
from utils.conquistas import atualizar_conquistas
from collections import Counter
import time
import asyncio 

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
        super().__init__(timeout=None)  # sem timeout automático
        self.ctx = ctx
        self.cartas = cartas
        self.caminho_imagem = caminho_imagem
        self.reivindicadas = {}
        self.claimed_users = set()
        self.message = None

        for i, carta in enumerate(cartas):
            self.add_item(ClaimButton(i, carta, self))

    async def mostrar_resultado(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

        resultado_embed = discord.Embed(
            title="📦 Resultado do Drop",
            description="Veja quem pegou o quê!",
            color=discord.Color.dark_purple()
        )

        for i, carta in enumerate(self.cartas):
            user_id = self.reivindicadas.get(i)
            if user_id:
                usuario = await get_usuario(user_id)
                user_cartas = usuario.get("cartas", [])
                era_carta = carta.get("era", "Desconhecida")

                carta_counts = Counter(user_cartas)

                cartas_era = [c for c in cartas_disponiveis if c.get("era") == era_carta]
                total_era = len(cartas_era)

                cartas_era_usuario_ids = {
                    cid for cid in set(user_cartas)
                    if any(c["id"] == cid and c.get("era") == era_carta for c in cartas_disponiveis)
                }

                progresso_era = f"{len(cartas_era_usuario_ids)}/{total_era}"
                qtd_carta = carta_counts.get(carta["id"], 0)
                quantidade_str = f"{qtd_carta}x" if qtd_carta > 0 else None

                dono_str = f"<@{user_id}>"
            else:
                dono_str = "Ninguém pegou"
                progresso_era = None
                quantidade_str = None

            value_lines = [
                f"👤 Dono: **{dono_str}**",
                f"🆔 ID: `{carta['id']}`",
                f"🧪 Raridade: {carta['raridade']}",
                f"📀 Era: {carta.get('era', 'Desconhecida')}"
            ]
            if quantidade_str is not None:
                value_lines.append(f"🎴 Quantidade: {quantidade_str}")
            if progresso_era is not None:
                value_lines.append(f"📊 Progresso na era: {progresso_era}")

            resultado_embed.add_field(
                name=f"{carta['nome']}",
                value="\n".join(value_lines),
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
            dono_id = self.parent_view.reivindicadas[self.index]
            await interaction.response.send_message(
                f"⚠️ A carta {self.carta['nome']} já foi escolhida por <@{dono_id}>.", ephemeral=True
            )
            return

        claim_cooldowns[user_id] = now
        self.parent_view.reivindicadas[self.index] = user_id  # salva user_id, não nome
        self.parent_view.claimed_users.add(user_id)

        user_data = await get_usuario(user_id)
        user_cartas = user_data.get("cartas", [])

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
        asyncio.create_task(mostrar_drop_depois(view))

        
    @drop.error
    async def drop_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            tempo = round(error.retry_after)
            minutos = tempo // 5
            segundos = tempo % 5

            tempo_formatado = f"{minutos}m {segundos}s" if minutos else f"{segundos}s"
            await ctx.send(f"🕒 Calma aí! Você só pode usar `drop` de novo em **{tempo_formatado}**.")
async def mostrar_drop_depois(view):
    await asyncio.sleep(30)
    await view.mostrar_resultado()



# carregar extensão
async def setup(bot):
    await bot.add_cog(Drop(bot))
