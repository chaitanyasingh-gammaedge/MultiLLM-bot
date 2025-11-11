from flask import Flask, send_from_directory
from config import Config
from routes.chat_routes import chat_bp
from routes.model_routes import model_bp
import os
from routes.rag_routes import rag_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(model_bp, url_prefix='/api/models')
    app.register_blueprint(rag_bp, url_prefix="/api/rag")

    @app.route('/')
    def index():
        static_dir = os.path.join(app.root_path, 'static')
        return send_from_directory(static_dir, 'index.html')

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5000, debug=True)
