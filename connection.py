import os
import json
from dotenv import load_dotenv
from notion_client import Client
from pymongo import MongoClient


# Charger le token
load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("NOTION_DB_ID")
mongo_uri = os.getenv("MONGO_URI")

# Initialiser le client Notion
notion = Client(auth=notion_token)
# Récupérer les livres
response = notion.databases.query(database_id=database_id)

try:
    # Récupérer les détails de la base
    database = notion.databases.retrieve(database_id=database_id)
    print("Connexion à la base réussie !")
    print(f"Nom de la base : {database['title'][0]['plain_text']}")
except Exception as e:
    print("Erreur lors de la connexion :")
    print(type(e).__name__)  # Type de l'exception
    print(e)  # Message détaillé de l'erreur


# Charger les données depuis le fichier JSON
with open("new_book.json", "r", encoding="utf-8") as file:
    new_book = json.load(file)

# Extraire le titre et l'auteur du nouveau livre
new_book_title = new_book.get("Titre", {}).get("title", [])[0].get("text", {}).get("content", "No title").strip()
new_book_author = new_book.get("Auteur", {}).get("rich_text", [])[0].get("text", {}).get("content", "No author").strip()

# Ajouter le nouveau livre à la base de données
try:

    books = response["results"]

    # Parcourir les livres existants pour vérifier les doublons
    book_exists = any(
        book["properties"].get("Titre", {}).get("title", [])[0].get("text", {}).get("content", "").strip() == new_book_title and
        book["properties"].get("Auteur", {}).get("rich_text", [])[0].get("text", {}).get("content", "").strip() == new_book_author
        for book in books
    )

    # Insertion d'un livre -> seulement s'il existe pas déjà (Titre, Auteur) déjà dans la table
    if book_exists:
        print(f"Le livre '{new_book_title}' de '{new_book_author}' existe déjà dans la base de données.")
    else:
        # Ajouter le nouveau livre à la base de données s'il n'est pas déjà dans la base
        notion.pages.create(
            parent={"database_id": database_id},
            properties=new_book
        )
        print("Livre ajouté avec succès !")
        

except Exception as e:
    print(f"Erreur lors de l'ajout du livre : {e}")


# Se connecter à MongoDB
client = MongoClient(mongo_uri)

# Créer une base de données
db = client["LivresDB"]

# Créer une collection
collection = db["Livres"]
print("Connexion à MongoDB réussie !")


for result in response["results"]:
    
    # Pour récupérer les titres des livres
    # title = result["properties"]["Titre"]["title"][0]["text"]["content"]
    title_property = result["properties"].get("Titre", {}).get("title", [])
    title = title_property[0].get("text", {}).get("content", "No title") if title_property else "No title"

    # Pour récupérer les auteurs des livres
    # author = result["properties"]["Auteur"]["rich_text"][0]["text"]["content"]
    author_property = result["properties"].get("Auteur", {}).get("rich_text", [])
    author = author_property[0].get("text", {}).get("content", "No author") if author_property else "No author"

    # Pour récupérer les tags/genres des livres
    tags = result["properties"].get("Tags", {}).get("multi_select", [])
    tags_list = [tag['name'] for tag in tags] if tags else []

    # Pour récupérer les status de lecture (à lire, en cours, lu)
    # status = result["properties"]["Status"]["status"]["name"]
    status = result["properties"].get("Status", {}).get("status", {}).get("name", "No status")

    # Récupérer la date de fin de lecture 
    date_json = result["properties"].get("Date de fin de lecture prévue", {}).get("date", None)
    if date_json is not None:
        reading_end_date = date_json["start"]
        # print(type(reading_end_date)) # date in str format for the moment

    else:
        reading_end_date = "No date"

    # Pour récupérer les favoris
    # favorite = result["properties"]["Favoris"]["checkbox"]
    # les élèments de cette colonnes ne peuvent pas être vides
    favorite = result["properties"].get("Favoris", {}).get("checkbox", False)

    # Pour récupérer la notation sur 10
    # rating_number = result["properties"]["Note sur 10"]["number"]
    rating_number = result["properties"].get("Note sur 10", {}).get("number", None)

    # Pour récupérer la notation en étoiles
    # stars_rating = result["properties"]["Etoiles"]["formula"]["string"]
    # les élèments de cette colonne ne peuvent pas être vides
    stars_rating = result["properties"].get("Etoiles", {}).get("formula", {}).get("string", "☆☆☆☆☆")

    # Récupérer les commentaires
    # comments = result["properties"]["Commentaire"]["rich_text"][0]["text"]["content"]
    comments_property = result["properties"].get("Commentaire", {}).get("rich_text", [])
    comments = comments_property[0].get("text", {}).get("content", "No comment") if comments_property else "No comment"

    # Transformer les données pour MongoDB
    book = {
        "Titre": title,
        "Auteur": author,
        "Tags": tags_list,
        "Status": status,
        "Date_de_fin_lecture": reading_end_date,
        "Favoris": favorite,
        "Note_sur_10": rating_number,
        "Commentaire": comments
    }

    # Insérer dans MongoDB
    try:
        collection.insert_one(book)
        print(f"Livre ajouté : {book['Titre']}")

    except Exception as e:
        print(f"Erreur lors de l'ajout : {e}")


# Fermeture explicite de la connexion MongoDB
client.close()
