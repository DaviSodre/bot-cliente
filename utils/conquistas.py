from database import update_usuario

async def atualizar_conquistas(user_data, carta, user_id):
    conquistas = user_data.get("conquistas", {})

    # garante que todas as chaves existem
    conquistas.setdefault("raridades", {})
    conquistas.setdefault("eras", {})
    conquistas.setdefault("grupos", {})

    mensagens = []

    # raridade
    raridade = carta.get("raridade", "Desconhecida")
    conquistas["raridades"][raridade] = conquistas["raridades"].get(raridade, 0) + 1
    count_raridade = conquistas["raridades"][raridade]
    if count_raridade in [5, 10, 25, 50]:
        mensagens.append(f"🏆 {user_data.get('nome', 'Um usuário')} colecionou {count_raridade} cartas **{raridade}**!")

    # era
    era = carta.get("era", "Desconhecida")
    conquistas["eras"][era] = conquistas["eras"].get(era, 0) + 1
    count_era = conquistas["eras"][era]
    if count_era in [5, 10, 25, 50]:
        mensagens.append(f"🏆 {user_data.get('nome', 'Um usuário')} colecionou {count_era} cartas da era **{era}**!")

    # grupo
    grupo = carta.get("grupo", "Desconhecido")
    conquistas["grupos"][grupo] = conquistas["grupos"].get(grupo, 0) + 1
    count_grupo = conquistas["grupos"][grupo]
    if count_grupo in [5, 10, 25, 50]:
        mensagens.append(f"🏆 {user_data.get('nome', 'Um usuário')} colecionou {count_grupo} cartas do grupo **{grupo}**!")

    # salvar conquistas no banco
    await update_usuario(user_id, {"conquistas": conquistas})
    return mensagens
