# 🚀 XOFlowers Instagram AI Agent - Deployment Guide

## Quick Start (5 minutes)

### Method 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd XOFlowers-Instagram-AI-agent-chatbot
```

2. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run with Docker**
```bash
docker-compose up -d
```

4. **Access the application**
- Main app: http://localhost:5000
- API health: http://localhost:5000/api/health
- Chat endpoint: http://localhost:5000/api/chat

### Method 2: Local Python

1. **Clone and setup**
```bash
git clone <your-repo-url>
cd XOFlowers-Instagram-AI-agent-chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Initialize database**
```bash
python setup_database.py
```

5. **Run the application**
```bash
python app.py
```

## Required API Keys

1. **OpenAI API Key** (Essential for AI features)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_KEY=sk-your-key-here`

2. **Instagram API Tokens** (For Instagram integration)
   - Get from: https://developers.facebook.com/
   - Add to `.env`: 
     ```
     INSTAGRAM_VERIFY_TOKEN=your_verify_token
     INSTAGRAM_ACCESS_TOKEN=your_access_token
     ```

## Features Included

✅ **Ultra-Fast ChromaDB** - 709 products loaded in <1 second  
✅ **AI-Powered Chat** - OpenAI GPT integration  
✅ **Multilingual Support** - Romanian, English, Russian  
✅ **Instagram Ready** - Webhook endpoints included  
✅ **Semantic Search** - Vector-based product matching  
✅ **Personalized Recommendations** - User-based suggestions  
✅ **Docker Support** - One-command deployment  
✅ **Production Ready** - Health checks, logging, error handling  

## Testing the System

### Test Chat API
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vreau trandafiri roșii pentru ziua de naștere", "user_id": "test_user"}'
```

### Test Ultra Search
```bash
curl -X POST http://localhost:5000/api/ultra-search \
  -H "Content-Type: application/json" \
  -d '{"query": "red roses", "n_results": 5}'
```

### Test Recommendations
```bash
curl http://localhost:5000/api/personalized-recommendations/test_user
```

## Performance Stats

- **709 products** loaded from complete XOFlowers catalog
- **Sub-second search** with ChromaDB ULTRA
- **Multilingual processing** with automatic language detection
- **Advanced metadata** for precise filtering
- **Caching system** for optimal performance

## Troubleshooting

### Common Issues

1. **"OPENAI_KEY not found"**
   - Solution: Add your OpenAI API key to `.env` file

2. **"ChromaDB initialization failed"**
   - Solution: Run `python setup_database.py` first

3. **"Port 5000 already in use"**
   - Solution: Stop other services or change port in app.py

4. **Docker build fails**
   - Solution: Ensure Docker has enough memory (4GB+)

### Check System Status
```bash
# Health check
curl http://localhost:5000/api/health

# Performance stats
curl http://localhost:5000/api/performance-stats

# Test ULTRA mode
curl http://localhost:5000/api/test-ultra
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Test API endpoints individually
4. Ensure all dependencies are installed

## Production Deployment

For production deployment:
1. Use environment variables instead of `.env` file
2. Enable HTTPS with nginx (included in docker-compose.yml)
3. Set `FLASK_ENV=production`
4. Configure proper logging and monitoring
5. Set up regular database backups

---

**Your XOFlowers AI Agent is ready to revolutionize customer service! 🌸🤖**
