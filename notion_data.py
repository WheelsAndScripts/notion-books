import os
import json
from dotenv import load_dotenv
from notion_client import Client


def notion_connexion(database_id):
    # Charger le token
    load_dotenv()
    notion_token = os.getenv("NOTION_TOKEN")

    # Initialiser le client Notion
    notion = Client(auth=notion_token)
    # Récupérer les livres
    response = notion.databases.query(database_id=database_id)

    try:
        # Récupérer les détails de la base
        database = notion.databases.retrieve(database_id=database_id)
        print("Connexion à la base réussie Notion !")
        print(f"Nom de la base : {database['title'][0]['plain_text']}")
    except Exception as e:
        print("Erreur lors de la connexion :")
        print(type(e).__name__)  # Type de l'exception
        print(e)  # Message détaillé de l'erreur
    
    # response correspond aux livres de la db notion
    return response, notion


def add_book_to_notion(database_id, response, notionClient):
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
            notionClient.pages.create(
                parent={"database_id": database_id},
                properties=new_book
            )
            print("Livre ajouté avec succès !")
            
    except Exception as e:
        print(f"Erreur lors de l'ajout du livre : {e}")