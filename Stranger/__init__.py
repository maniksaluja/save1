import sys
from os import getenv
from dotenv import load_dotenv
import logging
import pyromod.listen
from pyrogram import Client
from telethon.sync import TelegramClient


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
LOGGER_ID = int(getenv("LOGGER_ID"))
OWNER_ID = int(getenv("OWNER_ID"))
STRING = getenv("STRING_SESSION", None)

if not API_HASH or not API_ID or not BOT_TOKEN or not LOGGER_ID or not OWNER_ID or not STRING:
    print("One or more required environment variables are not set.")
    sys.exit(1)  # Exit the program with a non-zero status code

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

app = Client("bot", API_ID, API_HASH, bot_token=BOT_TOKEN)

userbot = Client("userbot" , API_ID, API_HASH, session_string=STRING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

