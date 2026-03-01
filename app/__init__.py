from flask import Flask
import os
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev')

    # Optional MongoDB connection (non-breaking). Set MONGO_URI env to enable.
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    mongo_db_name = os.getenv('MONGO_DB_NAME', 'event_management')
    try:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=500)
        # Trigger a quick ping to fail fast if server unavailable (but do not crash app)
        try:
            mongo_client.admin.command('ping')
        except Exception:
            pass
        app.mongo_client = mongo_client
        app.mongo_db = mongo_client[mongo_db_name]
    except Exception:
        # If Mongo is not available, keep the app running but without Mongo features
        app.mongo_client = None
        app.mongo_db = None

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .routes.user import user_bp
    app.register_blueprint(user_bp)
    from .routes.booking import booking_bp
    app.register_blueprint(booking_bp)
    from .routes.hotel import hotel_bp
    app.register_blueprint(hotel_bp)
    from .routes.vendor import vendor_bp
    app.register_blueprint(vendor_bp)
    from .routes.catering import catering_bp
    app.register_blueprint(catering_bp)
    from .routes.payment import payment_bp
    app.register_blueprint(payment_bp)
    from .routes.receipt import receipt
    app.register_blueprint(receipt)

    return app