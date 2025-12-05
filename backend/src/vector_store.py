"""
Module de gestion du vector store ChromaDB pour le RAG
"""
from typing import List, Optional
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from .config import (
    CHROMA_DIR, 
    COLLECTION_NAME,
    TOP_K_RESULTS
)


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Initialise le modèle d'embeddings HuggingFace (gratuit, pas besoin d'API)
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vector_store(documents: List[Document]) -> Chroma:
    """
    Crée un nouveau vector store à partir des documents
    """
    if not documents:
        raise ValueError("Aucun document à indexer")
    
    print(f"\n🔄 Création du vector store avec {len(documents)} documents...")
    
    embeddings = get_embeddings()
    
    # Créer le vector store avec persistance
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR)
    )
    
    print(f"✅ Vector store créé et sauvegardé dans {CHROMA_DIR}")
    
    return vector_store


def load_vector_store() -> Optional[Chroma]:
    """
    Charge un vector store existant
    """
    if not CHROMA_DIR.exists():
        print("⚠️  Aucun vector store trouvé. Veuillez d'abord indexer les documents.")
        return None
    
    embeddings = get_embeddings()
    
    try:
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR)
        )
        
        # Vérifier si la collection contient des documents
        collection_count = vector_store._collection.count()
        
        if collection_count == 0:
            print("⚠️  Le vector store est vide. Veuillez indexer les documents.")
            return None
        
        print(f"✅ Vector store chargé avec {collection_count} documents")
        return vector_store
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement du vector store: {e}")
        return None


def get_or_create_vector_store(documents: Optional[List[Document]] = None) -> Optional[Chroma]:
    """
    Charge le vector store existant ou en crée un nouveau si documents fournis
    """
    # Essayer de charger un vector store existant
    vector_store = load_vector_store()
    
    if vector_store is not None:
        return vector_store
    
    # Sinon, créer un nouveau si des documents sont fournis
    if documents:
        return create_vector_store(documents)
    
    return None


def search_documents(
    query: str, 
    vector_store: Optional[Chroma] = None,
    k: int = TOP_K_RESULTS
) -> List[Document]:
    """
    Recherche les documents les plus pertinents pour une requête
    """
    if vector_store is None:
        vector_store = load_vector_store()
    
    if vector_store is None:
        return []
    
    results = vector_store.similarity_search(query, k=k)
    
    return results


def search_with_scores(
    query: str, 
    vector_store: Optional[Chroma] = None,
    k: int = TOP_K_RESULTS
) -> List[tuple]:
    """
    Recherche les documents avec leurs scores de similarité
    """
    if vector_store is None:
        vector_store = load_vector_store()
    
    if vector_store is None:
        return []
    
    results = vector_store.similarity_search_with_score(query, k=k)
    
    return results


def delete_vector_store():
    """
    Supprime le vector store (pour réindexation complète)
    """
    import shutil
    
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        print(f"🗑️  Vector store supprimé: {CHROMA_DIR}")
    else:
        print("ℹ️  Aucun vector store à supprimer")
