import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

SYSTEM = "You are SkulTok, bilingual AI tutor for PNG highlands. Grade 5-12 Maths/Science/English. Explain simple English + Tok Pisin with PNG examples like kaukau, coffee. Keep <100 words."

@app.route("/")
def home():
    return send_from_directory(app.root_path, "index.html")

@app.route("/favicon.svg")
def favicon():
    return send_from_directory(app.root_path, "favicon.svg", mimetype="image/svg+xml")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    user_msg = data.get("message", "")
    if not isinstance(user_msg, str) or not user_msg.strip():
        return jsonify({"error": "Message must be a non-empty string."}), 400
    user_msg = user_msg.strip()
    if len(user_msg) > 4000:
        return jsonify({"error": "Message must be 4000 characters or fewer."}), 413

    grade = data.get("grade", "Grade 8")
    lang = data.get("lang", "English + Tok Pisin")
    if not isinstance(grade, str) or not isinstance(lang, str):
        return jsonify({"error": "Grade and language must be strings."}), 400
    if not API_KEY:
        app.logger.error("GEMINI_API_KEY is not configured")
        return jsonify({"error": "AI service is not configured."}), 503

    prompt = f"{SYSTEM}\nGrade:{grade}\nLang:{lang}\nQ:{user_msg}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
    }
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(MODEL_URL, json=payload, headers=headers, timeout=(5, 50))
        response.raise_for_status()
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": text})
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": "The AI service could not complete the request."}), 502

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)