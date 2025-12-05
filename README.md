# 🚗 Vehicle Assistant - Chatbot RAG Personnalisé

Un chatbot intelligent qui crée un assistant personnalisé pour **n'importe quel véhicule** en analysant les manuels PDF uploadés par l'utilisateur.

## ✨ Fonctionnalités

- **Upload de PDFs** : Glissez-déposez vos manuels de véhicule
- **Traitement automatique** : Extraction, découpage et indexation avec IA
- **Chatbot personnalisé** : Assistant dédié à VOTRE véhicule
- **Sessions isolées** : Chaque utilisateur a sa propre base de connaissances
- **Interface moderne** : Design sombre et élégant

## 🚀 Flux utilisateur

```
1. 📝 Page d'accueil
   └── Entrer le nom du véhicule
   └── Uploader les PDFs (manuels, guides...)

2. ⏳ Page de traitement
   └── Barre de progression en temps réel
   └── Extraction → Découpage → Indexation

3. 💬 Page Chatbot
   └── Assistant personnalisé "Mon [Véhicule]"
   └── Réponses basées sur VOS documents
```

## 🏗️ Architecture

```
Auris/
├── backend/                 # API Flask
│   ├── api.py               # Endpoints REST
│   ├── src/
│   │   ├── session_manager.py   # Gestion des sessions
│   │   ├── pdf_processor.py     # Traitement des PDFs
│   │   ├── session_chatbot.py   # Chatbot par session
│   │   ├── vector_store.py      # ChromaDB
│   │   └── config.py
│   └── data/sessions/       # Données par session
│
└── frontend/                # React + Vite
    └── src/pages/
        ├── UploadPage.jsx       # Upload des PDFs
        ├── ProcessingPage.jsx   # Progression
        └── ChatPage.jsx         # Interface chat
```

## 🔧 Installation locale

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configurer l'API key
cp .env.example .env
# Éditer .env avec votre GOOGLE_API_KEY

python api.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🌐 Déploiement

### Backend (Render)
- **Root Directory** : `backend`
- **Start Command** : `gunicorn api:app --bind 0.0.0.0:$PORT`
- **Variables** : `GOOGLE_API_KEY`, `FRONTEND_URL`

### Frontend (Vercel)
- **Root Directory** : `frontend`
- **Variable** : `VITE_API_URL` (URL de l'API Render)

## 📡 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/session/create` | Créer une session |
| POST | `/api/session/{id}/upload` | Uploader un PDF |
| POST | `/api/session/{id}/process` | Lancer le traitement |
| GET | `/api/session/{id}/status` | Statut de la session |
| POST | `/api/session/{id}/chat` | Envoyer un message |
| GET | `/api/health` | Santé de l'API |

## 🔒 Sécurité

- Sessions temporaires (non persistantes)
- Données isolées par utilisateur
- Pas de stockage permanent des PDFs
- `.env` jamais commité

## 🛠️ Technologies

- **Backend** : Python, Flask, LangChain, ChromaDB, Google Gemini
- **Frontend** : React 18, Vite, React Router
- **Embeddings** : HuggingFace sentence-transformers
