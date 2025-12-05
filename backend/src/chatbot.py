"""
Module du chatbot RAG spécialisé véhicules - Toyota Auris Hybride
"""
from typing import Optional, List, Tuple
import re

import google.generativeai as genai
from langchain_core.documents import Document
from langchain_chroma import Chroma

from .config import GOOGLE_API_KEY, LLM_MODEL, TOP_K_RESULTS
from .vector_store import load_vector_store, search_documents

# Configurer l'API Google
genai.configure(api_key=GOOGLE_API_KEY)


# Mots-clés pour détecter les questions sur les véhicules
VEHICLE_KEYWORDS = [
    # Général véhicules
    "voiture", "véhicule", "auto", "automobile", "conduite", "conduire",
    "car", "vehicle", "drive", "driving",
    
    # Marques/Modèles
    "toyota", "auris", "hybride", "hybrid", "prius", "yaris", "corolla",
    
    # Composants mécaniques
    "moteur", "engine", "batterie", "battery", "transmission", "boîte de vitesse",
    "frein", "brake", "embrayage", "clutch", "suspension", "amortisseur",
    "direction", "steering", "roue", "wheel", "pneu", "tire", "tyre",
    "échappement", "exhaust", "catalyseur", "turbo", "injection",
    
    # Électrique/Hybride
    "électrique", "electric", "recharge", "charging", "autonomie", "range",
    "régénération", "regeneration", "ev", "mode eco", "mode sport",
    
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


# Système prompt pour le chatbot
SYSTEM_PROMPT = """Tu es un assistant expert spécialisé dans les véhicules automobiles, avec une expertise particulière sur la Toyota Auris Hybride.

🚗 TON RÔLE:
- Répondre aux questions sur les véhicules, particulièrement la Toyota Auris Hybride
- Utiliser les informations du manuel utilisateur Toyota Auris fourni en contexte
- Donner des conseils pratiques sur l'entretien, l'utilisation et le fonctionnement des véhicules

📋 RÈGLES IMPORTANTES:
1. Base tes réponses sur le contexte fourni provenant des manuels Toyota Auris
2. Si l'information n'est pas dans le contexte, tu peux utiliser tes connaissances générales sur les véhicules
3. Sois précis et cite les pages/sections du manuel quand c'est pertinent
4. Si tu n'es pas sûr, dis-le clairement
5. Réponds toujours en français

🎯 SPÉCIALISATION:
- Questions sur la Toyota Auris Hybride: utilise prioritairement le contexte du manuel
- Questions générales sur les véhicules: utilise tes connaissances automobiles
- Questions hors sujet (non liées aux véhicules): refuse poliment

⚠️ HORS CHAMP:
Si la question n'est PAS liée aux véhicules ou à l'automobile, réponds:
"Désolé, je suis un assistant spécialisé dans les véhicules automobiles, particulièrement la Toyota Auris Hybride. Je ne peux pas répondre à des questions sur d'autres sujets. Posez-moi des questions sur votre véhicule, son entretien, son fonctionnement ou ses caractéristiques!"

---

CONTEXTE DU MANUEL TOYOTA AURIS:
{context}

---"""

# Prompt pour recherche internet (quand le manuel ne suffit pas)
SYSTEM_PROMPT_WEB = """Tu es un assistant expert spécialisé dans les véhicules automobiles.

🚗 TON RÔLE:
- Répondre aux questions sur les véhicules en utilisant les informations de recherche web fournies
- Donner des conseils pratiques sur l'entretien, l'utilisation et le fonctionnement des véhicules

📋 RÈGLES IMPORTANTES:
1. Base tes réponses sur les informations de recherche web fournies
2. Cite tes sources quand c'est possible
3. Sois précis et factuel
4. Si tu n'es pas sûr, dis-le clairement
5. Réponds toujours en français
6. Ne réponds qu'aux questions liées aux véhicules

---"""


HUMAN_PROMPT = """Question de l'utilisateur: {question}

Réponse:"""



def is_vehicle_related(question: str) -> Tuple[bool, float]:
    """
    Vérifie si la question est liée aux véhicules
    Retourne (is_related, confidence_score)
    """
    question_lower = question.lower()
    
    # Liste de mots-clés qui indiquent clairement un sujet NON lié aux véhicules
    non_vehicle_keywords = [
        # Cuisine/Alimentation
        "recette", "cuisine", "cuisiner", "tarte", "gâteau", "pizza", "soupe",
        "ingrédient", "cuire", "four", "casserole", "manger", "plat", "repas",
        "dessert", "pâtisserie", "pain", "légume", "fruit", "viande", "poisson",
        
        # Météo
        "météo", "temps qu'il fait", "température extérieure", "pluie", "neige",
        "ensoleillé", "nuageux", "orage", "prévision météo",
        
        # Politique/Actualité
        "président", "ministre", "gouvernement", "élection", "politique",
        "parti", "vote", "député", "sénat",
        
        # Sport (non automobile)
        "football", "basket", "tennis", "rugby", "match", "équipe de foot",
        
        # Divertissement
        "film", "série", "musique", "chanson", "acteur", "actrice", "cinéma",
        "concert", "album",
        
        # Santé personnelle (non véhicule)
        "médecin", "docteur", "hôpital", "maladie", "médicament", "ordonnance",
        
        # Animaux
        "chien", "chat", "animal de compagnie", "vétérinaire"
    ]
    
    # Vérifier d'abord les mots-clés négatifs
    for non_kw in non_vehicle_keywords:
        if non_kw in question_lower:
            return False, 0.0
    
    # Compter les mots-clés véhicules trouvés
    found_keywords = []
    for keyword in VEHICLE_KEYWORDS:
        if keyword.lower() in question_lower:
            found_keywords.append(keyword)
    
    # Calculer le score de confiance
    if len(found_keywords) >= 3:
        return True, 1.0
    elif len(found_keywords) >= 2:
        return True, 0.9
    elif len(found_keywords) == 1:
        return True, 0.7
    else:
        return False, 0.0


def format_context(documents: List[Document]) -> str:
    """
    Formate les documents récupérés pour le contexte
    """
    if not documents:
        return "Aucune information spécifique trouvée dans le manuel."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source_file", "Document inconnu")
        page = doc.metadata.get("page", "?")
        context_parts.append(f"[Source: {source}, Page {page}]\n{doc.page_content}")
    
    return "\n\n---\n\n".join(context_parts)


class AurisChatbot:
    """
    Chatbot RAG spécialisé véhicules - Toyota Auris Hybride
    """
    
    def __init__(self, vector_store: Optional[Chroma] = None):
        """
        Initialise le chatbot
        """
        self.vector_store = vector_store or load_vector_store()
        
        # Initialiser le modèle Gemini
        self.model = genai.GenerativeModel(LLM_MODEL)
        
        # Historique de conversation (pour le contexte)
        self.conversation_history = []
        
        print("🤖 Chatbot Auris initialisé")
        if self.vector_store:
            print("   ✅ Vector store connecté (manuel Toyota Auris)")
        else:
            print("   ⚠️  Aucun vector store")
        print("   🌐 Connaissances automobiles générales activées")
    
    def _is_context_relevant(self, context: str, question: str) -> bool:
        """
        Vérifie si le contexte du manuel est pertinent pour la question
        """
        if context == "Aucune information spécifique trouvée dans le manuel.":
            return False
        
        # Vérifier si le contexte contient des mots-clés de la question
        question_words = set(question.lower().split())
        context_lower = context.lower()
        
        # Compter combien de mots de la question sont dans le contexte
        matches = sum(1 for word in question_words if len(word) > 3 and word in context_lower)
        
        # Si moins de 2 mots significatifs correspondent, le contexte n'est probablement pas pertinent
        return matches >= 2
    
    def _search_web(self, question: str) -> str:
        """
        Utilise les connaissances générales de Gemini pour les questions véhicules hors manuel
        """
        try:
            prompt = f"""{SYSTEM_PROMPT_WEB}

Question sur les véhicules: {question}

Utilise tes connaissances automobiles pour répondre de manière précise et utile en français.
Si tu n'es pas sûr d'une information, indique-le clairement.
"""
            
            response = self.model.generate_content(prompt)
            
            # Ajouter une indication que la réponse vient des connaissances générales
            return f"🌐 *Réponse basée sur mes connaissances automobiles:*\n\n{response.text}"
            
        except Exception as e:
            # En cas d'erreur
            return None
    
    def chat(self, question: str) -> str:
        """
        Traite une question et retourne une réponse
        """
        # Vérifier si la question est liée aux véhicules
        is_related, confidence = is_vehicle_related(question)
        
        if not is_related:
            return (
                "🚫 Désolé, je suis un assistant spécialisé dans les véhicules automobiles, "
                "particulièrement la **Toyota Auris Hybride**.\n\n"
                "Je ne peux pas répondre à des questions sur d'autres sujets.\n\n"
                "💡 **Posez-moi des questions sur:**\n"
                "- 🔧 L'entretien de votre véhicule\n"
                "- ⚡ Le fonctionnement du système hybride\n"
                "- 🚗 Les caractéristiques de la Toyota Auris\n"
                "- 📖 Les instructions du manuel utilisateur\n"
                "- 🛠️ Le diagnostic de problèmes\n"
            )
        
        # Récupérer le contexte pertinent du manuel
        context = ""
        use_manual = False
        
        if self.vector_store:
            relevant_docs = search_documents(question, self.vector_store, k=TOP_K_RESULTS)
            context = format_context(relevant_docs)
            use_manual = self._is_context_relevant(context, question)
        
        # Générer la réponse
        try:
            if use_manual:
                # Utiliser le manuel Toyota
                full_prompt = SYSTEM_PROMPT.format(context=context) + "\n\n" + HUMAN_PROMPT.format(question=question)
                response = self.model.generate_content(full_prompt)
                answer = f"📖 *Réponse basée sur le manuel Toyota Auris:*\n\n{response.text}"
            else:
                # Essayer la recherche web pour les questions véhicules hors manuel
                web_answer = self._search_web(question)
                
                if web_answer:
                    answer = web_answer
                else:
                    # Fallback: utiliser le modèle standard avec connaissances générales
                    prompt = f"{SYSTEM_PROMPT_WEB}\n\n{HUMAN_PROMPT.format(question=question)}"
                    response = self.model.generate_content(prompt)
                    answer = f"💡 *Réponse basée sur mes connaissances générales:*\n\n{response.text}"
            
            # Ajouter à l'historique
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "confidence": confidence,
                "source": "manual" if use_manual else "web"
            })
            
            return answer
            
        except Exception as e:
            return f"❌ Erreur lors de la génération de la réponse: {str(e)}"

    
    def clear_history(self):
        """
        Efface l'historique de conversation
        """
        self.conversation_history = []
        print("🗑️ Historique effacé")
    
    def get_history(self) -> List[dict]:
        """
        Retourne l'historique de conversation
        """
        return self.conversation_history


def create_chatbot() -> AurisChatbot:
    """
    Factory function pour créer un chatbot
    """
    return AurisChatbot()
