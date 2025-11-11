Quick setup (Ubuntu + VSCode)
1. Open project in VSCode.
2. Create virtualenv: python3 -m venv .venv && source .venv/bin/activate
3. pip install -r requirements.txt
4. Install MySQL and create DB: sudo apt install mysql-server; mysql -u root -p
   CREATE DATABASE multi_llm_chat; CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'db_password'; GRANT ALL ON multi_llm_chat.* TO 'db_user'@'localhost';
5. Configure .env
6. Initialize DB: flask --app manage.py init-db
7. Run: flask run

# 🧠 Multi-LLM RAG Chatbot Backend

A **Retrieval-Augmented Generation (RAG)** powered chatbot built with **Flask**, designed to integrate and switch between multiple **Large Language Models (LLMs)** like **OpenAI GPT**, **Gemini**, **Claude**, **Mistral**, **Ollama**, and **Hugging Face**.

It supports **document uploads**, **semantic search** using **FAISS vector storage**, and dynamic context injection for grounded, reference-based answers.


## 🚀 Features

✅ Multi-LLM Support (OpenAI, Gemini, Claude, Mistral, Ollama, HuggingFace)  
✅ Retrieval-Augmented Generation (RAG)  
✅ FAISS Vector Search for semantic similarity  
✅ SentenceTransformer embeddings  
✅ Flask REST API backend  
✅ Document upload & context-based question answering  
✅ Small-talk fallback (no document mode)  
✅ Async LLM calls for performance  
✅ Modular code structure


## ⚙️ Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Framework** | Flask |
| **Vector Store** | FAISS |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Datastore** | Pickle + FAISS index |
| **Language Models** | OpenAI GPT, Gemini, Claude, Mistral, Ollama, Hugging Face |
| **Environment Management** | pyenv + venv |
| **Async Calls** | asyncio |

---

## 🧩 RAG (Retrieval-Augmented Generation) Flow

1. **Document Upload**
   - The document is split into text chunks.
   - Each chunk is embedded using SentenceTransformers.
   - Embeddings are stored in FAISS and mapped to text via a doc_store (pickle).

2. **Query Phase**
   - User sends a question.
   - Query embedding is computed and compared to document embeddings via FAISS.
   - Top-k similar chunks are retrieved.
   - These chunks form the **context** in the LLM prompt.

3. **Response Generation**
   - Context is inserted into the LLM prompt.
   - Selected model (OpenAI, Gemini, etc.) generates the final answer.

4. **No-Document Mode**
   - If no documents are uploaded:
     - Small-talk queries (“hi”, “hello”, etc.) → friendly responses.
     - Factual queries → polite message asking user to upload a document.

---

## 🧠 API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/api/chat/start` | POST | Start a new chat session |
| `/api/chat/<chat_id>/send` | POST | Send message to model (RAG enabled if docs exist) |
| `/api/chat/<chat_id>/messages` | GET | Fetch chat history |
| `/api/docs/upload` | POST | Upload new document (PDF/TXT) |
| `/api/models/list` | GET | List available LLMs |

---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/chaitanyasingh-gammaedge/Multi-LLM-RAG-chatbot.git
cd multi-llm-chat-backend


Enhancements & next steps:
- Add user auth (JWT) and per-user chat history.
- Add streaming (SSE / websockets) for assistant tokens.
- Add multi-document upload & chunking to vectorstore.
- Add admin panel to register new LLM keys, configure models and pricing.
- Add usage & cost tracking per provider.
