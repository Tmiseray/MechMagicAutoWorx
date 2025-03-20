
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import inventory_bp
from app.models import Inventory, db
from app.extensions import limiter, cache
from .schemas import inventory_schema, inventories_schema
from app.utils.util import token_required, mechanic_token_required


# Create Inventory


# Read/Get All Inventories


# Read/Get Specific Inventory


# Update Inventory


# Delete Inventory