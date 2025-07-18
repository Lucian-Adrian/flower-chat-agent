#!/usr/bin/env python3
"""
XOFlowers Instagram Bot
Connects to Meta's Graph API to handle Instagram messages
and leverages the new conversational AI system.
"""

import os
import sys
import logging
import hashlib
import hmac
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

# Add path to our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from intelligence.intent_classifier import classify_intent
    from intelligence.llm_client import call_llm
    from security.filters import validate_message_security
    print("All modules imported successfully")
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class XOFlowersInstagramBot:
    """
    The Instagram Bot for XOFlowers, handling webhooks from Meta.
    """

    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN')
        self.verify_token = os.getenv('INSTAGRAM_VERIFY_TOKEN')
        self.app_secret = os.getenv('META_APP_SECRET')

        if not all([self.access_token, self.verify_token, self.app_secret]):
            raise ValueError("Missing required Instagram environment variables.")

        # Using modular approach - no centralized manager needed
        self.app = Flask(__name__)
        self._setup_routes()

        logger.info("XOFlowers Instagram Bot initialized")

    def _setup_routes(self):
        @self.app.route('/webhook', methods=['GET'])
        def verify_webhook():
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("Webhook verified successfully")
                return challenge
            else:
                logger.warning("Webhook verification failed")
                return 'Failed verification', 403

        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            if not self._verify_signature(request.data, request.headers.get('X-Hub-Signature-256')):
                logger.warning("Invalid webhook signature")
                return 'Invalid signature', 403

            data = request.get_json()
            if data.get('object') == 'instagram':
                for entry in data.get('entry', []):
                    for message_event in entry.get('messaging', []):
                        if 'message' in message_event:
                            self._handle_message(message_event)
            return 'OK', 200

        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy'})

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        if not signature:
            return False
        expected_signature = 'sha256=' + hmac.new(
            self.app_secret.encode('utf-8'), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def _handle_message(self, message_event: dict):
        sender_id = message_event['sender']['id']
        message_data = message_event.get('message', {})

        if 'text' in message_data:
            user_message = message_data['text']
            logger.info(f"Message from {sender_id}: {user_message}")

            try:
                # Step 1: Security validation using modular approach
                message_security_data = {
                    "user_id": sender_id,
                    "message_text": user_message,
                    "platform": "instagram"
                }
                security_result = validate_message_security(message_security_data)
                
                if not security_result['is_allowed']:
                    self._send_message(sender_id, "Vă rog să păstrăm o conversație politicoasă.")
                    return

                # Step 2: Intent classification
                intent_result = classify_intent(user_message)
                
                # Step 3: Generate response based on intent
                if intent_result['intent_type'] == 'greeting':
                    response = "🌸 Bună ziua! Bine ați venit la XOFlowers! Cu ce vă pot ajuta astăzi?"
                elif intent_result['intent_type'] == 'product_search':
                    response = "🌸 Înțeleg că căutați flori! Permiteți-mi să vă ajut să găsesc ceva frumos pentru dumneavoastră."
                elif intent_result['intent_type'] == 'question':
                    response = "🌸 Cu plăcere vă răspund la întrebare! Suntem XOFlowers din Chișinău și oferim cele mai frumoase flori."
                else:
                    # Use LLM for complex responses
                    llm_result = call_llm(f"Generate a helpful response for XOFlowers customer who said: {user_message}")
                    if llm_result['success']:
                        response = llm_result['response']
                    else:
                        response = "🌸 Îmi pare rău, am întâmpinat o problemă tehnică. Cu ce vă pot ajuta?"
                
                self._send_message(sender_id, response)
                logger.info(f"Response sent to {sender_id} - Intent: {intent_result['intent_type']}")
                
            except Exception as e:
                logger.error(f"Error processing message with modular approach: {e}")
                self._send_message(sender_id, "Ne pare rău, am întâmpinat o eroare.")

        elif 'attachments' in message_data:
            self._send_message(sender_id, "Momentan pot procesa doar mesaje text.")

    def _send_message(self, recipient_id: str, message_text: str):
        url = f"https://graph.facebook.com/v18.0/me/messages"
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'access_token': self.access_token
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Error sending message: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error calling Instagram API: {e}")

    def run(self, host='0.0.0.0', port=5001):
        logger.info(f"Starting Instagram Bot server on {host}:{port}")
        self.app.run(host=host, port=port)


def main():
    try:
        bot = XOFlowersInstagramBot()
        port = int(os.getenv('WEBHOOK_PORT', 5001))
        bot.run(port=port)
    except (ValueError, KeyboardInterrupt) as e:
        logger.info(f"Bot stopped: {e}")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
