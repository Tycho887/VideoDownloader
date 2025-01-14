import dotenv
import os

dotenv.load_dotenv()

def get_bot_token():
    return os.getenv("DOWNLOAD_BOT_TOKEN")