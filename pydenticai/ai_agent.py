import os
import requests
from pydantic import BaseModel, field_validator
from typing import List
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# --------------------------
# Pydantic Models
# --------------------------
class EmojiSuggestion(BaseModel):
    emojis: List[str]
    message: str

    @field_validator('emojis')
    @classmethod
    def validate_emojis(cls, v):
        if len(v) < 3:
            raise ValueError("At least 3 emojis required")
        return v[:20]

# --------------------------
# Enhanced Sentiment Analysis
# --------------------------
class SentimentAnalyzer:
    def __init__(self):
        self.emoji_library = {
            'happy': ["😀", "😃", "😄", "😁", "😆", "🥹", "😅", "😂", "🤣", "🥲"],
            'sad': ["😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥺", "😥"],
            'love': ["🥰", "😍", "❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤"],
            'excited': ["🤩", "🥳", "😎", "🤠", "😏", "😸", "😹", "😺", "😻", "😼"],
            'greeting': ["👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤏", "✌️", "🤞", "🤟"],
            'neutral': ["😐", "😑", "😶", "🫥", "😶‍🌫️", "🙄", "😏", "😒", "🤨", "🧐"]
        }
        
        self.sentiment_map = {
            'happy': ["happy", "joy", "good", "great", "awesome"],
            'sad': ["sad", "bad", "upset", "unhappy"],
            'love': ["love", "heart", "adore", "cherish"],
            'excited': ["excited", "wow", "amazing", "thrilled"],
            'greeting': ["hello", "hi", "hey", "greetings"]
        }

    def detect_sentiment(self, message: str) -> str:
        lower_msg = message.lower()
        for sentiment, keywords in self.sentiment_map.items():
            if any(keyword in lower_msg for keyword in keywords):
                return sentiment
        if "?" in message:
            return 'confused'
        return 'neutral'

    def get_emojis(self, sentiment: str) -> List[str]:
        return self.emoji_library.get(sentiment, self.emoji_library['neutral'])

# --------------------------
# Gemini API Client (using gemini-2.0-flash)
# --------------------------
class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={'Content-Type': 'application/json'},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise ValueError(f"API request failed: {str(e)}")

# --------------------------
# AI Agent
# --------------------------
class AIAgent:
    def __init__(self):
        self.gemini = GeminiClient()
        self.sentiment = SentimentAnalyzer()
    
    def suggest_emojis(self, message: str) -> EmojiSuggestion:
        try:
            sentiment = self.sentiment.detect_sentiment(message)
            prompt = f"Suggest 10 emojis for this {sentiment} message: '{message}'. Return only emojis separated by spaces."
            response = self.gemini.generate(prompt)
            emojis = response.strip().split()
            return EmojiSuggestion(emojis=emojis[:15], message=message)
        except Exception as e:
            print(f"Using fallback emojis due to: {str(e)}")
            sentiment = self.sentiment.detect_sentiment(message)
            return EmojiSuggestion(
                emojis=self.sentiment.get_emojis(sentiment),
                message=message
            )

# --------------------------
# CLI Interface
# --------------------------
def main():
    print("\n🌟 Ultimate Emoji Suggester 🌟")
    print("----------------------------")
    print("Enter a message to get emoji suggestions!")
    print("Type 'q' to quit\n")
    
    agent = AIAgent()
    
    while True:
        message = input("Your message: ").strip()
        if message.lower() == 'q':
            print("\nGoodbye! 👋")
            break
        
        if not message:
            print("Please enter a message")
            continue
        
        suggestion = agent.suggest_emojis(message)
        print(f"\nFor: {suggestion.message}")
        print("Emojis:", " ".join(suggestion.emojis))
        print("="*50 + "\n")

if __name__ == "__main__":
    main()