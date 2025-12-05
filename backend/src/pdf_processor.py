"""
Processeur de PDFs pour une session
Gère l'extraction, le chunking et l'indexation
"""
import threading
from pathlib import Path
from typing import List, Callable, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from pypdf import PdfReader

from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .vector_store import get_embeddings
from .session_manager import session_manager, SessionStatus


class PDFProcessor:
    """Processeur de PDFs pour une session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session = session_manager.get_session(session_id)
        
        if not self.session:
            raise ValueError(f"Session {session_id} introuvable")
    
    def process_pdfs_async(self):
        """Lance le traitement en arrière-plan"""
        thread = threading.Thread(target=self._process_pdfs)
        thread.daemon = True
        thread.start()
    
    def _process_pdfs(self):
        """Traite tous les PDFs de la session"""
        try:
            session_manager.update_progress(
                self.session_id,
                status=SessionStatus.PROCESSING,
                progress=5,
                message="Démarrage du traitement...",
                current_step="initialization"
            )
            
            # 1. Lister les PDFs
            pdf_files = list(self.session.pdf_dir.glob("*.pdf"))
            if not pdf_files:
                raise ValueError("Aucun fichier PDF trouvé")
            
            session_manager.update_progress(
                self.session_id,
                progress=10,
                message=f"{len(pdf_files)} PDF(s) trouvé(s)",
                current_step="listing"
            )
            
            # 2. Extraire le texte de tous les PDFs
            all_documents = []
            total_pages = 0
            
            # Compter le total de pages d'abord
            for pdf_path in pdf_files:
                try:
                    reader = PdfReader(str(pdf_path))
                    total_pages += len(reader.pages)
                except:
                    pass
            
            session_manager.update_progress(
                self.session_id,
                total_pages=total_pages,
                message=f"Extraction de {total_pages} pages..."
            )
            
            processed_pages = 0
            for pdf_path in pdf_files:
                docs = self._extract_pdf(pdf_path, processed_pages, total_pages)
                all_documents.extend(docs)
                processed_pages += len(docs)
            
            if not all_documents:
                raise ValueError("Aucun texte extrait des PDFs")
            
            session_manager.update_progress(
                self.session_id,
                progress=50,
                message=f"{len(all_documents)} pages extraites",
                current_step="extraction_complete",
                processed_pages=processed_pages
            )
            
            # 3. Découper en chunks
            session_manager.update_progress(
                self.session_id,
                progress=60,
                message="Découpage du texte...",
                current_step="chunking"
            )
            
            chunks = self._chunk_documents(all_documents)
            
            session_manager.update_progress(
                self.session_id,
                progress=70,
                message=f"{len(chunks)} segments créés",
                current_step="chunking_complete"
            )
            
            # 4. Créer les embeddings et indexer
            session_manager.update_progress(
                self.session_id,
                progress=75,
                message="Indexation en cours...",
                current_step="indexing"
            )
            
            self._create_vector_store(chunks)
            
            # 5. Terminé !
            session_manager.update_progress(
                self.session_id,
                status=SessionStatus.READY,
                progress=100,
                message="Chatbot prêt !",
                current_step="complete"
            )
            
            print(f"✅ Session {self.session_id} traitée: {len(chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Erreur traitement session {self.session_id}: {e}")
            session_manager.update_progress(
                self.session_id,
                status=SessionStatus.ERROR,
                progress=0,
                message="Erreur lors du traitement",
                error=str(e)
            )
    
    def _extract_pdf(self, pdf_path: Path, processed_so_far: int, total_pages: int) -> List[Document]:
        """Extrait le texte d'un PDF"""
        documents = []
        
        try:
            reader = PdfReader(str(pdf_path))
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source_file": pdf_path.name,
                            "page": i + 1,
                            "total_pages": len(reader.pages)
                        }
                    )
                    documents.append(doc)
                
                # Mettre à jour la progression
                current_processed = processed_so_far + i + 1
                progress = 10 + int((current_processed / total_pages) * 40)  # 10-50%
                
                session_manager.update_progress(
                    self.session_id,
                    progress=progress,
                    processed_pages=current_processed,
                    message=f"Extraction: {current_processed}/{total_pages} pages"
                )
                
        except Exception as e:
            print(f"⚠️ Erreur lecture {pdf_path.name}: {e}")
        
        return documents
    
    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Découpe les documents en chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        chunks = splitter.split_documents(documents)
        return chunks
    
    def _create_vector_store(self, chunks: List[Document]):
        """Crée le vector store ChromaDB pour la session"""
        embeddings = get_embeddings()
        
        # Indexer par lots pour suivre la progression
        batch_size = 50
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        vector_store = None
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            progress = 75 + int((batch_num / total_batches) * 20)  # 75-95%
            session_manager.update_progress(
                self.session_id,
                progress=progress,
                message=f"Indexation: lot {batch_num}/{total_batches}"
            )
            
            if vector_store is None:
                vector_store = Chroma.from_documents(
                    documents=batch,
                    embedding=embeddings,
                    persist_directory=str(self.session.chroma_dir)
                )
            else:
                vector_store.add_documents(batch)
        
        return vector_store


def process_session_pdfs(session_id: str):
    """Fonction utilitaire pour lancer le traitement"""
    processor = PDFProcessor(session_id)
    processor.process_pdfs_async()
