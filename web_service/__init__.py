from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import DevelopmentConfig, ProductionConfig
from .routes import main_routes

config_class = DevelopmentConfig
#config_class = ProductionConfig

def create_app(environ=None, start_response=None, config_class=config_class):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.from_object(config_class)
    app.register_blueprint(main_routes)
    return app
