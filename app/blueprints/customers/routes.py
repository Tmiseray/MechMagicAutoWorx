
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from app.models import Customer, db
from .schemas import customer_schema, customers_schema
from app.extensions import limiter, cache
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update



# Create Customer
@customers_bp.route('/', methods=['POST'])
# @limiter.limit("3 per hour")
# Limit the number of customer creations to 3 per hour
# There shouldn't be a need to create more than 3 customers per hour
def create_customer():
    return validate_and_create(
        model=Customer,
        payload=request.json,
        schema=customer_schema,
        unique_fields=['email'],
        case_insensitive_fields=['email'],
        foreign_keys=None,
        commit=True,
        return_json=True
    )


# Get all customers
@customers_bp.route('/all', methods=['GET'])
# @limiter.limit("10 per hour")
# # Limit the number of retrievals to 10 per hour
# # There shouldn't be a need to retrieve all customers more than 10 per hour
# @cache.cached(timeout=60)
# # Cache the response for 60 seconds
# # This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all customers
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Customer)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(customers_schema.dump(result)), 200
    except:
        query = select(Customer)
        result = db.session.execute(query).scalars().all()
        return jsonify(customers_schema.dump(result)), 200


# Get single customer
@customers_bp.route('/<int:id>', methods=['GET'])
# @limiter.limit("10 per hour")
# # Limit the number of retrievals to 10 per hour
# # There shouldn't be a need to retrieve a single customer more than 10 per hour
# @mechanic_token_required
# # Only mechanics can retrieve a single customer
def get_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid Customer ID or Customer Not in Database"}), 404

    return jsonify(customer_schema.dump(customer)), 200


# Update a customer
@customers_bp.route('/<int:id>', methods=['PUT'])
# @customers_bp.route('/', methods=['PUT'])
# @token_required
def update_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"message": "Invalid Customer ID or Customer Not in Database"}), 404

    payload = request.json

    success, response, status_code = validate_and_update(
        instance=customer,
        schema=customer_schema,
        payload=payload,
        foreign_keys={},
        return_json=True
    )
    return response, status_code


# Delete a customer
@customers_bp.route('/<int:id>', methods=['DELETE'])
# @customers_bp.route('/', methods=['DELETE'])
# @token_required
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid Customer ID or Customer Not in Database"}), 404

    # Set customer_id to NULL for related service tickets
    for service_ticket in customer.service_tickets:
        service_ticket.customer_id = None

    # Set customer_id to NULL for related account
    if customer.account:
        db.session.delete(customer.account)

    # Set customer_id to NULL for related vehicles
    for vehicle in customer.vehicles or []:
        vehicle.customer_id = None

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer Successfully Deleted"}), 200
