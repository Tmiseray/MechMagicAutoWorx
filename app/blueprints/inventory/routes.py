
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import inventory_bp
from app.models import Inventory, db
from app.extensions import limiter, cache
from .schemas import inventory_schema, inventories_schema
from app.utils.util import token_required, mechanic_token_required


# Create Inventory
@inventory_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    new_inventory = Inventory(
        name=inventory_data['name'],
        stock=inventory_data['stock'],
        price=float(inventory_data['price'])
    )

    db.session.add(new_inventory)
    db.session.commit()

    return jsonify(inventory_schema.dump(new_inventory)), 201


# Read/Get All Inventory
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
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
@mechanic_token_required
# Only mechanics can retrieve a single inventory
def get_inventory(id):
    inventory = db.session.get(Inventory, id)

    if not inventory:
        return jsonify({"message": "Invalid inventory ID"}), 404

    return jsonify(inventory_schema.dump(inventory)), 200


# Update Inventory
@inventory_bp.route('/<int:id>', methods=['PUT'])
@mechanic_token_required
# Only mechanics can update inventory
def update_inventory(id):
    inventory = db.session.get(Inventory, id)

    if not inventory:
        return jsonify({"message": "Invalid inventory ID"}), 404

    try:
        inventory_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400

    inventory.name = inventory_data.get('name') or inventory.name
    inventory.stock = inventory_data.get('stock') or inventory.stock
    inventory.price = inventory_data.get('price') or inventory.price

    db.session.commit()

    return jsonify(inventory_schema.dump(inventory)), 200 


# Delete Inventory
