import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()  # carrega o .env

MONGO_URI = os.getenv("MONGO_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client["kpopbot"]
usuarios = db["usuarios"]

async def get_usuario(user_id):
    user = await usuarios.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "moedas": 0,
            "cartas": [],
            "xp": 0
        }
        await usuarios.insert_one(user)
    return user

async def get_ou_cria_usuario(user_id):
    usuario = await usuarios.find_one({"user_id": user_id})
    if not usuario:
        usuario = {
            "user_id": user_id,
            "moedas": 0,
            "cartas": [],
            "xp": 0
        }
        await usuarios.insert_one(usuario)
    return usuario

async def update_usuario(user_id, data):
    await usuarios.update_one({"user_id": user_id}, {"$set": data}, upsert=True)
