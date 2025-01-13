import os
from dotenv import load_dotenv
from pymongo import MongoClient


def mongo_connexion():
    # Charger le token
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    # Se connecter à MongoDB
    client = MongoClient(mongo_uri)

    # Créer une base de données
    db = client["LivresDB"]

    # Créer une collection
    collection = db["Livres"]
    print("Connexion à MongoDB réussie !")

    return client, collection


def insert_from_mongo_to_notion(notion_response, mongo_client, mongo_collection):

    for result in notion_response["results"]:
        
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
        # stars_rating = result["properties"].get("Etoiles", {}).get("formula", {}).get("string", "☆☆☆☆☆")

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
            mongo_collection.insert_one(book)
            print(f"Livre ajouté : {book['Titre']}")

        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")


    # Fermeture explicite de la connexion MongoDB
    mongo_client.close()


# Ajouter un livre
def add_book(book):
    _, collection = mongo_connexion()

    if collection.find_one({"Titre": book["Titre"], "Auteur": book["Auteur"]}):
        print("Le livre existe déjà dans la base.")
    else:
        collection.insert_one(book)
        print("Livre ajouté avec succès.")


# Modifier un livre
def update_book(title, updates):
    _, collection = mongo_connexion()

    # donner une liste finie d'option pour les tags
    result = collection.update_one({"Titre": title}, {"$set": updates})
    if result.matched_count > 0:
        print("Livre mis à jour.")
    else:
        print("Aucun livre trouvé avec ce titre.")


# Supprimer un livre
def delete_book(title):
    _, collection = mongo_connexion()

    result = collection.delete_one({"Titre": title})
    if result.deleted_count > 0:
        print("Livre supprimé.")
    else:
        print("Aucun livre trouvé avec ce titre.")


# Consulter tous les livres
def get_all_books():
    _, collection = mongo_connexion()

    books = collection.find()
    for book in books:
        print(book)
