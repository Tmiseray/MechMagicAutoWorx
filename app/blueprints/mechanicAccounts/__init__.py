
from flask import Blueprint

mechanic_accounts_bp = Blueprint('mechanic_accounts_bp', __name__)

from . import routes