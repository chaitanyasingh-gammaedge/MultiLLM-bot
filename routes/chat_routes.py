from flask import Blueprint, request, jsonify, current_app
from vectorstore import VectorStore
from llm_clients import (
    call_openai, call_gemini, call_claude, call_hf, call_ollama, call_mistral
)
import asyncio
import os

chat_bp = Blueprint("chat", __name__)

# In-memory chats: { chat_id: { model_key: str, messages: [ {role, content} ] } }
_chats = {}
_next_chat_id = 1

# Cached VectorStore
_vs = None


def get_vs():
    """Lazy initialize VectorStore if files exist, else return None."""
    global _vs
    cfg = current_app.config
    index_exists = os.path.exists(cfg["FAISS_INDEX_PATH"])
    store_exists = os.path.exists(cfg["DOC_STORE_PATH"])

    if not (index_exists and store_exists):
        # No documents uploaded yet
        _vs = None
        return None

    if _vs is None:
        try:
            _vs = VectorStore(cfg["EMBEDDING_MODEL"], cfg["FAISS_INDEX_PATH"], cfg["DOC_STORE_PATH"])
        except Exception as e:
            current_app.logger.error(f"Failed to load VectorStore: {e}")
            _vs = None
    return _vs


def build_prompt(user_text, docs):
    """
    Build the system prompt:
    - If docs exist → include them and require answers from them.
    - If no docs → answer using general knowledge.
    """
    if docs:
        context = "\n\n".join([f"- {d['text']}" for d in docs])
        return (
            "System: You are a helpful assistant that must only answer "
            "using the provided document context below. "
            "If the context doesn’t contain the answer, say: "
            "'I don’t have enough information from the uploaded documents to answer that.'\n\n"
            f"Context:\n{context}\n\n"
            f"User: {user_text}\n\nAssistant:"
        )
    else:
        return (
            "System: You are a helpful assistant. No external documents are provided. "
            "Answer normally using your own knowledge.\n\n"
            f"User: {user_text}\n\nAssistant:"
        )


@chat_bp.route("/start", methods=["POST"])
def start_chat():
    """Start a new chat session."""
    global _next_chat_id
    payload = request.json or {}
    model_key = payload.get("model_key", "openai-gpt")
    title = payload.get("title", "New Chat")

    chat_id = _next_chat_id
    _next_chat_id += 1

    _chats[chat_id] = {"model_key": model_key, "title": title, "messages": []}

    return jsonify({"chat_id": chat_id, "model_key": model_key, "title": title})


@chat_bp.route("/<int:chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    """Fetch message history for a chat."""
    chat = _chats.get(chat_id)
    if chat is None:
        return jsonify({"error": "chat not found"}), 404
    return jsonify({"chat_id": chat_id, "messages": chat["messages"]})


@chat_bp.route("/<int:chat_id>/send", methods=["POST"])
def send_message(chat_id):
    """Send user message and get model response (optionally RAG-powered)."""
    data = request.json or {}
    user_text = data.get("text", "").strip()
    if not user_text:
        return jsonify({"error": "text is required"}), 400

    chat = _chats.get(chat_id)
    if chat is None:
        return jsonify({"error": "chat not found"}), 404

    chat["messages"].append({"role": "user", "content": user_text})

    # --- Load VectorStore if available ---
    vs = get_vs()

    # Case 1️⃣: No VectorStore (no doc uploaded at all)
    if vs is None or (hasattr(vs, "index") and vs.index.ntotal == 0):
        smalltalk = ["hi", "hello", "hey", "good morning", "good evening", "how are you", "what's up"]
        text_lower = user_text.lower().strip()

        if any(phrase in text_lower for phrase in smalltalk):
            assistant_text = "Hello! I'm here and ready to chat. How can I help you today?"
        else:
            assistant_text = (
                "I don’t have any reference documents uploaded yet , "
                "so I don’t have enough knowledge to answer that. "
                "Please upload a document so I can assist better!"
            )

        chat["messages"].append({"role": "assistant", "content": assistant_text})
        return jsonify({"assistant": assistant_text, "docs_used": False})

    # Case 2️⃣: RAG available, perform similarity search
    try:
        docs = vs.query(user_text, top_k=4)
        if not docs:
            # No similar chunks found → behave like "no info"
            assistant_text = (
                "I looked through the uploaded documents, but couldn't find relevant information. "
                "Please provide more context or upload another reference document."
            )
            chat["messages"].append({"role": "assistant", "content": assistant_text})
            return jsonify({"assistant": assistant_text, "docs_used": True})
    except Exception as e:
        current_app.logger.error(f"VectorStore query failed: {e}")
        assistant_text = "There was an issue accessing your document database. Please re-upload it."
        chat["messages"].append({"role": "assistant", "content": assistant_text})
        return jsonify({"assistant": assistant_text, "docs_used": False})

    # Case 3️⃣: Valid docs found — build RAG prompt and call LLM
    model_key = chat["model_key"]
    prompt = build_prompt(user_text, docs)

    llm_map = {
        "openai-gpt": call_openai,
        "gemini": call_gemini,
        "claude": call_claude,
        "hf": call_hf,
        "ollama": call_ollama,
        "mistral": call_mistral
    }
    llm_func = llm_map.get(model_key, call_openai)

    assistant_text = asyncio.run(llm_func(prompt))
    chat["messages"].append({"role": "assistant", "content": assistant_text})

    return jsonify({"assistant": assistant_text, "docs_used": True})
