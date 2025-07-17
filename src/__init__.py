"""
XOFlowers AI Agent - Main Source Package
Instagram AI Agent for XOFlowers built with ChromaDB + LLMs
"""

from .api import TelegramApp, InstagramApp
from .intelligence import ChromaDBManager, ConversationManager
from .database import XOFlowersSearchEngine
from .security import SecurityFilter

__version__ = "2.0.0"
__all__ = ['TelegramApp', 'InstagramApp', 'ChromaDBManager', 'ConversationManager', 'XOFlowersSearchEngine', 'SecurityFilter']