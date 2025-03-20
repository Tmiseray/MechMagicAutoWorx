
from flask import Blueprint

service_items_bp = Blueprint('service_items_bp', __name__)

from . import routes