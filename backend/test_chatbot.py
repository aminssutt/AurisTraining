"""
Tests unitaires pour le chatbot Toyota Auris
"""
import pytest
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import GOOGLE_API_KEY, LLM_MODEL, CHROMA_DIR, PDF_DIR
from src.chatbot import is_vehicle_related, format_context, VEHICLE_KEYWORDS
from src.vector_store import load_vector_store, get_embeddings
from src.pdf_loader import get_pdf_files


class TestConfig:
    """Tests de configuration"""
    
    def test_google_api_key_exists(self):
        """Vérifie que la clé API Google est configurée"""
        assert GOOGLE_API_KEY is not None
        assert len(GOOGLE_API_KEY) > 0
        assert GOOGLE_API_KEY != "VOTRE_CLE_API_ICI"
    
    def test_llm_model_configured(self):
        """Vérifie que le modèle LLM est configuré"""
        assert LLM_MODEL is not None
        assert "gemini" in LLM_MODEL.lower()
    
    def test_directories_exist(self):
        """Vérifie que les répertoires existent"""
        assert PDF_DIR.exists(), f"Le répertoire PDF n'existe pas: {PDF_DIR}"
        assert CHROMA_DIR.exists(), f"Le répertoire ChromaDB n'existe pas: {CHROMA_DIR}"


class TestPDFLoader:
    """Tests du chargeur de PDFs"""
    
    def test_pdf_files_found(self):
        """Vérifie que des fichiers PDF sont présents"""
        pdf_files = get_pdf_files()
        assert len(pdf_files) > 0, "Aucun fichier PDF trouvé dans data/pdfs/"
    
    def test_pdf_files_are_valid(self):
        """Vérifie que les fichiers PDF sont valides"""
        pdf_files = get_pdf_files()
        for pdf in pdf_files:
            assert pdf.exists(), f"Le fichier PDF n'existe pas: {pdf}"
            assert pdf.suffix.lower() == '.pdf', f"Le fichier n'est pas un PDF: {pdf}"
            assert pdf.stat().st_size > 0, f"Le fichier PDF est vide: {pdf}"


class TestVectorStore:
    """Tests du vector store"""
    
    def test_embeddings_initialization(self):
        """Vérifie que les embeddings s'initialisent correctement"""
        embeddings = get_embeddings()
        assert embeddings is not None
    
    def test_vector_store_loads(self):
        """Vérifie que le vector store se charge correctement"""
        vector_store = load_vector_store()
        assert vector_store is not None, "Le vector store n'a pas pu être chargé"
    
    def test_vector_store_has_documents(self):
        """Vérifie que le vector store contient des documents"""
        vector_store = load_vector_store()
        if vector_store:
            count = vector_store._collection.count()
            assert count > 0, "Le vector store est vide"
            print(f"✅ Vector store contient {count} documents")


class TestChatbotLogic:
    """Tests de la logique du chatbot"""
    
    def test_vehicle_keywords_not_empty(self):
        """Vérifie que la liste de mots-clés n'est pas vide"""
        assert len(VEHICLE_KEYWORDS) > 0
    
    def test_vehicle_related_toyota_question(self):
        """Vérifie la détection des questions Toyota"""
        is_related, confidence = is_vehicle_related("Quelle est la pression des pneus de la Toyota Auris?")
        assert is_related == True
        assert confidence >= 0.7
    
    def test_vehicle_related_general_car_question(self):
        """Vérifie la détection des questions générales sur les voitures"""
        is_related, confidence = is_vehicle_related("Comment fonctionne un moteur hybride?")
        assert is_related == True
    
    def test_vehicle_related_maintenance_question(self):
        """Vérifie la détection des questions d'entretien"""
        is_related, confidence = is_vehicle_related("Quand faut-il faire la vidange?")
        assert is_related == True
    
    def test_not_vehicle_related_weather(self):
        """Vérifie le rejet des questions météo"""
        is_related, confidence = is_vehicle_related("Quel temps fait-il aujourd'hui?")
        assert is_related == False
    
    def test_not_vehicle_related_cooking(self):
        """Vérifie le rejet des questions cuisine"""
        is_related, confidence = is_vehicle_related("Comment faire une tarte aux pommes?")
        assert is_related == False
    
    def test_not_vehicle_related_politics(self):
        """Vérifie le rejet des questions politiques"""
        is_related, confidence = is_vehicle_related("Qui est le président de la France?")
        assert is_related == False
    
    def test_format_context_empty(self):
        """Vérifie le formatage du contexte vide"""
        result = format_context([])
        assert "Aucune information" in result
    
    def test_format_context_with_documents(self):
        """Vérifie le formatage du contexte avec documents"""
        from langchain_core.documents import Document
        docs = [
            Document(page_content="Test content", metadata={"source_file": "test.pdf", "page": 1})
        ]
        result = format_context(docs)
        assert "Test content" in result
        assert "test.pdf" in result


class TestAPIEndpoints:
    """Tests des endpoints API (sans serveur)"""
    
    def test_api_module_imports(self):
        """Vérifie que le module API s'importe correctement"""
        try:
            from api import app, SUGGESTED_QUESTIONS
            assert app is not None
            assert len(SUGGESTED_QUESTIONS) > 0
        except ImportError as e:
            pytest.skip(f"Module API non importable: {e}")
    
    def test_suggested_questions_format(self):
        """Vérifie le format des questions suggérées"""
        from api import SUGGESTED_QUESTIONS
        for q in SUGGESTED_QUESTIONS:
            assert "id" in q
            assert "text" in q
            assert "category" in q
            assert isinstance(q["id"], int)
            assert isinstance(q["text"], str)
            assert len(q["text"]) > 0


class TestIntegration:
    """Tests d'intégration"""
    
    def test_full_chatbot_creation(self):
        """Vérifie la création complète du chatbot"""
        from src.chatbot import create_chatbot
        chatbot = create_chatbot()
        assert chatbot is not None
        assert chatbot.model is not None
    
    def test_chatbot_responds_to_vehicle_question(self):
        """Vérifie que le chatbot répond aux questions véhicules"""
        from src.chatbot import create_chatbot
        chatbot = create_chatbot()
        response = chatbot.chat("Quelle est la capacité du coffre de l'Auris?")
        assert response is not None
        assert len(response) > 0
        assert "🚫" not in response  # Pas de refus
    
    def test_chatbot_rejects_non_vehicle_question(self):
        """Vérifie que le chatbot refuse les questions hors-sujet"""
        from src.chatbot import create_chatbot
        chatbot = create_chatbot()
        response = chatbot.chat("Quelle est la recette du tiramisu?")
        assert "🚫" in response or "spécialisé" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
