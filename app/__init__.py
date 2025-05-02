
from flask import Flask
import shutil
import subprocess

from .models import db
from .extensions import ma, limiter, cache
from .blueprints.docs import docs_bp
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
# from .utils.swagger_merge import combine_swagger_docs
from .utils.openapi_merge import combine_openapi_docs

# Swagger UI setup
SWAGGER_URL = '/api/docs'
# API_URL = '/static/combined_docs.yaml'
API_URL = '/static/cleaned_openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "MechMagic AutoWorx API"
    }
)

def bundle_openapi():
    """Bundle modular OpenAPI docs using Redocly CLI, with graceful fallback."""
    redocly_path = shutil.which("redocly")

    if redocly_path:
        try:
            subprocess.run(
                [redocly_path, "bundle", "app/static/openapi.yaml", "-o", "app/static/cleaned_openapi.yaml"],
                check=True
            )
            print("✅ OpenAPI docs bundled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Redocly failed to bundle OpenAPI docs: {e}")
    else:
        print("⚠️ Redocly CLI not found — skipping OpenAPI bundling. "
              "Install with: npm install -g @redocly/cli")


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Bundle OpenAPI docs
    if app.config.get("OPENAPI_AUTOBUNDLE"):
        bundle_openapi()

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
    app.register_blueprint(docs_bp)

    return app