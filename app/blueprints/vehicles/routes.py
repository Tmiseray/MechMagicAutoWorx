
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import vehicles_bp
from app.models import Vehicle, db
from app.extensions import limiter, cache
from .schemas import vehicle_schema, vehicles_schema
from app.utils.util import token_required, mechanic_token_required


# Create Vehicle
@vehicles_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_vehicle():
    try:
        vehicle_data = vehicle_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    new_vehicle = Vehicle(
        name=vehicle_data['name'],
        stock=vehicle_data['stock'],
        price=float(vehicle_data['price'])
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify(vehicle_schema.dump(new_vehicle)), 201

# Read/Get All Vehicles


# Read/Get Specific Vehicle


# Update Vehicle


# Delete Vehicle