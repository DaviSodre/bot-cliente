import random
from database import get_usuario, update_usuario
from PIL import Image
import aiohttp
import io
import discord
from cartas import cartas_disponiveis

async def pack_twice(bot, interaction):
    user_data = await get_usuario(interaction.user.id)

    cartas_twice = [c for c in cartas_disponiveis if c.get("grupo", "").upper() == "TWICE"]

    cartas_ganhas = random.sample(cartas_twice, min(10, len(cartas_twice)))
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
        title="📦 Pack TWICE Aberto!",
        description="As 10 cartas foram adicionadas ao seu inventário!",
        color=discord.Color.purple
    )
    embed.set_image(url="attachment://cartas.png")
    await interaction.followup.send(embed=embed, file=file)

async def pack_twice_5(bot, interaction):
    user_data = await get_usuario(interaction.user.id)

    cartas_twice = [c for c in cartas_disponiveis if c.get("grupo", "").upper() == "TWICE"]

    cartas_ganhas = random.sample(cartas_twice, min(5, len(cartas_twice)))
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
        title="📦 Pack TWICE Aberto!",
        description="As 5 cartas foram adicionadas ao seu inventário!",
        color=discord.Color.purple()
    )
    embed.set_image(url="attachment://cartas.png")
    await interaction.followup.send(embed=embed, file=file)

async def colar_cartas_em_grid(cartas, cols, rows):
    largura, altura = 400, 600 
    final = Image.new("RGBA", (largura * cols, altura * rows), (0,0,0,0))  # fundo transparente

    async with aiohttp.ClientSession() as session:
        for i, carta in enumerate(cartas):
            async with session.get(carta["imagem"]) as resp:
                img_bytes = await resp.read()
            img = Image.open(io.BytesIO(img_bytes)).convert("RGBA").resize((largura, altura))
            x = (i % cols) * largura
            y = (i // cols) * altura
            final.paste(img, (x, y), img)  # usa img como máscara pra manter transparência

    final_rgb = final.convert("RGB")
    img_bytes = io.BytesIO()
    final_rgb.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes
