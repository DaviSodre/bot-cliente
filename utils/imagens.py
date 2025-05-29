from PIL import Image, ImageOps
import requests
from io import BytesIO

def juntar_imagens_lado_a_lado(urls):
    largura_padrao = 200
    altura_padrao = 300
    tamanho_padrao = (largura_padrao, altura_padrao)

    imagens = []
    for url in urls:
        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code == 200 and 'image' in resposta.headers.get('Content-Type', ''):
                img = Image.open(BytesIO(resposta.content)).convert("RGBA")
                img = ImageOps.fit(img, tamanho_padrao, Image.LANCZOS)
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
        imagem_final.paste(img, (x_offset, 0))
        x_offset += largura_padrao

    caminho = "drop3_temp.png"
    imagem_final.save(caminho)
    return caminho
