
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import services_bp
from app.models import Service, db, ServiceItem
from app.extensions import limiter, cache
from .schemas import service_schema, services_schema
from app.blueprints.serviceItems.schemas import service_item_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update, check_and_update_inventory


# Create Service
@services_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_service():
    payload = request.json

    new_service, err = validate_and_create(Service, service_schema, payload, commit=False)
    if err:
        return err

    for item in payload.get("service_items", []):
        item["service_id"] = None  # Prevent invalid FK during creation
        service_item, _ = validate_and_create(ServiceItem, service_item_schema, item, commit=False)
        new_service.service_items.append(service_item)

    db.session.add(new_service)
    db.session.commit()

    return jsonify(service_schema.dump(new_service)), 201

# Read/Get All Services
@services_bp.route('/all', methods=['GET'])
# @cache.cached(timeout=60)
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
# @mechanic_token_required
# Only mechanics can update service
def update_service(id):
    service = db.session.get(Service, id)
    if not service:
        return jsonify({"message": "Invalid Service ID"}), 404

    payload = request.json

    # Begin item usage tracking
    all_uses = []

    # Replace service_items if provided
    if 'service_items' in payload:
        service.service_items = []  # Clear existing
        for item in payload['service_items']:
            all_uses.append({
                "item_id": item["item_id"],
                "quantity": item["quantity"]
            })

    # Validate inventory if needed
    if all_uses:
        success, result = check_and_update_inventory(all_uses)
        if not success:
            return jsonify(result), 409

    # Rebuild service_items if replaced
    if 'service_items' in payload:
        for item in payload['service_items']:
            item["service_id"] = id
            service_item = validate_and_create(
                model=ServiceItem,
                payload=item,
                commit=False
            )
            service.service_items.append(service_item)

    # Apply other field updates
    success, response, status_code = validate_and_update(
        instance=service,
        schema=service_schema,
        payload=payload
    )
    return response, status_code

# Delete Service
'''
Preserving Service history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''