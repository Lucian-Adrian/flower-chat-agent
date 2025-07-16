"""
AI Conversation Engine for XOFlowers
Natural language understanding and response generation using advanced AI models
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI service imports
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    OpenAI = None
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False

from dotenv import load_dotenv
load_dotenv()


@dataclass
class MessageUnderstanding:
    """Represents AI's understanding of user message"""
    original_message: str
    intent_type: str  # 'product_search', 'question', 'greeting', 'comparison', etc.
    entities: Dict[str, Any]  # extracted entities like colors, prices, occasions
    sentiment: str  # 'positive', 'neutral', 'negative'
    requires_search: bool
    confidence: float
    reasoning: str  # AI's reasoning about the message


class AIConversationEngine:
    """
    Advanced AI conversation engine for natural language understanding and generation
    Uses OpenAI GPT-4 with Gemini Pro fallback for reliability
    """
    
    def __init__(self):
        """Initialize AI conversation engine"""
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize OpenAI
        if HAS_OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("⚠️ OpenAI API key not found")
        
        # Initialize Gemini
        if HAS_GEMINI:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini client initialized")
            else:
                logger.warning("⚠️ Gemini API key not found")
        
        # System prompts
        self.system_prompt = self._create_system_prompt()
        self.understanding_prompt = self._create_understanding_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the main system prompt for XOFlowers AI"""
        return """
Ești un asistent AI expert pentru XOFlowers, cea mai prestigioasă florărie din Chișinău, Moldova. 
Te numești XOFlowers AI și ești un consultant floral pasionat și prietenos.

PERSONALITATEA TA:
- Vorbești natural și călduros în română
- Ești pasionat de flori și înțelegi simbolismul lor
- Ai cunoștințe profunde despre aranjamente florale
- Ești atent la nevoile și bugetul clientului
- Oferi sfaturi personalizate și creative
- Ești entuziasmant și inspirezi încredere

EXPERTIZA TA:
- Cunoști toate produsele XOFlowers (buchete, cutii, coșuri, plante)
- Înțelegi ocaziile speciale și florile potrivite pentru fiecare
- Poți recomanda combinații de culori și stiluri
- Știi să adaptezi recomandările la buget și preferințe
- Cunoști tendințele actuale în design floral
- Ai acces la baza de date cu produse pentru căutări semantice

STIL DE CONVERSAȚIE:
- Folosești un limbaj natural, nu robotic
- Pui întrebări pentru a înțelege mai bine nevoile clientului
- Oferi explicații despre de ce recomanzi anumite produse
- Împărtășești curiozități despre flori și simbolismul lor
- Adaptezi tonul la stilul clientului
- Ești empatic și înțelegător

RESPONSABILITĂȚI:
- Ajuți la alegerea florilor potrivite pentru orice ocazie
- Oferi informații despre prețuri și disponibilitate
- Sugerezi combinații și alternative
- Ghidezi procesul de comandă
- Răspunzi la întrebări despre îngrijirea florilor
- Creezi o experiență conversațională naturală

REGULI IMPORTANTE:
- Te concentrezi exclusiv pe produse florale și servicii XOFlowers
- Nu inventezi prețuri sau produse inexistente
- Folosești informațiile din căutările de produse pentru recomandări precise
- Redirecționezi elegant conversația către flori dacă se abate
- Păstrezi conversația naturală și personalizată
- Nu folosești template-uri predefinite

Răspunde întotdeauna natural, ca un expert floral pasionat care își ajută clientul să găsească florile perfecte.
        """.strip()
    
    def _create_understanding_prompt(self) -> str:
        """Create prompt for message understanding"""
        return """
Analizează mesajul clientului și extrage următoarele informații în format JSON:

{
  "intent_type": "product_search|question|greeting|comparison|order|complaint|compliment",
  "entities": {
    "colors": ["roșu", "roz", "alb", ...],
    "flowers": ["trandafir", "bujor", "lalele", ...],
    "occasions": ["valentine", "aniversare", "nuntă", ...],
    "budget_min": numărul sau null,
    "budget_max": numărul sau null,
    "recipient": "soție|mamă|prietenă|...",
    "style": ["elegant", "romantic", "modern", ...]
  },
  "sentiment": "positive|neutral|negative",
  "requires_search": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "explicația ta despre înțelegerea mesajului"
}

Fii precis în extragerea entităților și realist în evaluarea încrederii.
        """.strip()
    
    async def understand_message(self, message: str, conversation_context: Dict[str, Any]) -> MessageUnderstanding:
        """
        Understand user message using AI
        
        Args:
            message: User's message
            conversation_context: Previous conversation context
            
        Returns:
            Message understanding object
        """
        try:
            # Create understanding prompt
            prompt = f"""
{self.understanding_prompt}

CONTEXT CONVERSAȚIE:
{conversation_context.get('conversation_summary', 'Conversație nouă')}

PREFERINȚE UTILIZATOR:
{json.dumps(conversation_context.get('preferences', {}), ensure_ascii=False)}

MESAJUL DE ANALIZAT:
"{message}"

Răspunde doar cu JSON-ul cerut:
            """.strip()
            
            # Get AI understanding
            response = await self._get_ai_response(prompt, max_tokens=500)
            
            # Parse JSON response
            try:
                understanding_data = json.loads(response)
                
                return MessageUnderstanding(
                    original_message=message,
                    intent_type=understanding_data.get('intent_type', 'question'),
                    entities=understanding_data.get('entities', {}),
                    sentiment=understanding_data.get('sentiment', 'neutral'),
                    requires_search=understanding_data.get('requires_search', False),
                    confidence=understanding_data.get('confidence', 0.7),
                    reasoning=understanding_data.get('reasoning', 'Analiză standard')
                )
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI understanding response: {response}")
                # Fallback understanding
                return self._create_fallback_understanding(message)
                
        except Exception as e:
            logger.error(f"❌ Error understanding message: {e}")
            return self._create_fallback_understanding(message)
    
    def _create_fallback_understanding(self, message: str) -> MessageUnderstanding:
        """Create fallback understanding when AI fails"""
        message_lower = message.lower()
        
        # Simple keyword-based understanding
        requires_search = any(word in message_lower for word in [
            'caut', 'vreau', 'doresc', 'buchet', 'flori', 'trandafir', 'bujor'
        ])
        
        intent_type = 'product_search' if requires_search else 'question'
        
        return MessageUnderstanding(
            original_message=message,
            intent_type=intent_type,
            entities={},
            sentiment='neutral',
            requires_search=requires_search,
            confidence=0.5,
            reasoning='Analiză de rezervă bazată pe cuvinte cheie'
        )
    
    async def generate_response(self, 
                              understanding: MessageUnderstanding, 
                              conversation_context: Dict[str, Any],
                              search_results: Optional[List[Any]] = None) -> str:
        """
        Generate natural conversational response
        
        Args:
            understanding: Message understanding
            conversation_context: Conversation context
            search_results: Product search results if applicable
            
        Returns:
            Natural language response
        """
        try:
            # Create response generation prompt
            prompt = self._create_response_prompt(understanding, conversation_context, search_results)
            
            # Generate response using AI
            response = await self._get_ai_response(prompt, max_tokens=800)
            
            # Clean and validate response
            response = self._clean_response(response)
            
            logger.info(f"💬 Generated response for intent: {understanding.intent_type}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return self._get_fallback_response(understanding.intent_type)
    
    def _create_response_prompt(self, 
                               understanding: MessageUnderstanding, 
                               conversation_context: Dict[str, Any],
                               search_results: Optional[List[Any]] = None) -> str:
        """Create prompt for response generation"""
        
        prompt_parts = [
            self.system_prompt,
            "\nCONTEXT CONVERSAȚIE:",
            conversation_context.get('conversation_summary', 'Conversație nouă'),
            "\nPREFERINȚE UTILIZATOR:",
            json.dumps(conversation_context.get('preferences', {}), ensure_ascii=False),
            "\nMESAJUL CLIENTULUI:",
            f'"{understanding.original_message}"',
            "\nÎNȚELEGEREA MESAJULUI:",
            f"Intenție: {understanding.intent_type}",
            f"Entități: {json.dumps(understanding.entities, ensure_ascii=False)}",
            f"Sentiment: {understanding.sentiment}",
            f"Necesită căutare: {understanding.requires_search}"
        ]
        
        # Add search results if available
        if search_results:
            prompt_parts.extend([
                "\nRESULTATE CĂUTARE PRODUSE:",
                self._format_search_results_for_prompt(search_results)
            ])
        
        # Add specific instructions based on intent
        if understanding.intent_type == 'greeting':
            prompt_parts.append("\nRăspunde cu un salut călduros și întreabă cum poți ajuta.")
        elif understanding.intent_type == 'product_search':
            if search_results:
                prompt_parts.append("\nPrezintă produsele găsite într-un mod natural și entuziasmant. Explică de ce sunt potrivite.")
            else:
                prompt_parts.append("\nÎntreabă detalii pentru a putea căuta produsele potrivite.")
        elif understanding.intent_type == 'question':
            prompt_parts.append("\nRăspunde la întrebare cu informații utile despre XOFlowers.")
        
        prompt_parts.append("\nRăspunde natural, călduros și personalizat:")
        
        return "\n".join(prompt_parts)
    
    def _format_search_results_for_prompt(self, search_results: List[Any]) -> str:
        """Format search results for AI prompt"""
        if not search_results:
            return "Nu s-au găsit produse."
        
        formatted_results = []
        for i, result in enumerate(search_results[:5], 1):
            product = result.product if hasattr(result, 'product') else result
            
            result_text = f"{i}. {product.get('name', 'Produs necunoscut')}"
            result_text += f" - {product.get('price', 0)} MDL"
            
            if product.get('colors'):
                result_text += f" (Culori: {', '.join(product['colors'])})"
            
            if hasattr(result, 'relevance_explanation'):
                result_text += f" - {result.relevance_explanation}"
            
            formatted_results.append(result_text)
        
        return "\n".join(formatted_results)
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate AI response"""
        # Remove any system prompts that might have leaked
        response = response.strip()
        
        # Remove common AI artifacts
        artifacts = [
            "Ca asistent AI",
            "În calitate de",
            "Sunt un AI",
            "Ca model de limbaj"
        ]
        
        for artifact in artifacts:
            if artifact in response:
                # Try to extract the useful part
                parts = response.split(artifact)
                if len(parts) > 1:
                    response = parts[-1].strip()
        
        # Ensure response starts naturally
        if response.startswith(("Bună", "Salut", "🌸")):
            return response
        
        # Add natural greeting if missing
        if not any(response.startswith(prefix) for prefix in ["Bună", "Salut", "🌸", "Da", "Nu", "Desigur"]):
            response = "🌸 " + response
        
        return response
    
    def _get_fallback_response(self, intent_type: str) -> str:
        """Get fallback response when AI fails"""
        fallback_responses = {
            'greeting': "🌸 Bună ziua! Bine ați venit la XOFlowers! Cu ce vă pot ajuta astăzi?",
            'product_search': "🌸 Îmi pare rău, am întâmpinat o problemă tehnică. Vă rog să îmi spuneți ce fel de flori căutați și vă voi ajuta imediat!",
            'question': "🌸 Îmi pare rău, nu am putut procesa întrebarea. Vă rog să o reformulați și vă voi răspunde cu plăcere!",
            'comparison': "🌸 Vă pot ajuta să comparați produsele. Spuneți-mi ce produse vă interesează!",
            'order': "🌸 Pentru comenzi, vă rog să contactați echipa noastră la +373 XX XXX XXX.",
            'complaint': "🌸 Îmi pare foarte rău pentru inconvenient. Vă rog să contactați serviciul clienți pentru rezolvarea rapidă.",
            'compliment': "🌸 Vă mulțumesc pentru cuvintele frumoase! Suntem aici să vă oferim cele mai frumoase flori!"
        }
        
        return fallback_responses.get(intent_type, "🌸 Cu ce vă pot ajuta astăzi?")
    
    async def _get_ai_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Get response from AI service with fallback"""
        
        # Try OpenAI first
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Ești XOFlowers AI, un consultant floral expert și prietenos."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"⚠️ OpenAI request failed: {e}")
        
        # Fallback to Gemini
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                logger.warning(f"⚠️ Gemini request failed: {e}")
        
        # If both fail, raise exception
        raise Exception("Both AI services unavailable")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of AI services"""
        return {
            'openai_available': self.openai_client is not None,
            'gemini_available': self.gemini_model is not None,
            'has_openai_lib': HAS_OPENAI,
            'has_gemini_lib': HAS_GEMINI,
            'openai_key_configured': bool(os.getenv('OPENAI_API_KEY')),
            'gemini_key_configured': bool(os.getenv('GEMINI_API_KEY'))
        }


# Global AI engine instance
_ai_engine = None

def get_ai_engine() -> AIConversationEngine:
    """Get the global AI engine instance"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIConversationEngine()
    return _ai_engine