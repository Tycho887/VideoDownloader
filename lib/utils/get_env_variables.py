import dotenv
import os

dotenv.load_dotenv()

def get_bot_token():
    return os.getenv("DISCORD_BOT_TOKEN")