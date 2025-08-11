import os

# Token do bot do Telegram (lido das variáveis de ambiente no Heroku)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Chave e endpoint da API de reconhecimento facial da Azure
FACE_API_KEY = os.environ.get("FACE_API_KEY")
FACE_API_ENDPOINT = os.environ.get("FACE_API_ENDPOINT")
