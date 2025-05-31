import discord

def criar_embed_carta_preview(carta, usuario, bot):
    nome = usuario.display_name if hasattr(usuario, "display_name") else usuario.get("nome", "Desconhecido")
    avatar_url = usuario.display_avatar.url if hasattr(usuario, "display_avatar") else ""

    embed = discord.Embed(
        title=f"{carta['nome']} (ID: {carta['id']})",
        color=discord.Color.blurple()
    )
    embed.set_author(name=nome, icon_url=avatar_url)
    embed.set_image(url=carta.get('imagem', ''))
    embed.add_field(name="Raridade", value=carta.get('raridade', 'Desconhecida'), inline=True)
    embed.add_field(name="Grupo", value=carta.get('grupo', 'Desconhecido'), inline=True)
    embed.set_footer(text="Bot desenvolvido por TwiceFla & Kendo", icon_url=bot.user.avatar.url)
    return embed
