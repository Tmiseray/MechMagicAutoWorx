
from flask import Blueprint

vehicles_bp = Blueprint('vehicles_bp', __name__)

from . import routes