
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_items_bp
from app.models import ServiceItem, db
from app.extensions import limiter, cache
from .schemas import service_item_schema, service_items_schema
from app.utils.util import token_required, mechanic_token_required


# Create ServiceItem


# Read/Get All ServiceItems


# Read/Get Specific ServiceItem


# Update ServiceItem


# Delete ServiceItem