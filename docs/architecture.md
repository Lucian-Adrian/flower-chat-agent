# XOFlowers AI Agent - System Architecture

## Overview

The XOFlowers AI Agent is a sophisticated conversational AI system designed to provide intelligent customer support for the XOFlowers flower shop. The system integrates multiple AI services (Gemini 2.5 Flash primary, OpenAI fallback) with vector-based product search capabilities using ChromaDB, providing product-aware responses through Telegram and Instagram bots.

## Architecture Principles

- **AI-First Design**: Gemini 2.5 Flash as primary AI engine with OpenAI as fallback
- **Product-Aware Responses**: ChromaDB integration for intelligent product search and recommendations
- **Security-First**: AI-powered security validation for all incoming messages
- **Fallback Resilience**: Multiple fallback layers ensure system availability
- **Performance Monitoring**: Comprehensive logging and performance tracking
- **Modular Design**: Clean separation of concerns with clear interfaces

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │  Instagram Bot  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
            ┌────────▼────────┐
            │   AI Engine     │
            │  (Orchestrator) │
            └────────┬────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐  ┌──────▼──────┐  ┌─────▼─────┐
│ Gemini  │  │   ChromaDB  │  │ Security  │
│2.5 Flash│  │  Products   │  │    AI     │
└─────────┘  └─────────────┘  └───────────┘
     │
┌────▼────┐
│ OpenAI  │
│Fallback │
└─────────┘
```

## Core Components

### 1. Entry Points

#### src/api/telegram_app.py
- **Purpose**: Telegram Bot interface using python-telegram-bot
- **Features**: 
  - Enhanced message handling with product URL buttons
  - Inline keyboard markup for product recommendations
  - Error handling and logging
  - Integration with AI Engine
- **Key Classes**: `XOFlowersTelegramBot`
- **Dependencies**: AI Engine, System Definitions, Utils

#### src/api/main.py  
- **Purpose**: FastAPI web interface for API access
- **Features**:
  - RESTful endpoints for message processing
  - Pydantic validation for requests/responses
  - CORS middleware for web access
  - Background task processing
- **Key Classes**: `MessageRequest`, `MessageResponse`
- **Dependencies**: AI Engine, Telegram/Instagram routers

### 2. Intelligence Layer

#### src/intelligence/ai_engine.py
- **Purpose**: Main AI processing orchestrator
- **Features**:
  - Primary Gemini 2.5 Flash integration
  - OpenAI fallback system
  - Intent analysis and classification
  - Product search integration
  - Response caching and optimization
  - Performance monitoring
- **Key Classes**: `AIEngine`, `AIResponse`
- **Flow**: Security Check → Intent Analysis → Product Search → Response Generation

#### src/intelligence/security_ai.py
- **Purpose**: AI-powered message security validation
- **Features**:
  - Multi-layered security analysis
  - Risk assessment and classification
  - Automated response generation for threats
  - Both Gemini and OpenAI validation
- **Key Classes**: `SecurityAI`, `SecurityResult`
- **Integration**: Called by AI Engine before processing

#### src/intelligence/gemini_chat_manager.py
- **Purpose**: Gemini-specific chat session management
- **Features**:
  - Persistent chat sessions per user
  - Context management and memory
  - Enhanced conversational capabilities
  - Session cleanup and optimization
- **Key Classes**: `GeminiChatManager`, `GeminiChatSession`

### 3. Data Layer

#### src/data/chromadb_client.py
- **Purpose**: Vector database for product search
- **Features**:
  - Automatic CSV product loading (724 products)
  - Semantic product search with relevance scoring
  - Price filtering and category support
  - Fallback to CSV when ChromaDB unavailable
- **Key Methods**: `search_products()`, `search_with_price_filter()`
- **Data Source**: `src/database/products.csv` (724 products)

#### src/database/products.csv
- **Purpose**: Complete product database
- **Structure**: 
  - 724 products across multiple categories
  - Fields: chunk_id, primary_text, category, price, flower_type, url, etc.
  - Categories: Chando (aromă diffusers), Peonies, French Roses, Basket/Boxes
- **URL Integration**: Direct product links for Telegram buttons

### 4. Configuration & Utilities

#### src/utils/system_definitions.py
- **Purpose**: Centralized configuration management
- **Contents**:
  - Service configurations (API keys, endpoints)
  - AI prompts and templates
  - Business information and policies
  - Security and performance settings

#### src/utils/utils.py
- **Purpose**: Shared utilities and monitoring
- **Features**:
  - Logging setup and standardization
  - Performance monitoring and metrics
  - Request ID generation
  - Cache management utilities

### 5. Platform Integrations

#### src/api/telegram_integration.py
- **Purpose**: Telegram-specific routing and handling
- **Features**: Webhook management, message routing

#### src/api/instagram_integration.py
- **Purpose**: Instagram-specific integration
- **Features**: Meta webhook handling, message processing

## Data Flow

### 1. Message Processing Flow

```
User Message (Telegram/Instagram)
        │
        ▼
┌─────────────────┐
│ Platform Router │
│ (telegram_app)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Security AI    │
│ Message Validation │
└─────────┬───────┘
          │ ✓ Safe
          ▼
┌─────────────────┐
│   AI Engine     │
│  (Orchestrator) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Intent Analysis │
│ (Gemini/OpenAI) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Product Search  │
│   (ChromaDB)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│Response Generator│
│ (Enhanced Gemini)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Platform Response│
│ (with buttons)  │
└─────────────────┘
```

### 2. Product Search Integration

```
User Query: "roses under 1000 lei"
        │
        ▼
┌─────────────────┐
│ Intent Analysis │ → intent: "product_search"
│                 │   price_max: 1000
│                 │   category: "roses"
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ ChromaDB Search │ → Vector similarity search
│                 │   Price filtering
│                 │   Relevance scoring
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Enhanced Gemini │ → Natural Romanian response
│ Response Gen    │   Product recommendations
│                 │   Price comparisons
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Telegram Output │ → Text + Product buttons
│                 │   Direct purchase links
└─────────────────┘
```

## AI Services Configuration

### Primary: Gemini 2.5 Flash
- **Model**: `gemini-2.5-flash`
- **Usage**: Primary chat, intent analysis, response generation
- **Features**: Structured output, Romanian language, product awareness
- **Fallback**: OpenAI GPT-4o-mini when Gemini fails

### Secondary: OpenAI GPT-4o-mini
- **Model**: `gpt-4o-mini`
- **Usage**: Fallback for chat, security validation
- **Features**: JSON mode for structured responses
- **Role**: Backup when Gemini unavailable

## Product Recommendation System

### Configuration
- **Search Limit**: 10 products per search
- **Response Limit**: 5 products per recommendation
- **Categories**: Chando, Peonies, French Roses, Baskets/Boxes
- **Price Filtering**: Intelligent price range detection

### Features
- **Semantic Search**: Vector-based product matching
- **URL Integration**: Direct product links as Telegram buttons
- **Multiple Products**: Configurable recommendation count
- **Price Awareness**: Automatic price filtering and comparison

## Security Architecture

### Multi-Layer Validation
1. **Basic Filtering**: Keyword-based threat detection
2. **AI Analysis**: Gemini/OpenAI security assessment
3. **Risk Classification**: LOW/MEDIUM/HIGH threat levels
4. **Automated Response**: Context-aware security messages

### Threat Detection
- Spam and promotional content
- Inappropriate language
- Potential security threats
- Off-topic conversations

## Performance & Monitoring

### Metrics Tracking
- Response times per AI service
- Cache hit/miss ratios
- User activity patterns
- Error rates and fallback usage

### Optimization Features
- Response caching with TTL
- Batch product processing
- Connection pooling
- Automatic cleanup routines

## Environment Variables

### Required Configuration
```env
# AI Services
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_token

# Instagram (Optional)
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# Database
CHROMADB_PATH=./chroma_db_flowers
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Deployment Architecture

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Initialize ChromaDB
python -c "from src.data.chromadb_client import ChromaDBClient; ChromaDBClient()"

# Run Telegram bot
python src/api/telegram_app.py
```

### Production Considerations
- **Scaling**: Multiple bot instances with shared ChromaDB
- **Monitoring**: Comprehensive logging and alerts
- **Backup**: ChromaDB and conversation data backup
- **Security**: API key rotation and access controls

## File Structure

```
xoflowers-agent/
├── src/
│   ├── api/                    # Platform interfaces
│   │   ├── telegram_app.py     # Main Telegram bot
│   │   ├── main.py            # FastAPI web interface
│   │   ├── telegram_integration.py
│   │   └── instagram_integration.py
│   ├── intelligence/          # AI processing
│   │   ├── ai_engine.py       # Main AI orchestrator
│   │   ├── security_ai.py     # Security validation
│   │   ├── gemini_chat_manager.py
│   │   ├── intent_classifier.py
│   │   └── response_generator.py
│   ├── data/                  # Data management
│   │   ├── chromadb_client.py # Vector database
│   │   └── faq_manager.py
│   ├── database/              # Data storage
│   │   ├── products.csv       # 724 products
│   │   ├── vector_search.py
│   │   └── simplified_search.py
│   ├── utils/                 # Shared utilities
│   │   ├── system_definitions.py # Configuration
│   │   └── utils.py          # Logging & monitoring
│   ├── config/                # Environment setup
│   ├── security/              # Security modules
│   └── helpers/               # Helper functions
├── tests/                     # Test scripts
├── docs/                      # Documentation
└── requirements.txt           # Dependencies
```

## Testing & Validation

### Test Scripts Available
- `test_ai_engine.py` - AI engine functionality
- `test_gemini_analysis.py` - Gemini AI validation
- `test_telegram_integration.py` - Bot integration
- `test_enhanced_products.py` - Product recommendation UX
- `test_launch_readiness.py` - Full system validation

### Validation Commands
```bash
# Test AI engine
python test_ai_engine.py

# Test product features
python test_enhanced_products.py

# Launch readiness check
python test_launch_readiness.py
```

## Future Enhancements

### Planned Features
1. **Category Mapping**: Enhanced ChromaDB category filtering
2. **Redis Integration**: Persistent conversation context
3. **Analytics Dashboard**: Real-time performance monitoring
4. **Multi-language Support**: Extended language capabilities
5. **Advanced Recommendations**: ML-based product suggestions

### Scalability Roadmap
1. **Microservices**: Split AI engine into separate services
2. **Load Balancing**: Multiple bot instances
3. **Database Optimization**: Advanced ChromaDB configurations
4. **Caching Layer**: Redis-based response caching
5. **API Gateway**: Centralized request management

---

**Last Updated**: July 2025  
**Architecture Version**: 2.0  
**System Status**: Production Ready
