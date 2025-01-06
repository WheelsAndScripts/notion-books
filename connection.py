from notion_client import Client
import os
from dotenv import load_dotenv

# Charger le token
load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")

# Initialiser le client Notion
notion = Client(auth=notion_token)
