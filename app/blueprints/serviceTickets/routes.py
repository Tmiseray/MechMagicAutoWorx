
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import service_tickets_bp
from app.models import ServiceTicket, Customer, Vehicle, Mechanic, db
from .schemas import service_ticket_schema, service_tickets_schema
from app.extensions import limiter, cache
from app.utils.util import token_required, mechanic_token_required
from datetime import date


# Create service_ticket
@service_tickets_bp.route('/', methods=['POST'])
@limiter.limit("20 per hour")
# Limit the number of service_ticket creations to 20 per hour
# There shouldn't be a need to create more than 20 service_tickets per hour
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.get(Customer, service_ticket_data['customer_id'])
    vehicle = db.session.get(Vehicle, service_ticket_data['VIN'])

    if not vehicle:
        return jsonify({"message": "Vehicle Not Found in Database"}), 404
    elif not customer:
        return jsonify({"message": "Invalid Customer ID"}), 404

    new_service_ticket = ServiceTicket(
        VIN=vehicle.VIN,
        service_date=service_ticket_data['service_date'] or date.today(),
        service_desc=service_ticket_data['service_desc'],
        customer_id=customer.id
    )

    db.session.add(new_service_ticket)
    db.session.commit()

    return jsonify(service_ticket_schema.dump(new_service_ticket)), 201


# Get all service_tickets
@service_tickets_bp.route('/', methods=['GET'])
@limiter.limit("20 per hour")
# Limit the number of retrievals to 20 per hour
# There shouldn't be a need to retrieve all service_tickets more than 20 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
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
@limiter.limit("20 per hour")
# Limit the number of retrievals to 20 per hour
# There shouldn't be a need to retrieve a single service_ticket more than 20 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID or Service Ticket Not in Database"}), 404

    return jsonify(service_ticket_schema.dump(service_ticket)), 200


# Update a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID"}), 404

    try:
        service_ticket_data = service_ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.get(Customer, service_ticket_data['customer_id'])
    vehicle = db.session.get(Vehicle, service_ticket_data['VIN'])

    if not vehicle:
        return jsonify({"message": "Vehicle Not Found in Database"}), 404
    elif not customer:
        return jsonify({"message": "Invalid Customer ID"}), 404

    # Update basic fields
    service_ticket.VIN = vehicle.VIN or service_ticket.VIN
    service_ticket.service_date = service_ticket_data.get('service_date') or service_ticket.service_date
    service_ticket.service_desc = service_ticket_data.get('service_desc') or service_ticket.service_desc
    service_ticket.customer_id = customer.id or service_ticket.customer_id

    db.session.commit()

    return jsonify(service_ticket_schema.dump(service_ticket)), 200


# Delete a service_ticket
@service_tickets_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
@mechanic_token_required
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"message": "Service Ticket Not Found"}), 404

    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({"message": "Service Ticket Deleted Successfully"}), 200