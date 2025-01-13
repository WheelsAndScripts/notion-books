import os
from dotenv import load_dotenv
import notion_data
import mongo_data


def main():
    print("Starting program")

    # load env variables
    load_dotenv()
    database_id = os.getenv("NOTION_DB_ID")

    # 1) connexion API Notion
    notion_books_response, notion_client = notion_data.notion_connexion(database_id)

    # 2) ajout d'un livre dans la table Notion
    notion_data.add_book_to_notion(database_id, notion_books_response, notion_client)

    # 3) connexion à Mongo DB
    mongo_client, mongo_collection = mongo_data.mongo_connexion()

    # 4) insérer les livres de notion dans mongoDB (pas de duplica dans notion)
    # mongo_data.insert_from_mongo_to_notion(notion_books_response, mongo_client, mongo_collection)

    # 5) CRUD de livres dans mongoDB
    # book = {"Titre": "1984", "Auteur": "George Orwell"}
    # mongo_data.add_book(book)

    # mongo_data.update_book('1984', {"Auteur": 'Georges',"Tags": ['Classique', 'S-F'], "Status": 'A lire'})

    # mongo_data.delete_book('1984')

    # mongo_data.get_all_books()

    # 6) Synchro entre les deux bases


if __name__ == "__main__":
    main()
