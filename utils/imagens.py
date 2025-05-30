from PIL import Image, ImageOps
import requests
from io import BytesIO

def aplicar_borda(img_carta, raridade):
    bordas = {
        "comum": "./bordas/comum.png",
        "rara": "./bordas/rara.png",
        "epica": "./bordas/epica.png"
    }

    caminho_borda = bordas.get(raridade.lower())
    if not caminho_borda:
        return img_carta  # se não tiver borda pra raridade, retorna a imagem original

    borda = Image.open(caminho_borda).convert("RGBA")
    borda = ImageOps.fit(borda, img_carta.size, Image.LANCZOS)

    img_carta.paste(borda, (0, 0), borda)
    return img_carta

def juntar_imagens_lado_a_lado(cartas):
    """
    cartas: lista de dicts, cada um deve ter {'url': str, 'raridade': str}
    ex:
    [
      {"url": "https://...", "raridade": "Rara"},
      {"url": "https://...", "raridade": "Comum"},
      {"url": "https://...", "raridade": "Epica"}
    ]
    """

    largura_padrao = 200
    altura_padrao = 300
    tamanho_padrao = (largura_padrao, altura_padrao)

    imagens = []
    for carta in cartas:
        url = carta.get("url")
        raridade = carta.get("raridade", "comum")  # default comum

        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code == 200 and 'image' in resposta.headers.get('Content-Type', ''):
                img = Image.open(BytesIO(resposta.content)).convert("RGBA")
                img = ImageOps.fit(img, tamanho_padrao, Image.LANCZOS)

                # aplica borda conforme raridade
                img = aplicar_borda(img, raridade)

                imagens.append(img)
            else:
                print(f"⚠️ Erro ao baixar imagem (não é imagem): {url}")
        except Exception as e:
            print(f"❌ Erro ao baixar imagem: {url}\n{e}")

    if not imagens:
        print("❌ Nenhuma imagem válida.")
        return None

    largura_total = largura_padrao * len(imagens)
    imagem_final = Image.new("RGBA", (largura_total, altura_padrao))

    x_offset = 0
    for img in imagens:
        imagem_final.paste(img, (x_offset, 0), img)
        x_offset += largura_padrao

    caminho = "drop3_temp.png"
    imagem_final.save(caminho)
    return caminho
