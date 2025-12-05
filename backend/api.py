"""
API Flask pour le chatbot Toyota Auris
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.chatbot import create_chatbot
from src.vector_store import load_vector_store

app = Flask(__name__)

# Configuration CORS pour production et développement
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.vercel.app",  # Pour tous les sous-domaines Vercel
]

# Récupérer l'origine autorisée depuis les variables d'environnement
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# Initialiser le chatbot au démarrage
print("🚀 Initialisation du chatbot...")
chatbot = None

def get_chatbot():
    global chatbot
    if chatbot is None:
        chatbot = create_chatbot()
    return chatbot


# Questions suggérées
SUGGESTED_QUESTIONS = [
    {
        "id": 1,
        "text": "Quelle est la pression recommandée pour les pneus ?",
        "category": "entretien"
    },
    {
        "id": 2,
        "text": "Comment fonctionne le système hybride ?",
        "category": "hybride"
    },
    {
        "id": 3,
        "text": "Que signifie le voyant moteur allumé ?",
        "category": "diagnostic"
    },
    {
        "id": 4,
        "text": "Comment faire une vidange sur l'Auris ?",
        "category": "entretien"
    },
    {
        "id": 5,
        "text": "Quelle est la capacité du coffre ?",
        "category": "caracteristiques"
    },
    {
        "id": 6,
        "text": "Comment activer le mode EV électrique ?",
        "category": "hybride"
    },
    {
        "id": 7,
        "text": "Quand faut-il changer les plaquettes de frein ?",
        "category": "entretien"
    },
    {
        "id": 8,
        "text": "Comment connecter mon téléphone en Bluetooth ?",
        "category": "multimedia"
    }
]


@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API"""
    bot = get_chatbot()
    doc_count = 0
    if bot and bot.vector_store:
        try:
            doc_count = bot.vector_store._collection.count()
        except:
            doc_count = 0
    
    return jsonify({
        "status": "ok",
        "message": "API Toyota Auris Chatbot opérationnelle",
        "chatbot_ready": bot is not None,
        "documents_count": doc_count
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint principal pour le chat"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Message requis"
            }), 400
        
        question = data['message']
        
        # Obtenir la réponse du chatbot
        bot = get_chatbot()
        response = bot.chat(question)
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Retourne les questions suggérées"""
    return jsonify({
        "suggestions": SUGGESTED_QUESTIONS
    })


@app.route('/api/history', methods=['GET'])
def get_history():
    """Retourne l'historique de conversation"""
    bot = get_chatbot()
    return jsonify({
        "history": bot.get_history()
    })


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Efface l'historique de conversation"""
    bot = get_chatbot()
    bot.clear_history()
    return jsonify({
        "status": "ok",
        "success": True,
        "message": "Historique effacé"
    })


if __name__ == '__main__':
    # Pré-charger le chatbot
    get_chatbot()
    print("\n🌐 API démarrée sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
