
from flask import jsonify, request
from marshmallow import ValidationError
from app.models import ServiceItem, db, Service, Inventory





# Create ServiceItem
def create_service_item(payload=None, commit=True, return_json=False):
    from app.blueprints.serviceItems.schemas import service_item_schema
    if payload is None:
        payload = request.json

    try:
        service_item_data = service_item_schema.load(payload)
    except ValidationError as ve:
        return (
            jsonify(ve.messages), 400
            if return_json or request else ve.messages
        )
    
    service_id = service_item_data.service_id
    if service_id:
        service = db.session.get(Service, service_id)
        if not service:
            return (
                jsonify({"message": "Invalid Service ID"}), 404
                if return_json or request else {"error": "Invalid Service ID"}
            )
        
    new_service_item = ServiceItem(
        item_id=service_item_data.item_id,
        quantity=service_item_data.quantity,
        service_id=service_id
    )

    db.session.add(new_service_item)
    if commit:
        db.session.commit()

    return (
        jsonify(service_item_schema.dump(new_service_item)), 201
        if return_json or request else new_service_item
    )


def check_and_update_inventory(uses=list[dict], commit=False):
    if not uses:
        return True, []
    
    item_ids = [u['item_id'] for u in uses]
    inventory_map = {
        item.id: item for item in Inventory.query.filter(Inventory.id.in_(item_ids)).all()
    }

    updated_items = []

    for use in uses:
        item_id = use['item_id']
        qty = use['quantity']
        item = inventory_map.get(item_id)

        if not item:
            return False, {"message": f"Item ID {item_id} not found"}
        
        if item.stock < qty:
            return False, {
                "message": f"Insuficient stock for item '{item.name}' (ID {item.id})",
                "available": item.stock,
                "requested": qty
            }
        
        item.stock -= qty
        updated_items.append(item)

    if commit:
        db.session.commit()

    return True, updated_items