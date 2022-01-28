import os

from dotenv import load_dotenv

load_dotenv()

ADMIN = int(os.getenv('ADMIN'))
BOT_TOKEN = os.getenv('BOT_TOKEN')
POSTGRES_URI = os.getenv('POSTGRES_URI')
