
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_tickets_bp
from app.models import ServiceTicket, Customer, Vehicle, Mechanic, db
from .schemas import service_ticket_schema, service_tickets_schema
from app.extensions import limiter, cache
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_and_update
from datetime import date


# Create service_ticket
@service_tickets_bp.route('/', methods=['POST'])
# @limiter.limit("20 per hour")
# # Limit the number of service_ticket creations to 20 per hour
# # There shouldn't be a need to create more than 20 service_tickets per hour
def create_service_ticket():
    payload = request.json

    # Ensure foreign keys exist
    foreign_keys = {
        "customer_id": Customer,
        "VIN": Vehicle
    }

    return validate_and_create(
        model=ServiceTicket, 
        payload=payload, 
        schema=service_ticket_schema,
        unique_fields=[
            'service_desc',
            'service_date'
        ],
        case_insensitive_fields=[
            'service_desc',
            'service_date'
        ],
        foreign_keys=foreign_keys,
        commit=True,
        return_json=True
        )


# Get all service_tickets
@service_tickets_bp.route('/all', methods=['GET'])
# @limiter.limit("20 per hour")
# # Limit the number of retrievals to 20 per hour
# # There shouldn't be a need to retrieve all service_tickets more than 20 per hour
# @cache.cached(timeout=60)
# # Cache the response for 60 seconds
# # This will help reduce the load on the database
# @mechanic_token_required
def get_service_tickets():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(ServiceTicket)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(service_tickets_schema.dump(result)), 200
    except:
        query = select(ServiceTicket)
        result = db.session.execute(query).scalars().all()
        return jsonify(service_tickets_schema.dump(result)), 200


# Get single service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['GET'])
# @limiter.limit("20 per hour")
# # Limit the number of retrievals to 20 per hour
# # There shouldn't be a need to retrieve a single service_ticket more than 20 per hour
# @cache.cached(timeout=60)
# # Cache the response for 60 seconds
# # This will help reduce the load on the database
# @mechanic_token_required
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID or Service Ticket Not in Database"}), 404

    return jsonify(service_ticket_schema.dump(service_ticket)), 200


# Get customer's service tickets
@service_tickets_bp.route('/my-tickets/<int:customer_id>', methods=['GET'])
# @service_tickets_bp.route('/my-tickets', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a customer's service tickets more than 10 per hour
# @token_required
def get_my_service_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    service_tickets = db.session.execute(query).scalars().all()

    return jsonify(service_tickets_schema.dump(service_tickets)), 200


# Update a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
# @mechanic_token_required
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID"}), 404

    payload = request.json

    # Ensure foreign keys exist
    foreign_keys = {
        "customer_id": Customer,
        "VIN": Vehicle
    }

    # Proceed with generic validation and update
    success, response, status_code = validate_and_update(
        instance=service_ticket,
        schema=service_ticket_schema,
        payload=payload,
        foreign_keys=foreign_keys,
        return_json=True
    )
    return response, status_code


# # Delete a service_ticket
'''
Preserving Service Ticket history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''