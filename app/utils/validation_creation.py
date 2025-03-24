
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy import func
from app.models import db, Inventory


# Duplication Check
def is_duplicate(model, filters: dict, case_insensitive_fields: list = []):
    '''
    Universal reusable function
    Checks for duplicate data for other functionality
    '''
    query = model.query
    for key, value in filters.items():
        column = getattr(model, key)
        if key in case_insensitive_fields:
            query = query.filter(func.lower(column) == value.lower())
        else:
            query = query.filter(column == value)
    return query.first()


# Foreign Key Validation
def validate_foreign_key(model, id_, field_name="ID"):
    '''
    Universal reusable function
    Checks foreign keys before continuation of other functions
    '''
    instance = db.session.get(model, id_)
    if not instance:
        raise ValueError(f"Invalid {field_name}: {id_}")
    return instance


# Validation and Creation
def validate_and_create(model, payload, schema=None, unique_fields=None, case_insensitive_fields=None, commit=True, return_json=False):
    '''
    Universal reusable function
    Calls the is_duplicate check before continuation
    Then if not duplicate data allows for creation
    '''

    if unique_fields:
        filters = {field: payload[field] for field in unique_fields if field in payload}
        if is_duplicate(model, filters, case_insensitive_fields or []):
            msg = {"message": f"{model.__name__} with similar data already exists."}
            return (jsonify(msg), 409) if return_json else msg

    instance = model(**payload)

    db.session.add(instance)
    if commit:
        db.session.commit()

    if return_json and schema:
        return jsonify(schema.dump(instance)), 201
    return instance


# # Create ServiceItem
# def create_service_item(payload=None, commit=True, return_json=False):
#     from app.blueprints.serviceItems.schemas import service_item_schema
#     if payload is None:
#         payload = request.json

#     try:
#         service_item_data = service_item_schema.load(payload)
#     except ValidationError as ve:
#         if return_json:
#             return jsonify(ve.messages), 400
#         else:
#             raise
    
#     service_id = service_item_data.service_id
#     if service_id:
#         service = db.session.get(Service, service_id)
#         if not service:
#             if return_json:
#                 return jsonify({"message": "Invalid Service ID"}), 404
#             else:
#                 raise ValueError("Invalid Service ID")
        
#     new_service_item = ServiceItem(
#         item_id=service_item_data.item_id,
#         quantity=service_item_data.quantity,
#         service_id=service_id
#     )

#     db.session.add(new_service_item)
#     if commit:
#         db.session.commit()

#     if return_json:
#         return jsonify(service_item_schema.dump(new_service_item)), 201
#     return new_service_item


def check_and_update_inventory(uses=list[dict], commit=False):
    '''
    Ensures there is inventory available before allowing use of things
    If available, updates the inventory amounts respectively
    '''

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



def validate_and_update(instance, schema, payload, foreign_keys: dict = None):
    '''
    Validate and partially update a model instance using schema.

    Parameters:
    - instance: The object to update.
    - schema: The schema for validation.
    - payload: Dictionary of update values.
    - foreign_keys: Dict mapping foreign key fields to their corresponding model classes.

    Returns:
    - (True, updated_instance, 200) on success.
    - (False, response, error_code) on failure.
    '''

    try:
        data = schema.load(payload, instance=instance, partial=True)
    except ValidationError as ve:
        return False, jsonify(ve.messages), 400

    if foreign_keys:
        for field, model in foreign_keys.items():
            fk_id = payload.get(field)
            if fk_id is not None:
                valid, response = validate_foreign_key(model, fk_id)
                if not valid:
                    return False, response

    db.session.commit()
    return True, data, 200