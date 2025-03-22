
from flask import jsonify, request
from marshmallow import ValidationError
from app.models import ServiceItem, db, Service, Inventory
from app.blueprints.serviceItems.schemas import service_item_schema




# Create ServiceItem
def create_service_item(payload=None, commit=True, return_json=False):
    if payload is None:
        payload = request.json

    try:
        service_item_data = service_item_schema.load(payload)
    except ValidationError as ve:
        return (
            jsonify(ve.messages), 400
            if return_json or request else ve.messages
        )
    
    inventory_item = db.session.get(Inventory, service_item_data['item_id'])
    if not inventory_item:
        return (
            jsonify({"message": "Invalid Inventory Item ID"}), 404
            if return_json or request else {"error": "Invalid Inventory Item ID"}
        )
    
    service_id = service_item_data.get('service_id')
    if service_id:
        service = db.session.get(Service, service_id)
        if not service:
            return (
                jsonify({"message": "Invalid Service ID"}), 404
                if return_json or request else {"error": "Invalid Service ID"}
            )
        
    new_service_item = ServiceItem(
        item_id=service_item_data['item_id'],
        quantity=service_item_data['quantity'],
        service_id=service_id
    )


    db.session.add(new_service_item)
    if commit:
        db.session.commit()

    return (
        jsonify(service_item_schema.dump(new_service_item)), 201
        if return_json or request else new_service_item
    )