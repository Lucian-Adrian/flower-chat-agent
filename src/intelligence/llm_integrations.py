"""
LLM Integrations for XOFlowers Conversational AI
This module provides a unified interface for interacting with different
Large Language Models (LLMs) like OpenAI's GPT and Google's Gemini.
"""

import os
import logging
from typing import List, Dict, Any
import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

class LLMClient:
    """
    A client for interacting with a Large Language Model.
    """
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generates a response from the LLM.

        Args:
            messages: A list of messages in the conversation history.

        Returns:
            The generated response text.
        """
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """
    LLMClient implementation for OpenAI's GPT models.
    """
    def __init__(self, api_key: str, model: str = "gpt-4"):
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        self.api_key = api_key
        self.model = model

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1500,
            "temperature": 0.7,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENAI_API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error: {response.status} {error_text}")
                    raise Exception("Failed to get response from OpenAI.")


class GeminiClient(LLMClient):
    """
    LLMClient implementation for Google's Gemini models.
    """
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        if not api_key:
            raise ValueError("Gemini API key is required.")
        self.api_key = api_key
        self.model = model

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Gemini has a different message format, so we need to adapt it
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        # The last message should not be from the model
        if gemini_contents[-1]["role"] == "model":
            gemini_contents.pop()
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1500,
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error: {response.status} {error_text}")
                    raise Exception("Failed to get response from Gemini.")


def get_llm_client() -> LLMClient:
    """
    Factory function to get the preferred LLM client based on available API keys.
    It prioritizes OpenAI.
    """
    if OPENAI_API_KEY:
        logger.info("Using OpenAI GPT-4 as the LLM.")
        return OpenAIClient(api_key=OPENAI_API_KEY)
    elif GEMINI_API_KEY:
        logger.info("Using Google Gemini Pro as the LLM.")
        return GeminiClient(api_key=GEMINI_API_KEY)
    else:
        raise ValueError("No LLM API key found. Please set OPENAI_API_KEY or GEMINI_API_KEY.")

