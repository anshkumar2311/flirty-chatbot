# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, json

app = Flask(__name__)
CORS(app)

class OllamaChat:
    def __init__(self, model: str = "dolphin3"):
        # IMPORTANT: change this when deploying (your Ollama server URL)
        self.base_url = "http://localhost:11434/api"
        self.model = model
        self.history = []
        self.system_prompt = "You are now roleplaying as a flirty and mischievous girlfriend..."

    def generate_response(self, prompt: str) -> str:
        url = f"{self.base_url}/chat"
        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.history
        messages.append({"role": "user", "content": prompt})

        data = {"model": self.model, "messages": messages, "stream": False}

        try:
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            reply = response.json().get("message", {}).get("content", "")

            if reply:
                self.history.append({"role": "user", "content": prompt})
                if len(self.history) > 10:
                    self.history = self.history[-10:]
                self.history.append({"role": "assistant", "content": reply})

            return reply
        except Exception as e:
            return f"Error: {str(e)}"

chatbot = OllamaChat()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    return jsonify({'response': chatbot.generate_response(data['message'])})

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    chatbot.history = []
    return jsonify({'status': 'Chat history cleared'})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'OK', 'model': 'dolphin3'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
