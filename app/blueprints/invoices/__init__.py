
from flask import Blueprint

invoices_bp = Blueprint('invoices_bp', __name__)

from . import routes