
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import vehicles_bp
from app.models import Vehicle, db, Customer
from app.extensions import limiter, cache
from .schemas import vehicle_schema, vehicles_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_foreign_key, validate_and_update


# Create Vehicle
@vehicles_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_vehicle():
    payload = request.json

    try:
        validate_foreign_key(Customer, payload.get('customer_id'), "Customer ID")
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    
    return validate_and_create(
        model=Vehicle,
        payload=payload,
        schema=vehicle_schema,
        unique_fields=['VIN'],
        case_insensitive_fields=['VIN'],
        commit=True,
        return_json=True
    )


# Read/Get All Vehicles
@vehicles_bp.route('/all', methods=['GET'])
# @cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all vehicles
def get_all_vehicles():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Vehicle)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(vehicles_schema.dump(result)), 200
    except:
        query = select(Vehicle)
        result = db.session.execute(query).scalars().all()
        return jsonify(vehicles_schema.dump(result)), 200


# Read/Get Specific Vehicle
@vehicles_bp.route('/<VIN>')
# @mechanic_token_required
# Only mechanics can retrieve a single vehicle
def get_vehicles(VIN):
    vehicle = db.session.get(Vehicle, VIN)

    if not vehicle:
        return jsonify({"message": "Invalid vehicle ID"}), 404

    return jsonify(vehicle_schema.dump(vehicle)), 200


# Update Vehicle
@vehicles_bp.route('/<VIN>', methods=['PUT'])
# @mechanic_token_required
# Only mechanics can update vehicle
def update_vehicle(VIN):
    vehicle = db.session.get(Vehicle, VIN)
    if not vehicle:
        return jsonify({"message": "Vehicle not found"}), 404

    payload = request.json

    # Validate foreign key (customer_id)
    fk_checks = [(Customer, payload.get("customer_id"))] if "customer_id" in payload else []
    fk_error = validate_foreign_key(fk_checks)
    if fk_error:
        return fk_error

    # Proceed with update
    success, response, status_code = validate_and_update(
        instance=vehicle,
        schema=vehicle_schema,
        payload=payload
    )
    return response, status_code

# Delete Vehicle
'''
Preserving Vehicle history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''