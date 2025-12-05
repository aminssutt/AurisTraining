"""
Module de chargement et traitement des PDFs Toyota Auris
"""
import os
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from .config import PDF_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def get_pdf_files() -> List[Path]:
    """
    Récupère tous les fichiers PDF du répertoire data/pdfs
    """
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  Aucun fichier PDF trouvé dans {PDF_DIR}")
        print("   Veuillez télécharger les manuels Toyota Auris et les placer dans ce dossier.")
        return []
    
    print(f"📁 {len(pdf_files)} fichier(s) PDF trouvé(s):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    return pdf_files


def load_single_pdf(pdf_path: Path) -> List[Document]:
    """
    Charge un seul fichier PDF et retourne les documents
    """
    try:
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()
        
        # Ajouter des métadonnées
        for doc in documents:
            doc.metadata["source_file"] = pdf_path.name
            doc.metadata["vehicle"] = "Toyota Auris Hybride"
            doc.metadata["document_type"] = "manuel_utilisateur"
        
        print(f"   ✅ {pdf_path.name}: {len(documents)} pages chargées")
        return documents
    
    except Exception as e:
        print(f"   ❌ Erreur lors du chargement de {pdf_path.name}: {e}")
        return []


def load_all_pdfs() -> List[Document]:
    """
    Charge tous les PDFs du répertoire et retourne les documents combinés
    """
    pdf_files = get_pdf_files()
    
    if not pdf_files:
        return []
    
    all_documents = []
    print("\n📖 Chargement des PDFs...")
    
    for pdf_path in pdf_files:
        documents = load_single_pdf(pdf_path)
        all_documents.extend(documents)
    
    print(f"\n📊 Total: {len(all_documents)} pages chargées")
    return all_documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Découpe les documents en chunks pour le RAG
    """
    if not documents:
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✂️  Documents découpés en {len(chunks)} chunks")
    
    return chunks


def process_pdfs() -> List[Document]:
    """
    Pipeline complet: charge et découpe tous les PDFs
    """
    print("=" * 50)
    print("🚗 TRAITEMENT DES MANUELS TOYOTA AURIS HYBRIDE")
    print("=" * 50)
    
    # Charger les documents
    documents = load_all_pdfs()
    
    if not documents:
        return []
    
    # Découper en chunks
    chunks = split_documents(documents)
    
    print("=" * 50)
    print(f"✅ Traitement terminé: {len(chunks)} chunks prêts pour l'indexation")
    print("=" * 50)
    
    return chunks
