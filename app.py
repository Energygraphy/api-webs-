from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/api/chat": {
        "origins": [os.getenv("HTTP_REFERER", "https://larinst.org"), "http://larinst.org"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# MongoDB connection
mongo_uri = os.getenv("DBHOST")
if not mongo_uri:
    raise ValueError("DBHOST is not set in the .env file")

client = MongoClient(mongo_uri)
db = client.get_database()  # Gets the database specified in the URI
products_collection = db.products  # 'products' collection from your MongoDB URI

# Get API Key and other variables from environment variables
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is not set in the .env file")

JWT_SECRET = os.getenv("JWT_SECRET", "123")  # Default to "123" if not set
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('prompt')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Optionally store the user input in MongoDB
    try:
        products_collection.insert_one({
            "prompt": user_input,
            "timestamp": import_datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Failed to save to MongoDB: {str(e)}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": os.getenv("HTTP_REFERER", "https://larinst.org/lar-ai/"),
        "X-Title": os.getenv("X_TITLE", "LAR AI"),
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
            
            # Optionally store the response in MongoDB
            products_collection.update_one(
                {"prompt": user_input},
                {"$set": {"response": ai_response}}
            )
            return jsonify({"response": ai_response})
        else:
            error_details = response.json().get("error", {}).get("message", "Unknown error")
            print(f"Error from OpenRouter API: {error_details}")
            return jsonify({"error": "Failed to get a response from AI"}), 500
    except Exception as e:
        print(f"Internal Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))  # Use PORT from env or default to 8080
    app.run(debug=False, host='0.0.0.0', port=port)
