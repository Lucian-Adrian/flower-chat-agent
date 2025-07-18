"""
XOFlowers AI Agent - Main Source Package
Instagram AI Agent for XOFlowers built with ChromaDB + LLMs
"""

__version__ = "2.0.0"

# Import classes only when explicitly requested to avoid circular imports
def get_telegram_app():
    from .api.telegram_integration import TelegramApp
    return TelegramApp

def get_instagram_app():
    from .api.instagram_integration import InstagramApp
    return InstagramApp
