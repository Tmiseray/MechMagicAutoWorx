
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_tickets_bp
from app.models import MechanicTicket, db, Mechanic, ServiceTicket, Service, ServiceItem
from app.extensions import limiter, cache
from .schemas import mechanic_ticket_schema, mechanic_tickets_schema
from app.blueprints.serviceItems.schemas import service_item_schema
from app.utils.validation_creation import validate_and_create, check_and_update_inventory, validate_foreign_key, validate_and_update
from app.utils.util import mechanic_token_required
from datetime import date


# Create MechanicTicket
@mechanic_tickets_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_mechanic_ticket():
    payload = request.json
    payload['start_date'] = date.today()

    # Validate foreign keys
    try:
        validate_foreign_key(Mechanic, payload.get('mechanic_id'), "Mechanic ID")
        validate_foreign_key(ServiceTicket, payload.get('service_ticket_id'), "Service Ticket ID")
    except ValueError as e:
        return jsonify({"message": str(e)}), 404

    new_ticket, err = validate_and_create(MechanicTicket, mechanic_ticket_schema, payload, commit=False)
    if err:
        return err

    # Attach services
    service_ids = payload.get('service_ids', [])
    if service_ids:
        services = Service.query.filter(Service.id.in_(service_ids)).all()
        new_ticket.services.extend(services)

    # Collect inventory uses from service_items + additional_items
    all_uses = []
    for s in new_ticket.services:
        for si in s.service_items:
            all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    for item in payload.get('additional_items', []):
        all_uses.append({"item_id": item['item_id'], "quantity": item['quantity']})

    success, result = check_and_update_inventory(all_uses)
    if not success:
        return jsonify(result), 409

    # Add additional_items as service items
    for item in payload.get('additional_items', []):
        si_payload = {
            "item_id": item["item_id"],
            "quantity": item["quantity"]
        }
        service_item, _ = validate_and_create(ServiceItem, service_item_schema, si_payload, commit=False)
        new_ticket.additional_items.append(service_item)

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify(mechanic_ticket_schema.dump(new_ticket)), 201


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

    payload = request.json

    # Validate foreign keys
    fk_result = validate_foreign_key(payload, {
        "mechanic_id": Mechanic,
        "service_ticket_id": ServiceTicket
    })
    if fk_result:
        return fk_result

    all_uses = []

    # Replace services if provided
    if "service_ids" in payload:
        service_ids = payload["service_ids"]
        services = Service.query.filter(Service.id.in_(service_ids)).all()
        if len(services) != len(service_ids):
            return jsonify({"message": "One or more invalid service IDs."}), 404
        mechanic_ticket.services = services

        for s in services:
            for si in s.service_items:
                all_uses.append({"item_id": si.item_id, "quantity": si.quantity})

    # Replace additional_items if provided
    if "additional_items" in payload:
        mechanic_ticket.additional_items.clear()
        for item in payload["additional_items"]:
            all_uses.append({"item_id": item["item_id"], "quantity": item["quantity"]})

    # Check inventory
    if all_uses:
        success, result = check_and_update_inventory(all_uses)
        if not success:
            return jsonify(result), 409

    # Recreate additional_items using validate_and_create
    if "additional_items" in payload:
        for item in payload["additional_items"]:
            item["service_id"] = None  # Optional, since these are stand-alone
            new_item = validate_and_create(
                model=ServiceItem,
                payload=item,
                schema=service_item_schema,
                commit=False,
                return_json=False
            )
            mechanic_ticket.additional_items.append(new_item)

    # Final generic updates
    success, response, status_code = validate_and_update(
        instance=mechanic_ticket,
        schema=mechanic_ticket_schema,
        payload=payload,
        foreign_keys={},  # Already validated
    )
    return response, status_code


# Delete MechanicTicket
'''
Preserving Mechanic Ticket history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''