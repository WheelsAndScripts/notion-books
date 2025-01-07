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


try:
    # Récupérer les détails de la base de données
    database = notion.databases.retrieve(database_id=database_id)
    
    # Extraire les colonnes et leurs types
    properties = database["properties"]
    for column_name, column_info in properties.items():
        print(f"Nom de la colonne : {column_name}")
        print(f"Type : {column_info['type']}")
        print("-" * 40)

except Exception as e:
    print("Erreur lors de la récupération des colonnes :", e)
 

# Récupérer les livres
response = notion.databases.query(database_id=database_id)
for result in response["results"]:
    # Pour récupérer les titres des livres
    title = result["properties"]["Titre"]["title"][0]["text"]["content"]

    # Pour récupérer les auteurs des livres
    author = result["properties"]["Auteur"]["rich_text"][0]["text"]["content"]

    # Pour récupérer les tags/genres des livres
    # print(result["properties"]["Tags"])

    # Pour récupérer les status de lecture (à lire, en cours, lu)
    status = result["properties"]["Status"]["status"]["name"]

    # Pour récupérer l'image de couverture 
    # cover = result["properties"]["Cover"] # don't know what to do with the images for now, we'll see later

    # Récupérer la date de fin de lecture 
    date_json = result["properties"]["Date de fin de lecture prévue"]["date"]
    if date_json is not None :
        reading_end_date = date_json["start"]
        # print(type(reading_end_date)) # date in str format for the moment

    else :
        reading_end_date = "No date"

    # Pour récupérer les favoris
    favorite = result["properties"]["Favoris"]["checkbox"]

    # Pour récupérer la notation sur 10
    rating_number = result["properties"]["Note sur 10"]["number"]

    # Pour récupérer la notation en étoiles
    stars_rating = result["properties"]["Etoiles"]["formula"]["string"]

    # Récupérer les commentaires
    comments = result["properties"]["Commentaire"]["rich_text"][0]["text"]["content"]

