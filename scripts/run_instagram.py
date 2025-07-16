#!/usr/bin/env python3
"""
XOFlowers Instagram Bot Runner
Runs the Instagram bot with webhook server
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from the correct path
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def run_instagram_bot():
    """Run the Instagram bot with Flask server"""
    try:
        print("🌸 XOFlowers Instagram Bot Starting...")
        print("📸 Platform: Instagram")
        print("🤖 AI Models: OpenAI + Gemini")
        print("🌐 Server: Flask (Webhook)")
        print("🔗 Port: 5001")
        print("-" * 50)
        
        from api.instagram_app import XOFlowersInstagramBot
        
        bot = XOFlowersInstagramBot()
        
        print("✅ Instagram bot initialized successfully")
        print("🔄 Starting Flask server...")
        print("🎯 Webhook ready at: http://localhost:5001/webhook")
        print("💡 Remember to:")
        print("   1. Start ngrok: ngrok http 5001")
        print("   2. Configure webhook in Meta Developer Console")
        print("   3. Test with: curl http://localhost:5001/health")
        
        # Run the Flask app
        port = int(os.getenv('WEBHOOK_PORT', 5001))
        bot.run(port=port)
        
    except KeyboardInterrupt:
        print("\n👋 Instagram bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting Instagram bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_instagram_bot()