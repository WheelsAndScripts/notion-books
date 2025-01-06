from notion_client import Client
import os
from dotenv import load_dotenv

# Charger le token
load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("NOTION_DB_ID")

# Initialiser le client Notion
notion = Client(auth=notion_token)

try:
    # Récupérer les détails de la base
    database = notion.databases.retrieve(database_id=database_id)
    print("Connexion à la base réussie !")
    print(f"Nom de la base : {database['title'][0]['plain_text']}")
except Exception as e:
    print("Erreur lors de la connexion :")
    print(type(e).__name__)  # Type de l'exception
    print(e)  # Message détaillé de l'erreur
