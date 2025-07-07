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

class Intent:
    """Represents a detected intent with confidence score"""
    def __init__(self, name: str, confidence: float):
        self.name = name
        self.confidence = confidence

class EntityExtractor:
    """Advanced entity extraction for flower shop domain with fuzzy matching"""
    
    def __init__(self):
        self.multilingual_processor = MultilingualProcessor()
        
        # Enhanced entities with better coverage
        self.entities = {
            "product_type": [
                "buchet", "cutie", "plantă", "aranjament", "trandafiri", 
                "lalele", "orhidee", "crizanteme", "difuzor", "cadou",
                "flori", "floare", "bouquet", "box", "plant", "composition",
                "gifts", "roses", "tulips", "orchid", "bujori", "peony",
                "coș", "basket", "decorațiune", "decoration"
            ],
            "color": [
                "roșu", "alb", "roz", "galben", "albastru", "violet", 
                "portocaliu", "multicolor", "pastel", "verde", "negru",
                "red", "white", "pink", "yellow", "blue", "purple", "orange",
                "coral", "ivory", "cream", "burgundy", "crimson", "lavender"
            ],
            "occasion": [
                "ziua de naștere", "nuntă", "aniversare", "8 martie", 
                "valentine's day", "paște", "crăciun", "absolvire", 
                "mulțumire", "înmormântare", "botez", "logodnă", "iubire",
                "birthday", "wedding", "anniversary", "graduation", "funeral",
                "dragobete", "name day", "promotion", "congratulations"
            ],
            "style": [
                "elegant", "rustic", "modern", "clasic", "romantic", 
                "luxos", "minimal", "vintage", "contemporary", "traditional"
            ],
            "size": [
                "mic", "mare", "mediu", "small", "large", "medium", 
                "mini", "giant", "compact", "impressive", "spectacular"
            ],
            "subscription_type": [
                "săptămânal", "lunar", "trimestrial", "anual", 
                "ocazional", "sezonier", "weekly", "monthly", "quarterly", "yearly"
            ],
            "payment_method": [
                "card", "numerar", "transfer", "paypal", "la livrare",
                "cash", "ramburs", "credit card", "bank transfer"
            ]
        }
        
        # Enhanced price ranges
        self.price_ranges = {
            "very_budget": (0, 200),
            "budget": (201, 500),
            "medium": (501, 1000), 
            "premium": (1001, 2000),
            "luxury": (2001, 3000),
            "ultra_luxury": (3001, float('inf'))
        }
        
        # Content filtering with Romanian terms
        self.offensive_terms = [
            "stupid", "idiot", "hate", "kill", "die", "damn", "fuck", "shit",
            "prost", "idiot", "ură", "moarte", "dracu", "naiba", "tampitu"
        ]
        
        self.jailbreak_patterns = [
            r"ignore.*instruction",
            r"forget.*role",
            r"act.*as",
            r"pretend.*to.*be",
            r"bypass.*restrictions",
            r"ignoră.*instrucțiuni",
            r"uită.*rolul",
            r"comportă.*ca"
        ]
    
    def is_offensive(self, message: str) -> bool:
        """Check if message contains offensive content"""
        message_lower = message.lower()
        return any(term in message_lower for term in self.offensive_terms)
    
    def is_jailbreak_attempt(self, message: str) -> bool:
        """Detect jailbreak attempts"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.jailbreak_patterns)
    
    def extract_entities(self, message: str) -> Dict[str, str]:
        """Extract all possible entities from a message with fuzzy matching"""
        result = {}
        message_lower = message.lower()
        normalized_message = self.multilingual_processor.normalize_text(message)
        
        # Extract entities with fuzzy matching
        for entity_type, values in self.entities.items():
            best_match = None
            best_score = 0
            
            for value in values:
                # Exact match first
                if value.lower() in message_lower:
                    result[entity_type] = value
                    break
                
                # Fuzzy match
                score = self.multilingual_processor.fuzzy_match(normalized_message, value)
                if score > 0.8 and score > best_score:
                    best_match = value
                    best_score = score
            
            # Use best fuzzy match if no exact match
            if entity_type not in result and best_match:
                result[entity_type] = best_match
        
        # Enhanced price extraction
        result.update(self._extract_price_info(message_lower))
        
        # Extract quantity
        quantity = self._extract_quantity(message_lower)
        if quantity:
            result["quantity"] = quantity
        
        return result
    
    def _extract_price_info(self, message_lower: str) -> Dict[str, str]:
        """Extract comprehensive price information"""
        price_info = {}
        
        # Direct price mentions
        price_matches = re.findall(r'(\d+)\s*(lei|mdl|euro|eur|\$)', message_lower)
        if price_matches:
            price = int(price_matches[0][0])
            for range_name, (min_price, max_price) in self.price_ranges.items():
                if min_price <= price <= max_price:
                    price_info["price_range"] = range_name
                    price_info["specific_price"] = str(price)
                    break
        
        # Price range keywords
        price_keywords = {
            "very_budget": ["foarte ieftin", "foarte accesibil", "very cheap", "ultra budget"],
            "budget": ["ieftin", "accesibil", "cheap", "budget", "economic"],
            "medium": ["preț normal", "mediu", "average", "reasonable", "moderat"],
            "premium": ["premium", "calitate", "quality", "superior", "bun"],
            "luxury": ["luxos", "scump", "expensive", "luxury", "exclusiv"],
            "ultra_luxury": ["foarte scump", "ultra luxos", "very expensive", "elite"]
        }
        
        for range_name, keywords in price_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                price_info["price_range"] = range_name
                break
        
        return price_info
    
    def _extract_quantity(self, message_lower: str) -> Optional[str]:
        """Extract quantity from message"""
        # Numbers
        quantity_matches = re.findall(r'(\d+)\s*(?:buc|piese|pieces|bucăți)', message_lower)
        if quantity_matches:
            return quantity_matches[0]
        
        # Written numbers
        quantity_words = {
            "unul": "1", "doi": "2", "trei": "3", "patru": "4", "cinci": "5",
            "șase": "6", "șapte": "7", "opt": "8", "nouă": "9", "zece": "10",
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5"
        }
        
        for word, number in quantity_words.items():
            if word in message_lower:
                return number
        
        return None

class IntentRecognizer:
    """Advanced intent recognition using LLM and patterns"""
    
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        
        # Fallback intent patterns for when LLM is not available
        self.intent_patterns = {
            "find_product": [
                "vreau", "caut", "căutați", "aveți", "recomandă", "găsesc",
                "buchet", "cutie", "flori", "plantă", "cadou", "trandafiri",
                "want", "looking for", "need", "search", "find"
            ],
            "ask_question": [
                "care", "cum", "când", "unde", "cât", "costă", "program",
                "livrare", "livrați", "politica", "returnare", "factura",
                "what", "how", "when", "where", "cost", "delivery", "hours"
            ],
            "subscribe": [
                "abonament", "abonez", "lunar", "săptămânal", "recurring",
                "subscription", "subscribe", "regular", "periodic"
            ],
            "pay_for_product": [
                "plătesc", "plată", "plătire", "accept", "comanda", "finalizez",
                "card", "numerar", "transfer", "payment", "pay", "checkout", "buy"
            ],
            "greeting": [
                "salut", "bună", "hello", "hi", "hey", "bună ziua",
                "bună seara", "bună dimineața", "good morning", "good evening"
            ]
        }
    
    def recognize_intent_with_llm(self, message: str) -> Tuple[str, float]:
        """Use LLM for intent recognition"""
        try:
            system_prompt = """
            You are an intent classifier for XOFlowers, a flower shop. 
            Classify the user message into one of these intents:
            - find_product: user wants to search/buy flowers, bouquets, plants
            - ask_question: user asks about business info, delivery, hours, policies
            - subscribe: user wants subscription or regular deliveries
            - pay_for_product: user wants to pay/finalize an order
            - greeting: user is greeting or saying hello
            - unknown: message doesn't fit any category
            
            Respond with only the intent name and confidence (0-1).
            Format: intent_name,confidence
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Classify this message: '{message}'"}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,  # type: ignore
                temperature=0.1,
                max_tokens=50
            )
            
            content = response.choices[0].message.content
            if content:
                result = content.strip()
                if "," in result:
                    intent_name, confidence_str = result.split(",")
                    confidence = float(confidence_str.strip())
                    return intent_name.strip(), confidence
            
        except Exception as e:
            logger.error(f"Error in LLM intent recognition: {e}")
        
        return "unknown", 0.0
    
    def recognize_intent_fallback(self, message: str) -> Tuple[str, float]:
        """Fallback intent recognition using patterns"""
        message_lower = message.lower()
        intent_scores = {}
        
        for intent_name, keywords in self.intent_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += 1
            
            if score > 0:
                intent_scores[intent_name] = score / len(keywords)
        
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        
        return "unknown", 0.0
    
    def recognize_intent(self, message: str) -> Tuple[Intent, Dict]:
        """Main intent recognition method"""
        # Check for offensive content
        if self.entity_extractor.is_offensive(message):
            return Intent("offensive", 1.0), {}
        
        # Check for jailbreak attempts
        if self.entity_extractor.is_jailbreak_attempt(message):
            return Intent("jailbreak", 1.0), {}
        
        # Try LLM first, fallback to patterns
        intent_name, confidence = self.recognize_intent_with_llm(message)
        
        if confidence < 0.3:  # Low confidence, try fallback
            intent_name, confidence = self.recognize_intent_fallback(message)
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(message)
        
        return Intent(intent_name, confidence), entities

class ChromaDBManager:
    """ChromaDB manager for vector search and product storage"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create collections for different product categories
        self.collections = {
            "bouquets": self.client.get_or_create_collection("bouquets"),
            "boxes": self.client.get_or_create_collection("boxes"),
            "compositions": self.client.get_or_create_collection("compositions"),
            "plants": self.client.get_or_create_collection("plants"),
            "gifts": self.client.get_or_create_collection("gifts")
        }
        
        # Conversation history collection
        self.conversations = self.client.get_or_create_collection("conversations")
        
        logger.info("ChromaDB initialized with collections: " + ", ".join(self.collections.keys()))
    
    def add_product(self, product: Dict, category: str = "bouquets"):
        """Add a product to ChromaDB with enhanced metadata"""
        try:
            if category not in self.collections:
                category = "bouquets"  # Default category
            
            collection = self.collections[category]
            
            # Create rich description for embedding
            description_parts = [
                product['name'],
                product.get('description', ''),
                product.get('flower_type', ''),
                ' '.join(product.get('colors', [])),
                ' '.join(product.get('occasions', []))
            ]
            full_description = ' '.join(filter(None, description_parts))
            
            # Create embedding
            embedding = self.model.encode([full_description])[0].tolist()
            
            # Enhanced metadata
            metadata = {
                "id": product.get('id', str(uuid.uuid4())),
                "name": product['name'],
                "price": float(product.get('price', 0)),
                "category": product.get('category', category),
                "flower_type": product.get('flower_type', ''),
                "colors": json.dumps(product.get('colors', [])),
                "occasions": json.dumps(product.get('occasions', [])),
                "url": product.get('url', ''),
                "in_stock": product.get('in_stock', True)
            }
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[full_description],
                metadatas=[metadata],
                ids=[str(uuid.uuid4())]
            )
            
        except Exception as e:
            logger.error(f"Error adding product to ChromaDB: {e}")
    
    def search_products(self, query: str, filters: Optional[Dict] = None, n_results: int = 5) -> List[Dict]:
        """Enhanced product search using vector similarity and smart filtering"""
        try:
            if filters is None:
                filters = {}
                
            # Create enhanced query embedding
            query_parts = [query]
            
            # Enhance query with filter information for better semantic search
            if filters.get("color"):
                query_parts.append(f"color {filters['color']}")
            if filters.get("occasion"):
                query_parts.append(f"occasion {filters['occasion']}")
            if filters.get("price_range"):
                query_parts.append(f"price range {filters['price_range']}")
                
            enhanced_query = ' '.join(query_parts)
            query_embedding = self.model.encode([enhanced_query])[0].tolist()
            
            all_results = []
            
            # Determine which collections to search
            collections_to_search = list(self.collections.values())
            
            if filters.get("category"):
                category_mapping = {
                    "Chando": ["gifts"],
                    "Peonies": ["bouquets"], 
                    "French roses": ["bouquets"],
                    "Basket": ["boxes"],
                    "Boxes": ["boxes"],
                    "Author": ["bouquets"]
                }
                
                category = filters["category"]
                for key, collections in category_mapping.items():
                    if key.lower() in category.lower():
                        collections_to_search = [self.collections[col] for col in collections if col in self.collections]
                        break
            
            # Search in selected collections
            for collection in collections_to_search:
                try:
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(n_results * 2, 20),  # Get more results for filtering
                        include=['metadatas', 'documents', 'distances']
                    )
                    
                    if search_results.get('metadatas') and search_results.get('metadatas'):
                        metadatas = search_results['metadatas']
                        if metadatas and len(metadatas) > 0 and metadatas[0]:
                            for i, metadata in enumerate(metadatas[0]):
                                distances = search_results.get('distances')
                                if distances and len(distances) > 0 and len(distances[0]) > i:
                                    distance = distances[0][i]
                                else:
                                    distance = 1.0
                                similarity = max(0, 1 - distance)  # Convert distance to similarity
                                
                                # Parse JSON fields safely
                                try:
                                    colors_raw = metadata.get('colors', '[]')
                                    if isinstance(colors_raw, str):
                                        colors = json.loads(colors_raw)
                                    else:
                                        colors = []
                                        
                                    occasions_raw = metadata.get('occasions', '[]')
                                    if isinstance(occasions_raw, str):
                                        occasions = json.loads(occasions_raw)
                                    else:
                                        occasions = []
                                except Exception:
                                    colors = []
                                    occasions = []
                                
                                product = {
                                    'id': str(metadata.get('id', '')),
                                    'name': str(metadata.get('name', '')),
                                    'price': float(metadata.get('price', 0)) if metadata.get('price') else 0.0,
                                    'category': str(metadata.get('category', '')),
                                    'flower_type': str(metadata.get('flower_type', '')),
                                    'colors': colors,
                                    'occasions': occasions,
                                    'url': str(metadata.get('url', '')),
                                    'similarity': similarity,
                                    'in_stock': bool(metadata.get('in_stock', True))
                                }
                                
                                # Apply advanced filters
                                if self._matches_advanced_filters(product, filters):
                                    all_results.append(product)
                
                except Exception as e:
                    logger.error(f"Error searching in collection: {e}")
            
            # Sort by similarity and return top results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def _matches_advanced_filters(self, product: Dict, filters: Dict) -> bool:
        """Advanced filter matching for XOFlowers products"""
        if not filters:
            return True
        
        # Color filter - check if any product color matches filter
        if filters.get("color"):
            filter_color = filters["color"].lower()
            product_colors = [c.lower() for c in product.get("colors", [])]
            if not any(filter_color in color or color in filter_color for color in product_colors):
                return False
        
        # Price range filter with XOFlowers-specific ranges
        if filters.get("price_range"):
            price = product.get("price", 0)
            price_range = filters["price_range"].lower()
            
            if price_range in ["budget", "ieftin", "economic"]:
                if price > 500:
                    return False
            elif price_range in ["medium", "mediu", "mid-range"]:
                if price < 500 or price > 1000:
                    return False
            elif price_range in ["premium", "exclusiv"]:
                if price < 1000 or price > 2500:
                    return False
            elif price_range in ["luxury", "lux", "scump"]:
                if price < 2500:
                    return False
        
        # Occasion filter
        if filters.get("occasion"):
            filter_occasion = filters["occasion"].lower()
            product_occasions = [o.lower() for o in product.get("occasions", [])]
            if not any(filter_occasion in occasion or occasion in filter_occasion for occasion in product_occasions):
                return False
        
        # Category filter
        if filters.get("category"):
            filter_category = filters["category"].lower()
            product_category = product.get("category", "").lower()
            if filter_category not in product_category and product_category not in filter_category:
                return False
        
        # Flower type filter
        if filters.get("flower_type") or filters.get("product_type"):
            filter_type = (filters.get("flower_type") or filters.get("product_type", "")).lower()
            product_type = product.get("flower_type", "").lower()
            if filter_type not in product_type and product_type not in filter_type:
                return False
        
        return True
    
    def save_conversation(self, user_id: str, message: str, intent: str, entities: Dict, response: str):
        """Save conversation to ChromaDB"""
        try:
            conversation_text = f"User: {message} | Intent: {intent} | Response: {response}"
            embedding = self.model.encode([conversation_text])[0].tolist()
            
            self.conversations.add(
                embeddings=[embedding],
                documents=[conversation_text],
                metadatas=[{
                    "user_id": user_id,
                    "message": message,
                    "intent": intent,
                    "entities": json.dumps(entities),
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[str(uuid.uuid4())]
            )
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a user"""
        try:
            results = self.conversations.query(
                query_texts=[f"user_id:{user_id}"],
                n_results=limit,
                include=['metadatas']
            )
            
            if results['metadatas'] and results['metadatas'][0]:
                return [dict(metadata) for metadata in results['metadatas'][0]]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

class XOFlowersAgent:
    """Main agent class for handling Instagram messages"""
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.chroma_manager = ChromaDBManager()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.multilingual_processor = MultilingualProcessor()  # Add multilingual support
        
        # Initialize with real products from CSV
        self._initialize_products_from_csv()
        
        # Business information
        self.business_info = {
            "name": "XOFlowers",
            "website": "https://xoflowers.md",
            "hours": "Luni-Vineri: 9:00-18:00, Sâmbătă: 9:00-17:00, Duminică: închis",
            "delivery": "Livrăm în Chișinău și împrejurimi",
            "delivery_cost": "50 MDL",
            "phone": "+373 22 123 456",
            "address": "Chișinău, strada Florilor 123",
            "payment_methods": "Card, numerar, transfer bancar, PayPal"
        }
    
    def _initialize_products_from_csv(self):
        """Initialize ChromaDB with real products from chunks_data.csv"""
        try:
            import csv
            csv_path = "chunks_data.csv"
            
            if not os.path.exists(csv_path):
                logger.warning(f"CSV file {csv_path} not found. Loading sample products instead.")
                self._load_sample_products()
                return
            
            products_loaded = 0
            category_mapping = {
                "Chando": "gifts",
                "Peonies": "bouquets", 
                "French roses": "bouquets",
                "Basket / Boxes with flowers": "boxes",
                "Author's bouquets": "bouquets"
            }
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row['chunk_type'] == 'product':
                        # Extract product info
                        description = row['primary_text']
                        name = description.split(' - ')[0] if ' - ' in description else description[:100]
                        
                        # Map category to collection
                        original_category = row['category']
                        collection_name = category_mapping.get(original_category, "bouquets")
                        
                        # Extract colors from description
                        colors = self._extract_colors_from_text(description)
                        
                        # Extract occasions from description  
                        occasions = self._extract_occasions_from_text(description)
                        
                        product = {
                            "id": row['chunk_id'],
                            "name": name,
                            "description": description,
                            "price": float(row['price']) if row['price'] else 0.0,
                            "category": original_category,
                            "flower_type": row['flower_type'],
                            "colors": colors,
                            "occasions": occasions,
                            "url": row['url'],
                            "in_stock": True
                        }
                        
                        self.chroma_manager.add_product(product, collection_name)
                        products_loaded += 1
            
            logger.info(f"Loaded {products_loaded} real products from CSV into ChromaDB")
            
        except Exception as e:
            logger.error(f"Error loading products from CSV: {e}")
            self._load_sample_products()
    
    def _extract_colors_from_text(self, text: str) -> List[str]:
        """Extract color information from product description"""
        colors = []
        color_keywords = {
            "roșu": ["roșu", "red", "scarlet", "crimson"],
            "alb": ["alb", "white", "ivory", "cream"],
            "roz": ["roz", "pink", "rose"],
            "galben": ["galben", "yellow", "golden"],
            "violet": ["violet", "purple", "lilac", "lavender"],
            "coral": ["coral", "peach", "salmon"],
            "pastel": ["pastel", "soft", "delicate"],
            "multicolor": ["mix", "mixed", "multicolor", "various"]
        }
        
        text_lower = text.lower()
        for color, keywords in color_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                colors.append(color)
        
        return colors if colors else ["mixed"]
    
    def _extract_occasions_from_text(self, text: str) -> List[str]:
        """Extract occasion information from product description"""
        occasions = []
        occasion_keywords = {
            "romantic": ["romantic", "love", "valentine", "kiss"],
            "birthday": ["birthday", "celebration", "party"],
            "wedding": ["wedding", "bridal", "bride"],
            "anniversary": ["anniversary", "special"],
            "graduation": ["graduation", "achievement"],
            "sympathy": ["sympathy", "funeral", "memorial"],
            "thank_you": ["thank", "gratitude", "appreciation"],
            "luxury": ["luxury", "premium", "exclusive", "elegant"]
        }
        
        text_lower = text.lower()
        for occasion, keywords in occasion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                occasions.append(occasion)
        
        return occasions if occasions else ["general"]
    
    def _load_sample_products(self):
        """Fallback: load sample products if CSV is not available"""
        sample_products = [
            {
                "id": "sample_1",
                "name": "Buchet Trandafiri Premium",
                "description": "Buchet elegant cu trandafiri proaspeți în culori vibrante",
                "price": 450,
                "category": "Buchete Premium",
                "flower_type": "Trandafiri",
                "colors": ["roșu", "roz"],
                "occasions": ["romantic", "anniversary"],
                "url": "https://xoflowers.md/sample-bouquet"
            }
        ]
        
        for product in sample_products:
            self.chroma_manager.add_product(product, "bouquets")
    
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
            
            # Fallback to original processing if ULTRA is not available
            # Recognize intent and extract entities
            intent, entities = self.intent_recognizer.recognize_intent(message)
            
            # Handle special cases first
            if intent.name == "offensive":
                response = "Ne pare rău, dar nu putem tolera limbajul ofensator. Vă rugăm să comunicați respectuos. 🌸"
            
            elif intent.name == "jailbreak":
                response = "Sunt aici pentru a vă ajuta doar cu XOFlowers. Cum vă pot asista cu florile noastre? 🌺"
            
            else:
                # Generate response based on intent
                response = self._generate_response(intent, entities, message, user_id)
            
            # Save conversation to ChromaDB
            self.chroma_manager.save_conversation(user_id, message, intent.name, entities, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Ne pare rău, a apărut o eroare tehnică. Vă rugăm să ne contactați la +373 22 123 456. 🌸"
    
    def _generate_response(self, intent: Intent, entities: Dict, message: str, user_id: str) -> str:
        """Generate response based on intent and entities"""
        
        if intent.name == "find_product":
            return self._handle_find_product(message, entities)
        
        elif intent.name == "ask_question":
            return self._handle_ask_question(message)
        
        elif intent.name == "subscribe":
            return self._handle_subscribe(entities)
        
        elif intent.name == "pay_for_product":
            return self._handle_payment(entities)
        
        elif intent.name == "greeting":
            return "Bună! Bine ați venit la XOFlowers! 🌸 Suntem aici să vă ajutăm cu cele mai frumoase flori. Cum vă pot asista astăzi?"
        
        else:
            # Fallback response
            return self._get_fallback_response()
    
    def _handle_find_product(self, message: str, entities: Dict[str, str]) -> str:
        """Enhanced product search with multilingual support and better UX"""
        try:
            # Enhanced multilingual query processing
            enhanced_query = self.multilingual_processor.enhance_query_multilingual(message)
            detected_language = self.multilingual_processor.detect_language(message)
            
            # Build comprehensive filters from entities
            filters = {}
            
            # Color filtering with fuzzy matching
            if entities.get("color"):
                color = entities["color"].lower()
                # Map to standardized colors
                color_mappings = self.multilingual_processor.language_mappings["ro"]["colors"]
                for standard_color, synonyms in color_mappings.items():
                    if any(self.multilingual_processor.fuzzy_match(color, syn) > 0.7 for syn in synonyms):
                        filters["color"] = standard_color
                        break
                if "color" not in filters:
                    filters["color"] = color
            
            # Occasion filtering
            if entities.get("occasion"):
                occasion = entities["occasion"].lower()
                # Map to standardized occasions
                occasion_mappings = self.multilingual_processor.language_mappings["ro"]["occasions"]
                for standard_occasion, synonyms in occasion_mappings.items():
                    if any(self.multilingual_processor.fuzzy_match(occasion, syn) > 0.7 for syn in synonyms):
                        filters["occasion"] = standard_occasion
                        break
                if "occasion" not in filters:
                    filters["occasion"] = occasion
            
            # Price range filtering
            if entities.get("price_range"):
                filters["price_range"] = entities["price_range"]
            
            # Category/product type filtering
            if entities.get("product_type"):
                product_type = entities["product_type"].lower()
                if "trandaf" in product_type or "rose" in product_type:
                    filters["category"] = "French roses"
                elif "bujor" in product_type or "peony" in product_type:
                    filters["category"] = "Peonies"
                elif "cutie" in product_type or "box" in product_type:
                    filters["category"] = "Basket / Boxes with flowers"
                elif "difuzor" in product_type:
                    filters["category"] = "Chando"
                else:
                    filters["product_type"] = product_type
            
            # Perform enhanced search
            products = self.chroma_manager.search_products(enhanced_query, filters, 8)
            
            if not products:
                # Fallback search with broader terms
                fallback_query = message
                if detected_language == "ro":
                    fallback_terms = ["flori", "buchete", "cadouri", "trandafiri"]
                else:
                    fallback_terms = ["flowers", "bouquet", "gifts", "roses"]
                
                for term in fallback_terms:
                    if term.lower() in message.lower():
                        products = self.chroma_manager.search_products(term, {}, 5)
                        if products:
                            break
            
            if products:
                # Generate intelligent response based on language
                if detected_language == "ro":
                    response = self._generate_romanian_response(products, entities, message)
                elif detected_language == "en":
                    response = self._generate_english_response(products, entities, message)
                else:
                    response = self._generate_romanian_response(products, entities, message)  # Default to Romanian
                
                return response
            else:
                return self._generate_no_results_response(detected_language, entities)
            
        except Exception as e:
            logger.error(f"Error in enhanced product search: {e}")
            detected_language = self.multilingual_processor.detect_language(message)
            if detected_language == "en":
                return "🌸 Something went wrong with the search. Please visit https://xoflowers.md or contact us at +373 22 123 456."
            else:
                return "🌸 A apărut o problemă la căutare. Vă rugăm să vizitați https://xoflowers.md sau să ne contactați la +373 22 123 456."
    
    def _generate_romanian_response(self, products: List[Dict], entities: Dict[str, str], original_query: str) -> str:
        """Generate Romanian response for found products"""
        response = f"🌸 **Am găsit {len(products)} produse pentru dumneavoastră:**\n\n"
        
        # Add context about search
        if entities.get("color"):
            response += f"🎨 Căutare pentru culoarea: {entities['color']}\n"
        if entities.get("occasion"):
            response += f"🎉 Pentru ocazia: {entities['occasion']}\n"
        if entities.get("price_range"):
            response += f"💰 Categoria de preț: {entities['price_range']}\n"
        
        response += "\n"
        
        for i, product in enumerate(products[:5], 1):
            price_display = f"{product['price']:.0f} MDL" if product['price'] else "Preț la cerere"
            
            response += f"**{i}. {product['name']}**\n"
            response += f"💰 {price_display}"
            
            if product.get('colors'):
                colors_str = ", ".join(product['colors'][:3])
                response += f" | 🎨 {colors_str}"
            
            if product.get('occasions'):
                occasions_str = ", ".join(product['occasions'][:2])
                response += f" | 🎉 {occasions_str}"
            
            response += f"\n🔗 [Vezi detalii]({product['url']})\n\n"
        
        # Add smart suggestions
        response += "💡 **Recomandări:**\n"
        
        # Price-based suggestions
        avg_price = sum(p['price'] for p in products if p['price']) / len([p for p in products if p['price']])
        if avg_price > 1500:
            response += "• Acestea sunt produse premium - perfecte pentru ocazii speciale\n"
        elif avg_price < 500:
            response += "• Opțiuni accesibile și frumoase pentru orice buget\n"
        
        # Category suggestions
        categories = [p['category'] for p in products]
        if "Chando" in categories:
            response += "• Difuzoarele aromă sunt cadouri ideale care durează\n"
        if "Peonies" in categories:
            response += "• Bujori sunt florile perfecte pentru primăvară\n"
        
        response += "\n📞 **Contact:** +373 22 123 456\n"
        response += "🚚 **Livrare gratuită** în Chișinău pentru comenzi peste 500 MDL"
        
        return response
    
    def _generate_english_response(self, products: List[Dict], entities: Dict[str, str], original_query: str) -> str:
        """Generate English response for found products"""
        response = f"🌸 **Found {len(products)} products for you:**\n\n"
        
        # Add search context
        if entities.get("color"):
            response += f"🎨 Searching for color: {entities['color']}\n"
        if entities.get("occasion"):
            response += f"🎉 For occasion: {entities['occasion']}\n"
        if entities.get("price_range"):
            response += f"💰 Price range: {entities['price_range']}\n"
        
        response += "\n"
        
        for i, product in enumerate(products[:5], 1):
            price_display = f"{product['price']:.0f} MDL" if product['price'] else "Price on request"
            
            response += f"**{i}. {product['name']}**\n"
            response += f"💰 {price_display}"
            
            if product.get('colors'):
                colors_str = ", ".join(product['colors'][:3])
                response += f" | 🎨 {colors_str}"
            
            if product.get('occasions'):
                occasions_str = ", ".join(product['occasions'][:2])
                response += f" | 🎉 {occasions_str}"
            
            response += f"\n🔗 [View details]({product['url']})\n\n"
        
        # Add suggestions
        response += "💡 **Recommendations:**\n"
        
        avg_price = sum(p['price'] for p in products if p['price']) / len([p for p in products if p['price']])
        if avg_price > 1500:
            response += "• These are premium products - perfect for special occasions\n"
        elif avg_price < 500:
            response += "• Affordable and beautiful options for any budget\n"
        
        response += "\n📞 **Contact:** +373 22 123 456\n"
        response += "🚚 **Free delivery** in Chișinău for orders over 500 MDL"
        
        return response
    
    def _generate_no_results_response(self, language: str, entities: Dict[str, str]) -> str:
        """Generate no results response in appropriate language"""
        if language == "en":
            response = "🌸 **Sorry, no exact matches found.**\n\n"
            response += "💡 **Search suggestions:**\n"
            response += "• Try broader terms (e.g., 'bouquets', 'roses')\n"
            response += "• Specify desired color (red, white, pink)\n"
            response += "• Mention the occasion (birthday, wedding, etc.)\n\n"
            response += "🌺 **Our popular categories:**\n"
            response += "• French rose bouquets\n"
            response += "• Elegant flower boxes\n"
            response += "• Seasonal peonies\n"
            response += "• Chando aroma diffusers\n"
            response += "• Author's arrangements\n\n"
            response += "📞 Or contact us directly: +373 22 123 456"
        else:
            response = "🌸 **Ne pare rău, nu am găsit rezultate exacte.**\n\n"
            response += "💡 **Sugestii pentru căutare:**\n"
            response += "• Încercați termeni mai generali (ex: 'buchete', 'trandafiri')\n"
            response += "• Specificați culoarea dorită (roșu, alb, roz)\n"
            response += "• Menționați ocazia (ziua de naștere, nuntă, etc.)\n\n"
            response += "🌺 **Categoriile noastre populare:**\n"
            response += "• Buchete cu trandafiri francezi\n"
            response += "• Cutii elegante cu flori\n"
            response += "• Bujori de sezon\n"
            response += "• Difuzoare aromă Chando\n"
            response += "• Aranjamente de autor\n\n"
            response += "📞 Sau ne contactați direct: +373 22 123 456"
        
        return response
    
    def _handle_ask_question(self, message: str) -> str:
        """Handle general questions using OpenAI with business context"""
        try:
            detected_language = self.multilingual_processor.detect_language(message)
            
            if detected_language == "en":
                system_prompt = f"""
                You are an AI assistant for XOFlowers, a flower shop in Chisinau, Moldova.
                
                Business information:
                - Name: {self.business_info['name']}
                - Website: {self.business_info['website']}
                - Hours: {self.business_info['hours']}
                - Delivery: {self.business_info['delivery']}
                - Delivery cost: {self.business_info['delivery_cost']}
                - Phone: {self.business_info['phone']}
                - Address: {self.business_info['address']}
                - Payment methods: {self.business_info['payment_methods']}
                
                Available products: bouquets, flower boxes, plants, floral arrangements, gifts.
                
                Respond in English, professional but friendly. Use flower emojis.
                If you don't know the exact answer, provide contact information.
                """
            else:
                system_prompt = f"""
                Ești un asistent AI pentru XOFlowers, un magazin de flori din Chișinău, Moldova.
                
                Informații despre afacere:
                - Nume: {self.business_info['name']}
                - Website: {self.business_info['website']}
                - Program: {self.business_info['hours']}
                - Livrare: {self.business_info['delivery']}
                - Cost livrare: {self.business_info['delivery_cost']}
                - Telefon: {self.business_info['phone']}
                - Adresa: {self.business_info['address']}
                - Metode de plată: {self.business_info['payment_methods']}
                
                Produse disponibile: buchete, cutii cu flori, plante, aranjamente florale, cadouri.
                
                Răspunde în română, profesional dar prietenos. Folosește emoji-uri cu flori.
                Dacă nu știi răspunsul exact, oferă informațiile de contact.
                """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,  # type: ignore
                temperature=0.3,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            if content:
                return content.strip()
            else:
                return self._get_fallback_response()
                
        except Exception as e:
            logger.error(f"Error in ask question handler: {e}")
            return self._get_fallback_response()
    
    def _handle_subscribe(self, entities: Dict[str, str]) -> str:
        """Handle subscription requests"""
        detected_language = self.multilingual_processor.detect_language(" ".join(entities.values()))
        
        if detected_language == "en":
            response = "🌸 **Flower Subscription Service**\n\n"
            response += "We offer regular flower deliveries:\n"
            response += "• Weekly: Fresh bouquets every week\n"
            response += "• Monthly: Special arrangements monthly\n"
            response += "• Seasonal: Seasonal flower selections\n\n"
            response += "📞 **To subscribe, contact us:**\n"
            response += f"📱 Phone: {self.business_info['phone']}\n"
            response += f"🌐 Website: {self.business_info['website']}\n\n"
            response += "💡 We'll create a personalized plan based on your preferences!"
        else:
            response = "🌸 **Serviciu de Abonament Flori**\n\n"
            response += "Oferim livrări regulate de flori:\n"
            response += "• Săptămânal: Buchete proaspete în fiecare săptămână\n"
            response += "• Lunar: Aranjamente speciale lunare\n"
            response += "• Sezonier: Selecții florale de sezon\n\n"
            response += "📞 **Pentru abonament, contactați-ne:**\n"
            response += f"📱 Telefon: {self.business_info['phone']}\n"
            response += f"🌐 Website: {self.business_info['website']}\n\n"
            response += "💡 Vom crea un plan personalizat în funcție de preferințele dumneavoastră!"
        
        return response
    
    def _handle_payment(self, entities: Dict[str, str]) -> str:
        """Handle payment-related queries"""
        detected_language = self.multilingual_processor.detect_language(" ".join(entities.values()))
        
        if detected_language == "en":
            response = "💳 **Payment Options**\n\n"
            response += f"We accept: {self.business_info['payment_methods']}\n\n"
            response += "🚚 **Delivery & Payment:**\n"
            response += "• Cash on delivery available\n"
            response += "• Card payment at delivery\n"
            response += "• Online payment on website\n"
            response += f"• Delivery cost: {self.business_info['delivery_cost']}\n\n"
            response += "📞 **To finalize your order:**\n"
            response += f"📱 Call: {self.business_info['phone']}\n"
            response += f"🌐 Visit: {self.business_info['website']}"
        else:
            response = "💳 **Opțiuni de Plată**\n\n"
            response += f"Acceptăm: {self.business_info['payment_methods']}\n\n"
            response += "🚚 **Livrare & Plată:**\n"
            response += "• Plata ramburs disponibilă\n"
            response += "• Plata cu cardul la livrare\n"
            response += "• Plata online pe website\n"
            response += f"• Cost livrare: {self.business_info['delivery_cost']}\n\n"
            response += "📞 **Pentru finalizarea comenzii:**\n"
            response += f"📱 Sunați: {self.business_info['phone']}\n"
            response += f"🌐 Vizitați: {self.business_info['website']}"
        
        return response
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when other methods fail"""
        return f"""🌸 **XOFlowers - Florăria voastră din Chișinău**

📞 **Contact:** {self.business_info['phone']}
🌐 **Website:** {self.business_info['website']}
📍 **Adresa:** {self.business_info['address']}
⏰ **Program:** {self.business_info['hours']}

🌺 **Servicii:**
• Buchete și aranjamente florale
• Cutii elegante cu flori
• Difuzoare aromă Chando
• Livrare în Chișinău
• Aranjamente pentru evenimente

💐 Vă așteptăm cu drag!"""

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
        "collections": list(agent.chroma_manager.collections.keys()) if agent else [],
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
        
        # Execute personalized search
        recommendations = ai_agent.get_personalized_recommendations(
            user_id=user_id,
            preferences={
                'category': category,
                'price_range': price_range
            }
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
                'confidence': round(rec.confidence, 3),
                'reason': rec.recommendation_reason
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
            
        max_results = request.args.get('max_results', 3, type=int)
        
        recommendations = ai_agent.get_personalized_recommendations(
            user_id=user_id,
            max_results=max_results
        )
        
        results = []
        for rec in recommendations:
            results.append({
                'id': rec.id,
                'title': rec.title,
                'description': rec.description[:150] + '...',
                'price': rec.price,
                'price_tier': rec.price_tier,
                'confidence': round(rec.confidence, 2),
                'category': rec.category,
                'flower_type': rec.flower_type
            })
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'personalized_recommendations': results,
            'ultra_mode': True,
            'recommendation_basis': 'user_preferences' if user_id in ai_agent.user_preferences else 'popular_items'
        })
        
    except Exception as e:
        logger.error(f"Personalized recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/performance-stats", methods=["GET"])
def get_performance_stats():
    """Statistici de performanță pentru AI Agent"""
    try:
        if not ULTRA_MODE or not ai_agent:
            return jsonify({'error': 'AI Agent ULTRA not available'}), 500
            
        stats = ai_agent.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'ultra_mode': True,
            'database_stats': {
                'total_products': stats['database_size'],
                'total_queries': stats['total_queries'],
                'avg_query_time': f"{stats['avg_query_time']:.3f}s",
                'cache_hit_rate': f"{stats['cache_hit_rate']:.1f}%",
                'cache_size': stats['cache_size']
            },
            'ai_stats': stats['ai_agent_stats'],
            'system_health': 'excellent' if stats['avg_query_time'] < 0.3 else 'good' if stats['avg_query_time'] < 0.6 else 'needs_optimization',
            'uptime': 'active'
        })
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/test-ultra", methods=["GET"])
def test_ultra():
    """Test rapid pentru AI Agent ULTRA"""
    try:
        if not ULTRA_MODE or not ai_agent:
            return jsonify({'status': 'error', 'message': 'AI Agent ULTRA not initialized'}), 500
        
        # Test queries
        test_queries = [
            "trandafiri roșii",
            "buchet pentru nuntă", 
            "ceva ieftin și frumos"
        ]
        
        results = {}
        total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            recommendations = ai_agent.intelligent_search(query, max_results=2)
            query_time = time.time() - start_time
            total_time += query_time
            
            results[query] = {
                'results_count': len(recommendations),
                'query_time': f"{query_time:.3f}s",
                'best_match': recommendations[0].title if recommendations else 'No results',
                'confidence': f"{recommendations[0].confidence:.2f}" if recommendations else 0
            }
        
        stats = ai_agent.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'ultra_agent_status': 'active',
            'test_results': results,
            'avg_test_time': f"{total_time / len(test_queries):.3f}s",
            'database_size': stats['database_size'],
            'system_health': 'excellent'
        })
        
    except Exception as e:
        logger.error(f"AI Agent ULTRA test error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get("message")
        user_id = data.get("user_id", "web_user")
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process message with agent
        response = agent.process_message(user_id, user_message)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Verify webhook for Instagram"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    verify_token = os.getenv("INSTAGRAM_VERIFY_TOKEN", "xoflowers_verify_token")
    
    if mode and token:
        if mode == 'subscribe' and token == verify_token:
            return challenge
        else:
            return jsonify({"error": "Verification failed"}), 403
    
    return jsonify({"error": "Invalid request"}), 400

@app.route("/webhook", methods=["POST"])
def process_webhook():
    """Process Instagram webhook messages"""
    try:
        data = request.json
        
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                for messaging in entry.get('messaging', []):
                    sender_id = messaging.get('sender', {}).get('id')
                    message_text = messaging.get('message', {}).get('text')
                    
                    if sender_id and message_text:
                        # Process message
                        response = agent.process_message(sender_id, message_text)
                        
                        # Send response back to Instagram (API implementation)
                        send_instagram_message(sender_id, response)
                        
                        logger.info(f"Processed message from {sender_id}: {message_text}")
                        logger.info(f"Response: {response}")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

def send_instagram_message(recipient_id: str, message_text: str):
    """Send message via Instagram Graph API"""
    try:
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        page_id = os.getenv("INSTAGRAM_PAGE_ID")
        
        if not access_token or not page_id:
            logger.warning("Instagram API credentials not configured")
            return
        
        url = f"https://graph.facebook.com/v18.0/{page_id}/messages"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": access_token
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            logger.info(f"Message sent successfully to {recipient_id}")
        else:
            logger.error(f"Failed to send message: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Instagram message: {e}")

@app.route("/api/products/search", methods=["POST"])
def search_products():
    """Search products using ChromaDB vector search"""
    try:
        data = request.json
        query = data.get("query", "")
        filters = data.get("filters", {})
        n_results = data.get("n_results", 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        products = agent.chroma_manager.search_products(query, filters, n_results)
        
        return jsonify({
            "products": products,
            "query": query,
            "filters": filters,
            "count": len(products)
        })
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/products/add", methods=["POST"])
def add_product():
    """Add new product to ChromaDB"""
    try:
        data = request.json
        
        required_fields = ["name", "price", "category"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add product to ChromaDB
        agent.chroma_manager.add_product(data, data["category"])
        
        return jsonify({
            "message": "Product added successfully",
            "product": data
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/conversations/<user_id>", methods=["GET"])
def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    try:
        limit = request.args.get("limit", 10, type=int)
        
        conversations = agent.chroma_manager.get_conversation_history(user_id, limit)
        
        return jsonify({
            "user_id": user_id,
            "conversations": conversations,
            "count": len(conversations)
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get analytics from ChromaDB conversations"""
    try:
        # Get recent conversations
        conversations = agent.chroma_manager.conversations.get(
            include=['metadatas']
        )
        
        analytics = {
            "total_conversations": 0,
            "intent_distribution": {},
            "top_users": {},
            "recent_activity": []
        }
        
        if conversations and conversations.get('metadatas') and conversations['metadatas']:
            analytics["total_conversations"] = len(conversations['metadatas'])
            
            # Analyze intents and users
            for metadata in conversations['metadatas']:
                intent = metadata.get('intent', 'unknown')
                analytics["intent_distribution"][intent] = analytics["intent_distribution"].get(intent, 0) + 1
                
                # Analyze users
                user_id = metadata.get('user_id', 'unknown')
                analytics["top_users"][user_id] = analytics["top_users"].get(user_id, 0) + 1
        
        return jsonify({
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/test", methods=["POST"])
def test_intent():
    """Test intent recognition"""
    try:
        data = request.json
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        intent, entities = agent.intent_recognizer.recognize_intent(message)
        
        return jsonify({
            "message": message,
            "intent": {
                "name": intent.name,
                "confidence": intent.confidence
            },
            "entities": entities,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error testing intent: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/collections", methods=["GET"])
def get_collections_info():
    """Get information about ChromaDB collections"""
    try:
        collections_info = {}
        
        for name, collection in agent.chroma_manager.collections.items():
            try:
                count = collection.count()
                collections_info[name] = {
                    "name": name,
                    "count": count,
                    "status": "active"
                }
            except Exception as e:
                collections_info[name] = {
                    "name": name,
                    "count": 0,
                    "status": f"error: {str(e)}"
                }
        
        return jsonify({
            "collections": collections_info,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting collections info: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/scrape_products", methods=["POST"])
def scrape_xoflowers():
    """Endpoint to trigger product scraping from xoflowers.md"""
    try:
        # This would be implemented to scrape actual products from the website
        # For now, we'll return a placeholder response
        
        return jsonify({
            "message": "Product scraping endpoint - implementation needed",
            "note": "This endpoint would scrape products from https://xoflowers.md and add them to ChromaDB",
            "status": "placeholder"
        })
        
    except Exception as e:
        logger.error(f"Error in scraping endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Ensure ChromaDB directory exists
    os.makedirs("./chroma_db", exist_ok=True)
    
    # Start the Flask app
    app.run(debug=True, port=5000, host='0.0.0.0')