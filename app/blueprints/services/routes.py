
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import services_bp
from app.models import Service, db, ServiceItem
from app.extensions import limiter, cache
from .schemas import service_schema, services_schema
from app.blueprints.serviceItems.schemas import service_item_schema
from app.utils.util import mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update


# Create Service
@services_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_service():
    payload = request.json.copy()
    service_items_payload = payload.pop("service_items", [])

    new_service = validate_and_create(
        model=Service,
        payload=payload,
        schema=service_schema,
        commit=False
    )

    for item in service_items_payload:
        if "item_id" not in item or "quantity" not in item:
            return jsonify({"message": "Each additional item must include 'item_id' and 'quantity'."}), 400
        si_payload = {
            "item_id": item["item_id"],
            "quantity": item["quantity"],
            "service_id": None
        }
        service_item = validate_and_create(
            model=ServiceItem,
            payload=si_payload,
            schema=service_item_schema,
            commit=False
        )
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

    payload = request.json.copy()
    service_items_payload = payload.pop("service_items", None)

    success, response, status_code = validate_and_update(
        instance=service,
        schema=service_schema,
        payload=payload,
        foreign_keys={},
        return_json=False
    )
    if not success:
        return response, status_code

    # Handle service_items update
    if service_items_payload is not None:
        service.service_items.clear()
        for item in service_items_payload:
            if "item_id" not in item or "quantity" not in item:
                return jsonify({"message": "Each additional item must include 'item_id' and 'quantity'."}), 400
            si_payload = {
                "item_id": item["item_id"],
                "quantity": item["quantity"],
                "service_id": service.id
            }
            service_item, _ = validate_and_create(
                model=ServiceItem,
                payload=si_payload,
                schema=service_item_schema,
                commit=False
            )
            service.service_items.append(service_item)

    db.session.commit()
    return jsonify(service_schema.dump(service)), 200

# Delete Service
'''
Preserving Service history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''