
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
        VIN=vehicle_data['VIN'],
        year=vehicle_data['year'],
        make=vehicle_data['make'],
        model=vehicle_data['model'],
        mileage=vehicle_data['mileage'],
        customer_id=vehicle_data['customer_id']
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify(vehicle_schema.dump(new_vehicle)), 201


# Read/Get All Vehicles
@vehicles_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
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
@vehicles_bp.route('/<str:VIN>')
@mechanic_token_required
# Only mechanics can retrieve a single vehicle
def get_vehicles(VIN):
    vehicle = db.session.get(Vehicle, VIN)

    if not vehicle:
        return jsonify({"message": "Invalid vehicle ID"}), 404

    return jsonify(vehicles_schema.dump(vehicle)), 200


# Update Vehicle
@vehicles_bp.route('/<int:id>', methods=['PUT'])
@mechanic_token_required
# Only mechanics can update vehicle
def update_vehicle(VIN):
    vehicle = db.session.get(Vehicle, VIN)

    if not vehicle:
        return jsonify({"message": "Invalid VIN"}), 404

    try:
        vehicle_data = vehicle_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400

    vehicle.VIN = vehicle_data.get('VIN') or vehicle.VIN
    vehicle.year = vehicle_data.get('year') or vehicle.year
    vehicle.make = vehicle_data.get('make') or vehicle.make
    vehicle.model = vehicle_data.get('model') or vehicle.model
    vehicle.mileage = vehicle_data.get('mileage') or vehicle.mileage
    vehicle.customer_id = vehicle_data.get('customer_id') or vehicle.customer_id

    db.session.commit()

    return jsonify(vehicle_schema.dump(vehicle)), 200 

# Delete Vehicle