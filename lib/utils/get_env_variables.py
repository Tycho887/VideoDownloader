import dotenv
import os


dotenv.load_dotenv()
print(f"DOWNLOAD_BOT_TOKEN: {os.getenv('DOWNLOAD_BOT_TOKEN')}")


def get_bot_token():
    return os.getenv("DOWNLOAD_BOT_TOKEN")