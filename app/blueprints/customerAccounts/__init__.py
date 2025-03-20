
from flask import Blueprint

customer_accounts_bp = Blueprint('customer_accounts_bp', __name__)

from . import routes