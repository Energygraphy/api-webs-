from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv  # Import dotenv for loading environment variables
import os  # Import os module to access environment variables

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for your website
CORS(app, resources={
    r"/api/chat": {
        "origins": [os.getenv("HTTP_REFERER", "https://larinst.org"), "http://larinst.org"],  # Use HTTP_REFERER from .env
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Get API Key and other variables from environment variables
API_KEY = os.getenv("API_KEY")  # API Key from .env
if not API_KEY:
    raise ValueError("API_KEY is not set in the .env file")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('prompt')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    headers = {
        "Authorization": f"Bearer {API_KEY}",  # Use API_KEY from .env
        "HTTP-Referer": os.getenv("HTTP_REFERER", "https://larinst.org/lar-ai/"),  # Use HTTP_REFERER from .env
        "X-Title": os.getenv("X_TITLE", "LAR AI"),  # Use X_TITLE from .env
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": user_input},
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return jsonify({"response": ai_response})
        else:
            error_details = response.json().get("error", {}).get("message", "Unknown error")
            print(f"Error from OpenRouter API: {error_details}")
            return jsonify({"error": "Failed to get a response from AI"}), 500
    except Exception as e:
        print(f"Internal Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=int(os.getenv("PORT", 5000)))  # Use PORT from .env or default to 5000