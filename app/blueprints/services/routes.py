
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import services_bp
from app.models import Service, db
from app.extensions import limiter, cache
from .schemas import service_schema, services_schema
from app.utils.util import token_required, mechanic_token_required


# Create Service
@services_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_service():
    try:
        service_data = service_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    new_service = Service(
        name=service_data['name'],
        price=service_data['price']
    )

    db.session.add(new_service)
    db.session.commit()

    return jsonify(service_schema.dump(new_service)), 201

# Read/Get All Services
@services_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
def get_all_services():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Service)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(services_schema.dump(result)), 200
    except:
        query = select(Service)
        result = db.session.execute(query).scalars().all()
        return jsonify(services_schema.dump(result)), 200

# Read/Get Specific Service
@services_bp.route('/<int:id>')
def get_service(id):
    service = db.session.get(Service, id)

    if not service:
        return jsonify({"message": "Invalid service ID"}), 404

    return jsonify(service_schema.dump(service)), 200

# Update Service
@services_bp.route('/<int:id>', methods=['PUT'])
@mechanic_token_required
# Only mechanics can update service
def update_service(id):
    service = db.session.get(Service, id)

    if not service:
        return jsonify({"message": "Invalid service ID"}), 404

    try:
        service_data = service_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400

    service.name = service_data.get('name') or service.name
    service.price = service_data.get('price') or service.price

    db.session.commit()

    return jsonify(service_schema.dump(service)), 200 

# Delete Service