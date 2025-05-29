import discord
from discord.ext import commands
import os
from comandos import *
import importlib
import cartas

def get_cartas_atualizadas():
    importlib.reload(cartas)  # força recarregar o módulo
    return cartas.cartas_disponiveis  # retorna a lista atualizada


from dotenv import load_dotenv
load_dotenv()
print("MONGO_URI =", os.getenv("MONGO_URI"))

IDS_AUTORIZADOS = [209387134715559946, 1069582140834066442]  

intents = discord.Intents.default()
intents.message_content = True  # permite ler o conteúdo das mensagens

bot = commands.Bot(command_prefix='t!', intents=intents)

async def load_cogs():
    await bot.load_extension("trocar")
    
inventarios = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    await load_cogs()
    print("Comandos sincronizados!")
    print(f'bot conectado como {bot.user}')

async def load_cogs():
    for filename in os.listdir("./comandos"):
        if filename.endswith(".py"):
            nome = filename[:-3]
            try:
                await bot.load_extension(f"comandos.{nome}")
                print(f"Carregado comando {nome}")
            except Exception as e:
                print(f"Erro ao carregar {nome}: {e}")

@bot.event
async def on_connect():
    await load_cogs()

bot.run(os.getenv("DISCORD_TOKEN"))
