
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_tickets_bp
from app.models import MechanicTicket, db, Mechanic, ServiceTicket, Service, ServiceItem
from app.extensions import limiter, cache
from .schemas import mechanic_ticket_schema, mechanic_tickets_schema
from app.blueprints.serviceItems.schemas import service_item_schema
from app.utils.validation_creation import validate_and_create, check_and_update_inventory, validate_and_update
from app.utils.util import mechanic_token_required
from datetime import date


# Create MechanicTicket
@mechanic_tickets_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_mechanic_ticket():
    payload = request.json.copy()
    payload['start_date'] = date.today()
    service_ids = payload.pop('service_ids', [])
    additional_items = payload.pop('additional_items', [])

    new_ticket = validate_and_create(
        model=MechanicTicket, 
        payload=payload, 
        schema=mechanic_ticket_schema, 
        foreign_keys={
            "mechanic_id": Mechanic,
            "service_ticket_id": ServiceTicket
        },
        commit=False
        )

    # Attach services
    if service_ids:
        services = db.session.query(Service).filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            return jsonify({"message": "One or more service IDs are invalid."}), 404
        new_ticket.services.extend(services)

    # Collect inventory uses from service_items + additional_items
    all_uses = []
    for s in new_ticket.services:
        for si in s.service_items:
            all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    for item in additional_items:
        if 'item_id' not in item or 'quantity' not in item:
            return jsonify({"message": "Each additional item must include 'item_id' and 'quantity'."}), 400
        all_uses.append({"item_id": item['item_id'], "quantity": item['quantity']})

    success, result = check_and_update_inventory(all_uses)
    if not success:
        return jsonify(result), 409

    # Add additional_items as service items
    for item in additional_items:
        si_payload = {
            "item_id": item["item_id"],
            "quantity": item["quantity"]
        }
        service_item = validate_and_create(ServiceItem, si_payload, service_item_schema, commit=False)
        new_ticket.additional_items.append(service_item)

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify(mechanic_ticket_schema.dump(new_ticket)), 201


# Read/Get All MechanicTickets
@mechanic_tickets_bp.route('/all', methods=['GET'])
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve all MechanicTickets more than 10 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
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
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a single MechanicTicket more than 10 per hour
@mechanic_token_required
# Only mechanics can retrieve a single MechanicTicket
def get_mechanic_ticket(id):
    mechanic_ticket = db.session.get(MechanicTicket, id)

    if not mechanic_ticket:
        return jsonify({"message": "Invalid Mechanic Ticket ID"}), 404

    return jsonify(mechanic_ticket_schema.dump(mechanic_ticket)), 200

# Get Mechanic's tickets
# @mechanic_tickets_bp.route('/my-tickets/<int:id>', methods=['GET'])
@mechanic_tickets_bp.route('/my-tickets/', methods=['GET'])
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a mechanic's tickets more than 10 per hour
@mechanic_token_required
def get_my_tickets(id):
    query = select(MechanicTicket).where(MechanicTicket.mechanic_id == id)
    mechanic_tickets = db.session.execute(query).scalars().all()

    return jsonify(mechanic_tickets_schema.dump(mechanic_tickets)), 200


# Update MechanicTicket
# @mechanic_tickets_bp.route('/<int:id>', methods=['PUT'])
@mechanic_tickets_bp.route('/', methods=['PUT'])
@mechanic_token_required
def update_mechanic_ticket(id):
    mechanic_ticket = db.session.get(MechanicTicket, id)
    if not mechanic_ticket:
        return jsonify({"message": "Mechanic Ticket not found"}), 404

    payload = request.json.copy()
    service_ids = payload.pop("service_ids", None)
    additional_items = payload.pop("additional_items", None)

    # Update basic fields using validation
    success, response, status = validate_and_update(
        instance=mechanic_ticket,
        schema=mechanic_ticket_schema,
        payload=payload,
        foreign_keys={
            "mechanic_id": Mechanic,
            "service_ticket_id": ServiceTicket
        },
        return_json=True
    )
    if not success:
        return response, status

    # Update service associations if provided
    all_uses = []
    if service_ids is not None:
        services = db.session.query(Service).filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            return jsonify({"message": "One or more service IDs are invalid."}), 404
        mechanic_ticket.services = services

        for s in services:
            for si in s.service_items:
                all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    # Replace additional items if provided
    if additional_items is not None:
        mechanic_ticket.additional_items = []

        for item in additional_items:
            if "item_id" not in item or "quantity" not in item:
                return jsonify({"message": "Each additional item must include 'item_id' and 'quantity'."}), 400
            all_uses.append({"item_id": item["item_id"], "quantity": item["quantity"]})

    # Check inventory usage
    if all_uses:
        success, result = check_and_update_inventory(all_uses)
        if not success:
            return jsonify(result), 409

    # Add new additional_items
    if additional_items is not None:
        for item in additional_items:
            si_payload = {
                "item_id": item["item_id"],
                "quantity": item["quantity"]
            }
            service_item = validate_and_create(
                model=ServiceItem, 
                payload=si_payload, 
                schema=service_item_schema, 
                commit=False
                )
            mechanic_ticket.additional_items.append(service_item)

    db.session.commit()
    return response, status

# Delete MechanicTicket
'''
Preserving Mechanic Ticket history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''