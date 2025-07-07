import json
import os
import re
import logging
from typing import Dict, List, Tuple, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import requests
from datetime import datetime
import time
import chromadb
import csv
from sentence_transformers import SentenceTransformer
import hashlib
import uuid
from difflib import SequenceMatcher
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment variable
openai_key = os.getenv('OPENAI_KEY')
if openai_key:
    os.environ["OPENAI_KEY"] = openai_key
else:
    print("WARNING: OPENAI_KEY not found in environment variables. AI features may not work properly.")

# Import AI Agent ULTRA
try:
    from ai_agent_integration import create_ai_agent
    ai_agent = create_ai_agent()
    logger.info(f"🤖 AI Agent ULTRA loaded with {ai_agent.get_performance_stats()['database_size']} products")
    ULTRA_MODE = True
except Exception as e:
    logger.error(f"❌ Failed to initialize AI Agent ULTRA: {e}")
    ai_agent = None
    ULTRA_MODE = False

class MultilingualProcessor:
    """Advanced multilingual processing for XOFlowers"""
    
    def __init__(self):
        # Expanded language mappings
        self.language_mappings = {
            "ro": {
                "colors": {
                    "roșu": ["roșu", "roșie", "red", "rouge", "красный"],
                    "alb": ["alb", "albă", "white", "blanc", "белый"],
                    "roz": ["roz", "pink", "rose", "розовый"],
                    "galben": ["galben", "galbenă", "yellow", "jaune", "жёлтый"],
                    "violet": ["violet", "violetă", "purple", "violet", "фиолетовый"],
                    "albastru": ["albastru", "albastră", "blue", "bleu", "синий"],
                    "verde": ["verde", "green", "vert", "зелёный"],
                    "portocaliu": ["portocaliu", "orange", "оранжевый"],
                    "negru": ["negru", "neagră", "black", "noir", "чёрный"],
                    "multicolor": ["multicolor", "mixed", "mixte", "разноцветный"]
                },
                "occasions": {
                    "ziua_de_nastere": ["ziua de naștere", "birthday", "anniversaire", "день рождения"],
                    "nunta": ["nuntă", "wedding", "mariage", "свадьба"],
                    "valentine": ["valentine", "ziua îndrăgostiților", "saint valentin", "день святого валентина"],
                    "8_martie": ["8 martie", "ziua femeii", "womens day", "женский день"],
                    "paste": ["paște", "easter", "pâques", "пасха"],
                    "craciun": ["crăciun", "christmas", "noël", "рождество"],
                    "absolvire": ["absolvire", "graduation", "remise de diplôme", "выпускной"],
                    "multumire": ["mulțumire", "thank you", "merci", "спасибо"],
                    "inmormantare": ["înmormântare", "funeral", "funérailles", "похороны"]
                },
                "products": {
                    "buchet": ["buchet", "bouquet", "букет"],
                    "cutie": ["cutie", "box", "boîte", "коробка"],
                    "trandafiri": ["trandafiri", "roses", "roses", "розы"],
                    "bujori": ["bujori", "peonies", "pivoines", "пионы"],
                    "difuzor": ["difuzor", "diffuser", "diffuseur", "диффузор"],
                    "plantă": ["plantă", "plant", "plante", "растение"]
                }
            }
        }
        
        # Fuzzy matching threshold
        self.fuzzy_threshold = 0.8
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        # Remove diacritics
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Convert to lowercase and clean
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)      # Normalize whitespace
        
        return text
    
    def fuzzy_match(self, query: str, target: str) -> float:
        """Calculate fuzzy similarity between two strings"""
        query_norm = self.normalize_text(query)
        target_norm = self.normalize_text(target)
        
        return SequenceMatcher(None, query_norm, target_norm).ratio()
    
    def enhance_query_multilingual(self, query: str) -> str:
        """Enhance query with multilingual synonyms"""
        enhanced_parts = [query]
        query_lower = query.lower()
        
        # Add synonyms from all categories
        for category, items in self.language_mappings["ro"].items():
            for key, synonyms in items.items():
                # Check for fuzzy matches
                for synonym in synonyms:
                    if (synonym.lower() in query_lower or 
                        self.fuzzy_match(query, synonym) > self.fuzzy_threshold):
                        # Add other synonyms
                        enhanced_parts.extend([s for s in synonyms if s not in enhanced_parts])
                        break
        
        return " ".join(enhanced_parts)
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Romanian specific characters
        ro_chars = ['ă', 'â', 'î', 'ș', 'ț']
        if any(char in text.lower() for char in ro_chars):
            return "ro"
        
        # English common words
        en_words = ['the', 'and', 'for', 'with', 'bouquet', 'flowers', 'roses']
        if any(word in text.lower().split() for word in en_words):
            return "en"
        
        # Russian Cyrillic
        if any('\u0400' <= char <= '\u04FF' for char in text):
            return "ru"
        
        # French
        fr_words = ['le', 'la', 'de', 'et', 'pour', 'avec']
        if any(word in text.lower().split() for word in fr_words):
            return "fr"
        
        return "ro"  # Default to Romanian

class XOFlowersAgent:
    """Simplified agent for basic functionality"""
    
    def __init__(self):
        self.business_info = {
            "name": "XOFlowers",
            "website": "https://xoflowers.md",
            "phone": "+373 22 123 456"
        }
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process incoming message and generate response"""
        try:
            # Check if ULTRA mode is available first
            if ULTRA_MODE and ai_agent:
                # Use ULTRA AI Agent for enhanced processing
                recommendations = ai_agent.intelligent_search(
                    user_query=message,
                    max_results=3,
                    user_id=user_id
                )
                
                if recommendations:
                    response = "🌸 **XOFlowers AI ULTRA** - Am găsit aceste produse pentru tine:\n\n"
                    
                    for i, rec in enumerate(recommendations, 1):
                        confidence_emoji = "🎯" if rec.confidence > 0.7 else "✨" if rec.confidence > 0.4 else "💫"
                        
                        response += f"{confidence_emoji} **{i}. {rec.title}**\n"
                        response += f"   💰 {rec.price} MDL ({rec.price_tier})\n"
                        response += f"   📊 Match: {rec.confidence:.0%}\n"
                        
                        if rec.colors:
                            response += f"   🎨 Culori: {', '.join(rec.colors)}\n"
                        
                        if rec.occasions:
                            response += f"   🎉 Ocazii: {', '.join(rec.occasions)}\n"
                        
                        response += "\n"
                    
                    response += "💬 *Vrei să vezi mai multe detalii sau ai întrebări?*\n"
                    response += f"⚡ *Căutare ULTRA completă în {recommendations[0].search_time:.2f}s*"
                    
                    return response
                else:
                    # Fallback to enhanced no-results response
                    response = "🤔 Nu am găsit produse exacte pentru căutarea ta.\n\n"
                    response += "💡 *Încearcă cu:*\n"
                    response += "- Nume specific de flori (trandafiri, bujori)\n"
                    response += "- Culori (roșu, alb, roz)\n"
                    response += "- Ocazii (nuntă, aniversare, iubire)\n"
                    response += "- Buget (ieftin, premium, luxury)\n\n"
                    response += "📞 Sau contactează-ne direct: +373 22 123 456"
                    return response
            
            # Fallback response if ULTRA is not available
            return f"🌸 Bună! Sunt aici să te ajut cu florile de la {self.business_info['name']}. Te rog contactează-ne la {self.business_info['phone']} pentru asistență completă."
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Ne pare rău, a apărut o eroare tehnică. Vă rugăm să ne contactați la +373 22 123 456. 🌸"

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize XOFlowers agent
agent = XOFlowersAgent()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "XOFlowers Instagram AI Agent is running",
        "version": "3.0 - ChromaDB ULTRA Edition",
        "ultra_mode": ULTRA_MODE,
        "timestamp": datetime.now().isoformat(),
        "ultra_products": ai_agent.get_performance_stats()['database_size'] if ULTRA_MODE and ai_agent else 0
    })

@app.route("/api/ultra-search", methods=["POST"])
def ultra_search():
    """Ultra-fast intelligent search cu AI Agent"""
    try:
        if not ULTRA_MODE or not ai_agent:
            return jsonify({'error': 'AI Agent ULTRA not available'}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_query = data.get('query', '')
        user_id = data.get('user_id', f'user_{uuid.uuid4()}')
        max_results = data.get('max_results', 5)
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Execute intelligent search
        recommendations = ai_agent.intelligent_search(
            user_query=user_query,
            max_results=max_results,
            user_id=user_id
        )
        
        # Format results
        results = []
        for rec in recommendations:
            results.append({
                'id': rec.id,
                'title': rec.title,
                'description': rec.description[:200] + ('...' if len(rec.description) > 200 else ''),
                'price': rec.price,
                'price_tier': rec.price_tier,
                'category': rec.category,
                'flower_type': rec.flower_type,
                'colors': rec.colors,
                'occasions': rec.occasions,
                'confidence': round(rec.confidence, 3),
                'similarity_score': round(rec.similarity_score, 3),
                'search_time': round(rec.search_time, 3)
            })
        
        return jsonify({
            'status': 'success',
            'query': user_query,
            'user_id': user_id,
            'results': results,
            'total_found': len(results),
            'ultra_mode': True,
            'performance': {
                'search_time': f"{results[0]['search_time']:.3f}s" if results else "0s",
                'confidence_range': f"{min(r['confidence'] for r in results):.2f}-{max(r['confidence'] for r in results):.2f}" if results else "N/A"
            }
        })
        
    except Exception as e:
        logger.error(f"Ultra search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/personalized-recommendations/<user_id>", methods=["GET"])
def get_personalized_recommendations(user_id):
    """Obține recomandări personalizate pentru user"""
    try:
        if not ULTRA_MODE or not ai_agent:
            return jsonify({'error': 'AI Agent ULTRA not available'}), 500
            
        # Get user preferences from query params
        category = request.args.get('category', '')
        price_range = request.args.get('price_range', '')
        
        # Execute search with user preferences
        recommendations = ai_agent.intelligent_search(
            user_query=f"{category} {price_range}",
            max_results=5,
            user_id=user_id
        )
        
        # Format results
        results = []
        for rec in recommendations:
            results.append({
                'id': rec.id,
                'title': rec.title,
                'price': rec.price,
                'price_tier': rec.price_tier,
                'category': rec.category,
                'confidence': round(rec.confidence, 3)
            })
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'recommendations': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"Personalized recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/performance-stats", methods=["GET"])
def get_performance_stats():
    """Get system performance statistics"""
    try:
        if ULTRA_MODE and ai_agent:
            stats = ai_agent.get_performance_stats()
            return jsonify({
                'ultra_mode': True,
                'database_size': stats['database_size'],
                'avg_query_time': stats['avg_query_time'],
                'total_queries': stats['total_queries'],
                'cache_hit_rate': stats['cache_hit_rate'],
                'cache_size': stats['cache_size']
            })
        else:
            return jsonify({
                'ultra_mode': False,
                'message': 'Running in standard mode'
            })
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ultra_mode': ULTRA_MODE,
        'version': '3.0-ULTRA'
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = data.get("message")
        user_id = data.get("user_id", "web_user")
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process message with agent
        response = agent.process_message(user_id, user_message)
        
        return jsonify({
            'response': response,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'ultra_mode': ULTRA_MODE
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    print("🚀 Starting XOFlowers Flask App with AI Agent...")
    
    if ULTRA_MODE and ai_agent:
        stats = ai_agent.get_performance_stats()
        print(f"✅ AI Agent ULTRA loaded: {stats['database_size']} products")
        print(f"⚡ Average search time: {stats['avg_query_time']:.3f}s")
        print(f"💾 Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    else:
        print("⚠️ AI Agent ULTRA not available - using fallback system")
    
    print(f"🌐 Server starting on http://127.0.0.1:5000")
    print(f"📊 Mode: {'ULTRA' if ULTRA_MODE else 'Standard'}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
