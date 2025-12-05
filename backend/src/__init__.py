"""
Package Auris Chatbot - Chatbot RAG pour Toyota Auris Hybride
"""
from .config import GOOGLE_API_KEY, LLM_MODEL, EMBEDDING_MODEL
from .pdf_loader import process_pdfs
from .vector_store import create_vector_store, load_vector_store, search_documents
from .chatbot import AurisChatbot, create_chatbot

__all__ = [
    "GOOGLE_API_KEY",
    "LLM_MODEL", 
    "EMBEDDING_MODEL",
    "process_pdfs",
    "create_vector_store",
    "load_vector_store",
    "search_documents",
    "AurisChatbot",
    "create_chatbot"
]
