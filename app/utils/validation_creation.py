
from flask import jsonify
from sqlalchemy import func
from marshmallow import ValidationError
from app.models import db, Inventory


# Duplication Check
def is_duplicate(model, filters: dict, case_insensitive_fields: list = []):
    '''
    Universal reusable function
    Checks for duplicate data for other functionality
    '''
    query = db.session.query(model)
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


# Incase there are many FK to check
def validate_foreign_keys(payload: dict, model_map: dict):
    for key, model in model_map.items():
        id_ = payload.get(key)
        if id_ is not None:
            validate_foreign_key(model, id_, key)


# Validation and Creation
def validate_and_create(
        model, 
        payload, 
        schema=None, 
        unique_fields=None, 
        case_insensitive_fields=None, 
        foreign_keys=None,
        commit=True, 
        return_json=False
        ):
    '''
    Universal reusable function
    Calls the validate_foreign_keys before continuation
    Calls the is_duplicate check before continuation
    Then if not duplicate data allows for creation
    '''

    # 1. Validate Foreign Keys (if needed)
    if foreign_keys:
        try:
            validate_foreign_keys(payload, foreign_keys)
        except ValueError as e:
            msg = {"message": str(e)}
            return (jsonify(msg), 404) if return_json else msg
    
    # 2. Validate Unique Fields for Duplicate Data
    if unique_fields:
        filters = {field: payload[field] for field in unique_fields if field in payload}
        if is_duplicate(model, filters, case_insensitive_fields or []):
            msg = {"message": f"{model.__name__} with similar data already exists."}
            return (jsonify(msg), 409) if return_json else msg

    # 3. Validate Payload with Schema (if provided) & Create Instance
    if schema:
        try:
            instance = schema.load(payload)  # ✅ now instance, not dict
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400
    else:
        instance = model(**payload)

    # 4. Continue Creation
    db.session.add(instance)
    if commit:
        db.session.commit()

    if return_json and schema:
        return jsonify(schema.dump(instance)), 201
    return instance


def check_and_update_inventory(uses=list[dict], commit=False):
    '''
    Ensures there is inventory available before allowing use of things
    If available, updates the inventory amounts respectively
    '''

    if not uses:
        return True, []
    
    item_ids = [u['item_id'] for u in uses]
    inventory_map = {
        item.id: item for item in db.session.query(Inventory).filter(Inventory.id.in_(item_ids)).all()
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
                "message": f"Insufficient stock for item '{item.name}' (ID {item.id})",
                "available": item.stock,
                "requested": qty
            }
        
        item.stock -= qty
        updated_items.append(item)

    if commit:
        db.session.commit()

    return True, updated_items



def validate_and_update(
        instance, 
        schema, 
        payload, 
        foreign_keys=None, 
        return_json=False
        ):
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
    # 1. Validate foreign keys
    if foreign_keys:
        fk_result = validate_foreign_keys(payload, foreign_keys)
        if fk_result:
            return False, fk_result, 404

    # 2. Load into existing instance to avoid __init__ call
    updated_instance = schema.load(payload, instance=instance, partial=True)

    db.session.commit()

    if return_json:
        return True, jsonify(schema.dump(updated_instance)), 200
    return True, updated_instance, 200