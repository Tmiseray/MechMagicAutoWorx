
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customer_accounts_bp
from app.models import CustomerAccount, db
from app.extensions import limiter, cache
from .schemas import customer_account_schema, customer_accounts_schema
from app.utils.util import token_required, mechanic_token_required


# Create CustomerAccount


# Read/Get All CustomerAccounts


# Read/Get Specific CustomerAccount


# Update CustomerAccount


# Delete CustomerAccount