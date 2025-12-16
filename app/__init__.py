from flask import Flask
from app.db import init_db
import os

def create_app():
    app = Flask(__name__)

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        init_db(db_url)

    from app.db import Base, engine
    from app.models import Task
    Base.metadata.create_all(engine)
    
    from app.api import api_bp
    app.register_blueprint(api_bp)

    return app
