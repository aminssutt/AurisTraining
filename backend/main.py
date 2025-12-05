"""
Script principal du chatbot Toyota Auris Hybride
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pdf_loader import process_pdfs
from src.vector_store import (
    create_vector_store, 
    load_vector_store, 
    delete_vector_store,
    get_or_create_vector_store
)
from src.chatbot import AurisChatbot, create_chatbot


def index_documents():
    """
    Indexe les documents PDF dans le vector store
    """
    print("\n" + "=" * 60)
    print("📚 INDEXATION DES DOCUMENTS TOYOTA AURIS")
    print("=" * 60)
    
    # Charger et traiter les PDFs
    chunks = process_pdfs()
    
    if not chunks:
        print("\n❌ Aucun document à indexer. Vérifiez que les PDFs sont dans data/pdfs/")
        return False
    
    # Supprimer l'ancien index si existant
    delete_vector_store()
    
    # Créer le nouveau vector store
    vector_store = create_vector_store(chunks)
    
    print("\n✅ Indexation terminée avec succès!")
    return True


def interactive_chat():
    """
    Lance le chatbot en mode interactif
    """
    print("\n" + "=" * 60)
    print("🤖 CHATBOT TOYOTA AURIS HYBRIDE")
    print("=" * 60)
    print("\nCommandes spéciales:")
    print("  - 'quit' ou 'exit' : Quitter")
    print("  - 'clear' : Effacer l'historique")
    print("  - 'reindex' : Réindexer les documents")
    print("-" * 60)
    
    # Créer le chatbot
    chatbot = create_chatbot()
    
    if chatbot.vector_store is None:
        print("\n⚠️  Aucun index trouvé. Voulez-vous indexer les documents maintenant? (o/n)")
        response = input("> ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes']:
            if index_documents():
                chatbot = create_chatbot()  # Recréer avec le nouveau vector store
            else:
                print("Continuation sans index...")
    
    print("\n💬 Posez vos questions sur la Toyota Auris Hybride!\n")
    
    while True:
        try:
            question = input("Vous: ").strip()
            
            if not question:
                continue
            
            # Commandes spéciales
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir!")
                break
            
            if question.lower() == 'clear':
                chatbot.clear_history()
                continue
            
            if question.lower() == 'reindex':
                if index_documents():
                    chatbot = create_chatbot()
                continue
            
            # Obtenir la réponse
            print("\n🔄 Recherche en cours...")
            response = chatbot.chat(question)
            print(f"\n🤖 Assistant: {response}\n")
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}\n")


def main():
    """
    Point d'entrée principal
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Chatbot Toyota Auris Hybride")
    parser.add_argument(
        '--index', 
        action='store_true', 
        help="Indexer les documents PDF"
    )
    parser.add_argument(
        '--chat', 
        action='store_true', 
        help="Lancer le mode chat interactif"
    )
    parser.add_argument(
        '--question', '-q',
        type=str,
        help="Poser une question directement"
    )
    
    args = parser.parse_args()
    
    # Si aucun argument, lancer le mode interactif
    if not any([args.index, args.chat, args.question]):
        args.chat = True
    
    if args.index:
        index_documents()
    
    if args.question:
        chatbot = create_chatbot()
        response = chatbot.chat(args.question)
        print(f"\n{response}")
    
    if args.chat:
        interactive_chat()


if __name__ == "__main__":
    main()
