
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import invoices_bp
from app.models import Invoice, db
from app.extensions import limiter, cache
from .schemas import invoice_schema, invoices_schema
from app.utils.util import token_required, mechanic_token_required


# Create Invoice


# Read/Get All Invoices


# Read/Get Specific Invoice


# Update Invoice


# Delete Invoice