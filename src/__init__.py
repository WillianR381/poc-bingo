from flask import Flask, request, jsonify
from src.routes.bookmarks import bookmarks

from .extensions import db, migrate
 
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(bookmarks)

    return app
