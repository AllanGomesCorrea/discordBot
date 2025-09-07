import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import BOT_TOKEN
from commands import register_commands

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")

register_commands(bot)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Erro: BOT_TOKEN não encontrado nas variáveis de ambiente.")
        exit(1)
    
    bot.run(BOT_TOKEN)
