import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.items import items_bp
    from routes.trades import trades_bp
    from routes.profile import profile_bp
    from routes.messages import messages_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        _seed_categories()

    return app


def _seed_categories():
    from models import Category
    if Category.query.count() == 0:
        cats = [
            ('Electronics', 'fa-microchip', 'Gadgets, phones, computers'),
            ('Clothing & Fashion', 'fa-shirt', 'Apparel, shoes, accessories'),
            ('Books & Media', 'fa-book', 'Books, music, movies, games'),
            ('Tools & Hardware', 'fa-wrench', 'Hand tools, power tools, equipment'),
            ('Sports & Outdoors', 'fa-person-running', 'Sporting goods, outdoor gear'),
            ('Art & Collectibles', 'fa-palette', 'Artwork, antiques, collectibles'),
            ('Home & Garden', 'fa-house', 'Furniture, decor, garden'),
            ('Toys & Games', 'fa-puzzle-piece', 'Toys, board games, puzzles'),
            ('Vehicles & Parts', 'fa-car', 'Cars, bikes, auto parts'),
            ('Food & Beverages', 'fa-utensils', 'Homemade goods, specialty foods'),
            ('Jewelry & Watches', 'fa-gem', 'Fine jewelry, watches, gems'),
            ('Musical Instruments', 'fa-guitar', 'Instruments, audio equipment'),
            ('Health & Beauty', 'fa-heart-pulse', 'Wellness, skincare, fitness'),
            ('Services', 'fa-handshake', 'Skills, labor, freelance services'),
            ('Other', 'fa-box', 'Miscellaneous items'),
        ]
        for name, icon, desc in cats:
            db.session.add(Category(name=name, icon=icon, description=desc))
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
