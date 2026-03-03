from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.stocks import stocks_bp
from routes.orders import orders_bp
from routes.portfolio import portfolio_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')

    @app.route('/')
    def serve_frontend():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
