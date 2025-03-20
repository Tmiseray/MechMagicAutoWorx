
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import services_bp
from app.models import Service, db
from app.extensions import limiter, cache
from .schemas import service_schema, services_schema
from app.utils.util import token_required, mechanic_token_required


# Create Service


# Read/Get All Services


# Read/Get Specific Service


# Update Service


# Delete Service