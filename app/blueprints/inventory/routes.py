
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import inventory_bp
from app.models import Inventory, db
from app.extensions import limiter, cache
from .schemas import inventory_schema, inventories_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update


# Create Inventory
@inventory_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_inventory():
    return validate_and_create(
        model=Inventory,
        payload=request.json,
        schema=inventory_schema,
        unique_fields=['name'],
        case_insensitive_fields=['name'],
        commit=True,
        return_json=True
    )


# Read/Get All Inventory
@inventory_bp.route('/all', methods=['GET'])
# @cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all inventory
def get_all_inventory():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Inventory)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(inventories_schema.dump(result)), 200
    except:
        query = select(Inventory)
        result = db.session.execute(query).scalars().all()
        return jsonify(inventories_schema.dump(result)), 200


# Read/Get Specific Inventory
@inventory_bp.route('/<int:id>')
# @mechanic_token_required
# Only mechanics can retrieve a single inventory
def get_inventory(id):
    inventory = db.session.get(Inventory, id)

    if not inventory:
        return jsonify({"message": "Invalid Inventory ID"}), 404

    return jsonify(inventory_schema.dump(inventory)), 200


# Update Inventory
@inventory_bp.route('/<int:id>', methods=['PUT'])
# @mechanic_token_required
# Only mechanics can update inventory
def update_inventory(id):
    inventory = db.session.get(Inventory, id)
    if not inventory:
        return jsonify({"message": "Invalid Inventory ID"}), 404

    success, response, status_code = validate_and_update(
        instance=inventory,
        schema=inventory_schema,
        payload=request.json,
        foreign_keys={},
        return_json=True
    )
    return response, status_code


# Delete Inventory
'''
Preserving Inventory history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''