
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_accounts_bp
from app.models import MechanicAccount, db
from app.extensions import limiter, cache
from .schemas import mechanic_account_schema, mechanic_accounts_schema
from app.utils.util import mechanic_token_required


# Create MechanicAccount


# Read/Get All MechanicAccounts


# Read/Get Specific MechanicAccount


# Update MechanicAccount


# Delete MechanicAccount