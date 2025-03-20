
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from app.models import Mechanic, db
from app.extensions import limiter, cache
from .schemas import mechanic_schema, mechanics_schema
from app.utils.util import encode_mechanic_token, mechanic_token_required


# Create Mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("3 per hour")
# Limit the number of mechanic creations to 3 per hour
# There shouldn't be a need to create more than 3 mechanics per hour
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanic(
        name=mechanic_data['name'],
        email=mechanic_data['email'],
        phone=mechanic_data['phone'],
        salary=mechanic_data['salary']
    )

    db.session.add(new_mechanic)
    db.session.commit()

    return jsonify(mechanic_schema.dump(new_mechanic)), 201


# Get all mechanics
@mechanics_bp.route('/', methods=['GET'])
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve all mechanics more than 10 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
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
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a single mechanic more than 10 per hour
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    return jsonify(mechanic_schema.dump(mechanic)), 200


# Update a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@mechanic_token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    mechanic.name = mechanic_data.get('name') or mechanic.name
    mechanic.email = mechanic_data.get('email') or mechanic.email
    mechanic.phone = mechanic_data.get('phone') or mechanic.phone
    mechanic.salary = mechanic_data.get('salary') or mechanic.salary

    db.session.commit()

    return jsonify(mechanic_schema.dump(mechanic)), 200


# Delete a mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"message": "Invalid mechanic ID"}), 404

    # Set mechanic_id to NULL for related service mechanics
    for service_mechanic in mechanic.mechanic_tickets:
        service_mechanic.mechanic_id = None

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": "Mechanic deleted"}), 200


# Top Earners
@mechanics_bp.route('/top_earners', methods=['GET'])
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve the top earners more
# than 10 times per hour
def get_top_earners():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda m: len(m.mechanic_tickets), reverse=True)
    return jsonify(mechanics_schema.dump(mechanics)), 200