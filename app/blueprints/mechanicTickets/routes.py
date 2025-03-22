
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_tickets_bp
from app.models import MechanicTicket, db, Mechanic, ServiceTicket, Service, ServiceItem, Inventory
from app.extensions import limiter, cache
from .schemas import mechanic_ticket_schema, mechanic_tickets_schema
from app.blueprints.shared.creation import create_service_item
from app.utils.util import mechanic_token_required
from datetime import date


# Create MechanicTicket
@mechanic_tickets_bp.route('/', methods=['POST'])
@mechanic_token_required
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
    
    new_ticket = MechanicTicket(
        start_date=mechanic_ticket_data.get('start_date') or date.today(),
        end_date=mechanic_ticket_data.get('end_date') or None,
        hours_worked=mechanic_ticket_data.get('hours_worked') or 0.0,
        service_ticket_id=service_ticket.id,
        mechanic_id=mechanic.id
    )

    service_ids = request.json.get('service_ids', [])
    if service_ids:
        for id in service_ids:
            service = db.session.get(Service, id)
            if not service:
                return jsonify({"message": f"Invalid Service ID: {id}"}), 404
            new_ticket.services.extend(service)
    '''
    addtl_items: [
        | ServiceItems |
        {
            item_id: int,   -> | Inventory |
            quantity: int       id: int,
        }, {                    name: str,
            item_id: int,       stock: int,
            quantity: int       price: float
        }, 
    ]

    '''
    addtl_items = request.json.get('additional_items', [])
    if addtl_items:
        for addtl_item in addtl_items:
            item_id = addtl_item['item_id']
            quantity = addtl_item['quantity']
            item = db.session.get(Inventory, item_id)

            if not item:
                return jsonify({"message": f"Invalid Item ID: {item_id}"}), 404
            if item.stock <= quantity:
                return jsonify({
                    "message": "Insufficient Stock for Item",
                    "stock_level": f"{item.stock}"
                    }), 409

            item.stock -= quantity
                    
            payload = {
                "item_id": item.id,
                "quantity": quantity
            }
            service_item = create_service_item(payload, commit=False)

            new_ticket.additional_items.extend(service_item)

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify(mechanic_ticket_schema.dump(new_ticket)), 201


# Read/Get All MechanicTickets
@mechanic_tickets_bp.route('/', methods=['GET'])
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


# Update MechanicTicket
@mechanic_tickets_bp.route('/<int:id', methods=['PUT'])
@mechanic_token_required
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

    service_ids = request.json.get('service_ids', [])
    if service_ids:
        for id in service_ids:
            service = db.session.get(Service, id)
            if not service:
                return jsonify({"message": f"Invalid Service ID: {id}"}), 404
            if service in mechanic_ticket.services:
                return jsonify({"message": f"Service already exists in Mechanic Ticket"}), 409
            mechanic_ticket.services.extend(service)         
    '''
    addtl_items: [
        | ServiceItems |
        {
            item_id: int,   -> | Inventory |
            quantity: int       id: int,
        }, {                    name: str,
            item_id: int,       stock: int,
            quantity: int       price: float
        }, 
    ]

    '''
    addtl_items = request.json.get('additional_items', [])
    if addtl_items:
        for addtl_item in addtl_items:
            item = db.session.get(ServiceItem, addtl_item['id'])
            if item in mechanic_ticket.additional_items:
                return jsonify({"message": f"Additional Item already exists in Mechanic Ticket"}), 409
            if not item:
                id = addtl_item['id']
                quant = addtl_item['quantity']
                inventory_item = db.session.get(Inventory, id)
                if not inventory_item:
                    return jsonify({"message": f"Invalid Item ID: {id}"}), 404
                if inventory_item.stock <= quant:
                    return jsonify({
                        "message": "Insufficient Stock for Item",
                        "stock_level": f"{inventory_item.stock}"
                        }), 409

                inventory_item.stock -= quant
                        
                new_item = ServiceItem(
                    item_id=id,
                    quantity=quant
                )
                mechanic_ticket.additional_items.extend(new_item)

    db.session.commit()

    return jsonify(mechanic_ticket_schema.dump(mechanic_ticket)), 200


# Delete MechanicTicket