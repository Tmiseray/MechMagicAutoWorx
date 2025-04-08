
from flask import Flask
from .models import db
from .extensions import ma, limiter, cache
from .blueprints.customerAccounts import customer_accounts_bp
from .blueprints.customers import customers_bp
from .blueprints.inventory import inventory_bp
from .blueprints.invoices import invoices_bp
from .blueprints.mechanicAccounts import mechanic_accounts_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.mechanicTickets import mechanic_tickets_bp
from .blueprints.serviceItems import service_items_bp
from .blueprints.services import services_bp
from .blueprints.serviceTickets import service_tickets_bp
from .blueprints.vehicles import vehicles_bp
from flask_swagger_ui import get_swaggerui_blueprint
from .utils.swagger_merge import combine_swagger_docs

# Swagger UI setup
SWAGGER_URL = '/api/docs'
API_URL = '/static/combined_swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "MechMagic AutoWorx API"
    }
)


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Load the combined Swagger documentation
    combine_swagger_docs()

    # Database initialization
    db.init_app(app)

    # Extensions initialization
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Registering our blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(customer_accounts_bp, url_prefix='/customers/accounts')
    app.register_blueprint(vehicles_bp, url_prefix='/customers/vehicles')
    app.register_blueprint(service_tickets_bp, url_prefix='/customers/tickets')
    app.register_blueprint(invoices_bp, url_prefix='/customers/tickets/invoices')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(mechanic_accounts_bp, url_prefix='/mechanics/accounts')
    app.register_blueprint(mechanic_tickets_bp, url_prefix='/mechanics/tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(service_items_bp, url_prefix='/inventory/items')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app