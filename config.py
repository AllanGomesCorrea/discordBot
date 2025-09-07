import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do banco de dados
DATABASE_PATH = os.getenv("DATABASE_PATH", "expenses.db")

# Configurações do bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configurações de limite de mensagens
MAX_MESSAGE_HISTORY = int(os.getenv("MAX_MESSAGE_HISTORY", "500"))
