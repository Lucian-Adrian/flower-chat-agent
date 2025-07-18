"""
AI Processing Engine for XOFlowers
Main AI processing coordinator with fallback chain and comprehensive logging using NEW Gemini API
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from functools import lru_cache
import hashlib

from openai import OpenAI
# Use the NEW Gemini API as specified in the AI guide
from google import genai
from google.genai import types

from src.utils.system_definitions import get_service_config, get_ai_prompts
from src.utils.utils import (
    setup_logger, log_ai_interaction, log_fallback_activation, log_performance_metrics,
    log_ai_interaction_with_monitoring, log_error_with_monitoring, log_cache_operation,
    PerformanceTimer, get_performance_monitor
)
from .security_ai import check_message_security, generate_security_response
from .context_manager import get_context_for_ai, add_conversation_message
from .response_generator import generate_natural_response
from .gemini_chat_manager import (
    get_enhanced_context_for_ai, 
    send_message_with_enhanced_context,
    get_gemini_chat_manager
)


@dataclass
class AIResponse:
    """AI response data structure for enhanced processing"""
    response_text: str
    success: bool
    service_used: str
    intent: str = "general"
    confidence: float = 0.8
    products_included: list = None
    context_updated: bool = False
    processing_time: float = 0.0
    products_found: int = 0
    needs_product_search: bool = False
    products: list = None
    
    def __post_init__(self):
        if self.products_included is None:
            self.products_included = []
        if self.products is None:
            self.products = []


class AIEngine:
    """Main AI processing coordinator with fallback chain and performance optimizations"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.ai_prompts = get_ai_prompts()
        
        # Performance optimization: Response caching
        self._response_cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
        # Performance optimization: Connection pooling for AI services
        self._openai_semaphore = asyncio.Semaphore(10)  # Limit concurrent OpenAI calls
        self._gemini_semaphore = asyncio.Semaphore(10)  # Limit concurrent Gemini calls
        
        # Chat history management for conversation context
        self.user_chats: Dict[str, Any] = {}  # Store chat objects per user
        self.chat_max_age = 3600  # 1 hour chat timeout
        self.chat_cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = time.time()
        
        # Initialize AI services
        self._setup_openai()
        self._setup_gemini()
        
        self.logger.info("AI Engine initialized with OpenAI and Gemini support, caching enabled")
    
    def _setup_openai(self) -> None:
        """Initialize OpenAI client"""
        try:
            openai_config = self.service_config['openai']
            if openai_config['api_key']:
                self.openai_client = OpenAI(api_key=openai_config['api_key'])
                self.openai_available = True
                self.logger.info("OpenAI client initialized successfully")
            else:
                self.openai_client = None
                self.openai_available = False
                self.logger.warning("OpenAI API key not found, OpenAI unavailable")
        except Exception as e:
            self.openai_client = None
            self.openai_available = False
            self.logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _setup_gemini(self) -> None:
        """Initialize Gemini client using NEW Gemini API as specified in AI guide"""
        try:
            gemini_config = self.service_config['gemini']
            
            # Try primary key first using NEW API
            if gemini_config['api_key']:
                try:
                    self.gemini_client = genai.Client(api_key=gemini_config['api_key'])
                    self.gemini_model = gemini_config['model']  # Store model name
                    self.gemini_available = True
                    self.gemini_current_key = 'primary'
                    self.logger.info("[OK] Gemini client initialized with primary key (NEW API)")
                    return
                except Exception as e:
                    self.logger.warning(f"Primary Gemini key failed: {e}")
            
            # Try backup key if primary fails using NEW API
            if gemini_config['api_key_backup']:
                try:
                    self.gemini_client = genai.Client(api_key=gemini_config['api_key_backup'])
                    self.gemini_model = gemini_config['model']  # Store model name
                    self.gemini_available = True
                    self.gemini_current_key = 'backup'
                    self.logger.info("[OK] Gemini client initialized with backup key (NEW API)")
                    return
                except Exception as e:
                    self.logger.warning(f"Backup Gemini key failed: {e}")
            
            # No working keys
            self.gemini_available = False
            self.gemini_current_key = None
            self.gemini_model = None
            self.logger.error("No working Gemini API keys found")
            
        except Exception as e:
            self.gemini_available = False
            self.gemini_model = None
            self.logger.error(f"Failed to setup Gemini: {e}")
    
    def _get_or_create_chat(self, user_id: str) -> Optional[Any]:
        """Get or create a Gemini chat session for user with conversation history"""
        if not self.gemini_available:
            return None
        
        # Clean up old chats periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.chat_cleanup_interval:
            self._cleanup_old_chats()
            self.last_cleanup = current_time
        
        # Check if user has existing chat
        if user_id in self.user_chats:
            chat_info = self.user_chats[user_id]
            # Check if chat is not too old
            if current_time - chat_info['created_at'] < self.chat_max_age:
                chat_info['last_used'] = current_time
                return chat_info['chat']
            else:
                # Chat expired, remove it
                del self.user_chats[user_id]
        
        # Create new chat session
        try:
            from google import genai
            
            # System instruction for the consultant role
            system_instruction = """Tu ești consultantul floral expert al florăriei XOFlowers din Chișinău, Moldova. 
Ești prietenos, profesional și cunoscător în domeniul floristicii.

PERSONALITATEA TA:
- Vorbești natural în română, ca un consultant cu experiență
- Ești empatic și înțelegi nevoile emoționale ale clienților
- Oferi sfaturi personalizate bazate pe ocasie și buget
- Ții minte conversația anterioară cu clientul
- Ești proactiv în a oferi alternative și sugestii

OBIECTIVUL TĂU:
- Să ajuți clienții să găsească florile perfecte pentru nevoile lor
- Să oferi o experiență personalizată și memorabilă
- Să menții o conversație naturală și caldă

IMPORTANT: Ține minte tot ce discutați în conversație - numele, ocasiile, preferințele, bugetul."""
            
            chat = self.gemini_client.chats.create(
                model=self.gemini_model,
                config={
                    'system_instruction': system_instruction,
                    'temperature': 0.7
                }
            )
            
            # Store chat info
            self.user_chats[user_id] = {
                'chat': chat,
                'created_at': current_time,
                'last_used': current_time,
                'message_count': 0
            }
            
            self.logger.info(f"Created new Gemini chat session for user {user_id}")
            return chat
            
        except Exception as e:
            self.logger.error(f"Failed to create chat for user {user_id}: {e}")
            return None
    
    def _cleanup_old_chats(self):
        """Remove old chat sessions to prevent memory leaks"""
        current_time = time.time()
        expired_users = []
        
        for user_id, chat_info in self.user_chats.items():
            if current_time - chat_info['last_used'] > self.chat_max_age:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.user_chats[user_id]
            self.logger.debug(f"Cleaned up expired chat for user {user_id}")
        
        if expired_users:
            self.logger.info(f"Cleaned up {len(expired_users)} expired chat sessions")
    
    async def process_message_ai(self, user_message: str, user_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main AI processing pipeline entry point with enhanced Gemini chat integration
        
        Args:
            user_message: User's message text
            user_id: Unique user identifier
            context: Conversation context (optional, will use enhanced context if not provided)
        
        Returns:
            Dict with response, success status, and metadata
        """
        start_time = time.time()
        request_id = f"{user_id}_{int(start_time)}"
        
        self.logger.info(f"[{request_id}] Starting enhanced AI processing for user {user_id}")
        
        try:
            # Step 0: Get enhanced conversation context (Gemini chat + Redis fallback)
            if context is None:
                context = await get_enhanced_context_for_ai(user_id)
                context_type = context.get('conversation_type', 'none')
                self.logger.debug(f"[{request_id}] Retrieved {context_type} context: {len(context.get('recent_messages', []))} recent messages")
            
            # Step 1: Security check using AI-powered security system
            security_result = await check_message_security(user_message, user_id)
            
            if not security_result.is_safe:
                # Message failed security check, return safe response
                processing_time = time.time() - start_time
                safe_response = generate_security_response(security_result.detected_issues, security_result.risk_level)
                
                # Don't save security-blocked messages to context
                return {
                    "response": safe_response,
                    "success": True,  # Successfully handled security issue
                    "context_updated": False,
                    "security_blocked": True,
                    "risk_level": security_result.risk_level,
                    "detected_issues": security_result.detected_issues,
                    "processing_time": processing_time,
                    "service_used": security_result.service_used,
                    "request_id": request_id
                }
            
            # Step 2: Use ENHANCED Gemini Chat with intelligent ChromaDB integration
            self.logger.info(f"[{request_id}] Using enhanced Gemini Chat + ChromaDB integration")
            
            # Enhanced processing that combines Gemini intelligence with product search
            response_result = await self._enhanced_gemini_with_products(
                user_message, context, user_id, request_id
            )
            
            processing_time = time.time() - start_time
            
            # Save conversation to context if response was successful
            context_updated = False
            if response_result.success:
                context_updated = await add_conversation_message(
                    user_id, 
                    user_message, 
                    response_result.response_text,
                    response_result.intent,
                    response_result.confidence
                )
                
                if context_updated:
                    self.logger.debug(f"[{request_id}] Context updated successfully")
                else:
                    self.logger.warning(f"[{request_id}] Failed to update context")
            
            # Log the interaction with enhanced monitoring
            log_ai_interaction_with_monitoring(
                self.logger,
                user_id,
                user_message,
                response_result.response_text,
                processing_time,
                response_result.intent,
                response_result.confidence,
                response_result.service_used
            )
            
            return {
                "response": response_result.response_text,
                "success": response_result.success,
                "context_updated": context_updated,
                "intent": response_result.intent,
                "confidence": response_result.confidence,
                "products_found": getattr(response_result, 'products_found', 0),
                "products": getattr(response_result, 'products', []),  # Add products to return
                "processing_time": processing_time,
                "service_used": response_result.service_used,
                "request_id": request_id
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"[{request_id}] AI processing failed: {e}")
            
            # NO FALLBACK - System must work with proper AI services
            raise Exception(f"AI processing failed - system requires functional AI services: {e}")
    
    async def _analyze_intent(self, message: str, context: Dict) -> Dict[str, Any]:
        """
        Analyze user intent using AI
        
        Args:
            message: User message
            context: Conversation context
        
        Returns:
            Intent analysis results
        """
        prompt = self.ai_prompts['intent_analysis_prompt'].format(
            message=message,
            context=json.dumps(context, ensure_ascii=False)
        )
        
        try:
            # Try Gemini first (primary AI service)
            if self.gemini_available:
                result = await self._call_gemini_for_intent(prompt)
                if result:
                    return result
            
            # Try OpenAI as backup
            if self.openai_available:
                result = await self._call_openai_for_intent(prompt)
                if result:
                    return result
            
            # NO FALLBACK - AI services MUST work
            raise Exception("All AI services failed for intent analysis - system requires functional AI services")
            
        except Exception as e:
            self.logger.error(f"Intent analysis failed: {e}")
            raise Exception(f"AI intent analysis failed - system requires functional AI services: {e}")
    
    async def _call_openai_for_intent(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI for intent analysis with connection pooling"""
        async with self._openai_semaphore:  # Connection pooling
            try:
                start_time = time.time()
                
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=self.service_config['openai']['model'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.service_config['openai']['temperature'],
                    max_tokens=500,
                    timeout=self.service_config['openai']['timeout']
                )
                
                duration = time.time() - start_time
                log_performance_metrics(self.logger, "openai_intent_analysis", duration, True)
                
                content = response.choices[0].message.content.strip()
                try:
                    return json.loads(content)
                except json.JSONDecodeError as json_error:
                    self.logger.warning(f"Failed to parse OpenAI intent JSON: {json_error}")
                    return None
                
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                log_performance_metrics(self.logger, "openai_intent_analysis", duration, False, {"error": str(e)})
                log_fallback_activation(self.logger, "OpenAI", "Gemini", f"Intent analysis failed: {e}")
                return None
    
    async def _call_gemini_for_intent(self, prompt: str) -> Optional[Dict]:
        """Call Gemini for intent analysis with structured output and connection pooling"""
        async with self._gemini_semaphore:  # Connection pooling
            try:
                start_time = time.time()
                
                # Define structured schema for intent analysis
                from pydantic import BaseModel
                from typing import List
                
                class IntentAnalysis(BaseModel):
                    intent: str
                    confidence: float
                    entities: dict
                    requires_product_search: bool
                    requires_business_info: bool
                    sentiment: str
                    language: str
                    reasoning: str
                
                # Use the NEW Gemini API with structured output
                response = await asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model=self.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=self.service_config['gemini']['temperature'],
                        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
                    )
                )
                
                duration = time.time() - start_time
                log_performance_metrics(self.logger, "gemini_intent_analysis", duration, True)
                
                # NEW API returns structured JSON - parse it directly
                if hasattr(response, 'text') and response.text:
                    content = response.text.strip()
                    
                    # Clean up Gemini response (remove markdown code blocks)
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    elif content.startswith('```'):
                        content = content.replace('```', '').strip()
                    
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as json_error:
                        self.logger.error(f"Failed to parse Gemini intent JSON: {json_error}")
                        self.logger.error(f"Raw response: {content}")
                        raise Exception(f"Gemini returned invalid JSON: {json_error}")
                else:
                    raise Exception("No valid response from Gemini")
                
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                log_performance_metrics(self.logger, "gemini_intent_analysis", duration, False, {"error": str(e)})
                log_fallback_activation(self.logger, "Gemini", "basic_detection", f"Intent analysis failed: {e}")
                return None
    
    def _basic_intent_detection(self, message: str) -> Dict[str, Any]:
        """Basic intent detection fallback"""
        message_lower = message.lower()
        
        # Simple keyword-based intent detection as ultimate fallback
        if any(word in message_lower for word in ['trandafir', 'floare', 'buchet', 'aranjament']):
            intent = 'product_search'
        elif any(word in message_lower for word in ['program', 'orar', 'contact', 'telefon', 'adresa']):
            intent = 'business_info'
        elif any(word in message_lower for word in ['salut', 'bună', 'hello', 'hi']):
            intent = 'greeting'
        else:
            intent = 'general_question'
        
        return {
            "intent": intent,
            "confidence": 0.6,
            "entities": {},
            "requires_product_search": intent == 'product_search',
            "requires_business_info": intent == 'business_info',
            "sentiment": "neutral",
            "language": "ro",
            "reasoning": "Basic keyword detection fallback"
        }
    
    async def _enhanced_gemini_with_products(self, user_message: str, context: Dict, 
                                           user_id: str, request_id: str) -> AIResponse:
        """
        Enhanced Gemini Chat that intelligently integrates ChromaDB product search
        
        This method:
        1. Uses Gemini to analyze if product search is needed
        2. Calls ChromaDB with optimized queries when needed 
        3. Uses Gemini to generate natural responses with product context
        4. Maintains conversation context throughout
        
        Args:
            user_message: User's message text
            context: Conversation context
            user_id: User identifier
            request_id: Request identifier
            
        Returns:
            AIResponse with enhanced response and metadata
        """
        try:
            start_time = time.time()
            self.logger.info(f"[{request_id}] Enhanced Gemini+ChromaDB processing started")
            
            # Import here to avoid circular imports
            from google import genai
            
            # Ensure we have Gemini client
            if not self.gemini_available:
                raise Exception("Gemini API not available for enhanced processing")
            
            client = genai.Client(api_key=self.service_config['gemini']['api_key'])
            
            # Step 1: Analyze message with Gemini to determine if product search is needed
            analysis_prompt = f"""
Analizează acest mesaj de la un client al florăriei XOFlowers și determină dacă este nevoie de căutare de produse:

Mesajul clientului: "{user_message}"
Context conversație: {json.dumps(context.get('recent_messages', [])[-2:], ensure_ascii=False)}

Răspunde în format JSON exact:
{{
    "needs_product_search": true/false,
    "search_terms": "termeni de căutare optimizați (dacă este necesar)",
    "price_range": {{"min": număr, "max": număr}} (doar dacă este menționat explicit),
    "category": "categorie de produse (dacă este relevantă)",
    "intent": "product_search/greeting/question/business_info/other",
    "confidence": 0.0-1.0,
    "reasoning": "de ce este/nu este nevoie de căutare"
}}

Exemple:
- "Salut" → needs_product_search: false, intent: "greeting"
- "Caut buchete roșii" → needs_product_search: true, intent: "product_search"
- "Care e programul?" → needs_product_search: false, intent: "business_info"
"""
            
            self.logger.debug(f"[{request_id}] Analyzing message with Gemini for product search needs")
            
            analysis_response = client.models.generate_content(
                model=self.service_config['gemini']['model'],
                contents=analysis_prompt,
                config={'temperature': 0.3}  # Lower temperature for more consistent analysis
            )
            
            # Parse the analysis
            try:
                analysis_text = analysis_response.text
                if "```json" in analysis_text:
                    json_start = analysis_text.find("```json") + 7
                    json_end = analysis_text.find("```", json_start)
                    analysis_text = analysis_text[json_start:json_end].strip()
                
                analysis = json.loads(analysis_text)
                self.logger.debug(f"[{request_id}] Analysis result: {analysis}")
                
            except Exception as parse_error:
                self.logger.warning(f"[{request_id}] Failed to parse analysis JSON: {parse_error}")
                # Fallback analysis based on keywords
                message_lower = user_message.lower()
                analysis = {
                    "needs_product_search": any(word in message_lower for word in 
                                               ['buchet', 'flor', 'trandafir', 'lalel', 'produs', 'cumpăr', 'vreau']),
                    "intent": "product_search" if any(word in message_lower for word in 
                                                     ['buchet', 'flor', 'trandafir']) else "general",
                    "confidence": 0.7,
                    "reasoning": "Keyword-based fallback analysis"
                }
            
            # Step 2: Search products if needed
            products = []
            if analysis.get("needs_product_search", False):
                self.logger.info(f"[{request_id}] Product search needed - querying ChromaDB")
                
                try:
                    from ..data.chromadb_client import search_products_with_filters
                    
                    search_terms = analysis.get("search_terms", user_message)
                    price_range = analysis.get("price_range", {})
                    category = analysis.get("category")
                    
                    # Build filters dictionary for ChromaDB (be more lenient with categories)
                    filters = {}
                    
                    if price_range:
                        if price_range.get('max'):
                            filters['max_price'] = price_range['max']
                        if price_range.get('min'):
                            filters['min_price'] = price_range['min']
                    
                    # Skip category filtering for now as Gemini-generated categories may not match ChromaDB exactly
                    # TODO: Implement category mapping or validation
                    # if category:
                    #     filters['category'] = category
                    
                    self.logger.debug(f"[{request_id}] ChromaDB search - query: '{search_terms}', filters: {filters}")
                    self.logger.info(f"[{request_id}] About to call ChromaDB with query='{search_terms}', filters={filters}, max_results=10")
                    
                    # Call ChromaDB with proper parameters
                    products = await search_products_with_filters(
                        query=search_terms,
                        filters=filters,
                        max_results=10  # Increased from 6 to 10 for better variety
                    )
                    
                    self.logger.info(f"[{request_id}] ChromaDB returned {len(products)} products")
                    
                    # Safe debug logging - filter out None values
                    valid_products = [p for p in products[:3] if p is not None and isinstance(p, dict)]
                    self.logger.debug(f"[{request_id}] Product details: {[p.get('name', 'N/A')[:50] for p in valid_products]}")
                    
                    self.logger.info(f"[{request_id}] Found {len(products)} products in ChromaDB")
                    
                    # Additional price filtering if needed - with safety checks
                    if price_range.get("max") and 'max_price' not in filters:
                        max_price = price_range["max"]
                        # Safe filtering - check for valid products and price values
                        safe_products = []
                        for p in products:
                            if p is not None and isinstance(p, dict):
                                try:
                                    price = float(p.get('price', 0))
                                    if price <= max_price:
                                        safe_products.append(p)
                                except (ValueError, TypeError):
                                    # Skip products with invalid price data
                                    continue
                        products = safe_products
                        self.logger.debug(f"[{request_id}] After additional price filtering (≤{max_price}): {len(products)} products")
                    
                except Exception as search_error:
                    self.logger.error(f"[{request_id}] Product search failed: {search_error}")
                    products = []
            
            # Step 3: Generate natural response with Gemini using chat history for context
            chat = self._get_or_create_chat(user_id)
            
            if chat is None:
                raise Exception("Unable to create/get Gemini chat session")
            
            # Build enhanced message with product context (not a system prompt)
            if products:
                products_info = "PRODUSE DISPONIBILE:\n"
                for i, product in enumerate(products[:5], 1):
                    if product is not None and isinstance(product, dict):
                        name = product.get('name', 'Produs')
                        price = product.get('price', 'N/A')
                        category = product.get('category', '')
                        products_info += f"{i}. {name} - {price} MDL"
                        if category:
                            products_info += f" ({category})"
                        products_info += "\n"
                
                enhanced_message = f"{user_message}\n\n{products_info}"
            else:
                enhanced_message = user_message
            
            self.logger.debug(f"[{request_id}] Sending message to Gemini chat with conversation history")
            
            # Send message to chat (this maintains conversation history automatically)
            final_response = await asyncio.to_thread(
                chat.send_message,
                enhanced_message
            )
            
            # Update chat message count
            if user_id in self.user_chats:
                self.user_chats[user_id]['message_count'] += 1
            
            response_text = final_response.text
            processing_time = time.time() - start_time
            
            self.logger.info(f"[{request_id}] Enhanced processing completed in {processing_time:.2f}s")
            
            # Filter out None/invalid products before returning
            valid_products = [p for p in products[:5] if p is not None and isinstance(p, dict)]
            
            return AIResponse(
                response_text=response_text,
                success=True,
                service_used="enhanced_gemini_chat",
                intent=analysis.get("intent", "general"),
                confidence=analysis.get("confidence", 0.8),
                products_found=len(valid_products),
                needs_product_search=analysis.get("needs_product_search", False),
                products=valid_products  # Return only valid products for buttons/context
            )
            
        except Exception as e:
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            self.logger.error(f"[{request_id}] Enhanced Gemini processing failed: {e}")
            
            # NO FALLBACK - System must work with proper AI services
            raise Exception(f"Enhanced AI processing failed - system requires functional AI services: {e}")
    
    def _build_enhanced_response_prompt(self, user_message: str, context: Dict, 
                                      products: List, analysis: Dict, user_id: str) -> str:
        """Build comprehensive prompt for enhanced response generation"""
        
        # Get recent conversation context
        recent_messages = context.get('recent_messages', [])
        context_text = ""
        if recent_messages:
            context_text = "\n".join([
                f"Client: {msg.get('user_message', '')}" if msg.get('role') == 'user' else 
                f"Consultant: {msg.get('ai_response', '')}" 
                for msg in recent_messages[-4:]  # Last 4 messages for context
            ])
        
        # Build products section
        products_section = ""
        if products:
            products_section = "PRODUSE GĂSITE ÎN CATALOG:\n"
            for i, product in enumerate(products[:5], 1):  # Top 5 products
                # Safety check for None or invalid products
                if product is None or not isinstance(product, dict):
                    continue
                    
                price = product.get('price', 'N/A')
                name = product.get('name', 'Produs')
                category = product.get('category', '')
                description = product.get('description', '')
                
                # Safe description truncation
                if description and len(description) > 100:
                    description = description[:100]  # Truncate long descriptions
                
                products_section += f"{i}. {name} - {price} MDL"
                if category:
                    products_section += f" ({category})"
                if description:
                    products_section += f"\n   {description}..."
                products_section += "\n\n"
        else:
            products_section = "NU S-AU GĂSIT PRODUSE SPECIFICE ÎN CATALOG.\n"
        
        prompt = f"""
Tu ești consultantul floral expert al florăriei XOFlowers din Chișinău, Moldova. 
Ești prietenos, profesional și cunoscător în domeniul floristicii.

CONTEXT CONVERSAȚIE:
{context_text if context_text else "Prima interacțiune cu clientul."}

MESAJUL ACTUAL AL CLIENTULUI: "{user_message}"

ANALIZA MESAJULUI:
- Intenția: {analysis.get('intent', 'general')}
- Necesită căutare produse: {analysis.get('needs_product_search', False)}
- Încredere: {analysis.get('confidence', 0.8):.1f}

{products_section}

INSTRUCȚIUNI PENTRU RĂSPUNS:
1. Răspunde în română, natural și prietenos
2. Dacă există produse, menționează-le relevant în conversație
3. Oferă sfaturi și recomandări bazate pe experiența ta florală
4. Dacă nu există produse specifice, oferă alternative sau întreabă pentru clarificări
5. Păstrează tonul profesional dar călduraos
6. NU folosi markdown, formatare specială sau liste - doar text natural
7. Adaptează răspunsul la contextul conversației existente
8. Dacă clientul salută pentru prima dată, salută și întreabă cum îl poți ajuta
9. Pentru întrebări despre program/contact, oferă informații de business

Generează un răspuns natural, conversațional și util pentru client.
"""
        
        return prompt.strip()
    
    async def _generate_response_with_fallback(self, message: str, intent_data: Dict, 
                                             context: Dict, request_id: str) -> AIResponse:
        """
        Generate response using natural response generation system with AI fallback chain
        
        Args:
            message: User message
            intent_data: Intent analysis results
            context: Conversation context
            request_id: Request identifier
        
        Returns:
            AIResponse with generated response and metadata
        """
        try:
            # Use the new natural response generation system
            response_result = await generate_natural_response(message, intent_data, context)
            
            if response_result['success']:
                # Get the enhanced prompt from response generator
                enhanced_prompt = response_result['response']
                
                # Generate actual response using AI services with enhanced prompt
                ai_response = await self._call_ai_services_for_response(enhanced_prompt, request_id)
                
                if ai_response:
                    return AIResponse(
                        response_text=ai_response['response'],
                        intent_detected=intent_data.get('intent', 'unknown'),
                        confidence=intent_data.get('confidence', 0.0),
                        products_included=response_result.get('products_included', 0),
                        context_updated=True,
                        processing_time=response_result.get('processing_time', 0),
                        service_used=ai_response['service_used'],
                        success=True
                    )
            
            # NO FALLBACK - Natural response generation must work
            raise Exception(f"Natural response generation failed - system requires functional response generation")
            
        except Exception as e:
            self.logger.error(f"[{request_id}] Error in natural response generation: {e}")
            raise Exception(f"Response generation failed - system requires functional AI services: {e}")
        
        # NO FALLBACK - AI services MUST work
        raise Exception("All AI services failed - system requires functional AI services for proper operation")
    
    async def _call_ai_services_for_response(self, prompt: str, request_id: str) -> Optional[Dict[str, str]]:
        """
        Call AI services with fallback chain for response generation
        
        Args:
            prompt: Enhanced prompt for response generation
            request_id: Request identifier for logging
            
        Returns:
            Dict with response and service used, or None if all services fail
        """
        # Try Gemini first (primary AI service)
        if self.gemini_available:
            result = await self._call_gemini_for_response(prompt, request_id)
            if result:
                return {"response": result, "service_used": "gemini"}
        
        # Try OpenAI as backup
        if self.openai_available:
            result = await self._call_openai_for_response(prompt, request_id)
            if result:
                return {"response": result, "service_used": "openai"}
        
        # NO FALLBACK - AI services MUST work
        raise Exception("All AI services failed for response generation - system requires functional AI services")
    
    def _prepare_basic_response_prompt(self, message: str, intent_data: Dict, context: Dict) -> str:
        """Prepare basic response prompt as fallback"""
        return self.ai_prompts['response_generation_prompt'].format(
            message=message,
            intent_data=json.dumps(intent_data, ensure_ascii=False),
            products=[],  # Empty for basic fallback
            business_info={},  # Empty for basic fallback
            context=json.dumps(context, ensure_ascii=False)
        )
    
    async def _call_openai_for_response(self, prompt: str, request_id: str) -> Optional[str]:
        """Call OpenAI for response generation with connection pooling and caching"""
        # Check cache first
        cache_key = self._generate_cache_key(prompt, "openai")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            self.logger.debug(f"[{request_id}] Using cached OpenAI response")
            return cached_response
        
        async with self._openai_semaphore:  # Connection pooling
            try:
                start_time = time.time()
                
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=self.service_config['openai']['model'],
                    messages=[
                        {"role": "system", "content": self.ai_prompts['main_system_prompt']},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.service_config['openai']['temperature'],
                    max_tokens=self.service_config['openai']['max_tokens'],
                    timeout=self.service_config['openai']['timeout']
                )
                
                duration = time.time() - start_time
                log_performance_metrics(self.logger, "openai_response_generation", duration, True, 
                                      {"request_id": request_id})
                
                result = response.choices[0].message.content.strip()
                
                # Cache the response
                self._cache_response(cache_key, result)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                log_performance_metrics(self.logger, "openai_response_generation", duration, False, 
                                      {"error": str(e), "request_id": request_id})
                log_fallback_activation(self.logger, "OpenAI", "Gemini", f"Response generation failed: {e}", request_id)
                return None
    
    async def _call_gemini_for_response(self, prompt: str, request_id: str) -> Optional[str]:
        """Call Gemini for response generation with system instructions and connection pooling"""
        # Check cache first
        cache_key = self._generate_cache_key(prompt, "gemini")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            self.logger.debug(f"[{request_id}] Using cached Gemini response")
            return cached_response
        
        async with self._gemini_semaphore:  # Connection pooling
            try:
                start_time = time.time()
                
                # Use the NEW Gemini API with system instructions
                response = await asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model=self.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.ai_prompts['main_system_prompt'],
                        temperature=self.service_config['gemini']['temperature'],
                        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
                    )
                )
                
                duration = time.time() - start_time
                log_performance_metrics(self.logger, "gemini_response_generation", duration, True,
                                      {"request_id": request_id})
                
                # Extract text from NEW API response
                if hasattr(response, 'text') and response.text:
                    result = response.text.strip()
                else:
                    raise Exception("No valid text response from Gemini")
                
                # Cache the response
                self._cache_response(cache_key, result)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                log_performance_metrics(self.logger, "gemini_response_generation", duration, False,
                                      {"error": str(e), "request_id": request_id})
                log_fallback_activation(self.logger, "Gemini", "safe_response", f"Response generation failed: {e}", request_id)
                return None
    
    def _generate_cache_key(self, prompt: str, service: str) -> str:
        """Generate cache key for response caching"""
        # Create hash of prompt + service for cache key
        content = f"{service}:{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        if cache_key in self._response_cache:
            cached_item = self._response_cache[cache_key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                log_cache_operation(self.logger, "get", cache_key, True)
                return cached_item['response']
            else:
                # Remove expired cache entry
                del self._response_cache[cache_key]
                log_cache_operation(self.logger, "get", cache_key, False)
        else:
            log_cache_operation(self.logger, "get", cache_key, False)
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache response with timestamp"""
        self._response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # Clean up old cache entries periodically
        if len(self._response_cache) > 100:  # Limit cache size
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._response_cache.items()
            if current_time - value['timestamp'] > self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._response_cache[key]
        
        self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        current_time = time.time()
        active_entries = sum(
            1 for value in self._response_cache.values()
            if current_time - value['timestamp'] < self._cache_ttl
        )
        
        return {
            'total_entries': len(self._response_cache),
            'active_entries': active_entries,
            'cache_ttl_seconds': self._cache_ttl,
            'max_concurrent_openai': self._openai_semaphore._value,
            'max_concurrent_gemini': self._gemini_semaphore._value
        }
    
    def _get_safe_fallback_response(self) -> str:
        """Get safe fallback response when all AI services fail"""
        return ("Îmi pare rău, dar în acest moment întâmpin dificultăți tehnice. "
                "Te rog să încerci din nou în câteva momente sau să ne contactezi "
                "direct la telefon pentru asistență imediată. Mulțumesc pentru înțelegere!")


# Global AI engine instance
_ai_engine = None

def get_ai_engine() -> AIEngine:
    """Get global AI engine instance"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine


# Main entry point function
async def process_message_ai(user_message: str, user_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main entry point for AI message processing
    
    Args:
        user_message: User's message text
        user_id: Unique user identifier  
        context: Conversation context (optional)
    
    Returns:
        Dict with response, success status, and metadata
    """
    engine = get_ai_engine()
    return await engine.process_message_ai(user_message, user_id, context)