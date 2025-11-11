from flask import Blueprint, jsonify

model_bp = Blueprint("models", __name__)

@model_bp.route("/list", methods=["GET"])
def list_models():
    """
    Returns a list of available model providers for the frontend dropdown.
    """
    models = [
        {"key": "mistral", "name": "Mistral (API)"},
        {"key": "ollama", "name": "Ollama (Local)"},
        {"key": "hf", "name": "Hugging Face"},
        {"key": "openai-gpt", "name": "OpenAI (Stub)"},
        {"key": "google-gemini", "name": "Gemini (Stub)"},
        {"key": "anthropic-claude", "name": "Claude (Stub)"}
    ]
    return jsonify(models)
