
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_tickets_bp
from app.models import MechanicTicket, db, Mechanic, ServiceTicket, Service
from app.extensions import limiter, cache
from .schemas import mechanic_ticket_schema, mechanic_tickets_schema
from app.blueprints.shared.creation import create_service_item, check_and_update_inventory
from app.utils.util import mechanic_token_required
from datetime import date


# Create MechanicTicket
@mechanic_tickets_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_mechanic_ticket():
    try:
        mechanic_ticket_data = mechanic_ticket_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    mechanic = db.session.get(Mechanic, mechanic_ticket_data['mechanic_id'])
    service_ticket = db.session.get(ServiceTicket, mechanic_ticket_data['service_ticket_id'])

    if not mechanic:
        return jsonify({"message": "Invalid Mechanic ID"}), 404
    elif not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID"}), 404
    
    mechanic_ticket = MechanicTicket(
        start_date=mechanic_ticket_data.get('start_date') or date.today(),
        end_date=mechanic_ticket_data.get('end_date') or None,
        hours_worked=mechanic_ticket_data.get('hours_worked') or 0.0,
        service_ticket_id=service_ticket.id,
        mechanic_id=mechanic.id
    )

    all_uses = []

    service_ids = request.json.get('service_ids', [])
    if service_ids:
        services = Service.query.filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            return jsonify({"message": "One or more invalid service IDs."}), 404
        mechanic_ticket.services.extend(services)

        for service in services:
            for si in service.service_items:
                all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    addtl_items = request.json.get('additional_items', [])
    for addtl_item in addtl_items:
        all_uses.append({
            "item_id": addtl_item['item_id'],
            "quantity": addtl_item['quantity']
        })

    # Validate inventory
    success, result = check_and_update_inventory(all_uses)
    if not success:
        return jsonify(result), 409

    # Create service_items for additional_items
    for addtl_item in addtl_items:
        payload = {
            "item_id": addtl_item["item_id"],
            "quantity": addtl_item["quantity"]
        }
        service_item = create_service_item(payload, commit=False)
        mechanic_ticket.additional_items.append(service_item)

    db.session.add(mechanic_ticket)
    db.session.commit()
    return jsonify(mechanic_ticket_schema.dump(mechanic_ticket)), 201


# Read/Get All MechanicTickets
@mechanic_tickets_bp.route('/all', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve all MechanicTickets more than 10 per hour
# @cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all MechanicTickets
def get_mechanic_tickets():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(MechanicTicket)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(mechanic_tickets_schema.dump(result)), 200
    except:
        query = select(MechanicTicket)
        result = db.session.execute(query).scalars().all()
        return jsonify(mechanic_tickets_schema.dump(result)), 200


# Read/Get Specific MechanicTicket
@mechanic_tickets_bp.route('/<int:id>', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a single MechanicTicket more than 10 per hour
# @mechanic_token_required
# Only mechanics can retrieve a single MechanicTicket
def get_mechanic_ticket(id):
    mechanic_ticket = db.session.get(MechanicTicket, id)

    if not mechanic_ticket:
        return jsonify({"message": "Invalid Mechanic Ticket ID"}), 404

    return jsonify(mechanic_ticket_schema.dump(mechanic_ticket)), 200

# Get Mechanic's tickets
@mechanic_tickets_bp.route('/my-tickets/<int:id>', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a mechanic's tickets more than 10 per hour
# @mechanic_token_required
def get_my_tickets(id):
    query = select(MechanicTicket).where(MechanicTicket.mechanic_id == id)
    mechanic_tickets = db.session.execute(query).scalars().all()

    return jsonify(mechanic_tickets_schema.dump(mechanic_tickets)), 200


# Update MechanicTicket
@mechanic_tickets_bp.route('/<int:id>', methods=['PUT'])
# @mechanic_token_required
def update_mechanic_ticket(id):
    mechanic_ticket = db.session.get(MechanicTicket, id)

    if not mechanic_ticket:
        return jsonify({"message": "Invalid Mechanic Ticket ID"}), 404
    
    try:
        ticket_data = mechanic_ticket_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    mechanic_ticket.end_date = ticket_data.get('end_date') or mechanic_ticket.end_date
    mechanic_ticket.hours_worked = ticket_data.get('hours_worked') or mechanic_ticket.hours_worked

    all_uses = []

    # Replace services if provided
    if 'service_ids' in request.json:
        service_ids = request.json.get('service_ids', [])
        services = Service.query.filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            return jsonify({"message": "One or more invalid service IDs."}), 404

        mechanic_ticket.services = services
        for service in services:
            for si in service.service_items:
                all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    # Replace additional_items if provided
    if 'additional_items' in request.json:
        mechanic_ticket.additional_items = []
        addtl_items = request.json.get('additional_items', [])
        for item in addtl_items:
            all_uses.append({
                "item_id": item['item_id'],
                "quantity": item['quantity']
            })

    # Check inventory before proceeding
    if all_uses:
        success, result = check_and_update_inventory(all_uses)
        if not success:
            return jsonify(result), 409

    # Rebuild additional_items
    if 'additional_items' in request.json:
        for item in request.json['additional_items']:
            payload = {
                "item_id": item["item_id"],
                "quantity": item["quantity"]
            }
            service_item = create_service_item(payload, commit=False)
            mechanic_ticket.additional_items.append(service_item)

    db.session.commit()
    return jsonify(mechanic_ticket_schema.dump(mechanic_ticket)), 200


# Delete MechanicTicket