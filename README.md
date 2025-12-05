# 🚗 Toyota Auris Chatbot

Un chatbot intelligent spécialisé dans les véhicules Toyota Auris Hybride, utilisant la technologie RAG (Retrieval-Augmented Generation) avec les manuels officiels Toyota.

## 🌟 Fonctionnalités

- **Questions véhicules** : Répond aux questions sur l'entretien, le fonctionnement et les caractéristiques de l'Auris
- **RAG avec manuels Toyota** : Utilise les manuels officiels comme base de connaissances
- **Filtrage intelligent** : Ne répond qu'aux questions liées aux véhicules
- **Interface moderne** : Frontend React avec thème sombre

## 🏗️ Architecture

```
Auris/
├── backend/           # API Flask + Chatbot RAG
│   ├── api.py         # Endpoints REST
│   ├── src/
│   │   ├── chatbot.py     # Logique du chatbot
│   │   ├── config.py      # Configuration
│   │   ├── pdf_loader.py  # Chargement des PDFs
│   │   └── vector_store.py # ChromaDB
│   └── data/pdfs/     # Manuels Toyota (non inclus)
│
└── frontend/          # React + Vite
    └── src/
        ├── App.jsx    # Interface chat
        └── App.css    # Styles
```

## 🚀 Déploiement

### Backend (Render)

1. Créer un nouveau Web Service sur [Render](https://render.com)
2. Connecter le repo GitHub
3. Configurer :
   - **Root Directory** : `backend`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn api:app --bind 0.0.0.0:$PORT`
4. Ajouter les variables d'environnement :
   - `GOOGLE_API_KEY` : Votre clé API Google Gemini
   - `FRONTEND_URL` : URL du frontend Vercel

### Frontend (Vercel)

1. Importer le projet sur [Vercel](https://vercel.com)
2. Configurer :
   - **Root Directory** : `frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`
3. Ajouter la variable d'environnement :
   - `VITE_API_URL` : URL de l'API Render (ex: `https://votre-api.onrender.com/api`)

## 💻 Développement local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt

# Configurer l'API key
cp .env.example .env
# Éditer .env avec votre GOOGLE_API_KEY

# Indexer les PDFs (première fois)
python main.py --index

# Lancer l'API
python api.py
```

### Frontend

```bash
cd frontend
npm install

# Pour le développement
npm run dev

# Pour la production
npm run build
```

## 🔧 Technologies

- **Backend** : Python, Flask, LangChain, ChromaDB, Google Gemini
- **Frontend** : React, Vite
- **Embeddings** : HuggingFace sentence-transformers
- **Déploiement** : Render (backend), Vercel (frontend)

## ⚠️ Notes importantes

- Les fichiers PDF des manuels ne sont pas inclus dans le repo
- La base de données ChromaDB (`chroma_db/`) doit être régénérée localement
- Ne jamais commiter le fichier `.env` contenant les clés API

## 📝 Licence

Projet privé - Usage personnel uniquement.
