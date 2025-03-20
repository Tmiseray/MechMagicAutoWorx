
from flask import Blueprint

mechanic_tickets_bp = Blueprint('mechanic_tickets_bp', __name__)

from . import routes