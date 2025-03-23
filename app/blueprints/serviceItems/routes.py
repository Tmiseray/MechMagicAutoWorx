
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_items_bp
from app.models import ServiceItem, db
from app.extensions import limiter, cache
from .schemas import service_item_schema, service_items_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.creation import create_service_item



# Creating Reusable Route for shared/creation.py
@service_items_bp.route('/', methods=['POST'])
# @mechanic_token_required
# def create_service_item_route(user_id, role):
def create_service_item_route():
    return create_service_item()


# Read/Get All ServiceItems
@service_items_bp.route('/all', methods=['GET'])
@cache.cached(timeout=60)
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

    try:
        service_item_data = service_item_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400

    service_item.item_id = service_item_data.item_id or service_item.item_id
    service_item.quantity = service_item_data.quantity or service_item.quantity
    service_item.service_id = service_item_data.service_id or service_item.service_id

    db.session.commit()

    return jsonify(service_item_schema.dump(service_item)), 200 


# Delete ServiceItem