
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_items_bp
from app.models import ServiceItem, db, Service
from app.extensions import limiter, cache
from .schemas import service_item_schema, service_items_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_foreign_key, validate_and_update



# Create Service Item
@service_items_bp.route('/', methods=['POST'])
# @mechanic_token_required
# def create_service_item_route(user_id, role):
def create_service_item():
    return validate_and_create(
        model=ServiceItem,
        payload=request.json,
        schema=service_item_schema,
        commit=True,
        return_json=True
    )


# Read/Get All ServiceItems
@service_items_bp.route('/all', methods=['GET'])
# @cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all ServiceItems
def get_all_service_items():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(ServiceItem)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(service_items_schema.dump(result)), 200
    except:
        query = select(ServiceItem)
        result = db.session.execute(query).scalars().all()
        return jsonify(service_items_schema.dump(result)), 200


# Read/Get Specific ServiceItem
@service_items_bp.route('/<int:id>')
# @mechanic_token_required
# Only mechanics can retrieve a single ServiceItem
def get_service_item(id):
    service_item = db.session.get(ServiceItem, id)

    if not service_item:
        return jsonify({"message": "Invalid Service Item ID"}), 404

    return jsonify(service_item_schema.dump(service_item)), 200


# Update ServiceItem
@service_items_bp.route('/<int:id>', methods=['PUT'])
# @mechanic_token_required
# Only mechanics can update ServiceItem
def update_service_item(id):
    service_item = db.session.get(ServiceItem, id)
    if not service_item:
        return jsonify({"message": "Invalid Service Item ID"}), 404

    # Validate foreign key if service_id is present in payload
    if 'service_id' in request.json:
        fk_success, fk_error = validate_foreign_key(Service, request.json['service_id'], "Service")
        if not fk_success:
            return fk_error

    success, response, status_code = validate_and_update(
        instance=service_item,
        schema=service_item_schema,
        payload=request.json,
        foreign_keys={},
        return_json=True
    )
    return response, status_code


# Delete ServiceItem
'''
Preserving Service Items due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''