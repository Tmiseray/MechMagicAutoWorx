
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import vehicles_bp
from app.models import Vehicle, db
from app.extensions import limiter, cache
from .schemas import vehicle_schema, vehicles_schema
from app.utils.util import token_required, mechanic_token_required


# Create Vehicle


# Read/Get All Vehicles


# Read/Get Specific Vehicle


# Update Vehicle


# Delete Vehicle