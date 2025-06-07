import random
from database import get_usuario, update_usuario
from PIL import Image
import aiohttp
import io
import discord
from cartas import cartas_disponiveis

async def pack_blackpink(bot, interaction):
    user_data = await get_usuario(interaction.user.id)

    cartas_blackpink = [c for c in cartas_disponiveis if c.get("grupo", "").upper() == "BLACKPINK"]

    cartas_ganhas = random.sample(cartas_blackpink, 10)
    ids_ganhas = [c["id"] for c in cartas_ganhas]
    user_data["cartas"].extend(ids_ganhas)

    await update_usuario(interaction.user.id, user_data)

    cartas_epicas = [c for c in cartas_ganhas if c.get("raridade", "").upper() == "ÉPICA"]
    if cartas_epicas:
        embed_epica = discord.Embed(
            title="🌟 Você conseguiu uma carta ÉPICA!",
            description=f"**{cartas_epicas[0]['nome']}** ({cartas_epicas[0]['era']})",
            color=discord.Color.gold()
        )
        embed_epica.set_image(url=cartas_epicas[0]["gif"])
        await interaction.followup.send(embed=embed_epica)

    final_img = await colar_cartas_em_grid(cartas_ganhas, cols=5, rows=2)
    file = discord.File(fp=final_img, filename="cartas.png")

    embed = discord.Embed(
        title="📦 Pack Aberto!",
        description="As 10 cartas foram adicionadas ao seu inventário!",
        color=discord.Color.purple()
    )
    embed.set_image(url="attachment://cartas.png")
    await interaction.followup.send(embed=embed, file=file)

async def pack_blackpink_5(bot, interaction):
    user_data = await get_usuario(interaction.user.id)

    cartas_blackpink = [c for c in cartas_disponiveis if c.get("grupo", "").upper() == "BLACKPINK"]

    cartas_ganhas = random.sample(cartas_blackpink, 5)
    ids_ganhas = [c["id"] for c in cartas_ganhas]
    user_data["cartas"].extend(ids_ganhas)

    await update_usuario(interaction.user.id, user_data)

    cartas_epicas = [c for c in cartas_ganhas if c.get("raridade", "").upper() == "ÉPICA"]
    if cartas_epicas:
        embed_epica = discord.Embed(
            title="🌟 Você conseguiu uma carta ÉPICA!",
            description=f"**{cartas_epicas[0]['nome']}** ({cartas_epicas[0]['era']})",
            color=discord.Color.gold()
        )
        embed_epica.set_image(url=cartas_epicas[0]["gif"])
        await interaction.followup.send(embed=embed_epica)

    final_img = await colar_cartas_em_grid(cartas_ganhas, cols=5, rows=1)
    file = discord.File(fp=final_img, filename="cartas.png")

    embed = discord.Embed(
        title="📦 Pack Aberto!",
        description="As 5 cartas foram adicionadas ao seu inventário!",
        color=discord.Color.purple()
    )
    embed.set_image(url="attachment://cartas.png")
    await interaction.followup.send(embed=embed, file=file)

async def colar_cartas_em_grid(cartas, cols, rows):
    largura, altura = 400, 600
    final = Image.new("RGB", (largura * cols, altura * rows))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        for i, carta in enumerate(cartas):
            try:
                async with session.get(carta["imagem"], headers=headers) as resp:
                    if resp.status != 200:
                        print(f"Erro HTTP {resp.status} ao baixar imagem da carta {carta['nome']} - URL: {carta['imagem']}")
                        continue
                    img_bytes = await resp.read()
                img = Image.open(io.BytesIO(img_bytes)).resize((largura, altura))
            except Exception as e:
                print(f"Erro ao abrir imagem da carta {carta['nome']} - URL: {carta['imagem']}: {e}")
                continue

            x = (i % cols) * largura
            y = (i // cols) * altura
            final.paste(img, (x, y))

    img_bytes = io.BytesIO()
    final.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes
