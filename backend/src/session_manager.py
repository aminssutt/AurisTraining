"""
Gestionnaire de sessions utilisateur
Chaque session a sa propre base vectorielle ChromaDB
"""
import os
import uuid
import shutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from .config import DATA_DIR


class SessionStatus(Enum):
    """États possibles d'une session"""
    CREATED = "created"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


@dataclass
class SessionProgress:
    """Progression du traitement d'une session"""
    status: SessionStatus = SessionStatus.CREATED
    progress: int = 0  # 0-100
    message: str = "Session créée"
    current_step: str = ""
    total_pages: int = 0
    processed_pages: int = 0
    error: Optional[str] = None


@dataclass
class Session:
    """Représente une session utilisateur"""
    id: str
    vehicle_name: str
    created_at: datetime
    pdf_files: List[str] = field(default_factory=list)
    progress: SessionProgress = field(default_factory=SessionProgress)
    
    @property
    def session_dir(self) -> Path:
        """Répertoire de la session"""
        return DATA_DIR / "sessions" / self.id
    
    @property
    def pdf_dir(self) -> Path:
        """Répertoire des PDFs de la session"""
        return self.session_dir / "pdfs"
    
    @property
    def chroma_dir(self) -> Path:
        """Répertoire ChromaDB de la session"""
        return self.session_dir / "chroma_db"
    
    def to_dict(self) -> dict:
        """Convertit la session en dictionnaire"""
        return {
            "id": self.id,
            "vehicle_name": self.vehicle_name,
            "created_at": self.created_at.isoformat(),
            "pdf_files": self.pdf_files,
            "status": self.progress.status.value,
            "progress": self.progress.progress,
            "message": self.progress.message,
            "current_step": self.progress.current_step,
            "total_pages": self.progress.total_pages,
            "processed_pages": self.progress.processed_pages,
            "error": self.progress.error
        }


class SessionManager:
    """Gestionnaire de sessions en mémoire"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        
        # Créer le répertoire des sessions
        sessions_dir = DATA_DIR / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        print("📁 SessionManager initialisé")
    
    def create_session(self, vehicle_name: str) -> Session:
        """Crée une nouvelle session"""
        session_id = str(uuid.uuid4())
        
        session = Session(
            id=session_id,
            vehicle_name=vehicle_name,
            created_at=datetime.now()
        )
        
        # Créer les répertoires
        session.pdf_dir.mkdir(parents=True, exist_ok=True)
        session.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        with self._lock:
            self.sessions[session_id] = session
        
        print(f"✅ Session créée: {session_id} pour {vehicle_name}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Récupère une session par son ID"""
        with self._lock:
            return self.sessions.get(session_id)
    
    def update_progress(self, session_id: str, 
                       status: Optional[SessionStatus] = None,
                       progress: Optional[int] = None,
                       message: Optional[str] = None,
                       current_step: Optional[str] = None,
                       total_pages: Optional[int] = None,
                       processed_pages: Optional[int] = None,
                       error: Optional[str] = None):
        """Met à jour la progression d'une session"""
        session = self.get_session(session_id)
        if not session:
            return
        
        with self._lock:
            if status is not None:
                session.progress.status = status
            if progress is not None:
                session.progress.progress = progress
            if message is not None:
                session.progress.message = message
            if current_step is not None:
                session.progress.current_step = current_step
            if total_pages is not None:
                session.progress.total_pages = total_pages
            if processed_pages is not None:
                session.progress.processed_pages = processed_pages
            if error is not None:
                session.progress.error = error
    
    def add_pdf(self, session_id: str, filename: str):
        """Ajoute un PDF à la liste des fichiers de la session"""
        session = self.get_session(session_id)
        if session:
            with self._lock:
                session.pdf_files.append(filename)
    
    def delete_session(self, session_id: str) -> bool:
        """Supprime une session et ses fichiers"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Supprimer les fichiers
        if session.session_dir.exists():
            shutil.rmtree(session.session_dir)
        
        # Supprimer de la mémoire
        with self._lock:
            del self.sessions[session_id]
        
        print(f"🗑️ Session supprimée: {session_id}")
        return True
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Nettoie les sessions plus vieilles que max_age_hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        sessions_to_delete = []
        with self._lock:
            for session_id, session in self.sessions.items():
                if session.created_at < cutoff:
                    sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            self.delete_session(session_id)
        
        if sessions_to_delete:
            print(f"🧹 {len(sessions_to_delete)} sessions nettoyées")


# Instance globale
session_manager = SessionManager()
