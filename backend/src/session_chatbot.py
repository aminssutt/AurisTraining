"""
Chatbot RAG pour une session spécifique
"""
from typing import Optional, List, Tuple

import google.generativeai as genai
from langchain_core.documents import Document
from langchain_chroma import Chroma

from .config import GOOGLE_API_KEY, LLM_MODEL, TOP_K_RESULTS
from .vector_store import get_embeddings
from .session_manager import session_manager

# Configurer l'API Google
genai.configure(api_key=GOOGLE_API_KEY)


# Mots-clés pour détecter les questions sur les véhicules
VEHICLE_KEYWORDS = [
    # Général véhicules
    "voiture", "véhicule", "auto", "automobile", "conduite", "conduire",
    "car", "vehicle", "drive", "driving",
    
    # Composants mécaniques
    "moteur", "engine", "batterie", "battery", "transmission", "boîte de vitesse",
    "frein", "brake", "embrayage", "clutch", "suspension", "amortisseur",
    "direction", "steering", "roue", "wheel", "pneu", "tire", "tyre",
    "échappement", "exhaust", "catalyseur", "turbo", "injection",
    
    # Électrique/Hybride
    "électrique", "electric", "recharge", "charging", "autonomie", "range",
    "régénération", "regeneration", "ev", "mode eco", "mode sport", "hybride",
    
    # Carrosserie
    "carrosserie", "body", "portière", "door", "coffre", "trunk", "boot",
    "capot", "hood", "bonnet", "pare-brise", "windshield", "rétroviseur", "mirror",
    "phare", "headlight", "feu", "light", "clignotant", "indicator",
    
    # Intérieur
    "siège", "seat", "ceinture", "seatbelt", "volant", "tableau de bord", "dashboard",
    "climatisation", "air conditioning", "chauffage", "heating", "ventilation",
    "autoradio", "radio", "gps", "navigation", "bluetooth", "usb",
    
    # Entretien
    "entretien", "maintenance", "révision", "service", "vidange", "oil change",
    "filtre", "filter", "bougie", "spark plug", "liquide", "fluid",
    "niveau", "level", "pression", "pressure", "usure", "wear",
    
    # Sécurité
    "sécurité", "safety", "airbag", "abs", "esp", "traction", "stabilité",
    "alarme", "alarm", "antivol", "immobilizer", "verrouillage", "lock",
    
    # Fonctionnement
    "démarrage", "start", "allumage", "ignition", "arrêt", "stop",
    "accélération", "acceleration", "vitesse", "speed", "consommation", "consumption",
    "carburant", "fuel", "essence", "petrol", "diesel", "gazole",
    
    # Problèmes/Diagnostics
    "panne", "breakdown", "problème", "problem", "erreur", "error",
    "voyant", "warning light", "indicateur", "bruit", "noise", "vibration",
    "fuite", "leak", "surchauffe", "overheat", "diagnostic",
    
    # Documents/Manuel
    "manuel", "manual", "notice", "guide", "instruction", "spécification",
    "caractéristique", "specification", "dimension", "capacité", "capacity",
    
    # Actions véhicule
    "régler", "adjust", "configurer", "configure", "activer", "activate",
    "désactiver", "deactivate", "ouvrir", "fermer", "démonter", "remonter",
    "remplacer", "replace", "réparer", "repair", "vérifier", "check"
]

# Mots-clés négatifs
NON_VEHICLE_KEYWORDS = [
    "recette", "cuisine", "cuisiner", "tarte", "gâteau", "pizza", "soupe",
    "ingrédient", "cuire", "four", "casserole", "manger", "plat", "repas",
    "météo", "temps qu'il fait", "pluie", "neige", "ensoleillé",
    "président", "ministre", "gouvernement", "élection", "politique",
    "football", "basket", "tennis", "rugby", "match",
    "film", "série", "musique", "chanson", "acteur", "cinéma",
    "médecin", "docteur", "hôpital", "maladie", "médicament",
    "chien", "chat", "animal", "vétérinaire"
]


def is_vehicle_related(question: str) -> Tuple[bool, float]:
    """Vérifie si la question est liée aux véhicules"""
    question_lower = question.lower()
    
    # Vérifier les mots-clés négatifs
    for kw in NON_VEHICLE_KEYWORDS:
        if kw in question_lower:
            return False, 0.0
    
    # Compter les mots-clés véhicules
    found = sum(1 for kw in VEHICLE_KEYWORDS if kw.lower() in question_lower)
    
    if found >= 3:
        return True, 1.0
    elif found >= 2:
        return True, 0.9
    elif found >= 1:
        return True, 0.7
    else:
        return False, 0.0


def format_context(documents: List[Document]) -> str:
    """Formate les documents pour le contexte"""
    if not documents:
        return "Aucune information spécifique trouvée dans les documents."
    
    parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source_file", "Document")
        page = doc.metadata.get("page", "?")
        parts.append(f"[Source: {source}, Page {page}]\n{doc.page_content}")
    
    return "\n\n---\n\n".join(parts)


class SessionChatbot:
    """Chatbot RAG pour une session utilisateur"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session = session_manager.get_session(session_id)
        
        if not self.session:
            raise ValueError(f"Session {session_id} introuvable")
        
        # Charger le vector store de la session
        self.vector_store = self._load_vector_store()
        
        # Modèle Gemini
        self.model = genai.GenerativeModel(LLM_MODEL)
        
        # Historique de conversation
        self.conversation_history = []
    
    def _load_vector_store(self) -> Optional[Chroma]:
        """Charge le vector store de la session"""
        chroma_dir = self.session.chroma_dir
        
        if not chroma_dir.exists():
            return None
        
        embeddings = get_embeddings()
        return Chroma(
            persist_directory=str(chroma_dir),
            embedding_function=embeddings
        )
    
    def chat(self, question: str) -> str:
        """Traite une question et retourne la réponse"""
        
        # Vérifier si c'est une question véhicule
        is_vehicle, confidence = is_vehicle_related(question)
        
        if not is_vehicle and confidence < 0.5:
            return f"""🚫 **Question hors sujet**

Je suis un assistant spécialisé pour votre **{self.session.vehicle_name}**. 
Je ne peux répondre qu'aux questions concernant votre véhicule, son entretien, son fonctionnement ou ses caractéristiques.

💡 Essayez une question comme :
- "Comment fonctionne le système de freinage ?"
- "Quelle est la pression recommandée des pneus ?"
- "Que signifie le voyant moteur ?"
"""
        
        # Rechercher dans le contexte
        context = ""
        if self.vector_store:
            docs = self.vector_store.similarity_search(question, k=TOP_K_RESULTS)
            context = format_context(docs)
        
        # Construire le prompt
        prompt = f"""Tu es un assistant expert spécialisé pour le véhicule **{self.session.vehicle_name}**.

🚗 TON RÔLE:
- Répondre aux questions sur ce véhicule en utilisant les documents fournis
- Donner des conseils pratiques sur l'entretien et le fonctionnement
- Être précis et citer les sources quand possible

📋 RÈGLES:
1. Base tes réponses sur le contexte fourni (documents du propriétaire)
2. Si l'info n'est pas dans le contexte, utilise tes connaissances générales sur les véhicules
3. Réponds toujours en français
4. Sois concis mais complet

---
CONTEXTE (Documents du véhicule):
{context}
---

Question: {question}

Réponse:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Ajouter à l'historique
            self.conversation_history.append({
                "role": "user",
                "content": question
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": answer
            })
            
            return f"📖 {answer}"
            
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def get_history(self) -> list:
        """Retourne l'historique de conversation"""
        return self.conversation_history
    
    def clear_history(self):
        """Efface l'historique"""
        self.conversation_history = []


# Cache des chatbots par session
_chatbot_cache = {}

def get_session_chatbot(session_id: str) -> SessionChatbot:
    """Récupère ou crée un chatbot pour une session"""
    if session_id not in _chatbot_cache:
        _chatbot_cache[session_id] = SessionChatbot(session_id)
    return _chatbot_cache[session_id]

def clear_chatbot_cache(session_id: str):
    """Supprime un chatbot du cache"""
    if session_id in _chatbot_cache:
        del _chatbot_cache[session_id]
