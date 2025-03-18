
from flask import Flask
from .models import db
from .extensions import ma, limiter, cache


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Database initialization
    db.init_app(app)

    # Extensions initialization
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    return app