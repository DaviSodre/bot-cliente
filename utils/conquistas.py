from database import update_usuario

async def atualizar_conquistas(user_data, carta, user_id):
    conquistas = user_data.get("conquistas", {
        "raridades": {},
        "eras": {},
        "grupos": {}
    })

    atingidas = user_data.get("conquistas_atingidas", {
        "raridades": [],
        "eras": [],
        "grupos": []
    })

    mensagens = []

    def check_e_registra(tipo, chave, count, texto):
        id_conquista = f"{count}-{chave}"
        if id_conquista not in atingidas[tipo]:
            mensagens.append(texto)
            atingidas[tipo].append(id_conquista)

    # raridade
    raridade = carta.get("raridade", "Desconhecida")
    conquistas["raridades"][raridade] = conquistas["raridades"].get(raridade, 0) + 1
    count_raridade = conquistas["raridades"][raridade]
    if count_raridade in [5, 10, 25, 50]:
        check_e_registra("raridades", raridade, count_raridade,
                         f"🏆 <@{user_id}> colecionou {count_raridade} cartas **{raridade}**!")

    # era
    era = carta.get("era", "Desconhecida")
    conquistas["eras"][era] = conquistas["eras"].get(era, 0) + 1
    count_era = conquistas["eras"][era]
    if count_era in [5, 10, 25, 50]:
        check_e_registra("eras", era, count_era,
                         f"🏆 <@{user_id}> colecionou {count_era} cartas da era **{era}**!")

    # grupo
    grupo = carta.get("grupo", "Desconhecido")
    conquistas["grupos"][grupo] = conquistas["grupos"].get(grupo, 0) + 1
    count_grupo = conquistas["grupos"][grupo]
    if count_grupo in [5, 10, 25, 50]:
        check_e_registra("grupos", grupo, count_grupo,
                         f"🏆 <@{user_id}> colecionou {count_grupo} cartas do grupo **{grupo}**!")

    # salva no banco
    await update_usuario(user_id, {
        "conquistas": conquistas,
        "conquistas_atingidas": atingidas
    })

    return mensagens

