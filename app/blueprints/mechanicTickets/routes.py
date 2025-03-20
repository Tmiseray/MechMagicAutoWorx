
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_tickets_bp
from app.models import MechanicTicket, db
from app.extensions import limiter, cache
from .schemas import mechanic_ticket_schema, mechanic_tickets_schema
from app.utils.util import mechanic_token_required


# Create MechanicTicket


# Read/Get All MechanicTickets


# Read/Get Specific MechanicTicket


# Update MechanicTicket


# Delete MechanicTicket