
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from app.models import Mechanic, db
from app.extensions import limiter, cache
from .schemas import mechanic_schema, mechanics_schema
from app.utils.util import encode_mechanic_token, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update


# Create Mechanic
@mechanics_bp.route('/', methods=['POST'])
# @limiter.limit("3 per hour")
# # Limit the number of mechanic creations to 3 per hour
# # There shouldn't be a need to create more than 3 mechanics per hour
def create_mechanic():
    return validate_and_create(
        model=Mechanic,
        payload=request.json,
        schema=mechanic_schema,
        unique_fields=['email'],
        case_insensitive_fields=['email'],
        commit=True,
        return_json=True
    )


# Get all mechanics
@mechanics_bp.route('/all', methods=['GET'])
# @limiter.limit("10 per hour")
# # Limit the number of retrievals to 10 per hour
# # There shouldn't be a need to retrieve all mechanics more than 10 per hour
# @cache.cached(timeout=60)
# # Cache the response for 60 seconds
# # This will help reduce the load on the database
def get_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Mechanic)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(mechanics_schema.dump(result)), 200
    except:
        query = select(Mechanic)
        result = db.session.execute(query).scalars().all()
        return jsonify(mechanics_schema.dump(result)), 200


# Get single mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
# @mechanics_bp.route('/', methods=['GET'])
# @limiter.limit("10 per hour")
# # Limit the number of retrievals to 10 per hour
# # There shouldn't be a need to retrieve a single mechanic more than 10 per hour
# @mechanic_token_required
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    return jsonify(mechanic_schema.dump(mechanic)), 200


# Update a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
# @mechanics_bp.route('/', methods=['PUT'])
# @mechanic_token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    payload = request.json

    # Use generic validation & update logic
    success, response, status_code = validate_and_update(
        instance=mechanic,
        schema=mechanic_schema,
        payload=payload,
        foreign_keys={},
        return_json=True
    )
    return response, status_code


# Delete a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
# @mechanics_bp.route('/', methods=['DELETE'])
# @mechanic_token_required
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    # Set mechanic_id to NULL for related service mechanics
    for mt in mechanic.mechanic_tickets:
        mt.mechanic_id = None

    # Delete the associated mechanic account if exists
    if mechanic.account:
        db.session.delete(mechanic.account)

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": "Mechanic deleted"}), 200


# Top Mechanics
@mechanics_bp.route('/top-mechanics', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve the top mechanics more
# than 10 times per hour
def get_top_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda m: len(m.mechanic_tickets), reverse=True)
    return jsonify(mechanics_schema.dump(mechanics)), 200