Quick setup (Ubuntu + VSCode)
1. Open project in VSCode.
2. Create virtualenv: python3 -m venv .venv && source .venv/bin/activate
3. pip install -r requirements.txt
4. Install MySQL and create DB: sudo apt install mysql-server; mysql -u root -p
   CREATE DATABASE multi_llm_chat; CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'db_password'; GRANT ALL ON multi_llm_chat.* TO 'db_user'@'localhost';
5. Configure .env
6. Initialize DB: flask --app manage.py init-db
7. Run: flask run

How to add provider implementation:
- Replace stub functions in llm_clients.py with real SDK or HTTP calls.
- Handle streaming responses if desired.

Frontend suggestion (quick):
- A single-page React app where the landing page lists models (GET /api/models/list).
- On click, POST /api/chat/start to create chat for that model, then open chat UI connected to /api/chat/<id>/send.
- Save chat_id in local state and fetch messages periodically or via websockets.

Enhancements & next steps:
- Add user auth (JWT) and per-user chat history.
- Add streaming (SSE / websockets) for assistant tokens.
- Add multi-document upload & chunking to vectorstore.
- Add admin panel to register new LLM keys, configure models and pricing.
- Add usage & cost tracking per provider.
