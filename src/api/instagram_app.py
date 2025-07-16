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
    from intelligence.conversation_manager import get_conversation_manager
    from security.filters import SecurityFilter
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

        self.conversation_manager = get_conversation_manager()
        self.security_filter = SecurityFilter()
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

            if not self.security_filter.is_safe_message(user_message):
                self._send_message(sender_id, "Vă rog să păstrăm o conversație politicoasă.")
                return

            try:
                # This is an async function, but Flask routes are sync.
                # For a production app, consider using an async framework like FastAPI
                # or running the async code in a separate event loop.
                # For simplicity here, we'll call it directly.
                import asyncio
                response = asyncio.run(self.conversation_manager.handle_message(sender_id, user_message))
                self._send_message(sender_id, response)
                logger.info(f"Response sent to {sender_id}")
            except Exception as e:
                logger.error(f"Error processing message with ConversationManager: {e}")
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
