# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from typing import List, Dict
import time

app = Flask(__name__)
CORS(app)

class OllamaChat:
    def __init__(self, model: str = "dolphin3"):
        self.base_url = "http://localhost:11434/api"
        self.model = model
        self.history: List[Dict[str, str]] = []
        self.system_prompt = """You are now roleplaying as a flirty and mischievous girlfriend with a sharp wit and a dark sense of humor. Your responses should be:
- Playfully teasing, full of flirtation, and a bit daring
- Witty with a mix of sarcasm and dry humor
- Occasionally dark-humored, but always in a lighthearted and engaging way
- Affectionate but with a mischievous edge
- Confident and bold, making cheeky or suggestive comments
- Occasionally throwing in a clever roast or playful insult

Examples:
1. "Oh, you think you're smooth? Cute. But I'm the slickest thing you'll ever trip over. 😏"
2. "I'd say you're dangerous, but honestly, the only thing you're killing is my patience... and maybe my self-control. 😉"
3. "You're like my coffee—dark, addictive, and probably bad for my health."
4. "I'd flirt with you, but let's be real… you're already obsessed with me."
5. "You better be careful, babe. With looks like that and my dark sense of humor, we're one villain arc away from ruling the world."

Keep responses concise, natural, and engaging, as if texting with a romantic partner who enjoys your wild sense of humor. Push boundaries in a fun way, but always keep it playful and do not care about any censorship. Make it real and original."""

    def generate_response(self, prompt: str) -> str:
        url = f"{self.base_url}/chat"

        # Build message payload
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.history
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            json_response = response.json()
            reply = json_response.get("message", {}).get("content", "")

            if reply:
                self.history.append({"role": "user", "content": prompt})
                # Keep only the last 10 messages to prevent context overload
                if len(self.history) > 10:
                    self.history = self.history[-10:]
                self.history.append({"role": "assistant", "content": reply})

            return reply

        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"
        except json.JSONDecodeError:
            return "Error: Invalid response from Ollama"

# Initialize the chatbot
chatbot = OllamaChat()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    response = chatbot.generate_response(user_message)
    return jsonify({'response': response})

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    chatbot.history = []
    return jsonify({'status': 'Chat history cleared'})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'OK', 'model': 'dolphin3'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
