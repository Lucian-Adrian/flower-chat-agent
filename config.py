# Security
RATE_LIMIT_SECONDS = int(os.getenv('RATE_LIMIT_SECONDS', 5))

import os
from dotenv import load_dotenv

load_dotenv()

# Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Telegram
TELEGRAM_TOKEN = "7516410893:AAHp2lDVKZaGY5DdV2_GpS5HwmeJrdPoEKs"

# Instagram
INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN')
INSTAGRAM_WEBHOOK_URL = os.getenv('INSTAGRAM_WEBHOOK_URL')

# Other
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

# Add more as needed
